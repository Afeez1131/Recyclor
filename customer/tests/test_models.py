from decimal import Decimal
import random, string
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError
from django.test import TestCase, Client
from django.utils import timezone
from customer.models import Customer, ServiceHistory


def get_user_data(username="testuser", password="testpass123"):
    if User.objects.filter(username=username).exists():
        username = random_username()
    return {"username": username, "password": password}


def get_customer_data(username="testuser"):
    return {
        "user": User.objects.create_user(**get_user_data()),
        "name": "Meta",
        "address": "Silicon valley",
        "email": "mail@gmail.com",
        "phone": "08120202020",
        "schedule": "weekly",
    }


def random_username():
    return f"testuser{random.randint(1, 100)}"


def random_mail():
    wl = string.ascii_letters
    return "".join([random.choice(wl) for _ in range(11)]) + "@mail.com"


class CustomerModelTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer_data = get_customer_data()

    def test_customer_model_string_repr(self):
        customer = Customer.objects.create(**self.customer_data)
        self.assertEqual(str(customer), self.customer_data.get("name"))

    def test_customer_model_creation(self):
        customer = Customer.objects.create(**self.customer_data)
        self.assertTrue(isinstance(customer, Customer))
        self.assertEqual(Customer.objects.count(), 1)

    def test_customer_model_update(self):
        customer = Customer.objects.create(**self.customer_data)
        customer.name = "Facebook"
        customer.save()
        self.assertEqual(customer.name, "Facebook")
        self.assertEqual(Customer.objects.count(), 1)

    def test_customer_model_deletion(self):
        customer = Customer.objects.create(**self.customer_data)
        self.assertEqual(Customer.objects.count(), 1)
        customer.delete()
        self.assertEqual(Customer.objects.count(), 0)

    def test_email_uniqueness(self):
        Customer.objects.create(**self.customer_data)
        with self.assertRaises(Exception):
            Customer.objects.create(**self.customer_data)

    def test_customer_create_invalid_data(self):
        self.customer_data.update({"email": "invalid_email"})
        c = Customer(**self.customer_data)
        with self.assertRaises(ValidationError):
            c.full_clean()

    def test_customer_name_max_length(self):
        name = "".join(random.choices(string.ascii_letters, k=500))
        self.customer_data.update({"name": name, "email": random_mail()})
        with self.assertRaises(ValidationError):
            Customer.objects.create(**self.customer_data).full_clean()

    def test_company_address_required(self):
        self.customer_data.pop("address")
        self.customer_data.update({"email": random_mail()})
        with self.assertRaises(ValidationError):
            Customer.objects.create(**self.customer_data).full_clean()

    def test_company_get_schedule_property(self):
        customer = Customer.objects.create(**self.customer_data)
        self.assertEqual(customer.get_schedule_display(), "Weekly")

    def test_company_get_last_service_property(self):
        customer = Customer.objects.create(**self.customer_data)
        with self.assertRaises(ObjectDoesNotExist):
            customer.get_last_service

        customer.services.create(
            cost=Decimal(5000), created_by=User.objects.create_user(**get_user_data())
        )
        data = get_user_data()
        data.update({"username": "testuser2"})
        customer.services.create(
            cost=Decimal(12000), created_by=User.objects.create_user(**data)
        )
        self.assertTrue(isinstance(customer.get_last_service, ServiceHistory))
        self.assertEqual(customer.get_last_service.cost, Decimal(12000))

    def test_company_get_last_service_date_property(self):
        customer = Customer.objects.create(**self.customer_data)
        customer.services.create(
            cost=Decimal(5000), created_by=User.objects.create_user(**get_user_data())
        )
        data = get_user_data()
        data.update({"username": "testuser2"})
        customer.services.create(
            cost=Decimal(12000), created_by=User.objects.create_user(**data)
        )
        self.assertEqual(customer.get_last_service_date, timezone.now().date())

    def test_company_property_get_next_service_date(self):
        customer = Customer.objects.create(**self.customer_data)
        customer.services.create(
            cost=Decimal(5000), created_by=User.objects.create_user(**get_user_data())
        )
        self.assertEqual(
            customer.get_next_service_date,
            timezone.now().date() + timezone.timedelta(weeks=1),
        )


class CustomerServiceHistoryTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        random_username = f"testuser{random.randint(1, 100)}"
        self.user_data = get_user_data(username=random_username)
        self.customer_data = get_customer_data()
        self.user = User.objects.create_user(**self.user_data)
        self.customer_data.update({"user_id": self.user.id})
        self.customer = Customer.objects.create(**self.customer_data)

    def test_service_history_string_repr(self):
        history = ServiceHistory.objects.create(
            customer=self.customer, cost=Decimal(5000), created_by=self.user
        )
        self.assertEqual(
            str(history),
            f"{self.customer.name} - {history.created.date()} - {history.cost}",
        )

    def test_service_history_creation_without_customer(self):
        with self.assertRaises(IntegrityError):
            ServiceHistory.objects.create(cost=Decimal(5000), created_by=self.user)

    def test_service_history_creation_without_valid_customer(self):
        with self.assertRaises(ObjectDoesNotExist):
            ServiceHistory.objects.create(
                customer=Customer.objects.get(id=100),
                cost=Decimal(5000),
                created_by=self.user,
            )

    def test_service_history_creation(self):
        self.assertEqual(ServiceHistory.objects.count(), 0)
        service = ServiceHistory.objects.create(
            customer=self.customer, cost=Decimal(5000), created_by=self.user
        )
        self.assertEqual(ServiceHistory.objects.count(), 1)
        self.assertEqual(service.customer, self.customer)
        self.assertEqual(service.cost, Decimal(5000))

    def test_service_history_update(self):
        service = ServiceHistory.objects.create(
            customer=self.customer, cost=Decimal(5000), created_by=self.user
        )
        service.cost = Decimal(10000)
        service.save()
        self.assertEqual(service.cost, Decimal(10000))

    def test_service_history_deletion(self):
        service = ServiceHistory.objects.create(
            customer=self.customer, cost=Decimal(5000), created_by=self.user
        )
        self.assertEqual(ServiceHistory.objects.count(), 1)
        service.delete()
        self.assertEqual(ServiceHistory.objects.count(), 0)

    def test_service_history_ordering(self):
        history1 = ServiceHistory.objects.create(
            customer=self.customer, cost=Decimal(12000), created_by=self.user
        )
        history2 = ServiceHistory.objects.create(
            customer=self.customer, cost=Decimal(25000), created_by=self.user
        )
        self.assertListEqual(list(ServiceHistory.objects.all()), [history2, history1])
        self.assertEqual(ServiceHistory.objects.first(), history2)
