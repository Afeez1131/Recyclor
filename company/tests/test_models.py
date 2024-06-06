from django.db.models.query import IntegrityError
from django.forms import ValidationError
from django.test import TestCase
import string, random

from django.utils import timezone
from company.models import Company

def random_mail():
    wl = string.ascii_letters
    return "".join([random.choice(wl) for _ in range(11)]) + "@mail.com"
    
    
def company_data():
    return {
        "name":"Test Company",
        "email":"company@mail.com",
        "address":"Test Address",
        "phone":"1234567890",
        "description":"Test Description",
        "website":"http://www.company.com",
        "established_date":"2020-01-01"
    }
    
    
class CompanyModelTestCase(TestCase):
    def setUp(self):
        self.data = company_data()
        self.company: Company = Company.objects.create(
            **self.data
        )
        
        
    def test_company_model_created_successfully(self):
        self.assertEqual(self.company.name, "Test Company")
        self.assertEqual(self.company.email, "company@mail.com")
        self.assertEqual(self.company.address, "Test Address")
        self.assertEqual(Company.objects.count(), 1)
        self.assertQuerysetEqual(Company.objects.all(), Company.objects.filter(id=self.company.id))
        
        
    def test_company_model_str_method(self):
        self.assertEqual(str(self.company), "Test Company")
        
    def test_email_uniqueness(self):
        with self.assertRaises(IntegrityError):
            Company.objects.create(
                **self.data
            )
            
    def test_company_model_update_with_valid_data(self):
        update_data = {
            "name": "Updated Company",
            "mail": "updated@company.com",
            "url": "http://www.updatedcompany.com",
            "date": "2024-06-04"
        }
        self.company.name = update_data.get('name')
        self.company.email = update_data.get('mail')
        self.company.website = update_data.get('url')
        self.company.established_date = update_data.get('date')
        self.company.save()
        self.assertEqual(self.company.name, update_data.get('name'))
        self.assertEqual(self.company.email, update_data.get('mail'))
        self.assertEqual(self.company.website, update_data.get('url'))
        self.assertEqual(self.company.established_date, update_data.get('date'))
        
    def test_company_update_with_invalid_data(self):
        self.company.email = "invalidemail"
        self.company.website = "invalidurl"
        self.company.established_date = "hello world"
        self.company.email = "1234567890"
            
        with self.assertRaises(ValidationError):
            self.company.full_clean()
            
        
    def test_company_model_delete(self):
        self.company.delete()
        self.assertEqual(Company.objects.count(), 0)
        
    def test_company_phone_invalid_max_length(self):
        phone = "".join([str(i) for i in range(100)])
        self.data.update({"phone":phone, "email": random_mail()})
        c = Company.objects.create(**self.data)
        with self.assertRaises(ValidationError):
            c.full_clean()
            
    def test_company_website_invalid_url(self):
        website = "www-company"
        self.data.update({"website":website, "email": random_mail()})
        with self.assertRaises(ValidationError):
            Company.objects.create(
                **self.data
            ).full_clean()
            
    def test_company_website_valid_url(self):
        website = "http://www.company.com"
        self.data.update({"website":website, "email": random_mail()})
        company = Company.objects.create(
            **self.data
        )
        self.assertEqual(company.website, website)
        
    def test_future_established_data(self):
        date = timezone.now().date() + timezone.timedelta(days=100)
        self.data.update({"established_date": date, "email": random_mail()})
        
        with self.assertRaises(ValidationError):
            Company.objects.create(**self.data).full_clean()
        
    
    def test_company_name_max_length(self):
        name = "".join(random.choices(string.ascii_letters, k=156))
        self.data.update({"name": name, "email": random_mail()})
        with self.assertRaises(ValidationError):
            Company.objects.create(
                **self.data
            ).full_clean()

    def test_company_address_required(self):
        self.data.pop("address")
        self.data.update({"email": random_mail()})
        with self.assertRaises(ValidationError):
            Company.objects.create(
                **self.data
            ).full_clean()

    def test_company_description_required(self):
        self.data.pop("description")
        self.data.update({"email": random_mail()})
        with self.assertRaises(ValidationError):
            Company.objects.create(
                **self.data
            ).full_clean()

    def test_company_established_date_required(self):
        self.data.pop("established_date")
        self.data.update({"email": random_mail()})
        with self.assertRaises(IntegrityError):
            Company.objects.create(
                **self.data
            ).full_clean()

    def test_company_phone_required(self):
        self.data.pop("phone")
        self.data.update({"email": random_mail()})
        with self.assertRaises(ValidationError):
            Company.objects.create(
                **self.data
            ).full_clean()

    def test_company_email_required(self):
        self.data.pop("email")
        with self.assertRaises(ValidationError):
            Company.objects.create(
                **self.data
            ).full_clean()

    def test_company_website_required(self):
        self.data.pop("website")
        self.data.update({"email": random_mail()})
        with self.assertRaises(ValidationError):
            Company.objects.create(
                **self.data
            ).full_clean()
            

    def test_company_clean_method(self):
        date = timezone.now().date() - timezone.timedelta(days=365*20)
        company = Company(
            name="Test Company",
            email="test@example.com",
            address="Test Address",
            phone="1234567890",
            description="Test Description",
            website="http://www.example.com",
            established_date=date
        )
        company.full_clean()
        self.assertEqual(company.name, "Test Company")
        self.assertEqual(company.email, "test@example.com")
        self.assertEqual(company.address, "Test Address")
        self.assertEqual(company.phone, "1234567890")
        self.assertEqual(company.description, "Test Description")
        self.assertEqual(company.website, "http://www.example.com")
        self.assertEqual(company.established_date, date)
