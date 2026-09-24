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
