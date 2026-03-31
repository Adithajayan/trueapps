from django.shortcuts import render, redirect, get_object_or_404
from .models import Job


# ---------------- ENQUIRY ADD ----------------
def add_enquiry(request):

    if request.method == "POST":
        Job.objects.create(
            job_type="ENQUIRY",
            name=request.POST.get("name"),
            place=request.POST.get("place"),
            care_of=request.POST.get("care_of"),
            date=request.POST.get("date"),
        )
        return redirect("enquiry_list")

    return render(request, "job_management/add_enquiry.html")


# ---------------- MAINTENANCE ADD ----------------
def add_maintenance(request):

    if request.method == "POST":
        Job.objects.create(
            job_type="MAINTENANCE",
            name=request.POST.get("name"),
            place=request.POST.get("place"),
            date=request.POST.get("date"),
            maintenance_details=request.POST.get("details"),
        )
        return redirect("maintenance_list")

    return render(request, "job_management/add_maintenance.html")


# ---------------- SERVICE ADD ----------------
def add_service(request):

    if request.method == "POST":
        Job.objects.create(
            job_type="SERVICE",
            name=request.POST.get("name"),
            place=request.POST.get("place"),
            date=request.POST.get("date"),
            next_maintenance_date=request.POST.get("next_date"),
        )
        return redirect("service_list")

    return render(request, "job_management/add_service.html")


# ---------------- LIST PAGES ----------------
from django.db.models import Q
from datetime import date

def enquiry_list(request):

    status_filter = request.GET.get("status")
    search_query = request.GET.get("q")

    jobs = Job.objects.filter(job_type="ENQUIRY")

    # SEARCH
    if search_query:
        jobs = jobs.filter(
            Q(name__icontains=search_query) |
            Q(place__icontains=search_query)
        )

    # STATUS FILTER
    if status_filter:
        jobs = jobs.filter(status=status_filter)

    # TODAY HIGHLIGHT
    today = date.today()

    total_count = Job.objects.filter(job_type="ENQUIRY").count()
    pending_count = Job.objects.filter(job_type="ENQUIRY",status="PENDING").count()
    completed_count = Job.objects.filter(job_type="ENQUIRY",status="COMPLETED").count()

    context = {
        "jobs": jobs,
        "today": today,
        "status_filter": status_filter,
        "search_query": search_query,
        "total_count": total_count,
        "pending_count": pending_count,
        "completed_count": completed_count,
    }

    return render(request,"job_management/enquiry_list.html",context)



def toggle_status(request, id):
    job = get_object_or_404(Job, id=id)

    if job.status == "PENDING":
        job.status = "COMPLETED"
    else:
        job.status = "PENDING"

    job.save()
    return redirect(request.META.get('HTTP_REFERER'))




from django.db.models import Q, Count
from datetime import date
import calendar


def maintenance_list(request):

    jobs = Job.objects.filter(job_type="MAINTENANCE")

    # ================= SEARCH =================
    search = request.GET.get("q")
    if search:
        jobs = jobs.filter(
            Q(name__icontains=search) |
            Q(place__icontains=search)
        )

    # ================= MONTH FILTER =================
    month = request.GET.get("month")
    if month:
        jobs = jobs.filter(date__month=month)

    # ================= STATUS FILTER =================
    status = request.GET.get("status")
    if status:
        jobs = jobs.filter(status=status)

    # ================= MONTH PENDING ALERT =================
    pending_summary = (
        Job.objects.filter(
            job_type="MAINTENANCE",
            status="PENDING"
        )
        .values("date__month")
        .annotate(total=Count("id"))
        .order_by("date__month")
    )

    month_pending = []
    for item in pending_summary:
        month_pending.append({
            "month": calendar.month_name[item["date__month"]],
            "count": item["total"]
        })

    # JAN → DEC dropdown data
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    context = {
        "jobs": jobs.order_by("-date"),
        "month_pending": month_pending,
        "months": months,
        "selected_month": month,
        "selected_status": status,
        "search": search,
    }

    return render(
        request,
        "job_management/maintenance_list.html",
        context
    )


