from django.db import models
from product.models import Product
from customer.models import Customer


# -------------------------
# MAIN QUOTATION
# -------------------------
class Quotation(models.Model):

    STATUS_CHOICES = (
        ('QUOTATION', 'Quotation'),
        ('INVOICE', 'Invoice'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    quotation_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='QUOTATION'
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    advance_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    balance_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total_profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QT-{self.id} - {self.customer}"


# -------------------------
# QUOTATION ITEMS
# -------------------------
class QuotationItem(models.Model):

    quotation = models.ForeignKey(
        Quotation,
        related_name='items',
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    selling_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    cost_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    profit = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return self.product.name


# -------------------------
# QUOTATION TEMPLATE
# -------------------------
class QuotationTemplate(models.Model):

    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class QuotationTemplateItem(models.Model):

    template = models.ForeignKey(
        QuotationTemplate,
        related_name='items',
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    default_qty = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.product.name
