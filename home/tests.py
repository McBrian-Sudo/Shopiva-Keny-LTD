from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from .forms import CustomerRegistrationForm
from .models import Order, OrderItem, SellerProfile, SellerSettlement, SellerWallet, Product
from .payments import _create_seller_settlements


class CustomerRegistrationTests(TestCase):
    def test_duplicate_username_is_rejected_case_insensitively(self):
        User.objects.create_user(username="McBrianTech", email="one@example.com", password="StrongPass123!")
        form = CustomerRegistrationForm(
            data={
                "username": "mcbraintech",
                "email": "two@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Username exists", str(form.errors["username"]))

    def test_duplicate_email_is_rejected_case_insensitively(self):
        User.objects.create_user(username="firstuser", email="User@Example.com", password="StrongPass123!")
        form = CustomerRegistrationForm(
            data={
                "username": "seconduser",
                "email": "user@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("already registered", str(form.errors["email"]))


class SellerSettlementTests(TestCase):
    def test_confirmed_order_creates_pending_seller_settlement(self):
        user = User.objects.create_user(username="seller", email="seller@example.com", password="StrongPass123!")
        seller = SellerProfile.objects.create(user=user, business_name="Seller Shop", commission_percent=Decimal("10.00"))
        SellerWallet.objects.create(seller=seller)
        product = Product.objects.create(name="Test Phone", sku="TEST-001", price=Decimal("10000.00"), stock_quantity=5, seller=seller)
        order = Order.objects.create(customer_name="Buyer", email="buyer@example.com", phone="254700000000", address="Eldoret", total_amount=Decimal("10000.00"))
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=Decimal("10000.00"),
            seller=seller,
            seller_gross=Decimal("10000.00"),
            platform_commission=Decimal("1000.00"),
            seller_net=Decimal("9000.00"),
        )

        _create_seller_settlements(order)

        settlement = SellerSettlement.objects.get(order=order, seller=seller)
        wallet = SellerWallet.objects.get(seller=seller)
        self.assertEqual(settlement.seller_amount, Decimal("9000.00"))
        self.assertEqual(settlement.platform_commission, Decimal("1000.00"))
        self.assertEqual(settlement.status, "pending")
        self.assertEqual(wallet.pending_balance, Decimal("9000.00"))

    def test_settlement_creation_is_idempotent(self):
        user = User.objects.create_user(username="seller2", email="seller2@example.com", password="StrongPass123!")
        seller = SellerProfile.objects.create(user=user, business_name="Seller Shop 2")
        SellerWallet.objects.create(seller=seller)
        product = Product.objects.create(name="Test Item", sku="TEST-002", price=Decimal("500.00"), stock_quantity=5, seller=seller)
        order = Order.objects.create(customer_name="Buyer", email="buyer2@example.com", phone="254700000001", address="Nakuru", total_amount=Decimal("500.00"))
        OrderItem.objects.create(order=order, product=product, quantity=2, price=Decimal("250.00"), seller=seller, seller_gross=Decimal("500.00"), platform_commission=Decimal("50.00"), seller_net=Decimal("450.00"))

        _create_seller_settlements(order)
        _create_seller_settlements(order)

        self.assertEqual(SellerSettlement.objects.filter(order=order, seller=seller).count(), 1)
        self.assertEqual(SellerWallet.objects.get(seller=seller).pending_balance, Decimal("450.00"))
