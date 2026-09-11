from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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
