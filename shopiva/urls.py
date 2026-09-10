from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from home.admin import shopiva_admin_site
from home.views import (
    add_to_cart,
    cart,
    categories,
    checkout,
    customer_addresses,
    customer_dashboard,
    customer_login,
    customer_logout,
    customer_orders,
    customer_profile,
    customer_register,
    customer_wishlist,
    delivery_ping_location,
    delivery_portal,
    delivery_update_location,
    home,
    order_success,
    product_detail,
    products,
)

urlpatterns = [
    # =========================
    # SHOPIVA MARKET
    # =========================
    path("", home, name="home"),
    path("products/", products, name="products"),
    path("categories/", categories, name="categories"),
    path("product/<int:product_id>/", product_detail, name="product_detail"),

    # Cart
    path("cart/", cart, name="cart"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),

    # Checkout
    path("checkout/", checkout, name="checkout"),
    path(
        "order-success/<int:order_id>/",
        order_success,
        name="order_success",
    ),

    # =========================
    # CUSTOMER ACCOUNT
    # =========================
    path("customer/register/", customer_register, name="customer_register"),
    path("customer/login/", customer_login, name="customer_login"),
    path("customer/logout/", customer_logout, name="customer_logout"),
    path("account/", customer_dashboard, name="customer_dashboard"),
    path("account/orders/", customer_orders, name="customer_orders"),
    path("account/profile/", customer_profile, name="customer_profile"),
    path("account/addresses/", customer_addresses, name="customer_addresses"),
    path("account/wishlist/", customer_wishlist, name="customer_wishlist"),

    # =========================
    # DELIVERY PORTAL
    # =========================
    path("delivery/", delivery_portal, name="delivery_portal"),
    path("delivery/location/", delivery_update_location, name="delivery_update_location"),
    path("delivery/location/ping/", delivery_ping_location, name="delivery_ping_location"),

    # =========================
    # SHOPIVA ADMIN
    # =========================
    path("admin/", shopiva_admin_site.urls),
]

# =========================
# DEVELOPMENT MEDIA
# =========================
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
