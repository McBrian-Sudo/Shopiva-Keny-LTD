from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from cloudinary.models import CloudinaryField


class ProductMedia(models.Model):
    """Additional real seller-supplied product photos for Shopiva showcases."""

    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="media",
    )
    image = CloudinaryField(
        "image",
        folder="shopiva/product-media",
    )
    position = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(7)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("position", "created_at")
        constraints = [
            models.UniqueConstraint(
                fields=("product", "position"),
                name="unique_product_media_position",
            ),
        ]

    def __str__(self):
        return f"{self.product.name} media #{self.position + 1}"
