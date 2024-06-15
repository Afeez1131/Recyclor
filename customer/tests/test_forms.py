from django.contrib.auth.models import User
from django.db import IntegrityError
from django.forms.forms import ValidationError
from django.utils import timezone
from company.models import Company
from django.test import TestCase
from company.forms import CompanyCreateForm
import random

from customer.forms import CreateCustomerForm, CreateServiceHistory
from customer.models import Customer


def random_date():
    n = random.randint(1, 30)
    return timezone.now().date() - timezone.timedelta(days=360 * n)


def get_user_data(username="testuser", password="testpass123"):
    return {"username": username, "password": password}


class CreateCustomerFormTestCase(TestCase):
    def setUp(self):
        self.form = CreateCustomerForm
        self.user = User.objects.create_user(**get_user_data())
        self.data = {
            "name": "META",
            "email": "company@mail.com",
            "address": "Nigeria",
            "phone": "08105505056",
            "schedule": "weekly",
        }

    def test_form_instance(self):
        form = self.form()
        self.assertIsInstance(form, CreateCustomerForm)

    def test_form_fields(self):
        form = self.form()
        for field in self.data.keys():
            self.assertTrue(field in form.fields)

    def test_form_fields_label(self):
        form = self.form()
        for field in self.data.keys():
            self.assertEqual(form.fields[field].label, field.title())

    def test_form_field_widget_attrs(self):
        form = self.form()
        for field in self.data.keys():
            field_widget = form.fields[field].widget
            self.assertTrue(field_widget.attrs.get("class") == "form-control")

    def test_form_valid_data(self):
        form = self.form(data=self.data)
        self.assertTrue(form.is_valid())
        self.assertDictEqual(form.errors, {})

    def test_form_invalid_email(self):
        self.data.update({"email": "invalid_email"})
        form = self.form(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("Enter a valid email address.", form.errors.get("email"))

    def test_form_invalid_schedule(self):
        self.data.update({"schedule": "invalid_schedule"})
        form = self.form(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIsNotNone(form.errors)
        self.assertIn("schedule", form.errors)

    def test_form_save_with_valid_data(self):
        form = self.form(data=self.data)
        self.assertTrue(form.is_valid())
        form.instance.user = self.user
        form.save()
        self.assertTrue(Customer.objects.filter(name=self.data.get("name")).exists())


class CreateServiceHistoryFormTestCase(TestCase):
    def setUp(self):
        self.form = CreateServiceHistory
        self.data = {
            "name": "META",
            "email": "company@mail.com",
            "address": "Nigeria",
            "phone": "08105505056",
            "schedule": "weekly",
        }
        random_username = f"testuser{random.randint(1, 100)}"
        self.user_data = get_user_data(username=random_username)
        self.user = User.objects.create_user(**self.user_data)
        self.data.update({"user_id": self.user.id})
        self.customer = Customer.objects.create(**self.data)
        self.user_data = get_user_data()

    def test_service_form_instance(self):
        form = self.form()
        self.assertIsInstance(form, CreateServiceHistory)

    def test_service_form_fields(self):
        form = self.form()
        self.assertIn("cost", form.fields)

    def test_service_form_fields_label(self):
        form = self.form()
        self.assertEqual(form.fields["cost"].label, "Cost of Service")

    def test_service_form_field_widget_attrs(self):
        form = self.form()
        field_widget = form.fields["cost"].widget
        self.assertTrue(field_widget.attrs.get("class") == "form-control")

    def test_service_form_with_valid_cost(self):
        form = self.form({"cost": 12000})
        self.assertTrue(form.is_valid())
        self.assertDictEqual(form.errors, {})

    def test_service_form_with_invalid_cost(self):
        form = self.form({"cost": -100})
        self.assertFalse(form.is_valid())
        self.assertIn("cost", form.errors)
        self.assertIn("Cost cannot be negative", form.errors.get("cost"))

    def test_service_form_with_invalid_data(self):
        form = self.form({"cost": "invalid_cost"})
        self.assertFalse(form.is_valid())
        self.assertIn("cost", form.errors)
        self.assertIn("Enter a number.", form.errors.get("cost"))

    def test_service_form_not_saved_without_all_required_fields(self):
        form = self.form({"cost": 12000})
        with self.assertRaises(IntegrityError):
            form.save()

    def test_service_form_save_with_all_required_fields(self):
        form = self.form({"cost": 12000})
        form.instance.customer = self.customer
        form.instance.created_by = self.user
        self.assertTrue(form.is_valid())
        self.assertDictEqual(form.errors, {})
        service = form.save()
        self.assertEqual(service.customer, self.customer)
        self.assertIsInstance(service.customer, Customer)
        self.assertEqual(service.created_by, self.user)
        self.assertEqual(service.cost, 12000)
