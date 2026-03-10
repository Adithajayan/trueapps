from django.db import models
from django.utils import timezone
from django.db.models import Sum  # 🔥 Ithu nirbandhamaanu
from supplier_master.models import Supplier
from product.models import Product

class Purchase(models.Model):
    PAYMENT_TYPE = (
        ('CREDIT', 'Credit Purchase'),
        ('CASH', 'Cash Purchase'),
        ('UPI', 'UPI Purchase'),
        ('BANK', 'Bank Transfer'),
    )

    TAX_TYPE = (
        ('EXCLUSIVE', 'Exclusive'),
        ('INCLUSIVE', 'Inclusive'),
    )

    invoice_no = models.CharField(max_length=50, unique=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    purchase_date = models.DateField(default=timezone.now)

    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
    tax_type = models.CharField(max_length=20, choices=TAX_TYPE, default='EXCLUSIVE')

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            from .models import InvoiceSettings
            settings = InvoiceSettings.objects.first()
            prefix = settings.purchase_prefix if settings else "TBT-PUR"

            last = Purchase.objects.filter(
                invoice_no__startswith=prefix
            ).order_by('-id').first()

            if last:
                try:
                    last_num = int(last.invoice_no.split('-')[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1

            self.invoice_no = f"{prefix}-{str(new_num).zfill(3)}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_no


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(
        'Purchase',
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    qty = models.DecimalField(max_digits=10, decimal_places=2)

    # Available stock in this specific batch
    quantity_at_hand = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Remaining quantity in this batch"
    )

    rate = models.DecimalField(max_digits=10, decimal_places=2)
    cgst = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    selling_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Selling price for this batch (used in sales)"
    )
    total = models.DecimalField(max_digits=12, decimal_places=2)

    # 1. Total Sold Qty (Returns illathe aage ethra poyi)
    def get_total_sold(self):
        from sales.models import SalesItemBatch
        # Filter batches related to this specific PurchaseItem
        return SalesItemBatch.objects.filter(purchase_item=self).aggregate(Sum('qty'))['qty__sum'] or 0

    # 2. Total Returned Qty (Ethra thirichu vannu)
    def get_total_returned(self):
        # Calculation: (Current Available + Sold) - Original Purchased Qty
        net_change = (self.quantity_at_hand + self.get_total_sold()) - self.qty
        return max(0, net_change)

    def save(self, *args, **kwargs):
        if not self.id:
            self.quantity_at_hand = self.qty
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - Batch ID: {self.id}"


class InvoiceSettings(models.Model):
    purchase_prefix = models.CharField(
        max_length=20,
        default="TBT-PUR"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Purchase Prefix: {self.purchase_prefix}"


class PurchaseReturn(models.Model):
    # Ethu purchase-inte ethireyaanu return ennu ariyaan
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='returns')
    return_no = models.CharField(max_length=50, unique=True, blank=True)
    return_date = models.DateField(default=timezone.now)
    reason = models.TextField(blank=True, null=True)
    total_return_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.return_no:
            # Simple logic for Return No (e.g., TBT-RET-001)
            last = PurchaseReturn.objects.all().order_by('-id').first()
            if last:
                last_id = last.id + 1
            else:
                last_id = 1
            self.return_no = f"TBT-RET-{str(last_id).zfill(3)}"
        super().save(*args, **kwargs)

class PurchaseReturnItem(models.Model):
    purchase_return = models.ForeignKey(PurchaseReturn, on_delete=models.CASCADE, related_name='return_items')
    # Ethu Batch-il ninnaanu return cheyyunnath ennu select cheyyaan
    purchase_item = models.ForeignKey(PurchaseItem, on_delete=models.CASCADE)
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2) # Return rate (usually same as purchase rate)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Return: {self.purchase_item.product.name}"