from django.db import models
from django.contrib.auth.models import User

class PermissionTable(models.Model):
    privilege = models.CharField(max_length=100)
    class Meta:
        permissions = (
            ("c_admin", "Administrator"),
            ("c_customer", "Customer"),
        )
        
        
