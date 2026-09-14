from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

from .models import Product, ProductReview
from .media_pipeline import enhance_product_image
from .product_catalog import catalog_choices, catalog_item


def _validate_unique_username(username, *, error_message):
    """Normalize and enforce Shopiva's case-insensitive username rule in one place."""
    normalized = str(username or "").strip()
    if normalized and User.objects.filter(username__iexact=normalized).exists():
        raise forms.ValidationError(error_message)
    return normalized


class _ShopivaUsernameBoundary:
    """Single deterministic username validation boundary for registration forms."""

    username_error_message = "Username exists. Please choose a different username."

    def clean_username(self):
        username = self.cleaned_data.get("username", "")
        return _validate_unique_username(
            username,
            error_message=self.username_error_message,
        )

    def validate_unique(self):
        """Prevent Django's second model-level username check from replacing our message."""
        return None


class CustomerRegistrationForm(_ShopivaUsernameBoundary, UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "you@example.com",
                "autocomplete": "email",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "This email is already registered. Please use a different email or sign in."
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["username"].strip()
        user.email = self.cleaned_data["email"].strip().lower()
        if commit:
            user.save()
        return user


class SellerRegistrationForm(_ShopivaUsernameBoundary, UserCreationForm):
    username_error_message = "Username exists. Please choose another username."
    email = forms.EmailField(required=True)
    business_name = forms.CharField(max_length=200)
    mpesa_phone = forms.CharField(
        max_length=30,
        help_text="Kenyan M-PESA number for future seller payouts.",
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()
        user.username = self.cleaned_data["username"].strip()
        if commit:
            user.save()
        return user


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.FileField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        if not data:
            return []
        if isinstance(data, (list, tuple)):
            return [super().clean(item, initial=None) for item in data]
        return [super().clean(data, initial=initial)]


class SellerProductForm(forms.ModelForm):
    catalog_product = forms.ChoiceField(
        required=False,
        label="Master Product Catalogue",
        choices=catalog_choices,
        help_text=(
            "Choose the closest manufacturer/brand product from Shopiva's master directory. "
            "The product name and category are filled in automatically. Use a custom product "
            "name when your item is not listed."
        ),
        widget=forms.Select(attrs={"class": "shopiva-catalog-select", "title": "Search by typing a brand or product"}),
    )
    discount_percent = forms.IntegerField(
        min_value=0,
        max_value=100,
        required=False,
        help_text=(
            "Optional customer discount from the original price. Example: 20 means the "
            "customer pays 80% of the listed price. Leave 0 for no discount."
        ),
    )
    promo_text = forms.CharField(
        max_length=120,
        required=False,
        help_text=(
            "Optional short marketing message shown with the product, e.g. "
            "'Free delivery' or 'Weekend Deal'. This is promotional text, not the price."
        ),
    )
    gallery_images = MultipleImageField(
        required=False,
        label="Additional product photos (up to 8)",
        help_text="Use real photos of the same product. Shopiva automatically enhances them for the marketplace gallery.",
    )

    class Meta:
        model = Product
        fields = (
            "catalog_product",
            "name",
            "description",
            "category",
            "price",
            "stock_quantity",
            "discount_percent",
            "promo_text",
            "image",
            "gallery_images",
            "is_active",
            "is_featured",
        )
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Catalogue selection will fill this, or enter a custom product"}),
            "description": forms.Textarea(attrs={"rows": 5}),
            "category": forms.TextInput(attrs={"placeholder": "Electronics, Fashion, Groceries..."}),
            "image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def clean_catalog_product(self):
        key = self.cleaned_data.get("catalog_product", "")
        if not key:
            return ""
        if not catalog_item(key):
            raise forms.ValidationError("That catalogue product is not available. Please choose another item.")
        return key

    def clean(self):
        cleaned = super().clean()
        item = catalog_item(cleaned.get("catalog_product"))
        if item:
            cleaned["name"] = item["name"]
            cleaned["category"] = item["category"]
        elif not cleaned.get("name"):
            self.add_error("name", "Choose a master catalogue product or enter a custom product name.")
        return cleaned

    def save(self, commit=True):
        product = super().save(commit=False)
        item = catalog_item(self.cleaned_data.get("catalog_product"))
        if item:
            product.name = item["name"]
            product.category = item["category"]

        uploaded_main = self.files.get("image")
        if uploaded_main:
            product.image = enhance_product_image(uploaded_main, product.name)

        if not product.sku:
            prefix = slugify(product.name or "product").replace("-", "").upper()[:24] or "PRODUCT"
            product.sku = f"SPV-{prefix}-{uuid.uuid4().hex[:8].upper()}"

        # Existing seller views intentionally use commit=False so location
        # validation and product save remain inside their transaction.
        product._shopiva_gallery_files = self.cleaned_data.get("gallery_images", [])[:8]

        if commit:
            product.save()
        return product


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ("rating", "comment")
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} / 5") for i in range(5, 0, -1)]),
            "comment": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Tell other shoppers about your experience.",
                }
            ),
        }
