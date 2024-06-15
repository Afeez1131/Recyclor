from django.contrib.messages.api import get_messages
from django.template.loader import render_to_string
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser, User
from urllib.parse import urlencode, quote

from account.forms import RegisterForm

"""
CLIENT first
"""


def get_user_data(username="testuser", password="testpass123"):
    return {"username": username, "password": password}


def get_registration_data():
    return {
        "full_name": "Afeez Lawal Doe",
        "email": "mail@gmail.com",
        "password1": "testpass123",
        "password2": "testpass123",
    }


LOGIN_URL = reverse("account:login")
LOGOUT_URL = reverse("account:logout")
DASHBOARD_URL = reverse("core:dashboard")
REGISTRATION_URL = reverse("account:register")


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = get_user_data()
        self.user = User.objects.create_user(**self.user_data)

    def test_login_view_does_not_require_authentication(self):
        """Test that login page does no require authentication"""
        response = self.client.get(LOGIN_URL)
        self.assertEqual(response.status_code, 200)

    def test_login_view_user_correct_template(self):
        response = self.client.get(LOGIN_URL)
        self.assertTemplateUsed(response, "account/login.html")

    def test_login_view_with_authentication(self):
        """Test that authenticated user visiting login page get redirected to dashboard."""
        self.client.login(**self.user_data)
        response = self.client.get(LOGIN_URL)
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, DASHBOARD_URL)

    def test_login_view_with_valid_user_data(self):
        response = self.client.post(LOGIN_URL, data=self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, DASHBOARD_URL)

    def test_login_view_authenticates_user(self):
        response = self.client.post(LOGIN_URL, data=self.user_data)
        response = self.client.get(DASHBOARD_URL)
        self.assertEqual(response.status_code, 200)
        context = response.context
        user = context.get("user")
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, self.user_data.get("username"))

    def test_login_invalid_user_data(self):
        self.user_data.update({"username": "invalids"})
        response = self.client.post(LOGIN_URL, data=self.user_data, follow=True)
        self.assertEqual(response.status_code, 200)
        storage = get_messages(response.wsgi_request)
        messages = [msg.message for msg in storage]
        self.assertIn("Invalid username or password.", messages)

    def test_login_view_with_next(self):
        response = self.client.get(DASHBOARD_URL, follow=True)
        self.assertEqual(response.status_code, 200)
        request = response.request
        current_path = request.get("PATH_INFO")
        query_params = request.get("QUERY_STRING")
        full_path = f"{current_path}?{query_params}" if query_params else current_path
        params = {"next": DASHBOARD_URL}
        custom_path = f"{LOGIN_URL}?" + urlencode(params)
        self.assertEqual(full_path, custom_path)

        response = self.client.post(current_path, data=self.user_data, follow=True)
        self.assertEqual(response.status_code, 200)
        request = response.request
        current_path = request.get("PATH_INFO")
        self.assertEqual(current_path, DASHBOARD_URL)


class LogoutTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = get_user_data()
        self.user = User.objects.create_user(**self.user_data)

    def test_logout_not_authenticated_user(self):
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, LOGIN_URL)

    def test_logout_authenticated_user(self):
        self.client.login(**self.user_data)
        response = self.client.get(LOGOUT_URL, follow=True)
        self.assertEqual(response.status_code, 200)
        request = response.request
        current_path = request.get("PATH_INFO")
        self.assertEqual(current_path, LOGIN_URL)
        user = response.context.get("user")
        self.assertFalse(user.is_authenticated)
        self.assertEqual(user, AnonymousUser())


class RegisterUserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = get_user_data()
        self.user = User.objects.create_user(**self.user_data)
        self.registration_data = get_registration_data()

    def test_registration_view_get(self):
        response = self.client.get(REGISTRATION_URL)
        self.assertEqual(response.status_code, 200)

    def test_registration_view_template(self):
        response = self.client.get(REGISTRATION_URL)
        self.assertTemplateUsed(response, "account/register.html")
        context = {"title": "Registration Page", "form": RegisterForm}
        expected = render_to_string("account/register.html", context)
        template = response.content.decode("utf8")
        self.assertEqual(expected, template)

    def test_registration_view_context(self):
        response = self.client.get(REGISTRATION_URL)
        context = response.context
        self.assertIn("form", context)
        self.assertIn("title", context)
        title = context.get("title")
        self.assertEqual("Registration Page", title)
        form = context.get("form")
        self.assertIsInstance(form, RegisterForm)

    def test_register_user_with_valid_data(self):
        response = self.client.post(
            REGISTRATION_URL, data=self.registration_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        request = response.request
        storage = get_messages(response.wsgi_request)
        messages = [msg.message for msg in storage]
        self.assertIn("User created succcessfully", messages)
        current_path = request.get("PATH_INFO")
        self.assertEqual(current_path, LOGIN_URL)

    def test_register_user_with_invalid_data(self):
        self.registration_data.update({"email": "email.coom"})
        response = self.client.post(
            REGISTRATION_URL, self.registration_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        storage = get_messages(response.wsgi_request)
        content = response.content.decode("utf8")
        self.assertIn("Enter a valid email address.", content)
        form = response.context.get("form")
        self.assertFormError(response, "form", "email", "Enter a valid email address.")
        current_path = response.request.get("PATH_INFO")
        self.assertEqual(current_path, REGISTRATION_URL)

    def test_register_with_existing_email(self):
        response = self.client.post(
            REGISTRATION_URL,
            self.registration_data,
        )
        self.assertEqual(response.status_code, 302)
        self.registration_data.update({"username": "newuser"})
        response = self.client.post(
            REGISTRATION_URL, self.registration_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        form = response.context.get("form")
        self.assertFormError(response, "form", "email", "User with this email exists")
