from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from income.models import CustomerWork, WorkPayment



from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


# views.py

def login_view(request):
    # User mumbere login aayittundengil dashboard-ilekku vidunnu
    if request.user.is_authenticated:
        return redirect('dashboard' if request.user.is_superuser else 'job_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('dashboard')
            else:
                return redirect('job_dashboard')
        else:
            messages.error(request, 'Invalid username or password')

            return render(request, 'login.html', {'username': username})

    return render(request, 'login.html')



from datetime import datetime
from decimal import Decimal
from django.shortcuts import render
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth

from sales.models import SalesMaster, SalesItemBatch
from purchase.models import Purchase, PurchaseItem
from quotation.models import Quotation
from supplier_ledger.models import SupplierLedger
from income.models import CustomerWork, WorkPayment
from attendance.models import Attendance
from expense.models import Expense
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    # ================= SECURITY CHECK =================
    # If the user is a staff member (not superuser),
    # redirect them away from the financial dashboard.
    if not request.user.is_superuser:
        return redirect('job_dashboard')

    today = datetime.today()

    # ================= MONTH FILTER =================
    selected_month = request.GET.get("month")

    if selected_month:
        year, month = selected_month.split("-")
        from_date = datetime(int(year), int(month), 1).date()

        if int(month) == 12:
            to_date = datetime(int(year) + 1, 1, 1).date()
        else:
            to_date = datetime(int(year), int(month) + 1, 1).date()
    else:
        from_date = today.replace(day=1).date()
        to_date = today.date()

    # ================= SALES =================
    sales = SalesMaster.objects.filter(date__range=[from_date, to_date])
    purchases = Purchase.objects.filter(purchase_date__range=[from_date, to_date])

    total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    total_purchase = purchases.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

    net_profit = SalesItemBatch.objects.filter(
        sales_item__sales__in=sales
    ).aggregate(total=Sum('profit'))['total'] or Decimal('0')

    stock_value = PurchaseItem.objects.filter(
        quantity_at_hand__gt=0
    ).aggregate(total=Sum(F('quantity_at_hand') * F('rate')))['total'] or Decimal('0')

    # ================= KPI =================
    today_present = Attendance.objects.filter(date=today.date(), status="P").count()

    month_sales_count = sales.count()
    month_purchase_count = purchases.count()

    month_quotation_count = Quotation.objects.filter(
        quotation_date__range=[from_date, to_date]
    ).count()

    # ================= SUPPLIER LEDGER (EDITED) =================
    # Overall balance kittan date filter matti
    supplier_qs_all = SupplierLedger.objects.all()

    supplier_debit = supplier_qs_all.aggregate(total=Sum('debit'))['total'] or Decimal('0')
    supplier_credit = supplier_qs_all.aggregate(total=Sum('credit'))['total'] or Decimal('0')

    # Supplier Logic: Total Bills (Credit) - Total Payments (Debit)
    supplier_ledger_total = supplier_credit - supplier_debit

    # ================= CUSTOMER OUTSTANDING (EDITED) =================
    # Overall balance kittan date filter matti
    total_work_all = CustomerWork.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    total_received_all = WorkPayment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    customer_ledger_total = total_work_all - total_received_all

    # ================= EXPENSE =================
    month_expense_total = Expense.objects.filter(
        date__range=[from_date, to_date],
        expense_type__is_active=True
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # ================= PROFIT STATUS =================
    profit_percentage = (net_profit / total_sales * 100) if total_sales else 0

    if profit_percentage >= 20:
        business_status, status_color, status_icon = "Excellent", "success", "bi-graph-up-arrow"
    elif profit_percentage >= 10:
        business_status, status_color, status_icon = "Healthy", "primary", "bi-emoji-smile"
    elif profit_percentage >= 5:
        business_status, status_color, status_icon = "Average", "warning", "bi-emoji-neutral"
    else:
        business_status, status_color, status_icon = "Risk Zone", "danger", "bi-exclamation-triangle"

    # ================= GRAPH =================
    monthly_profit = (
        SalesItemBatch.objects
        .annotate(month=TruncMonth('sales_item__sales__date'))
        .values('month')
        .annotate(total=Sum('profit'))
        .order_by('month')
    )

    months = [m['month'].strftime("%b %Y") for m in monthly_profit if m['month']]
    profits = [float(m['total']) for m in monthly_profit if m['month']]

    context = {
        'total_sales': total_sales,
        'total_purchase': total_purchase,
        'net_profit': net_profit,
        'total_stock_value': stock_value,
        'profit_percentage': round(profit_percentage, 2),
        'business_status': business_status,
        'status_color': status_color,
        'status_icon': status_icon,
        'graph_months': months,
        'graph_profits': profits,

        'today_present': today_present,
        'month_sales_count': month_sales_count,
        'month_purchase_count': month_purchase_count,
        'month_quotation_count': month_quotation_count,
        'supplier_ledger_total': supplier_ledger_total,  # Fix aayi
        'customer_ledger_total': customer_ledger_total,  # Fix aayi
        'month_expense_total': month_expense_total,
        'selected_month': selected_month,
    }

    return render(request, 'dashboard/dashboard.html', context)




from django.contrib.auth.models import User
from django.http import HttpResponse

def create_admin_manual(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'trueapps@gmail.com', 'Trueapps@2026')
        return HttpResponse("Admin created successfully!")
    else:
        return HttpResponse("Admin already exists!")