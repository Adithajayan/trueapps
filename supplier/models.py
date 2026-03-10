from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class SupplierPurchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_date = models.DateField()

    def __str__(self):
        return f"{self.supplier.name} - {self.product_name}"


class SupplierPayment(models.Model):
    purchase = models.ForeignKey(SupplierPurchase, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    mode = models.CharField(max_length=50)  # Cash / UPI / Bank
    date = models.DateField()
    note = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.purchase.supplier.name} - {self.amount}"
