from decimal import Decimal
from io import BytesIO
from unittest.mock import patch
import json

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import (
    DeliveryAgent,
    Order,
    OrderItem,
    PaymentTransaction,
    Product,
    SellerPayoutRequest,
    SellerProfile,
    SellerWallet,
)
from .payouts import request_seller_payout, transition_seller_payout
from .payments import normalize_phone


class PayoutHardeningTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("payoutseller", "seller@example.com", "test-pass-1")
        self.seller = SellerProfile.objects.create(
            user=self.user, business_name="Payout Seller",
            mpesa_phone="254712345678", is_active=True,
        )
        self.wallet = SellerWallet.objects.create(
            seller=self.seller, available_balance=Decimal("1000.00")
        )

    def test_reservation_and_terminal_failure_refund(self):
        payout, created = request_seller_payout(
            self.seller, "600", "0712345678", "payout-key-1"
        )
        self.assertTrue(created)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.available_balance, Decimal("400.00"))
        self.assertEqual(payout.phone, "254712345678")
        transition_seller_payout(payout.id, "processing")
        transition_seller_payout(payout.id, "failed", failure_reason="provider")
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.available_balance, Decimal("1000.00"))

    def test_duplicate_key_does_not_reserve_twice(self):
        first, created = request_seller_payout(
            self.seller, "500", "0712345678", "payout-key-2"
        )
        second, again = request_seller_payout(
            self.seller, "500", "0712345678", "payout-key-2"
        )
        self.wallet.refresh_from_db()
        self.assertTrue(created)
        self.assertFalse(again)
        self.assertEqual(first.id, second.id)
        self.assertEqual(self.wallet.available_balance, Decimal("500.00"))
        self.assertEqual(SellerPayoutRequest.objects.count(), 1)

    def test_terminal_payout_cannot_be_reopened(self):
        payout, _ = request_seller_payout(
            self.seller, "100", "0712345678", "payout-key-3"
        )
        transition_seller_payout(payout.id, "paid")
        with self.assertRaises(ValidationError):
            transition_seller_payout(payout.id, "failed")


