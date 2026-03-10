from django.db import models

class Supplier(models.Model):

    supplier_code = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    name = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)

    email = models.EmailField(blank=True)
    gstin = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True, null=True)

    opening_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    image = models.ImageField(
        upload_to='suppliers/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.supplier_code:
            last = Supplier.objects.order_by('-id').first()
            if last:
                last_id = int(last.supplier_code.replace('SUP', ''))
                self.supplier_code = f"SUP{last_id + 1:03d}"
            else:
                self.supplier_code = "SUP001"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.supplier_code} - {self.name}"



