from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import OrderItem, Notification
from .notification_service import notify_user


@receiver(post_save, sender=OrderItem)
def notify_seller_of_new_order(sender, instance, created, **kwargs):
    """Create one in-app seller notification per seller/order when an item is ordered."""
    if not created:
        return

    seller = instance.seller or getattr(instance.product, "seller", None)
    if not seller or not seller.is_active or not seller.user_id:
        return

    # Keep the order item linked to the actual seller even when legacy checkout code
    # only supplied the Product relation.
    if instance.seller_id != seller.id:
        sender.objects.filter(pk=instance.pk, seller__isnull=True).update(seller=seller)

    order = instance.order
    title = f"New Shopiva order {order.tracking_code or order.id}"
    message = (
        f"You received {instance.quantity} x {instance.product.name}. "
        f"Order total: KSh {order.total_amount}. Status: {order.get_status_display()}."
    )
    link = f"/seller/?order={order.id}"

    # One seller notification per order, even when the customer buys multiple
    # products from the same seller.
    if Notification.objects.filter(user=seller.user, title=title).exists():
        return

    notify_user(
        seller.user,
        notification_type="order",
        title=title,
        message=message,
        link=link,
        email=seller.user.email,
        phone=seller.mpesa_phone,
    )
