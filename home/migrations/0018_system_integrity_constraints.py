from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [("home", "0017_align_notification_and_commission_fields")]

    operations = [
        migrations.AddConstraint(
            model_name="sellerwallet",
            constraint=models.CheckConstraint(condition=Q(pending_balance__gte=0), name="sellerwallet_pending_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="sellerwallet",
            constraint=models.CheckConstraint(condition=Q(available_balance__gte=0), name="sellerwallet_available_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="sellerwallet",
            constraint=models.CheckConstraint(condition=Q(total_sales__gte=0), name="sellerwallet_sales_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="sellerwallet",
            constraint=models.CheckConstraint(condition=Q(total_commission__gte=0), name="sellerwallet_commission_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.CheckConstraint(condition=Q(price__gt=0), name="product_price_gt_0"),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.CheckConstraint(condition=Q(discount_percent__gte=0, discount_percent__lte=100), name="product_discount_0_100"),
        ),
        migrations.AddConstraint(
            model_name="order",
            constraint=models.CheckConstraint(condition=Q(total_amount__gte=0), name="order_total_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(condition=Q(quantity__gt=0), name="orderitem_quantity_gt_0"),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(condition=Q(price__gte=0), name="orderitem_price_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(condition=Q(seller_gross__gte=0), name="orderitem_gross_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(condition=Q(platform_commission__gte=0), name="orderitem_commission_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(condition=Q(seller_net__gte=0), name="orderitem_net_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="deliverylocationping",
            constraint=models.CheckConstraint(condition=Q(latitude__gte=-90, latitude__lte=90), name="deliveryping_latitude_range"),
        ),
        migrations.AddConstraint(
            model_name="deliverylocationping",
            constraint=models.CheckConstraint(condition=Q(longitude__gte=-180, longitude__lte=180), name="deliveryping_longitude_range"),
        ),
        migrations.AddConstraint(
            model_name="deliverylocationping",
            constraint=models.CheckConstraint(condition=Q(accuracy_meters__gte=0) | Q(accuracy_meters__isnull=True), name="deliveryping_accuracy_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="deliverylocationping",
            constraint=models.CheckConstraint(condition=Q(speed_mps__gte=0) | Q(speed_mps__isnull=True), name="deliveryping_speed_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="paymenttransaction",
            constraint=models.CheckConstraint(condition=Q(amount__gt=0), name="payment_amount_gt_0"),
        ),
        migrations.AddConstraint(
            model_name="customeraddress",
            constraint=models.UniqueConstraint(condition=Q(is_default=True), fields=("user",), name="unique_default_shopiva_address"),
        ),
        migrations.AddConstraint(
            model_name="sellerpayoutrequest",
            constraint=models.CheckConstraint(condition=Q(amount__gt=0), name="sellerpayout_amount_gt_0"),
        ),
        migrations.AddConstraint(
            model_name="sellersettlement",
            constraint=models.CheckConstraint(condition=Q(gross_amount__gte=0), name="settlement_gross_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="sellersettlement",
            constraint=models.CheckConstraint(condition=Q(platform_commission__gte=0), name="settlement_commission_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="sellersettlement",
            constraint=models.CheckConstraint(condition=Q(seller_amount__gte=0), name="settlement_seller_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="productreview",
            constraint=models.CheckConstraint(condition=Q(rating__gte=1, rating__lte=5), name="productreview_rating_1_5"),
        ),
    ]
