from datetime import date
import calendar
from staff.models import Staff
from .models import Attendance
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.http import JsonResponse
from datetime import date
import calendar

from datetime import date
import calendar
from .models import Attendance, Staff

from datetime import date
import calendar
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from staff.models import Staff
from .models import Attendance

from datetime import date
import calendar
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from staff.models import Staff
from .models import Attendance


@login_required
def attendance_mark(request):

    month = int(request.GET.get("month", date.today().month))
    year = int(request.GET.get("year", date.today().year))

    # ✅ dropdown data
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years = list(range(2024, 2036))

    staffs = Staff.objects.filter(status=True)

    total_days = calendar.monthrange(year, month)[1]
    days = list(range(1, total_days + 1))

    attendance_data = Attendance.objects.filter(
        date__month=month,
        date__year=year
    )

    attendance_map = {}

    for att in attendance_data:
        attendance_map.setdefault(att.staff_id, {})
        attendance_map[att.staff_id][att.date.day] = att.status

    attendance_rows = []

    for staff in staffs:
        row_days = []

        for d in days:
            status = attendance_map.get(staff.id, {}).get(d)

            row_days.append({
                "day": d,
                "status": status
            })

        attendance_rows.append({
            "staff": staff,
            "days": row_days
        })

    context = {
        "attendance_rows": attendance_rows,
        "days": days,
        "month": month,
        "year": year,
        "months": months,
        "years": years,
        "month_name": calendar.month_name[month],
    }

    return render(request, "attendance/attendance_mark.html", context)










from django.http import JsonResponse
from datetime import datetime

@login_required
def mark_attendance(request):
    staff_id = request.POST.get('staff_id')
    day = int(request.POST.get('day'))
    month = int(request.POST.get('month'))
    year = int(request.POST.get('year'))
    status = request.POST.get('status')

    attendance_date = date(year, month, day)

    Attendance.objects.update_or_create(
        staff_id=staff_id,
        date=attendance_date,
        defaults={'status': status}
    )

    return JsonResponse({'success': True})




from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Count, Sum, Q, DecimalField


@login_required
def attendance_summary(request):
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    # 1. Attendance Counts separately to avoid Join duplication issues
    staffs = Staff.objects.filter(status=True).annotate(
        present_count=Count('attendance', filter=Q(
            attendance__date__month=month,
            attendance__date__year=year,
            attendance__status='P'
        )),
        absent_count=Count('attendance', filter=Q(
            attendance__date__month=month,
            attendance__date__year=year,
            attendance__status='A'
        )),
        halfday_count=Count('attendance', filter=Q(
            attendance__date__month=month,
            attendance__date__year=year,
            attendance__status='H'
        )),
    )

    # 2. Get Advance Sums separately
    advances = Advance.objects.filter(
        date__month=month,
        date__year=year
    ).values('staff_id').annotate(
        total_adv=Sum('amount')
    )

    # Mapping advance to a dictionary for easy lookup: {staff_id: amount}
    advance_map = {item['staff_id']: item['total_adv'] for item in advances}

    summary_data = []

    for s in staffs:
        daily = s.daily_salary
        # Advance map-il ninnu staff-inte amount edukkunnu
        staff_advance = Decimal(advance_map.get(s.id, 0))

        # Full precision calculation
        total_earned = (Decimal(s.present_count) * daily) + \
                       (Decimal(s.halfday_count) * (daily / Decimal('2')))

        final_salary = total_earned - staff_advance

        # -------------------------------------------------------
        # 👇 POINT ROUNDING LOGIC
        # final_salary.quantize(Decimal('1')) ennulath point ozhivakkum
        # ROUND_HALF_UP upayogikkunnathukondu .5-nu melaaneki round-up aakum
        # -------------------------------------------------------
        rounded_salary = final_salary.quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        summary_data.append({
            'staff': s,
            'present': s.present_count,
            'absent': s.absent_count,
            'halfday': s.halfday_count,
            'advance': staff_advance,
            'salary': rounded_salary, # Ippo ₹ 5058 aayi varum
        })

    return render(request, 'attendance/attendance_summary.html', {
        'summary_data': summary_data,
        'month': month,
        'year': year,
    })



