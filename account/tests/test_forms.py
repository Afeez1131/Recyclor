from django.test import TestCase, Client
from account.forms import RegisterForm
from django.contrib.auth.models import User
from django.forms import Form


class RegistrationFormTestCase(TestCase):
    def setUp(self):
        self.form = RegisterForm()
        self.fields = ["full_name", "email", "password1", "password2"]
        self.data = {
            "full_name": "Recyclor",
            "email": "mail@gmail.com",
            "password1": "testpass123",
            "password2": "testpass123",
        }

    def test_registration_form_is_valid(self):
        self.assertIsInstance(self.form, Form)

    def test_registration_form_fields_exists(self):
        self.assertIn("full_name", self.form.fields)
        self.assertIn("email", self.form.fields)
        self.assertIn("password1", self.form.fields)
        self.assertIn("password2", self.form.fields)

    def test_registration_form_fields_attrs(self):
        self.assertEqual(self.form.fields["full_name"].max_length, 100)
        self.assertEqual(self.form.fields["full_name"].required, True)

        self.assertEqual(self.form.fields["email"].max_length, 100)
        self.assertEqual(self.form.fields["email"].required, True)

    def test_registration_form_fields_widget_attrs(self):
        for field in self.fields:
            field_widget = self.form.fields[field].widget
            self.assertEqual(field_widget.attrs.get("class"), "form-control")
        self.assertEqual(
            self.form.fields["full_name"].widget.attrs.get("placeholder"), "Full Name"
        )
        self.assertEqual(
            self.form.fields["email"].widget.attrs.get("placeholder"), "Email"
        )

    def test_registration_form_with_invalid_email(self):
        self.data.update({"email": "email.com"})
        form = RegisterForm(self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors.keys())
        self.assertIn("Enter a valid email address.", form.errors.get("email"))

    def test_registration_form_with_existing_mail(self):
        User.objects.create_user(
            username="testing", password="123445", email="email@gmail.com"
        )
        self.data.update({"email": "email@gmail.com"})
        form = RegisterForm(self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors.keys())
        self.assertIn("User with this email exists", form.errors.get("email"))

    def test_registration_form_without_password(self):
        self.data.pop("password1", None)
        self.data.pop("password2", None)
        form = RegisterForm(self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("password1", form.errors.keys())
        self.assertIn("password2", form.errors.keys())
        self.assertIn("Password is required", form.errors.get("password1"))
        self.assertIn("Password is required", form.errors.get("password2"))

    def test_registration_form_with_password_mismatch(self):
        self.data.update({"password2": "testpass1234"})
        form = RegisterForm(self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("password1", form.errors.keys())
        self.assertIn("password2", form.errors.keys())
        self.assertIn("Passwords do not match", form.errors.get("password1"))
        self.assertIn("Passwords do not match", form.errors.get("password2"))

    def test_registration_form_with_invalid_password(self):
        self.data.update({"password1": "password", "password2": "password"})
        form = RegisterForm(self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("password1", form.errors.keys())
        self.assertIn("This password is too common.", form.errors.get("password1"))

    def test_registration_form_save_with_valid_data(self):
        form = RegisterForm(self.data)
        if form.is_valid():
            response = form.save()
            user = response.get("user")
            self.assertTrue(form.is_valid())
            self.assertTrue(form.is_bound)
            self.assertDictEqual(form.errors, {})
            self.assertTrue(User.objects.filter(id=user.id).exists())
            self.assertEqual(user.email, self.data.get("email"))