class CheckoutAndCartHardeningTests(TestCase):
    def setUp(self):
        user = User.objects.create_user("checkoutseller", "checkout@example.com", "test-pass-2")
        self.seller = SellerProfile.objects.create(
            user=user, business_name="Checkout Seller",
            business_latitude=Decimal("-1.300000"),
            business_longitude=Decimal("36.800000"),
            is_active=True,
        )
        SellerWallet.objects.create(seller=self.seller)
        self.product = Product.objects.create(
            name="Checkout Test", price=Decimal("100.00"),
            stock_quantity=20, sku="CHECKOUT-TEST-1", seller=self.seller,
        )

    @patch("home.checkout_map.calculate_order_quote")
    def test_same_checkout_key_creates_only_one_order(self, quote):
        quote.return_value = {
            "subtotal": Decimal("100.00"), "commission": Decimal("5.00"),
            "delivery_fee": Decimal("150.00"), "distance_km": Decimal("1.20"),
            "distance_source": "estimated", "seller_count": 1,
            "total": Decimal("255.00"),
        }
        client = Client()
        session = client.session
        session["cart"] = {str(self.product.id): 1}
        session.save()
        key = "4e4d8a5d-7fc6-4a2c-a8cc-bc7d8e4c0f53"
        payload = {
            "customer_name": "Test Customer", "email": "customer@example.com",
            "phone": "0712345678", "address": "Test address",
            "delivery_latitude": "-1.290000", "delivery_longitude": "36.820000",
            "payment_method": "cod", "checkout_key": key,
        }
        self.assertEqual(client.post(reverse("checkout"), payload).status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(PaymentTransaction.objects.count(), 1)
        session = client.session
        session["cart"] = {str(self.product.id): 1}
        session["checkout_key"] = key
        session.save()
        self.assertEqual(client.post(reverse("checkout"), payload).status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(PaymentTransaction.objects.count(), 1)

    def test_cart_add_get_is_rejected(self):
        self.assertEqual(
            self.client.get(reverse("add_to_cart", args=[self.product.id])).status_code, 405
        )


class FulfillmentAndPaymentHardeningTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            "customer-harden", "customer-harden@example.com", "test-pass-3"
        )
        seller_user = User.objects.create_user(
            "seller-harden", "seller-harden@example.com", "test-pass-4"
        )
        self.seller = SellerProfile.objects.create(
            user=seller_user,
            business_name="Hardening Seller",
            business_latitude=Decimal("-1.300000"),
            business_longitude=Decimal("36.800000"),
            is_active=True,
        )
        SellerWallet.objects.create(seller=self.seller)
        self.product = Product.objects.create(
            name="Harden Product",
            price=Decimal("100.00"),
            stock_quantity=10,
            sku="HARDEN-PRODUCT-1",
            seller=self.seller,
        )
        self.order = Order.objects.create(
            customer_name="Hardening Customer",
            customer=self.customer,
            email=self.customer.email,
            phone="0712345678",
            address="Test address",
            total_amount=Decimal("255.00"),
            items_subtotal=Decimal("100.00"),
            platform_commission_amount=Decimal("5.00"),
            delivery_fee=Decimal("150.00"),
            payment_status="pending",
            status="pending",
            tracking_code="SPV-HARDENING",
        )
        OrderItem.objects.create(
            order=self.order, product=self.product, quantity=1,
            price=Decimal("100.00"), seller=self.seller,
            seller_gross=Decimal("100.00"),
            platform_commission=Decimal("5.00"),
            seller_net=Decimal("100.00"),
        )
        self.product.stock_quantity = 9
        self.product.save(update_fields=["stock_quantity"])

    @patch("home.payments.query_mpesa_stk")
    def test_provider_query_failure_blocks_positive_callback(self, query):
        payment = PaymentTransaction.objects.create(
            order=self.order, method="mpesa", provider="daraja",
            amount=Decimal("255.00"), phone="254712345678",
            merchant_request_id="MERCHANT-1",
            checkout_request_id="CHECKOUT-1",
            idempotency_key="MPESA-HARDEN-1",
            status="pending",
        )
        query.return_value = {
            "ResponseCode": "0",
            "ResultCode": "2002",
            "ResultDesc": "merchant mismatch",
            "CheckoutRequestID": "CHECKOUT-1",
            "MerchantRequestID": "MERCHANT-1",
        }
        payload = {
            "Body": {"stkCallback": {
                "ResultCode": 0, "ResultDesc": "Success",
                "CheckoutRequestID": "CHECKOUT-1",
                "MerchantRequestID": "MERCHANT-1",
                "CallbackMetadata": {"Item": [
                    {"Name": "Amount", "Value": 255},
                    {"Name": "MpesaReceiptNumber", "Value": "QABC123"},
                    {"Name": "PhoneNumber", "Value": 254712345678},
                ]},
            }}
        }
        response = self.client.post(
            reverse("mpesa_callback"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.order.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(payment.status, "failed")
        self.assertEqual(self.order.payment_status, "failed")
        self.assertEqual(self.product.stock_quantity, 10)

    @patch("home.payments.query_mpesa_stk")
    def test_successful_query_requires_matching_callback_metadata(self, query):
        payment = PaymentTransaction.objects.create(
            order=self.order, method="mpesa", provider="daraja",
            amount=Decimal("255.00"), phone="254712345678",
            merchant_request_id="MERCHANT-2",
            checkout_request_id="CHECKOUT-2",
            idempotency_key="MPESA-HARDEN-2",
            status="pending",
        )
        query.return_value = {
            "ResponseCode": "0", "ResultCode": "0",
            "ResultDesc": "success",
            "CheckoutRequestID": "CHECKOUT-2",
            "MerchantRequestID": "MERCHANT-2",
        }
        bad_payload = {
            "Body": {"stkCallback": {
                "ResultCode": 0, "ResultDesc": "Success",
                "CheckoutRequestID": "CHECKOUT-2",
                "MerchantRequestID": "MERCHANT-2",
                "CallbackMetadata": {"Item": [
                    {"Name": "Amount", "Value": 254},
                    {"Name": "MpesaReceiptNumber", "Value": "QABC123"},
                    {"Name": "PhoneNumber", "Value": 254712345678},
                ]},
            }}
        }
        response = self.client.post(
            reverse("mpesa_callback"),
            data=json.dumps(bad_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(payment.status, "pending")
        self.assertEqual(self.order.payment_status, "pending")


class DeliverySecurityHardeningTests(TestCase):
    def test_inactive_delivery_agent_cannot_self_activate(self):
        user = User.objects.create_user(
            "pending-delivery", "pending-delivery@example.com", "test-pass-5"
        )
        agent = DeliveryAgent.objects.create(
            user=user,
            phone="254712345679",
            vehicle_type="Motorbike",
            is_active=False,
            status="offline",
        )
        response = self.client.post(
            reverse("delivery_login"),
            {"username": user.username, "password": "test-pass-5"},
        )
        self.assertEqual(response.status_code, 200)
        agent.refresh_from_db()
        self.assertFalse(agent.is_active)

    def test_preflight_accepts_current_fee_bearing_order_accounting(self):
        call_command("system_preflight")


class VoiceSecurityHardeningTests(TestCase):
    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "shopiva-voice-auth-tests",
            }
        }
    )
    def test_voice_endpoints_require_login(self):
        self.assertEqual(
            self.client.post(reverse("voice_transcribe")).status_code, 401
        )
        self.assertEqual(
            self.client.post(reverse("voice_speak"), {"text": "hello"}).status_code, 401
        )
        self.assertEqual(
            self.client.post(
                reverse("realtime_action"), {"action": "search_products"}
            ).status_code,
            401,
        )
        self.assertEqual(
            self.client.post(
                reverse("realtime_call"),
                b"v=0",
                content_type="application/sdp",
            ).status_code,
            401,
        )

    @override_settings(
        OPENAI_API_KEY="test-key",
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "shopiva-voice-rate-tests",
            }
        },
    )
    def test_realtime_action_is_rate_limited(self):
        user = User.objects.create_user(
            "voice-hardening", "voice-hardening@example.com", "test-pass-6"
        )
        self.client.force_login(user)
        for _ in range(8):
            self.assertEqual(
                self.client.post(
                    reverse("realtime_action"), {"action": "unknown"}
                ).status_code,
                400,
            )
        self.assertEqual(
            self.client.post(
                reverse("realtime_action"), {"action": "unknown"}
            ).status_code,
            429,
        )


class ProductUploadHardeningTests(TestCase):
    def test_tiny_product_image_is_rejected(self):
        image = Image.new("RGB", (100, 100))
        output = BytesIO()
        image.save(output, format="PNG")
        upload = SimpleUploadedFile(
            "tiny.png", output.getvalue(), content_type="image/png"
        )
        form = SellerProductForm(
            data={
                "catalog_product": "CUSTOM PRODUCT",
                "name": "Tiny Product",
                "description": "",
                "category": "General",
                "brand": "",
                "gtin": "",
                "mpn": "",
                "price": "100",
                "stock_quantity": "1",
                "discount_percent": "0",
                "promo_text": "",
            },
            files={"image": upload},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)
