from home.views import home, product_detail, add_to_cart, cart, checkout, order_success
"""
URL configuration for shopiva project.
"""

from django.contrib import admin
from django.urls import path
from home.views import home, product_detail, add_to_cart, cart, checkout, order_success

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("product/<int:product_id>/", product_detail, name="product_detail"),
    path("cart/", cart, name="cart"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("checkout/", checkout, name="checkout"),
    path("order-success/<int:order_id>/", order_success, name="order_success"),
]
