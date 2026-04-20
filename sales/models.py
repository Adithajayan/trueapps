from django.db import models
from customer.models import Customer
from product.models import Product


class SalesMaster(models.Model):
    SALE_TYPE_CHOICES = [
        ('B2B', 'B2B (Business)'),
        ('B2C', 'B2C (Consumer)'),
    ]
    invoice_no = models.CharField(max_length=50, unique=True)
    invoice_prefix = models.CharField(max_length=20, default='INV')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    sale_type = models.CharField(max_length=5, choices=SALE_TYPE_CHOICES, default='B2C')
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    material_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.invoice_no

    @property
    def get_taxable_total(self):
        return sum((item.qty * item.selling_price) for item in self.items.all())

    @property
    def get_gst_split(self):
        taxable = self.get_taxable_total
        total_gst = self.total_amount - taxable
        return round(total_gst / 2, 2)

    @property
    def get_gst_total(self):
        return self.total_amount - self.get_taxable_total


class SalesItem(models.Model):
    sales = models.ForeignKey(SalesMaster, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    hsn_code = models.CharField(max_length=50)
    qty = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cgst = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def profit(self):
        return (self.selling_price - self.purchase_price) * self.qty


class InvoiceSetting(models.Model):
    name = models.CharField(max_length=50, unique=True)  # eg: SALES
    prefix = models.CharField(max_length=20)             # eg: TBT-IN

    def __str__(self):
        return f"{self.name} - {self.prefix}"


# Pinneedulla report-ukalku vendi ee 2 models add cheyyu
class SalesReturn(models.Model):
    sale = models.ForeignKey(SalesMaster, on_delete=models.CASCADE, related_name='returns')
    date = models.DateField(auto_now_add=True)
    total_return_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Return for {self.sale.invoice_no}"

class SalesReturnItem(models.Model):
    sales_return = models.ForeignKey(SalesReturn, related_name='return_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty_returned = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2) # Return samayathe rate
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.qty_returned}"


from purchase.models import PurchaseItem

class SalesItemBatch(models.Model):
    sales_item = models.ForeignKey(
        'SalesItem',
        related_name='batches',
        on_delete=models.CASCADE
    )

    purchase_item = models.ForeignKey(
        PurchaseItem,
        on_delete=models.CASCADE
    )

    qty = models.DecimalField(max_digits=10, decimal_places=2)

    purchase_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    selling_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    profit = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.purchase_item.product.name} | {self.qty}"
