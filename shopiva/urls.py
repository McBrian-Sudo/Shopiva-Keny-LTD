from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from home.admin import shopiva_admin_site
from home.business_intelligence import business_intelligence
from home.ai import shop_assistant
from home.customer_tracking import customer_order_tracking
from home.platform import app_install, app_manifest, service_worker
from home.payments import checkout_mpesa, mpesa_callback, mpesa_payment_status, mpesa_waiting
from home.views import (
    add_to_cart,
    cart,
    categories,
    customer_addresses,
    customer_dashboard,
    customer_delivery_location,
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
    path("", home, name="home"),
    path("products/", products, name="products"),
    path("categories/", categories, name="categories"),
    path("product/<int:product_id>/", product_detail, name="product_detail"),
    path("install/", app_install, name="app_install"),
    path("manifest.webmanifest", app_manifest, name="app_manifest"),
    path("service-worker.js", service_worker, name="service_worker"),
    path("cart/", cart, name="cart"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),

    # Checkout / payments
    path("checkout/", checkout_mpesa, name="checkout"),
    path("payments/mpesa/callback/", mpesa_callback, name="mpesa_callback"),
    path("payments/mpesa/status/<int:order_id>/", mpesa_payment_status, name="mpesa_payment_status"),
    path("payments/mpesa/waiting/<int:order_id>/", mpesa_waiting, name="mpesa_waiting"),
    path("order-success/<int:order_id>/", order_success, name="order_success"),

    # Customer account
    path("customer/register/", customer_register, name="customer_register"),
    path("customer/login/", customer_login, name="customer_login"),
    path("customer/logout/", customer_logout, name="customer_logout"),
    path("account/", customer_dashboard, name="customer_dashboard"),
    path("account/orders/", customer_orders, name="customer_orders"),
    path("account/orders/<int:order_id>/", customer_order_tracking, name="customer_order_tracking"),
    path("account/profile/", customer_profile, name="customer_profile"),
    path("account/addresses/", customer_addresses, name="customer_addresses"),
    path("account/wishlist/", customer_wishlist, name="customer_wishlist"),
    path("account/delivery-location/", customer_delivery_location, name="customer_delivery_location"),

    # Delivery portal
    path("delivery/", delivery_portal, name="delivery_portal"),
    path("delivery/location/", delivery_update_location, name="delivery_update_location"),
    path("delivery/location/ping/", delivery_ping_location, name="delivery_ping_location"),

    # Admin / intelligence
    path("admin/business-intelligence/", business_intelligence, name="business_intelligence"),
    path("ai/shop-assistant/", shop_assistant, name="shop_assistant"),
    path("admin/", shopiva_admin_site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