def delete_maintenance(request, id):

    job = get_object_or_404(Job, id=id)

    if request.method == "POST":
        job.delete()
        return redirect("maintenance_list")

    return render(
        request,
        "job_management/delete_maintenance.html",
        {"job": job}
    )


from django.shortcuts import render, redirect, get_object_or_404
from .models import Job


def edit_maintenance(request, id):

    job = get_object_or_404(
        Job,
        id=id,
        job_type="MAINTENANCE"
    )

    if request.method == "POST":

        job.name = request.POST.get("name")
        job.place = request.POST.get("place")
        job.date = request.POST.get("date")
        job.maintenance_details = request.POST.get("details")

        job.save()

        return redirect("maintenance_list")

    return render(
        request,
        "job_management/edit_maintenance.html",
        {"job": job}
    )

from django.shortcuts import render, get_object_or_404
from .models import Job


def view_maintenance(request, id):

    job = get_object_or_404(Job, id=id)

    # same customer previous maintenance history
    history = Job.objects.filter(
        job_type="MAINTENANCE",
        name=job.name,
        place=job.place
    ).order_by("-date")

    context = {
        "job": job,
        "history": history,
    }

    return render(
        request,
        "job_management/view_maintenance.html",
        context
    )




from django.db.models import Q
from datetime import date


def service_list(request):

    search = request.GET.get("q")
    month = request.GET.get("month")
    status = request.GET.get("status")

    services = Job.objects.filter(job_type="SERVICE")

    # SEARCH
    if search:
        services = services.filter(
            Q(name__icontains=search) |
            Q(place__icontains=search)
        )

    # MONTH FILTER
    if month:
        services = services.filter(date__month=month)

    # STATUS FILTER
    if status:
        services = services.filter(status=status)

    # PREVIOUS MONTH PENDING ALERT
    today = date.today()

    previous_pending = Job.objects.filter(
        job_type="SERVICE",
        status="PENDING",
        date__month__lt=today.month
    )

    context = {
        "services": services.order_by("-date"),
        "previous_pending": previous_pending,
        "search": search,
        "month": month,
        "status": status,
    }

    return render(
        request,
        "job_management/service_list.html",
        context
    )

def view_service(request, id):

    job = get_object_or_404(Job, id=id)

    history = Job.objects.filter(
        job_type="SERVICE",
        name=job.name,
        place=job.place
    ).order_by("-date")

    return render(
        request,
        "job_management/view_service.html",
        {"job": job, "history": history}
    )

def edit_service(request, id):

    job = get_object_or_404(Job, id=id)

    if request.method == "POST":
        job.name = request.POST.get("name")
        job.place = request.POST.get("place")
        job.date = request.POST.get("date")
        job.next_maintenance_date = request.POST.get("next_date")
        job.save()

        return redirect("service_list")

    return render(
        request,
        "job_management/edit_service.html",
        {"job": job}
    )

# ================= DELETE SERVICE =================
def delete_service(request, id):

    job = get_object_or_404(Job, id=id, job_type="SERVICE")

    if request.method == "POST":
        job.delete()
        return redirect("service_list")

    return render(
        request,
        "job_management/delete_service.html",
        {"job": job}
    )





# ---------------- COMPLETE BUTTON ----------------
def mark_completed(request, id):
    job = get_object_or_404(Job, id=id)
    job.status = "COMPLETED"
    job.save()
    return redirect(request.META.get('HTTP_REFERER'))


from .models import Job, Reminder


