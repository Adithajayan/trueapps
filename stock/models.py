from django.db import models
from product.models import Product


class Stock(models.Model):

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='stock'
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name


# stock/models.py
# stock/models.py update
class StockHistory(models.Model):
    STOCK_TYPE = (
        ('OPENING', 'Opening Stock'),
        ('PURCHASE', 'Purchase'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.DecimalField(max_digits=10, decimal_places=2)

    # GST breakdown
    cgst = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    sgst = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    # Rates
    selling_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Basic Rate

    type = models.CharField(max_length=20, choices=STOCK_TYPE)
    reference_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_gst(self):
        return self.cgst + self.sgst


from purchase.models import PurchaseItem
from sales.models import SalesItem
from django.db.models import Sum

def detailed_stock_register(request):

    purchase_items = PurchaseItem.objects.select_related(
        'product',
        'purchase',
        'purchase__supplier'
    ).order_by('-purchase__purchase_date')

    stock_rows = []

    for item in purchase_items:
        sold_qty = SalesItem.objects.filter(
            purchase_item=item
        ).aggregate(total=Sum('qty'))['total'] or 0

        balance_qty = item.qty - sold_qty

        stock_rows.append({
            'product': item.product.name,
            'supplier': item.purchase.supplier.name,
            'date': item.purchase.purchase_date,
            'rate': item.rate,
            'purchased_qty': item.qty,
            'sold_qty': sold_qty,
            'balance_qty': balance_qty,
        })

    return render(request, 'stock/stock_register_detailed.html', {
        'stock_rows': stock_rows
    })
