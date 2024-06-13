from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import timedelta

from customer.enums import ScheduleChoices

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=33)
    email = models.EmailField(unique=True)
    schedule = models.CharField(max_length=255, 
        choices=ScheduleChoices.choices, 
        default=ScheduleChoices.WEEKLY
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
        
    class Meta:
        ordering = ["-created"]
    
    @property
    def get_schedule(self):
        return self.schedule
        
    @property
    def get_last_service(self):
        return self.services.latest()
        
    @property
    def get_last_service_date(self):
        return self.get_last_service.created.date()
        
    @property
    def get_next_service_date(self):
        if self.schedule == ScheduleChoices.DAILY:
            return self.get_last_service_date + timedelta(days=1)
        elif self.schedule == ScheduleChoices.WEEKLY:
            return self.get_last_service_date + timedelta(weeks=1)
        elif self.schedule == ScheduleChoices.MONTHLY:
            return self.get_last_service_date + timedelta(days=30)
        elif self.schedule == ScheduleChoices.QUARTERLY:
            return self.get_last_service_date + timedelta(days=90)
        elif self.schedule == ScheduleChoices.YEARLY:
            return self.get_last_service_date + timedelta(days=365)
        return None
            
    
        
class ServiceHistory(models.Model):
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name="services"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer.name} - {self.created.date()} - {self.cost}"
        
    class Meta:
        verbose_name_plural = "Service History"
        ordering = ["-created"]
        get_latest_by = ("created")