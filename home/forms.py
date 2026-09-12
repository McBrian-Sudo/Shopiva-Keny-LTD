from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, ProductReview


class CustomerRegistrationForm(UserCreationForm):
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

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "Username exists. Please choose a different username."
            )

        return username

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


class SellerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    business_name = forms.CharField(max_length=200)
    mpesa_phone = forms.CharField(max_length=30, help_text="Kenyan M-PESA number for future seller payouts.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Username exists. Please choose another username.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()
        if commit:
            user.save()
        return user


class SellerProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # SKU is intentionally excluded: Shopiva assigns it automatically.
        fields = ("name", "description", "category", "price", "stock_quantity", "discount_percent", "promo_text", "image", "is_active", "is_featured")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ("rating", "comment")
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} / 5") for i in range(5, 0, -1)]),
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell other shoppers about your experience."}),
        }
