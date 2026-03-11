from django.shortcuts import render
from django.db.models import Sum, Count, Avg
from collections import defaultdict

from sales.models import SalesMaster, SalesItemBatch, SalesItem


def sales_report(request):

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    sale_type = request.GET.get('sale_type')

    sales = SalesMaster.objects.all()

    # -------- DATE FILTER --------
    if from_date and to_date:
        sales = sales.filter(date__range=[from_date, to_date])

    # -------- SALE TYPE FILTER --------
    if sale_type and sale_type != "ALL":
        sales = sales.filter(sale_type=sale_type)

    sales = sales.select_related('customer').order_by('-date')

    # -------- PROFIT PER INVOICE --------
    for sale in sales:
        profit = SalesItemBatch.objects.filter(
            sales_item__sales=sale
        ).aggregate(total_profit=Sum('profit'))['total_profit'] or 0

        sale.total_profit = profit

    # -------- SUMMARY --------
    summary = sales.aggregate(
        total_sales=Sum('total_amount'),
        invoice_count=Count('id'),
        avg_bill=Avg('total_amount')
    )

    total_profit = SalesItemBatch.objects.filter(
        sales_item__sales__in=sales
    ).aggregate(total=Sum('profit'))['total'] or 0

    # =====================================================
    # ✅ SQLITE SAFE DAILY SALES GRAPH
    # =====================================================
    daily_totals = defaultdict(float)

    for sale in sales:
        day = sale.date.strftime("%Y-%m-%d")
        daily_totals[day] += float(sale.total_amount)

    graph_labels = list(daily_totals.keys())
    graph_values = list(daily_totals.values())

    # =====================================================
    # ✅ TOP SELLING PRODUCTS
    # =====================================================
    top_products = SalesItem.objects.filter(
        sales__in=sales
    ).values('product__name').annotate(
        total_qty=Sum('qty')
    ).order_by('-total_qty')[:5]

    product_labels = [i['product__name'] for i in top_products]
    product_values = [float(i['total_qty']) for i in top_products]

    # =====================================================
    # ✅ CUSTOMER WISE SALES
    # =====================================================
    customer_sales = sales.values(
        'customer__name'
    ).annotate(
        total=Sum('total_amount')
    ).order_by('-total')[:5]

    customer_labels = [i['customer__name'] for i in customer_sales]
    customer_values = [float(i['total']) for i in customer_sales]

    context = {
        'sales': sales,
        'total_sales': summary['total_sales'] or 0,
        'invoice_count': summary['invoice_count'] or 0,
        'avg_bill': summary['avg_bill'] or 0,
        'total_profit': total_profit,

        'graph_labels': graph_labels,
        'graph_values': graph_values,

        'product_labels': product_labels,
        'product_values': product_values,

        'customer_labels': customer_labels,
        'customer_values': customer_values,
    }

    return render(request, 'reports/sales_report.html', context)


from django.http import HttpResponse
from django.template.loader import render_to_string


from sales.models import SalesMaster, SalesItemBatch
from django.db.models import Sum


def sales_report_pdf(request):
    from weasyprint import HTML

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    sale_type = request.GET.get('sale_type')

    sales = SalesMaster.objects.all().select_related('customer')

    if from_date and to_date:
        sales = sales.filter(date__range=[from_date, to_date])

    if sale_type and sale_type != "ALL":
        sales = sales.filter(sale_type=sale_type)

    # PROFIT
    for sale in sales:
        profit = SalesItemBatch.objects.filter(
            sales_item__sales=sale
        ).aggregate(total_profit=Sum('profit'))['total_profit'] or 0

        sale.total_profit = profit

    total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or 0

    total_profit = SalesItemBatch.objects.filter(
        sales_item__sales__in=sales
    ).aggregate(total=Sum('profit'))['total'] or 0

    html_string = render_to_string(
        'reports/sales_report_pdf.html',
        {
            'sales': sales,
            'total_sales': total_sales,
            'total_profit': total_profit,
        }
    )

    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Sales_Report.pdf"'
    return response






def reports_home(request):
    return render(request, 'reports/reports_home.html')


