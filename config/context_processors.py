from job_management.models import Job, Reminder
from datetime import date


def job_notifications(request):

    # pending jobs badge (Job Management)
    pending_jobs = Job.objects.filter(status="PENDING").count()

    # 🔔 MANUAL REMINDERS (TODAY)
    today = date.today()

    reminder_count = Reminder.objects.filter(
        reminder_date=today,
        is_completed=False
    ).count()

    return {
        "pending_jobs_count": pending_jobs,
        "reminder_count": reminder_count,
    }