def job_dashboard(request):

    # ================= JOB COUNTS =================
    enquiry_count = Job.objects.filter(
        job_type="ENQUIRY",
        status="PENDING"
    ).count()

    maintenance_count = Job.objects.filter(
        job_type="MAINTENANCE",
        status="PENDING"
    ).count()

    service_count = Job.objects.filter(
        job_type="SERVICE",
        status="PENDING"
    ).count()

    # ================= REMINDERS =================
    today = date.today()

    # total pending
    reminder_count = Reminder.objects.filter(
        is_completed=False
    ).count()

    # today reminders
    today_reminders = Reminder.objects.filter(
        reminder_date=today,
        is_completed=False
    ).order_by("reminder_date")

    # 🔴 overdue reminders
    overdue_count = Reminder.objects.filter(
        reminder_date__lt=today,
        is_completed=False
    ).count()

    context = {
        "enquiry_count": enquiry_count,
        "maintenance_count": maintenance_count,
        "service_count": service_count,
        "reminder_count": reminder_count,
        "today_reminders": today_reminders,
        "overdue_count": overdue_count,
        "today": today,
    }

    return render(
        request,
        "job_management/job_dashboard.html",
        context
    )





def edit_job(request, id):

    job = get_object_or_404(Job, id=id)

    if request.method == "POST":
        job.name = request.POST.get("name")
        job.place = request.POST.get("place")
        job.date = request.POST.get("date")
        job.save()

        return redirect("enquiry_list")

    return render(request, "job_management/edit_job.html", {"job": job})




def today_reminders(request):

    today = date.today()

    today_reminders = Reminder.objects.filter(
        reminder_date=today,
        is_completed=False
    ).order_by("reminder_date")

    return render(
        request,
        "job_management/today_reminders.html",
        {"today_reminders": today_reminders}
    )



def add_reminder(request):

    if request.method == "POST":

        title = request.POST.get("title")
        reminder_type = request.POST.get("reminder_type")
        reminder_date = request.POST.get("reminder_date")
        notes = request.POST.get("notes")

        Reminder.objects.create(
            title=title,
            reminder_type=reminder_type,
            reminder_date=reminder_date,
            notes=notes,
        )

        # save kazhinjal dashboard lek
        return redirect("job_dashboard")

    return render(request, "job_management/add_reminder.html")

from django.shortcuts import render, redirect, get_object_or_404
from .models import Reminder
from datetime import date



def complete_reminder(request, id):

    reminder = get_object_or_404(Reminder, id=id)
    reminder.is_completed = True
    reminder.save()

    return redirect("reminders")
def edit_reminder(request, id):

    reminder = get_object_or_404(Reminder, id=id)

    if request.method == "POST":
        reminder.title = request.POST.get("title")
        reminder.reminder_type = request.POST.get("reminder_type")
        reminder.reminder_date = request.POST.get("reminder_date")
        reminder.notes = request.POST.get("notes")
        reminder.save()

        return redirect("reminders")

    return render(
        request,
        "job_management/edit_reminder.html",
        {"r": reminder}
    )

def delete_reminder(request, id):

    reminder = get_object_or_404(Reminder, id=id)

    if request.method == "POST":
        reminder.delete()
        return redirect("reminders")

    return render(
        request,
        "job_management/delete_reminder.html",
        {"r": reminder}
    )


from django.shortcuts import get_object_or_404, redirect

def toggle_reminder_status(request, id):

    reminder = get_object_or_404(Reminder, id=id)

    reminder.is_completed = not reminder.is_completed
    reminder.save()

    return redirect("reminders")


from datetime import date

def reminder_list(request):

    today = date.today()

    pending_reminders = Reminder.objects.filter(
        is_completed=False
    ).order_by("reminder_date")

    completed_reminders = Reminder.objects.filter(
        is_completed=True
    ).order_by("-reminder_date")

    context = {
        "pending_reminders": pending_reminders,
        "completed_reminders": completed_reminders,
        "today": today,
    }

    return render(
        request,
        "job_management/reminder_list.html",
        context
    )


# ================= DELETE ENQUIRY =================
def delete_enquiry(request, id):
    job = get_object_or_404(Job, id=id, job_type="ENQUIRY")

    if request.method == "POST":
        job.delete()
        return redirect("enquiry_list")

    return render(
        request,
        "job_management/delete_enquiry.html",
        {"job": job}
    )