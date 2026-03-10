from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Product(models.Model):

    UNIT_CHOICES = (
        ('PCS', 'PCS'),
        ('LTR', 'LTR'),
        ('MTR', 'MTR'),
    )

    product_code = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )

    hsn_code = models.CharField(max_length=50, blank=True)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    purchase_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    sales_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    mrp = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    cgst = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    sgst = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    cess = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default='PCS'
    )

    # ✅ NEW FIELD (LOW STOCK ALERT)
    minimum_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=5
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.product_code:
            last = Product.objects.order_by('-id').first()
            if last and last.product_code:
                num = int(last.product_code.replace('PRD', '')) + 1
            else:
                num = 1
            self.product_code = f"PRD{num:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_code} - {self.name}"



@receiver(post_save, sender=Product)
def create_stock(sender, instance, created, **kwargs):
    if created:
        from stock.models import Stock   # ✅ lazy import (THIS IS KEY)
        Stock.objects.create(product=instance)
