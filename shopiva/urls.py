from django.urls import path

from home.admin import shopiva_admin_site
from home.views import (
    add_to_cart,
    cart,
    categories,
    checkout,
    home,
    order_success,
    product_detail,
    products,
)

urlpatterns = [
    # Shopiva Market
    path("", home, name="home"),
    path("products/", products, name="products"),
    path("categories/", categories, name="categories"),
    path("product/<int:product_id>/", product_detail, name="product_detail"),
    path("cart/", cart, name="cart"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("checkout/", checkout, name="checkout"),
    path("order-success/<int:order_id>/", order_success, name="order_success"),

    # Shopiva Admin Control Center
    path("admin/", shopiva_admin_site.urls),
]
