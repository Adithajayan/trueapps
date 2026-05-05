from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    address = models.TextField()
    daily_salary = models.DecimalField(max_digits=20, decimal_places=10, default=0.00)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name