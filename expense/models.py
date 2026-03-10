from django.db import models


class ExpenseType(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ExpenseCategory(models.Model):
    expense_type = models.ForeignKey(
        ExpenseType,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.expense_type.name} - {self.name}"


class Partner(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Expense(models.Model):

    STATUS_CHOICES = (
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
    )

    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    expense_type = models.ForeignKey(
        ExpenseType,
        on_delete=models.CASCADE
    )

    # CATEGORY OPTIONAL
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # PARTNER OPTIONAL
    partner = models.ForeignKey(
        Partner,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    note = models.TextField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PAID'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.category:
            return f"{self.category.name} - {self.amount}"
        return f"Uncategorized Expense - {self.amount}"