@login_required
def add_advance(request):

    staffs = Staff.objects.filter(status=True)

    if request.method == "POST":
        Advance.objects.create(
            staff_id=request.POST.get('staff'),
            date=request.POST.get('date'),
            amount=request.POST.get('amount'),
            payment_mode=request.POST.get('payment_mode'),
            note=request.POST.get('note'),
        )
        return redirect('advance_list')

    return render(request, 'attendance/add_advance.html', {
        'staffs': staffs
    })

from django.db.models import Sum
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from datetime import date
from .models import Advance
from staff.models import Staff


def advance_list(request):

    month = int(request.GET.get('month', date.today().month))
    year = int(request.GET.get('year', date.today().year))

    advances = Advance.objects.filter(
        date__month=month,
        date__year=year
    ).order_by('-date')

    total_advance = advances.aggregate(
        total=Sum('amount')
    )['total'] or 0

    return render(request, 'attendance/advance_list.html', {
        'advances': advances,
        'month': month,
        'year': year,
        'total_advance': total_advance
    })


def advance_add(request):

    staffs = Staff.objects.all()

    month = request.GET.get('month')
    year = request.GET.get('year')

    if request.method == 'POST':
        Advance.objects.create(
            staff_id=request.POST['staff'],
            date=request.POST['date'],
            amount=request.POST['amount'],
            payment_mode=request.POST['payment_mode'],
            note=request.POST.get('note')
        )
        return redirect(f"/advance/?month={month}&year={year}")

    return render(request, 'attendance/advance_add.html', {
        'staffs': staffs,
        'month': month,
        'year': year
    })


def advance_edit(request, id):

    adv = get_object_or_404(Advance, id=id)
    staffs = Staff.objects.all()

    if request.method == 'POST':
        adv.staff_id = request.POST['staff']
        adv.date = request.POST['date']
        adv.amount = request.POST['amount']
        adv.payment_mode = request.POST['payment_mode']
        adv.note = request.POST.get('note')
        adv.save()
        return redirect('/advance/')

    return render(request, 'attendance/advance_edit.html', {
        'adv': adv,
        'staffs': staffs
    })


def advance_delete(request, id):

    adv = get_object_or_404(Advance, id=id)

    if request.method == 'POST':
        adv.delete()
        return redirect('/advance/')

    return render(request, 'attendance/advance_delete.html', {
        'adv': adv
    })


from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum
from datetime import date

from staff.models import Staff
from .models import Attendance, Advance


