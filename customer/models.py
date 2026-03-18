from django.db import models


class Customer(models.Model):

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=100, blank=True)
    place = models.CharField(max_length=150, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
