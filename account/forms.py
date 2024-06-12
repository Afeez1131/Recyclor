from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password


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

        
    def save(self):
        try:
            # cleaned_data = self.cleaned_data
            full_name = self.cleaned_data.get('name', '')
            email = self.cleaned_data.get('email', '')
            password = self.cleaned_data.get('password1', '')
            name_split = full_name.split(' ')
            first_name = ''
            last_name = ''
            if len(name_split) == 1:
                first_name = name_split[0]
            elif len(name_split) == 2:
                first_name, last_name = name_split
            else:
                first_name = name_split[0]
                last_name = ' '.join(name_split[1:])
            user = User.objects.create_user(
                username=email, 
                email=email, 
                password=password,
                first_name=first_name,
                last_name=last_name)
            return {'status': 'success', 'info': 'User created succcessfully', 'user': user}
        except Exception as e:
            return {'status': 'error', 'info': f'Error occured {str(e)}'}
            
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email", "")
        password1 = cleaned_data.get("password1", "")
        password2 = cleaned_data.get("password2", "")
        if email and User.objects.filter(email=email).exists():
            self.add_error("email", "User with this email exists")
        if not password1 or not password2:
            self.add_error("password1", "Password is required")
            self.add_error("password2", "Password is required")
        if password1 != password2:
            self.add_error("password1", "Passwords do not match")
            self.add_error("password2", "Passwords do not match")
        try:
            validate_password(password1)
        except forms.ValidationError as errs:
            raise forms.ValidationError({"password1": errs.messages})
        
        return cleaned_data
        
