from django.db import models
from decimal import Decimal

class Staff(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    address = models.TextField()
    # 👇 DAILY salary (decimal support)
    daily_salary = models.DecimalField(
        max_digits=15,
        decimal_places=10
    )
    status = models.BooleanField(default=True)
    def __str__(self):
        return self.name