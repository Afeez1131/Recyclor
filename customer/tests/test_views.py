import random
from django.template.loader import render_to_string
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from customer.forms import CreateCustomerForm
from customer.models import Customer, ServiceHistory

CREATE_CUSTOMER_URL = reverse("customer:create")

def get_user_data(username='testuser', password='testpass123'):
    return {
        "username": username,
        "password": password
    }
    
def random_username():
    return f"testuser{random.randint(1, 100)}"
    
def get_customer_data():
    return {
        "name": "Meta",
        "address": "Silicon valley",
        "email": "mail@gmail.com",
        "phone": "08120202020",
        "schedule": "weekly",
    }
    
class CreateCustomerViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = get_user_data()
        self.customer_data = get_customer_data()
        random_user = random_username()
        self.customer_data.update({
            "user_id": User.objects.create_user(**get_user_data(username=random_user)).id}
        )
        self.user = User.objects.create_user(**self.user_data)
        
    def test_create_customer_view_without_authentication(self):
        response = self.client.get(CREATE_CUSTOMER_URL)
        redirect_path = reverse("account:login") + "?next=" + CREATE_CUSTOMER_URL
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_path)
        
    def test_create_customer_view_with_authentication(self):
        self.client.login(**self.user_data)
        response = self.client.get(CREATE_CUSTOMER_URL)
        self.assertEqual(response.status_code, 200)
        
    def test_create_customer_view_context(self):
        self.client.login(**self.user_data)
        response = self.client.get(CREATE_CUSTOMER_URL)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context.get("form"), CreateCustomerForm)
        self.assertIn("title", response.context)
        
    def test_create_customer_view_correct_template(self):
        self.client.login(**self.user_data)
        response = self.client.get(CREATE_CUSTOMER_URL)
        expected_template = "customer/create.html"
        context = {
            "title": "Register as a Customer",
            "form": response.context.get("form")
        }
        expected_template_content = render_to_string(expected_template, context)
        self.assertTemplateUsed(response, expected_template)
        self.assertEqual(response.content.decode("utf8"), expected_template_content)
        
    def test_create_customer_view_post_request_with_valid_data(self):
        self.client.login(**self.user_data)
        user = User.objects.create_user(**get_user_data(random_username()))
        data = {
            "name": "Meta",
            "address": "Silicon valley",
            "email": "mail@gmail.com",
            "phone": "08120202020",
            "schedule": "weekly",
        }
        response = self.client.post(
            CREATE_CUSTOMER_URL,
            data=data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Customer.objects.count(), 1)
        
        
    def test_create_customer_view_post_request_with_invalid_data(self):
        self.client.login(**self.user_data)
        user = User.objects.create_user(**get_user_data(random_username()))
        self.customer_data.update({"email": "invalid-email", "schedule": "invalid-schedule"})
        response = self.client.post(
            CREATE_CUSTOMER_URL,
            data=self.customer_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "email", "Enter a valid email address.")
        self.assertFormError(response, "form", "schedule", "Select a valid choice. invalid-schedule is not one of the available choices.")
        
    def test_user_can_create_multiple_customers(self):
        self.client.login(**self.user_data)
        data = self.customer_data
        response = self.client.post(
            CREATE_CUSTOMER_URL,
            data=data
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("core:dashboard"))
        self.customer_data.update({"email": "test@mail.com"})
        
class UpdateCustomerViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = get_user_data()
        self.user = User.objects.create_user(**self.user_data)
        self.customer_data = get_customer_data()
        self.customer = Customer.objects.create(user=self.user, **self.customer_data)
        self.update_url = reverse("customer:update", kwargs={"pk": self.customer.id})
        
    def test_update_customer_view_without_authentication(self):
        response = self.client.get(self.update_url)
        redirect_path = reverse("account:login") + "?next=" + self.update_url
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_path)
        
    def test_update_customer_view_with_authentication(self):
        self.client.login(**self.user_data)
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        
    def test_update_customer_view_context(self):
        self.client.login(**self.user_data)
        response = self.client.get(self.update_url)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context.get("form"), CreateCustomerForm)
        self.assertIn("title", response.context)
        self.assertEqual(response.context.get("title"), "Update Customer Information")
        
    def test_update_customer_view_correct_template(self):
        self.client.login(**self.user_data)
        response = self.client.get(self.update_url)
        expected_template = "customer/update.html"
        context = {
            "title": "Update Customer Information",
            "form": response.context.get("form")
        }
        expected_template_content = render_to_string(expected_template, context)
        print("template: ", expected_template_content)
        self.assertTemplateUsed(response, expected_template)
        self.assertEqual(response.content.decode("utf8"), expected_template_content)
        
    def test_update_customer_view_post_request_with_valid_data(self):
        self.client.login(**self.user_data)
        data = {
            "name": "Meta (EX. Facebook)",
            "address": "Silicon valley (updated)",
            "email": "updated@mail.com",
            "phone": "08120202020",
            "schedule": "monthly",
        }
        response = self.client.post(
            self.update_url,
            data=data
        )
        self.customer.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("core:dashboard"))
        self.assertEqual(self.customer.name, data["name"])
        self.assertEqual(self.customer.address, data["address"])
        self.assertEqual(self.customer.email, data["email"])
        self.assertEqual(self.customer.phone, data["phone"])
        self.assertEqual(self.customer.schedule, data["schedule"])
        