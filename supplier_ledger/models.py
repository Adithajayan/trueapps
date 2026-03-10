from django.db import models
from supplier_master.models import Supplier


class SupplierLedger(models.Model):

    SOURCE_CHOICES = (
        ('OPENING', 'Opening Balance'),
        ('PURCHASE', 'Purchase'),
        ('PAYMENT', 'Payment'),
        ('MANUAL', 'Manual Entry'),
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='ledgers'
    )

    date = models.DateField()

    particular = models.CharField(max_length=255)

    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES
    )

    reference_id = models.IntegerField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'id']

    def __str__(self):
        return f"{self.supplier.name} | {self.particular}"
