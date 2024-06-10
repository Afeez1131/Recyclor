from django.forms.forms import ValidationError
from django.utils import timezone
from company.models import Company
from django.test import TestCase
from company.forms import CompanyCreateForm
import random


def random_date():
    n = random.randint(1, 30)
    return timezone.now().date() - timezone.timedelta(days=360 * n)


class CompanyFormTestCase(TestCase):
    def setUp(self):
        self.form = CompanyCreateForm
        self.data = {
            "name": "Company name",
            "email": "company@mail.com",
            "address": "Nigeria",
            "phone": "08105505056",
            "description": "Dummy description",
            "website": "www.company.com",
            "established_date": random_date(),
        }

    def test_company_form_has_all_fields(self):
        form = self.form()
        for field in self.data.keys():
            self.assertIn(field, form.fields)

    def test_company_form_fields_attributes(self):
        for field in self.data.keys():
            form = self.form()
            field_attrs = form.fields[field].widget.attrs
            self.assertEqual(
                form.fields[field].label, field.replace("_", " ").capitalize()
            )
            self.assertEqual(form.fields[field].help_text, "")
            self.assertEqual(field_attrs["class"], "form-control")

    def test_company_form_requires_all_fields(self):
        original_data = self.data.copy()
        for field in original_data.keys():
            data = original_data.copy()
            data.pop(field)
            form = self.form(data)
            self.assertFalse(form.is_valid())
            self.assertIn("This field is required.", form.errors.get(field, ""))
            self.assertTrue(form.errors)

    def test_company_form_saved_with_valid_data(self):
        form = self.form(self.data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.is_bound)
        self.assertEqual(form.errors, {})

    def test_company_form_invalid_email(self):
        self.data.update({"email": "invalid_email"})
        form = self.form(self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_company_form_name_max_length(self):
        self.data.update({"name": "lorem" * 501})
        form = self.form(self.data)
        form.full_clean()
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_company_form_phone_max_length(self):
        self.data.update({"phone": "081828" * 20})
        form = self.form(self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_company_form_invalid_website(self):
        self.data.update({"website": "invalid_website"})
        form = self.form(self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("website", form.errors)
