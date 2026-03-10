from django.db import models
from staff.models import Staff

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('P', 'Present'),
        ('A', 'Absent'),
        ('H', 'Half Day'),
    )

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('staff', 'date')

    def __str__(self):
        return f"{self.staff.name} - {self.date}"


class Advance(models.Model):

    PAYMENT_MODE = (
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('GPay', 'GPay'),
        ('PhonePe', 'PhonePe'),
        ('Bank', 'Bank Transfer'),
    )

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.PositiveIntegerField()
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE)
    note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.staff.name} - {self.amount}"


class Salary(models.Model):

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()

    present = models.IntegerField(default=0)
    half_day = models.IntegerField(default=0)
    absent = models.IntegerField(default=0)

    daily_salary = models.PositiveIntegerField(default=500)
    advance_amount = models.PositiveIntegerField(default=0)

    total_salary = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.staff.name} - {self.month}/{self.year}"
