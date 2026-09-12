import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from .commission import get_platform_commission_percent, split_sale_amount
from .forms import CustomerRegistrationForm, SellerRegistrationForm
from .models import (
    CustomerAddress,
    Order,
    OrderItem,
    PaymentTransaction,
    SellerProfile,
    SellerSettlement,
    SellerWallet,
    Product,
    ProductReview,
)
from .payments import _create_seller_settlements


class CustomerRegistrationTests(TestCase):
    def test_duplicate_username_is_rejected_case_insensitively(self):
        User.objects.create_user(username="McBrianTech", email="one@example.com", password="StrongPass123!")
        form = CustomerRegistrationForm(data={
            "username": "mCbRiAnTeCh", "email": "two@example.com",
            "password1": "StrongPass123!", "password2": "StrongPass123!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("Username exists", str(form.errors["username"]))

    def test_duplicate_email_is_rejected_case_insensitively(self):
        User.objects.create_user(username="firstuser", email="User@Example.com", password="StrongPass123!")
        form = CustomerRegistrationForm(data={
            "username": "seconduser", "email": "user@example.com",
            "password1": "StrongPass123!", "password2": "StrongPass123!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("already registered", str(form.errors["email"]))


class SellerRegistrationTests(TestCase):
    def test_duplicate_username_is_rejected_case_insensitively(self):
        User.objects.create_user(username="SellerPrime", email="seller1@example.com", password="StrongPass123!")
        form = SellerRegistrationForm(data={
            "username": "sellerprime", "email": "seller2@example.com",
            "password1": "StrongPass123!", "password2": "StrongPass123!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("Username exists", str(form.errors["username"]))


class CommissionScheduleTests(TestCase):
    def test_commission_rate_rises_with_price(self):
        self.assertEqual(get_platform_commission_percent(Decimal("500.00")), Decimal("5.00"))
        self.assertEqual(get_platform_commission_percent(Decimal("1000.00")), Decimal("7.50"))
        self.assertEqual(get_platform_commission_percent(Decimal("5000.00")), Decimal("10.00"))
        self.assertEqual(get_platform_commission_percent(Decimal("10000.00")), Decimal("12.50"))
        self.assertEqual(get_platform_commission_percent(Decimal("50000.00")), Decimal("15.00"))

    def test_sale_split_is_price_based(self):
        rate, commission, seller_amount = split_sale_amount(Decimal("10000.00"))
        self.assertEqual(rate, Decimal("12.50"))
        self.assertEqual(commission, Decimal("1250.00"))
        self.assertEqual(seller_amount, Decimal("8750.00"))


class AdminLoginTests(TestCase):
    def test_admin_login_page_loads(self):
        response = self.client.get(reverse("admin_login"), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shopiva Control Center")

    def test_staff_can_login_to_control_center(self):
        User.objects.create_user(username="admin_test", email="admin@example.com", password="StrongPass123!", is_staff=True)
        response = self.client.post(
            reverse("admin_login"),
            {"username": "admin_test", "password": "StrongPass123!"},
            secure=True,
        )
        self.assertRedirects(response, reverse("shopiva_admin:index"), fetch_redirect_response=False)

    def test_customer_cannot_login_to_control_center(self):
        User.objects.create_user(username="customer_test", email="customer@example.com", password="StrongPass123!", is_staff=False)
        response = self.client.post(
            reverse("admin_login"),
            {"username": "customer_test", "password": "StrongPass123!"},
            secure=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "not authorized")


class SellerSettlementTests(TestCase):
    def test_confirmed_order_creates_pending_seller_settlement(self):
        user = User.objects.create_user(username="seller", email="seller@example.com", password="StrongPass123!")
        seller = SellerProfile.objects.create(user=user, business_name="Seller Shop")
        SellerWallet.objects.create(seller=seller)
        product = Product.objects.create(name="Test Phone", sku="TEST-001", price=Decimal("10000.00"), stock_quantity=5, seller=seller)
        order = Order.objects.create(customer_name="Buyer", email="buyer@example.com", phone="254700000000", address="Eldoret", total_amount=Decimal("10000.00"))
        OrderItem.objects.create(order=order, product=product, quantity=1, price=Decimal("10000.00"), seller=seller, seller_gross=Decimal("10000.00"), platform_commission=Decimal("1250.00"), seller_net=Decimal("8750.00"))

        _create_seller_settlements(order)
        settlement = SellerSettlement.objects.get(order=order, seller=seller)
        wallet = SellerWallet.objects.get(seller=seller)
        self.assertEqual(settlement.seller_amount, Decimal("8750.00"))
        self.assertEqual(settlement.platform_commission, Decimal("1250.00"))
        self.assertEqual(settlement.status, "pending")
        self.assertEqual(wallet.pending_balance, Decimal("8750.00"))

    def test_settlement_creation_is_idempotent(self):
        user = User.objects.create_user(username="seller2", email="seller2@example.com", password="StrongPass123!")
        seller = SellerProfile.objects.create(user=user, business_name="Seller Shop 2")
        SellerWallet.objects.create(seller=seller)
        product = Product.objects.create(name="Test Item", sku="TEST-002", price=Decimal("500.00"), stock_quantity=5, seller=seller)
        order = Order.objects.create(customer_name="Buyer", email="buyer2@example.com", phone="254700000001", address="Nakuru", total_amount=Decimal("500.00"))
        OrderItem.objects.create(order=order, product=product, quantity=2, price=Decimal("250.00"), seller=seller, seller_gross=Decimal("500.00"), platform_commission=Decimal("25.00"), seller_net=Decimal("475.00"))

        _create_seller_settlements(order)
        _create_seller_settlements(order)

        self.assertEqual(SellerSettlement.objects.filter(order=order, seller=seller).count(), 1)
        self.assertEqual(SellerWallet.objects.get(seller=seller).pending_balance, Decimal("475.00"))


class DataIntegrityConstraintTests(TestCase):
    def test_product_price_cannot_be_zero(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(name="Invalid", sku="BAD-PRICE", price=Decimal("0.00"), stock_quantity=1)

    def test_product_discount_cannot_exceed_100(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(name="Invalid", sku="BAD-DISC", price=Decimal("100.00"), discount_percent=101, stock_quantity=1)

    def test_review_rating_must_be_between_one_and_five(self):
        user = User.objects.create_user(username="reviewer", email="reviewer@example.com", password="StrongPass123!")
        product = Product.objects.create(name="Review Item", sku="REVIEW-001", price=Decimal("100.00"), stock_quantity=1)
        order = Order.objects.create(customer_name="Reviewer", email="reviewer@example.com", phone="254700000002", address="Nairobi", total_amount=Decimal("100.00"))
        with self.assertRaises(IntegrityError):
            ProductReview.objects.create(product=product, customer=user, order=order, rating=6)

    def test_only_one_default_address_is_allowed(self):
        user = User.objects.create_user(username="addressuser", email="address@example.com", password="StrongPass123!")
        CustomerAddress.objects.create(user=user, label="Home", full_name="Buyer", phone="254700000003", county="Nairobi", town="Nairobi", address_line="One", is_default=True)
        with self.assertRaises(IntegrityError):
            CustomerAddress.objects.create(user=user, label="Office", full_name="Buyer", phone="254700000003", county="Nairobi", town="Nairobi", address_line="Two", is_default=True)


class MpesaCallbackSafetyTests(TestCase):
    def _payment_fixture(self):
        user = User.objects.create_user(username="mpesabuyer", email="mpesa@example.com", password="StrongPass123!")
        product = Product.objects.create(name="M-PESA Item", sku="MPESA-001", price=Decimal("1000.00"), stock_quantity=2)
        order = Order.objects.create(customer_name="Buyer", email=user.email, phone="254712345678", address="Nairobi", total_amount=Decimal("1000.00"), payment_status="pending")
        OrderItem.objects.create(order=order, product=product, quantity=1, price=Decimal("1000.00"), seller_gross=Decimal("1000.00"), platform_commission=Decimal("0.00"), seller_net=Decimal("1000.00"))
        payment = PaymentTransaction.objects.create(order=order, method="mpesa", status="pending", provider="daraja", amount=Decimal("1000.00"), phone="254712345678", checkout_request_id="ws_CO_TEST_001", idempotency_key="MPESA-TEST-001")
        product.stock_quantity = 1
        product.save(update_fields=["stock_quantity"])
        return order, payment, user

    def test_success_callback_missing_receipt_does_not_mark_paid(self):
        order, payment, _ = self._payment_fixture()
        payload = {"Body": {"stkCallback": {"CheckoutRequestID": payment.checkout_request_id, "ResultCode": 0, "ResultDesc": "Success", "CallbackMetadata": {"Item": [{"Name": "Amount", "Value": 1000}, {"Name": "PhoneNumber", "Value": 254712345678}]}}}}
        response = self.client.post(reverse("mpesa_callback"), data=json.dumps(payload), content_type="application/json", secure=True)
        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(payment.status, "pending")
        self.assertEqual(order.payment_status, "pending")
        self.assertEqual(order.payment_reference, "")

    def test_success_callback_amount_mismatch_does_not_mark_paid(self):
        order, payment, _ = self._payment_fixture()
        payload = {"Body": {"stkCallback": {"CheckoutRequestID": payment.checkout_request_id, "ResultCode": 0, "ResultDesc": "Success", "CallbackMetadata": {"Item": [{"Name": "Amount", "Value": 999}, {"Name": "MpesaReceiptNumber", "Value": "RCP123"}, {"Name": "PhoneNumber", "Value": 254712345678}]}}}}
        response = self.client.post(reverse("mpesa_callback"), data=json.dumps(payload), content_type="application/json", secure=True)
        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(payment.status, "pending")
        self.assertEqual(order.payment_status, "pending")
