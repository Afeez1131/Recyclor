from django import forms
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Full Name"}
        ),
    )
    email = forms.EmailField(
        max_length=100,
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email"}
        ),
    )
    password1 = forms.CharField(
        label="Password", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
