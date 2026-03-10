from django.db import models


class Job(models.Model):

    JOB_TYPE_CHOICES = (
        ('ENQUIRY', 'Enquiry'),
        ('MAINTENANCE', 'Maintenance'),
        ('SERVICE', 'Service'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Finished'),
    )

    # common fields
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)

    name = models.CharField(max_length=100)
    place = models.CharField(max_length=150)
    care_of = models.CharField(max_length=100, blank=True)

    date = models.DateField()

    maintenance_details = models.TextField(blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.job_type}"


class Reminder(models.Model):

    REMINDER_TYPE = (
        ('CALL', 'Call'),
        ('PAYMENT', 'Payment'),
        ('VISIT', 'Visit'),
        ('OTHER', 'Other'),
    )

    title = models.CharField(max_length=200)
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE)
    reminder_date = models.DateField()

    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
