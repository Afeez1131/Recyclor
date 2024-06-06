from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Company(models.Model):
    name = models.CharField(max_length=155)
    email = models.EmailField(unique=True)
    address = models.TextField()
    phone = models.CharField(max_length=33)
    description = models.TextField()
    website = models.URLField()
    established_date = models.DateField()
    
    def clean(self):
        super().clean()
        value = self.established_date
        if isinstance(value, str):
            try:
                value = timezone.datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError({"established_date": "Invalid established date provided"})
        if value >= timezone.now().date():
            raise ValidationError({"established_data": "Established data cannot be greater than today"})
        
    
    
    def __str__(self):
        return str(self.name)
    