# -----------------stock------

from stock.models import Stock
from django.shortcuts import render
from django.db import models


def low_stock_report(request):

    low_stocks = Stock.objects.select_related('product').filter(
        quantity__lte=models.F('product__minimum_stock')
    ).order_by('quantity')

    return render(request, 'reports/low_stock_report.html', {
        'low_stocks': low_stocks
    })


# -------------------------------------- purchase---------------

from django.shortcuts import render
from django.db.models import Sum, Count, Avg
from collections import defaultdict

from purchase.models import Purchase, PurchaseItem
from supplier_master.models import Supplier


def purchase_report(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    supplier_id = request.GET.get('supplier')
    payment_type = request.GET.get('payment_type')

    purchases = Purchase.objects.select_related('supplier').all()

    # ---------------- DATE FILTER ----------------
    if from_date and to_date:
        purchases = purchases.filter(purchase_date__range=[from_date, to_date])

    # ---------------- SUPPLIER FILTER ----------------
    if supplier_id:
        purchases = purchases.filter(supplier_id=supplier_id)

    # ---------------- PAYMENT FILTER ----------------
    if payment_type and payment_type != "ALL":
        purchases = purchases.filter(payment_type=payment_type)

    purchases = purchases.order_by('-purchase_date')

    # ---------------- SUMMARY CARDS ----------------
    summary = purchases.aggregate(
        total_purchase=Sum('total_amount'),
        bill_count=Count('id'),
        avg_bill=Avg('total_amount')
    )
    supplier_count = purchases.values('supplier').distinct().count()

    # Daily Graph Logic
    daily_totals = defaultdict(float)
    for p in purchases:
        day = p.purchase_date.strftime("%Y-%m-%d")
        daily_totals[day] += float(p.total_amount)

    purchase_graph_labels = list(daily_totals.keys())
    purchase_graph_values = list(daily_totals.values())

    # Top Products Logic
    top_products = PurchaseItem.objects.filter(
        purchase__in=purchases
    ).values('product__name').annotate(
        total_qty=Sum('qty')
    ).order_by('-total_qty')[:5]

    product_labels = [i['product__name'] for i in top_products]
    product_values = [float(i['total_qty']) for i in top_products]

    context = {
        'purchases': purchases,
        'suppliers': Supplier.objects.all(),

        # Ithaanu puthiya part: Filter values thirichu ayakkunnu
        'from_date': from_date,
        'to_date': to_date,
        'selected_supplier': supplier_id,
        'selected_payment': payment_type,

        'total_purchase': summary['total_purchase'] or 0,
        'bill_count': summary['bill_count'] or 0,
        'avg_bill': summary['avg_bill'] or 0,
        'supplier_count': supplier_count,

        'purchase_graph_labels': purchase_graph_labels,
        'purchase_graph_values': purchase_graph_values,

        'product_labels': product_labels,
        'product_values': product_values,
    }

    return render(request, 'reports/purchase_report.html', context)


from django.http import HttpResponse
from django.template.loader import render_to_string



def purchase_report_pdf(request):
    from weasyprint import HTML

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    supplier_id = request.GET.get('supplier')
    payment_type = request.GET.get('payment_type')

    purchases = Purchase.objects.select_related('supplier').all()

    if from_date and to_date:
        purchases = purchases.filter(
            purchase_date__range=[from_date, to_date]
        )

    if supplier_id:
        purchases = purchases.filter(supplier_id=supplier_id)

    if payment_type and payment_type != "ALL":
        purchases = purchases.filter(payment_type=payment_type)

    total_purchase = purchases.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    html_string = render_to_string(
        'reports/purchase_report_pdf.html',
        {
            'purchases': purchases,
            'total_purchase': total_purchase,
            'from_date': from_date,
            'to_date': to_date,
            'payment_type': payment_type,
        }
    )

    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Purchase_Report.pdf"'
    return response



# -------------------------------profit & loss ---------------------------




from sales.models import SalesMaster, SalesItemBatch
from purchase.models import Purchase, PurchaseItem # PurchaseItem koodi import cheyyuka
from stock.models import Stock
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth
from decimal import Decimal
from django.shortcuts import render
import json

def profit_loss_report(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    sales = SalesMaster.objects.all()
    purchases = Purchase.objects.all()

    # DATE FILTER
    if from_date and to_date:
        sales = sales.filter(date__range=[from_date, to_date])
        purchases = purchases.filter(purchase_date__range=[from_date, to_date])

    # TOTAL SALES
    total_sales = sales.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')

    # TOTAL PURCHASE
    total_purchase = purchases.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')

    # NET PROFIT (SalesItemBatch logic)
    total_profit = SalesItemBatch.objects.filter(
        sales_item__sales__in=sales
    ).aggregate(total=Sum('profit'))['total'] or Decimal('0')

    net_profit = total_profit

    # ================= OPTION B: STOCK VALUE (CORRECTED) =================
    # Ninte PurchaseItem model-il 'quantity_at_hand' und.
    # Athu 'rate' (purchase rate) vechu multiply cheythaal godown-ile correct value kittum.
    stock_value_query = PurchaseItem.objects.filter(quantity_at_hand__gt=0).aggregate(
        total=Sum(F('quantity_at_hand') * F('rate'))
    )
    total_stock_value = stock_value_query['total'] or Decimal('0')
    # =====================================================================

    # PROFIT %
    profit_percentage = 0
    if total_sales > 0:
        profit_percentage = (net_profit / total_sales) * 100

    # BUSINESS STATUS
    if profit_percentage >= 20:
        business_status = "Excellent"
        status_color = "success"
        status_icon = "bi-graph-up-arrow"
    elif profit_percentage >= 10:
        business_status = "Healthy"
        status_color = "primary"
        status_icon = "bi-emoji-smile"
    elif profit_percentage >= 5:
        business_status = "Average"
        status_color = "warning"
        status_icon = "bi-emoji-neutral"
    else:
        business_status = "Risk Zone"
        status_color = "danger"
        status_icon = "bi-exclamation-triangle"

    # MONTHLY PROFIT GRAPH
    monthly_profit = (
        SalesItemBatch.objects
        .filter(sales_item__sales__in=sales)
        .annotate(month=TruncMonth('sales_item__sales__date'))
        .values('month')
        .annotate(total=Sum('profit'))
        .order_by('month')
    )

    months = []
    profits = []
    for item in monthly_profit:
        if item['month']:
            months.append(item['month'].strftime("%b %Y"))
            profits.append(float(item['total']))

    # BUSINESS COMPARISON GRAPH
    monthly_sales = (
        sales.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )
    monthly_purchase = (
        purchases.annotate(month=TruncMonth('purchase_date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )

    sales_dict = {i['month']: float(i['total']) for i in monthly_sales if i['month']}
    purchase_dict = {i['month']: float(i['total']) for i in monthly_purchase if i['month']}
    all_months = sorted(set(list(sales_dict.keys()) + list(purchase_dict.keys())))

    compare_labels = []
    sales_data = []
    purchase_data = []
    profit_data = []

    for m in all_months:
        s = sales_dict.get(m, 0)
        p = purchase_dict.get(m, 0)
        compare_labels.append(m.strftime("%b %Y"))
        sales_data.append(s)
        purchase_data.append(p)
        profit_data.append(s - p)

    context = {
        'total_sales': total_sales,
        'total_purchase': total_purchase,
        'net_profit': net_profit,
        'total_stock_value': total_stock_value, # 👈 Ippo ithu correct aayirikkum
        'profit_percentage': round(profit_percentage, 2),
        'business_status': business_status,
        'status_color': status_color,
        'status_icon': status_icon,
        'graph_months': json.dumps(months),
        'graph_profits': json.dumps(profits),
        'compare_labels': json.dumps(compare_labels),
        'compare_sales': json.dumps(sales_data),
        'compare_purchase': json.dumps(purchase_data),
        'compare_profit': json.dumps(profit_data),
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, 'reports/profit_loss_report.html', context)


from django.http import HttpResponse
from django.template.loader import render_to_string

from decimal import Decimal
from django.db.models import Sum
from sales.models import SalesMaster, SalesItemBatch
from purchase.models import Purchase


def profit_loss_pdf(request):
    from weasyprint import HTML

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    sales = SalesMaster.objects.all()
    purchases = Purchase.objects.all()

    # ✅ DATE FILTER ONLY IF VALID
    if from_date and to_date and from_date != "None" and to_date != "None":
        sales = sales.filter(date__range=[from_date, to_date])
        purchases = purchases.filter(purchase_date__range=[from_date, to_date])
    else:
        from_date = None
        to_date = None

    total_sales = sales.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')

    total_purchase = purchases.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')

    net_profit = SalesItemBatch.objects.filter(
        sales_item__sales__in=sales
    ).aggregate(total=Sum('profit'))['total'] or Decimal('0')

    profit_percentage = 0
    if total_sales > 0:
        profit_percentage = (net_profit / total_sales) * 100

    html_string = render_to_string(
        'reports/pdf/profit_loss_pdf.html',
        {
            'total_sales': total_sales,
            'total_purchase': total_purchase,
            'net_profit': net_profit,
            'profit_percentage': round(profit_percentage,2),
            'from_date': from_date,
            'to_date': to_date,
        }
    )

    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Profit_Loss_Report.pdf"'
    return response




# -------------------------------------backup----------------------------------
import io
import zipfile
import openpyxl
from django.http import HttpResponse

# Models Imports
from customer.models import Customer
from supplier_master.models import Supplier
from product.models import Product
from purchase.models import Purchase
from sales.models import SalesMaster
from stock.models import Stock
from expense.models import Expense
from staff.models import Staff
from attendance.models import Attendance
from income.models import CustomerWork
from job_management.models import Job

# Google Drive Imports
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


# 1. Helper function to create Excel in memory
def create_excel(data, headers, sheet_name):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.append(headers)

    for row in data:
        clean_row = []
        for value in row:
            if hasattr(value, "tzinfo") and value.tzinfo is not None:
                value = value.replace(tzinfo=None)
            clean_row.append(value)
        ws.append(clean_row)

    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)
    return file_stream


# 2. Google Drive Upload Function (Placed before the view)
from googleapiclient.http import MediaIoBaseUpload


def upload_to_drive(file_stream, filename):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    DRIVE_FOLDER_ID = "1os-jNHE_FHPKfz0ziHpTP5nGgtnYSWWs"
    TARGET_EMAIL = "truebitbackup@gmail.com"  # Ninte main email id

    try:
        credentials = service_account.Credentials.from_service_account_file(
            'backup_key.json',
            scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=credentials)

        file_stream.seek(0)
        file_metadata = {'name': filename, 'parents': [DRIVE_FOLDER_ID]}
        media = MediaIoBaseUpload(file_stream, mimetype='application/zip', resumable=False)

        # 1. File Upload cheyyunnu
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        file_id = file.get('id')

        # 2. IMPORTANT STEP: Ownership Transfer cheyyunnu
        # Ithu cheythaal 'Quota' error varilla, karanam file ninte storage-ilekk maarum.
        permission = {
            'role': 'owner',
            'type': 'user',
            'emailAddress': TARGET_EMAIL
        }

        # TransferOwnership=True ennoru parameter koodi venam
        service.permissions().create(
            fileId=file_id,
            body=permission,
            transferOwnership=True,
            fields='id'
        ).execute()

        print(f"Success! Uploaded and Ownership transferred. ID: {file_id}")
        return file_id

    except Exception as e:
        print(f"Drive Error: {e}")
        return None

# 3. Main View Function
def export_all_excel(request):
    zip_buffer = io.BytesIO()

    # STEP 1: Zip file-lekk excel files ellam add cheyyunnu
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        # CUSTOMER
        customers = Customer.objects.all()
        c_data = [[c.id, c.name, c.phone, c.place, c.created_at] for c in customers]
        zip_file.writestr("customers.xlsx",
                          create_excel(c_data, ["ID", "Name", "Phone", "Place", "Created"], "Customers").getvalue())

        # SUPPLIER
        suppliers = Supplier.objects.all()
        s_data = [[s.id, s.supplier_code, s.name, s.contact_number, s.email] for s in suppliers]
        zip_file.writestr("suppliers.xlsx",
                          create_excel(s_data, ["ID", "Code", "Name", "Phone", "Email"], "Suppliers").getvalue())

        # PRODUCT
        products = Product.objects.all()
        p_data = [[p.id, p.product_code, p.name, p.purchase_rate, p.sales_rate] for p in products]
        zip_file.writestr("products.xlsx",
                          create_excel(p_data, ["ID", "Code", "Name", "Pur.Rate", "Sal.Rate"], "Products").getvalue())

        # PURCHASE
        purchases = Purchase.objects.all()
        pur_data = [[p.id, p.invoice_no, p.supplier.name if p.supplier else "N/A", p.purchase_date, p.total_amount] for
                    p in purchases]
        zip_file.writestr("purchase.xlsx",
                          create_excel(pur_data, ["ID", "Invoice", "Supplier", "Date", "Total"], "Purchase").getvalue())

        # SALES
        sales = SalesMaster.objects.all()
        sal_data = [[s.id, s.invoice_no, s.customer.name if s.customer else "N/A", s.date, s.total_amount] for s in
                    sales]
        zip_file.writestr("sales.xlsx",
                          create_excel(sal_data, ["ID", "Invoice", "Customer", "Date", "Total"], "Sales").getvalue())

        # STOCK
        stocks = Stock.objects.all()
        st_data = [[s.id, s.product.name, s.quantity, s.updated_at] for s in stocks]
        zip_file.writestr("stock.xlsx",
                          create_excel(st_data, ["ID", "Product", "Quantity", "Updated"], "Stock").getvalue())

        # EXPENSE
        expenses = Expense.objects.all()
        ex_data = [[e.id, e.date, e.amount, e.expense_type.name if e.expense_type else "N/A", e.status] for e in
                   expenses]
        zip_file.writestr("expenses.xlsx",
                          create_excel(ex_data, ["ID", "Date", "Amount", "Type", "Status"], "Expenses").getvalue())

        # STAFF & ATTENDANCE
        staffs = Staff.objects.all()
        stf_data = [[s.id, s.name, s.designation, s.status] for s in staffs]
        zip_file.writestr("staff.xlsx", create_excel(stf_data, ["ID", "Name", "Desig", "Status"], "Staff").getvalue())

        attendances = Attendance.objects.all()
        att_data = [[a.id, a.staff.name, a.date, a.status] for a in attendances]
        zip_file.writestr("attendance.xlsx",
                          create_excel(att_data, ["ID", "Staff", "Date", "Status"], "Attendance").getvalue())

        # CUSTOMER WORK & JOBS
        works = CustomerWork.objects.all()
        w_data = [[w.id, w.customer.name, w.title, w.total_amount] for w in works]
        zip_file.writestr("customer_work.xlsx",
                          create_excel(w_data, ["ID", "Customer", "Title", "Amount"], "Works").getvalue())

        jobs = Job.objects.all()
        j_data = [[j.id, j.name, j.place, j.status] for j in jobs]
        zip_file.writestr("jobs.xlsx", create_excel(j_data, ["ID", "Name", "Place", "Status"], "Jobs").getvalue())

    # --- IVIDEYAANU MAIN CHANGE ---

    # 1. Drive upload-nu munpu buffer thudakkathilekku reset cheyyunnu
    zip_buffer.seek(0)

    # 2. Drive upload call cheyyunnu
    drive_id = upload_to_drive(zip_buffer, "trueapps_backup.zip")

    # Upload success aayo ennu terminal-il print cheyyan
    if drive_id:
        print(f"File uploaded successfully to Drive. ID: {drive_id}")
    else:
        print("Drive upload failed. Check the terminal for error messages.")

    # 3. Download-nu munpu buffer pointer veendum reset cheyyenam
    zip_buffer.seek(0)

    # 4. Final response with .read()
    response = HttpResponse(zip_buffer.read(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="system_export.zip"'

    return response