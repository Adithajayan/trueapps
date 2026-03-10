from django.db import models
from customer.models import Customer   # ✅ MASTER CUSTOMER

class CustomerWork(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    work_date = models.DateField()

    def __str__(self):
        return f"{self.customer.name} - {self.title}"


class WorkPayment(models.Model):
    work = models.ForeignKey(CustomerWork, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    mode = models.CharField(max_length=50)
    date = models.DateField()
    note = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.work.customer.name} - {self.amount}"

