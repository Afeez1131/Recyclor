from django.conf.global_settings import LOGIN_URL
from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from core.views import DashboardView


def get_user(username="testuser", password="password"):
    return {"username": username, "password": password}


DASHBOARD_URL = reverse("core:dashboard")
LOGIN_URL = reverse("account:login")


class DashboardViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = get_user()
        self.user = User.objects.create_user(**self.user_data)

    def test_dashboard_view_without_authentication(self):
        response = self.client.get(DASHBOARD_URL)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{LOGIN_URL}?next={DASHBOARD_URL}")

    def test_dashbboard_view_with_authentication(self):
        self.client.login(**self.user_data)
        response = self.client.get(DASHBOARD_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/dashboard.html")

    def test_dashboard_view_valid_context(self):
        self.client.login(**self.user_data)
        response = self.client.get(DASHBOARD_URL)
        context = response.context
        self.assertIn("title", context)
        self.assertEqual(context.get("title"), "Dashboard")

    def test_dashboard_view_invalid_context(self):
        self.client.login(**self.user_data)
        response = self.client.get(DASHBOARD_URL)
        context = response.context
        self.assertNotIn("invalidcontext", context)
        self.assertNotIn("form", context)


"""
The next section would be using RequestFactory for test, instead of the TestCase.
Why RequestFactory?
- It allows testing the view in isolation without the complete request -> response cycle.
- since it does not require the request -> response cycle, it is faster than using the TestCase.
- since I am not working with database
- middleware is sideline, we are only dealing with the view itself.

TestCase?
- It is slower than RequestFactory
- It completes the request -> response cycle
- can access database
"""


class DashboardViewRequestFactoryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_data = get_user()
        self.user = User.objects.create_user(**self.user_data)

    def test_dashboard_view_without_authentication(self):
        request = self.factory.get(DASHBOARD_URL)
        request.user = AnonymousUser()
        response = DashboardView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        redirect_to = f"{LOGIN_URL}?next={DASHBOARD_URL}"
        self.assertEqual(response.get("location"), redirect_to)

    def test_dashboard_view_with_authentication(self):
        request = self.factory.get(DASHBOARD_URL)
        request.user = self.user
        response = DashboardView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    #
    def test_dashboard_view_context(self):
        request = self.factory.get(DASHBOARD_URL)
        request.user = self.user
        response = DashboardView.as_view()(request)
        self.assertIn("title", response.context_data)
        self.assertEqual(response.context_data.get("title"), "Dashboard")

    def test_dashboard_view_invalid_context(self):
        request = self.factory.get(DASHBOARD_URL)
        request.user = self.user

        response = DashboardView.as_view()(request)
        context = response.context_data
        self.assertNotIn("invalidcontext", context)

    def test_dashboard_view_template(self):
        request = self.factory.get(DASHBOARD_URL)
        request.user = self.user
        response = DashboardView.as_view()(request)
        self.assertIn("core/dashboard.html", response.template_name)
