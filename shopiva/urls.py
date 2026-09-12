from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from home.admin import shopiva_admin_site
from home.admin_helpers import admin_ai_assistant, admin_login, admin_logout
from home.business_intelligence import business_intelligence
from home.ai import shop_assistant
from home.customer_tracking import customer_order_tracking
from home.checkout_map import checkout_mpesa_map
from home.google_admin_map import google_admin_delivery_map
from home.map_views import customer_addresses_map, customer_delivery_location_map, seller_product_add_map, seller_product_edit_map
from home.platform import app_install, app_manifest, service_worker
from home.payments import mpesa_callback, mpesa_payment_status, mpesa_waiting
from home.seller_auth import seller_login, seller_logout, seller_login_required
from home.voice_ai import realtime_action, realtime_call, speak_text, transcribe_voice
from shopiva.health import health
from home.views import add_to_cart, cart, categories, customer_dashboard, customer_login, customer_logout, customer_orders, customer_profile, customer_register, customer_wishlist, seller_dashboard, seller_product_toggle, seller_product_delete, product_review, customer_notifications, seller_register, seller_request_payout, delivery_ping_location, delivery_portal, delivery_update_location, home, order_success, product_detail, products

urlpatterns = [
    path("", home, name="home"),
    path("health/", health, name="health"),
    path("products/", products, name="products"),
    path("categories/", categories, name="categories"),
    path("product/<int:product_id>/", product_detail, name="product_detail"),
    path("install/", app_install, name="app_install"),
    path("manifest.webmanifest", app_manifest, name="app_manifest"),
    path("service-worker.js", service_worker, name="service_worker"),
    path("cart/", cart, name="cart"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),

    path("checkout/", checkout_mpesa_map, name="checkout"),
    path("payments/mpesa/callback/", mpesa_callback, name="mpesa_callback"),
    path("payments/mpesa/status/<int:order_id>/", mpesa_payment_status, name="mpesa_payment_status"),
    path("payments/mpesa/waiting/<int:order_id>/", mpesa_waiting, name="mpesa_waiting"),
    path("order-success/<int:order_id>/", order_success, name="order_success"),

    path("seller/register/", seller_register, name="seller_register"),
    path("seller/login/", seller_login, name="seller_login"),
    path("seller/logout/", seller_logout, name="seller_logout"),
    path("seller/", seller_login_required(seller_dashboard), name="seller_dashboard"),
    path("seller/products/add/", seller_login_required(seller_product_add_map), name="seller_product_add"),
    path("seller/products/<int:product_id>/edit/", seller_login_required(seller_product_edit_map), name="seller_product_edit"),
    path("seller/products/<int:product_id>/toggle/", seller_login_required(seller_product_toggle), name="seller_product_toggle"),
    path("seller/products/<int:product_id>/hide/", seller_login_required(seller_product_delete), name="seller_product_delete"),
    path("seller/payout/request/", seller_login_required(seller_request_payout), name="seller_request_payout"),

    path("customer/register/", customer_register, name="customer_register"),
    path("customer/login/", customer_login, name="customer_login"),
    path("customer/logout/", customer_logout, name="customer_logout"),
    path("account/", customer_dashboard, name="customer_dashboard"),
    path("account/orders/", customer_orders, name="customer_orders"),
    path("account/orders/<int:order_id>/", customer_order_tracking, name="customer_order_tracking"),
    path("account/profile/", customer_profile, name="customer_profile"),
    path("account/addresses/", customer_addresses_map, name="customer_addresses"),
    path("account/wishlist/", customer_wishlist, name="customer_wishlist"),
    path("account/notifications/", customer_notifications, name="customer_notifications"),
    path("product/<int:product_id>/review/", product_review, name="product_review"),
    path("account/delivery-location/", customer_delivery_location_map, name="customer_delivery_location"),

    path("delivery/", delivery_portal, name="delivery_portal"),
    path("delivery/location/", delivery_update_location, name="delivery_update_location"),
    path("delivery/location/ping/", delivery_ping_location, name="delivery_ping_location"),

    path("admin/business-intelligence/", business_intelligence, name="business_intelligence"),
    path("admin/google-delivery-map/", google_admin_delivery_map, name="google_delivery_map"),
    path("ai/shop-assistant/", shop_assistant, name="shop_assistant"),
    path("ai/voice/transcribe/", transcribe_voice, name="voice_transcribe"),
    path("ai/realtime/call/", realtime_call, name="realtime_call"),
    path("ai/realtime/action/", realtime_action, name="realtime_action"),
    path("ai/voice/speak/", speak_text, name="voice_speak"),

    path("admin/login/", admin_login, name="admin_login"),
    path("admin/ai-assistant/", admin_ai_assistant, name="admin_ai_assistant"),
    path("admin/logout/", admin_logout, name="admin_logout"),
    path("admin/", shopiva_admin_site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
