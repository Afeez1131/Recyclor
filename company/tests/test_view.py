from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from http import HTTPStatus
from django.http.response import HttpResponseNotAllowed
from company.forms import CompanyCreateForm
from company.models import Company


def get_user(username="testuser", password="password"):
    return {"username": username, "password": password}


def company_data():
    return {
        "name": "Test Company",
        "email": "company@mail.com",
        "address": "Test Address",
        "phone": "1234567890",
        "description": "Test Description",
        "website": "http://www.company.com",
        "established_date": "2020-01-01",
    }


class TestCreateCompanyViews(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(**get_user())
        self.user = get_user()
        self.company_data = company_data()

    def test_company_create_view_unauthenticated_user(self):
        response = self.client.get(reverse("company:create_company"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("account:login") + "?next=" + reverse("company:create_company"),
        )

    def test_company_create_view_authenticated_user(self):
        self.client.login(**self.user)
        response = self.client.get(reverse("company:create_company"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "company/create_company.html")
        self.assertContains(response, "Create Company")

    def test_company_create_valid_methods(self):
        self.client.login(**self.user)
        response = self.client.get(reverse("company:create_company"))
        # response = self.client.put(reverse("company:create_company"))
        # response = self.client.patch(reverse("company:create_company"))
        response = self.client.post(reverse("company:create_company"))

    def test_invalid_method(self):
        self.client.login(**self.user)
        response = self.client.delete(reverse("company:create_company"))
        self.assertEqual(response.status_code, 405)
        self.assertIsInstance(response, HttpResponseNotAllowed)
        
    def test_company_create(self):
        self.client.login(**self.user)
        response = self.client.post(
            reverse("company:create_company"), 
            data=self.company_data, 
            follow=True
        )
        # if i am not following the rediection, then the response would be a 302
        # but, there would not be a way to access the context of the response
        # since the response is not completed yet
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("core:dashboard"))
        self.assertTrue(Company.objects.filter(name=self.company_data["name"]).exists())
        
    def test_company_create_success_message(self):
        self.client.login(**self.user)
        response = self.client.post(reverse("company:create_company"), data=self.company_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("core:dashboard"))
        messages = list(response.context.get("messages", []))
        self.assertEqual(len(messages), 1)
        message = messages[0]
        self.assertEqual(str(message), f"{self.company_data.get('name')} has been created successfully")
        
    def test_company_create_invalid_data(self):
        self.client.login(**self.user)
        self.company_data.update({"name": "", "email": "hello.com"})
        response = self.client.post(reverse("company:create_company"), data=self.company_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "name", "This field is required.")
        self.assertFormError(response, "form", "email", "Enter a valid email address.")
        
    def test_company_create_context(self):
        self.client.login(**self.user)
        response = self.client.get(reverse("company:create_company"))
        self.assertIn("form", response.context)
        self.assertIn("title", response.context)
        self.assertEqual(response.context["title"], "Create Company")
        self.assertIsInstance(response.context["form"], CompanyCreateForm)
        # self.assertEqual(response.context.get("form_class"), CompanyCreateForm)
        # 
    def test_company_create_invalid_context(self):
        self.client.login(**self.user)
        response = self.client.get(reverse("company:create_company"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("invalidform", response.context)
        self.assertNotIn("invalidtitle", response.context)


class CompanyUpdateTestCase(TestCase):
    def setUp(self):
        self.user = get_user()
        User.objects.create_user(**get_user())
        self.client = Client()
        self.company_data = company_data()
        self.company = Company.objects.create(**self.company_data)

    def test_company_update_not_authenticated(self):
        response = self.client.get(
            reverse("company:update_company", args=[self.company.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("account:login") + "?next=" + reverse("company:update_company", args=[self.company.id]),
        )

    def test_company_update_authenticated(self):
        self.client.login(**self.user)
        response = self.client.get(
            reverse("company:update_company", args=[self.company.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "company/update_company.html")
        self.assertContains(response, f"Update {self.company.name}")

    def test_company_update(self):
        self.client.login(**self.user)
        self.company_data.update({
            "name": "Updated Company Name",
            "email": "update@mail.com",
            "address": "Updated Address",
        })
        response = self.client.post(
            reverse("company:update_company", args=[self.company.id]),
            data=self.company_data
        )
        self.company.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("core:dashboard"))
        self.assertEqual(self.company.name, "Updated Company Name")
        self.assertEqual(self.company.email, "update@mail.com")
        self.assertEqual(self.company.address, "Updated Address")
        
    def test_company_update_invalid_data(self):
        self.client.login(**self.user)
        self.company_data.update({
            "email": "invalid",
            "website": "invalid@mail"
        })
        response = self.client.post(reverse("company:update_company", args=[self.company.id]),data=self.company_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "email", "Enter a valid email address.")
        self.assertFormError(response, "form", "website", "Enter a valid URL.")
        
        
    def test_company_update_invalid_methods(self):
        self.client.login(**self.user)
        response = self.client.delete(
            reverse("company:update_company", args=[self.company.id])
        )
        self.assertEqual(response.status_code, 405)
        self.assertIsInstance(response, HttpResponseNotAllowed)
        
    def test_company_update_invalid_company(self):
        self.client.login(**self.user)
        response = self.client.get(reverse("company:update_company", args=[100]))
        self.assertEqual(response.status_code, 404)
        
    def test_company_update_success_message(self):
        self.client.login(**self.user)
        self.company_data.update({
            "name": "Updated Company Name",
            "email": "updated@mail.com"
            })
        response = self.client.post(reverse("company:update_company", args=[self.company.id]), data=self.company_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("core:dashboard"))
        messages = list(response.context.get("messages", []))
        self.assertEqual(len(messages), 1)
        message = str(messages[0])
        self.assertEqual(message, f"{self.company_data.get('name')} has been updated successfully")
        
    def test_company_update_context(self):
        self.client.login(**self.user)
        response = self.client.get(reverse("company:update_company", args=[self.company.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertIn("title", response.context)
        self.assertIsInstance(response.context.get("form"), CompanyCreateForm)
        
    def test_company_update_invalid_context(self):
        self.client.login(**self.user)
        response = self.client.get(reverse("company:update_company", args=[self.company.id]))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("invalidform", response.context)
        self.assertNotIn("invalidtitle", response.context)
        
    