def salary_total(request):
    month = int(request.GET.get('month'))
    year = int(request.GET.get('year'))

    staffs = Staff.objects.filter(status=True)

    rows = []
    grand_total = Decimal('0')  # Ippo kaiyil ninnum pokunna cash (Net)
    total_actual_salary = Decimal('0')  # Advance kuraykkatha full salary (Gross)
    total_advance_given = Decimal('0')  # Kodutha aake advance

    for staff in staffs:
        present = Attendance.objects.filter(
            staff=staff,
            status='P',
            date__month=month,
            date__year=year
        ).count()

        half = Attendance.objects.filter(
            staff=staff,
            status='H',
            date__month=month,
            date__year=year
        ).count()

        advance = Advance.objects.filter(
            staff=staff,
            date__month=month,
            date__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0

        daily = staff.daily_salary

        # Deduction-u munpulla calculation
        actual_salary = (present * daily) + (half * (daily / Decimal('2')))

        # Deduction-u sheshamulla calculation
        final_salary = round(actual_salary - Decimal(advance))

        rows.append({
            'staff': staff,
            'present': present,
            'half': half,
            'advance': advance,
            'salary': final_salary
        })

        # Grand totals calculation
        grand_total += Decimal(final_salary)
        total_actual_salary += Decimal(actual_salary)
        total_advance_given += Decimal(advance)

    context = {
        'rows': rows,
        'month': month,
        'year': year,
        'grand_total': grand_total,
        'total_actual_salary': round(total_actual_salary),
        'total_advance_given': total_advance_given,
    }

    return render(request, 'attendance/salary_total.html', context)







@login_required
def salary_sheet(request):
    return render(request, 'attendance/salary_sheet.html')


from django.db.models import Sum

def calculate_salary(staff, month, year, daily_salary=500):

    present = Attendance.objects.filter(
        staff=staff,
        date__month=month,
        date__year=year,
        status='P'
    ).count()

    half = Attendance.objects.filter(
        staff=staff,
        date__month=month,
        date__year=year,
        status='H'
    ).count()

    advance = Advance.objects.filter(
        staff=staff,
        date__month=month,
        date__year=year
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_salary = (
        present * daily_salary +
        half * (daily_salary // 2)
    ) - advance

    return {
        'present': present,
        'half': half,
        'advance': advance,
        'salary': total_salary
    }


from django.template.loader import render_to_string

from django.http import HttpResponse
import calendar

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.db.models import Sum

import calendar

def staff_salary_pdf(request, staff_id):
    from weasyprint import HTML

    month = int(request.GET.get("month", 1))
    year = int(request.GET.get("year", 2024))

    staff = get_object_or_404(Staff, id=staff_id)

    presents = Attendance.objects.filter(
        staff=staff,
        status='P',
        date__month=month,
        date__year=year
    )

    absents = Attendance.objects.filter(
        staff=staff,
        status='A',
        date__month=month,
        date__year=year
    )

    halfdays = Attendance.objects.filter(
        staff=staff,
        status='H',
        date__month=month,
        date__year=year
    )

    advances = Advance.objects.filter(
        staff=staff,
        date__month=month,
        date__year=year
    )

    advance_total = advances.aggregate(
        total=Sum('amount')
    )['total'] or 0

    salary = (
        presents.count() * staff.daily_salary +
        halfdays.count() * (staff.daily_salary / 2)
    ) - advance_total

    html = render_to_string(
        "attendance/salary_pdf.html",
        {
            "staff": staff,
            "month": month,
            "year": year,
            "month_name": calendar.month_name[month],
            "total_days": calendar.monthrange(year, month)[1],
            "present": presents.count(),
            "absent": absents.count(),
            "half": halfdays.count(),
            "absent_dates": ", ".join(
                [a.date.strftime("%d/%m/%Y") for a in absents]
            ) or "None",
            "half_dates": ", ".join(
                [a.date.strftime("%d/%m/%Y") for a in halfdays]
            ) or "None",
            "advances": advances,
            "advance_total": advance_total,
            "salary": round(salary),
        }
    )

    pdf = HTML(
        string=html,
        base_url=request.build_absolute_uri('/')
    ).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")

    response['Content-Disposition'] = \
        f'attachment; filename="{staff.name}_salary_{month}_{year}.pdf"'

    return response


from django.template.loader import render_to_string



def export_salary_total_pdf(request):
    from weasyprint import HTML
    month = int(request.GET.get('month'))
    year = int(request.GET.get('year'))
    staffs = Staff.objects.filter(status=True)

    rows = []
    grand_total = Decimal('0')
    total_actual_salary = Decimal('0')
    total_advance_given = Decimal('0')

    for staff in staffs:
        present = Attendance.objects.filter(staff=staff, status='P', date__month=month, date__year=year).count()
        half = Attendance.objects.filter(staff=staff, status='H', date__month=month, date__year=year).count()
        advance = \
        Advance.objects.filter(staff=staff, date__month=month, date__year=year).aggregate(total=Sum('amount'))[
            'total'] or 0

        daily = staff.daily_salary
        actual_salary = (present * daily) + (half * (daily / Decimal('2')))
        final_salary = round(actual_salary - Decimal(advance))

        rows.append({
            'staff': staff,
            'present': present,
            'half': half,
            'advance': advance,
            'salary': final_salary
        })

        grand_total += Decimal(final_salary)
        total_actual_salary += Decimal(actual_salary)
        total_advance_given += Decimal(advance)

    context = {
        'rows': rows,
        'month': month,
        'year': year,
        'grand_total': grand_total,
        'total_actual_salary': round(total_actual_salary),
        'total_advance_given': total_advance_given,
        'month_name': calendar.month_name[month],
    }

    html_string = render_to_string('attendance/salary_total_pdf_template.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Salary_Report_{month}_{year}.pdf"'
    HTML(string=html_string).write_pdf(response)
    return response