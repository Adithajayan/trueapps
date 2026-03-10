from django.shortcuts import render, redirect, get_object_or_404
from .models import SupplierLedger
from supplier_master.models import Supplier
from django.db.models import Sum
from datetime import date


# ==================================================
# 1️⃣ SUPPLIER LEDGER SUMMARY (MAIN PAGE)
# ==================================================
from django.shortcuts import render
from supplier_master.models import Supplier
from .models import SupplierLedger
from django.db.models import Sum


def supplier_ledger_summary(request):

    filter_type = request.GET.get("filter", "all")

    suppliers = Supplier.objects.all()
    data = []

    for supplier in suppliers:

        total_debit = SupplierLedger.objects.filter(
            supplier=supplier
        ).aggregate(Sum('debit'))['debit__sum'] or 0

        total_credit = SupplierLedger.objects.filter(
            supplier=supplier
        ).aggregate(Sum('credit'))['credit__sum'] or 0

        balance = total_debit - total_credit

        # ---------- FILTER ----------
        if filter_type == "pending" and balance <= 0:
            continue

        if filter_type == "finished" and balance != 0:
            continue

        data.append({
            "supplier": supplier,
            "debit": total_debit,
            "credit": total_credit,
            "balance": balance
        })

    return render(request, "supplier_ledger/ledger_summary.html", {
        "data": data,
        "filter": filter_type
    })



# ==================================================
# 2️⃣ SUPPLIER LEDGER DETAIL (RUNNING BALANCE)
# ==================================================
def supplier_ledger_detail(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    # Date and ID vechu order cheyyunnu
    ledgers = SupplierLedger.objects.filter(
        supplier=supplier
    ).order_by('date', 'id')

    running = 0
    rows = []
    total_payment = 0
    total_return = 0

    for l in ledgers:
        # Basic balance calculation
        running += l.debit
        running -= l.credit

        # Summary-il thirichu kaanikkanulla logic
        # Purchase source aayirikkukayum credit-il amount undavenkilum ath 'Return' aanu
        if l.source == 'PURCHASE' and l.credit > 0:
            total_return += float(l.credit)
        # Payment source-o athallengil Credit side-il varunna manual entries-o 'Payment' aayi koottam
        elif l.source == 'PAYMENT' or (l.source == 'MANUAL' and l.credit > 0):
            total_payment += float(l.credit)
        # Opening balance credit side-ilaanengil athum payment logic-il varum
        elif l.source == 'OPENING' and l.credit > 0:
            total_payment += float(l.credit)

        rows.append({
            "row": l,
            "balance": running
        })

    total_debit = sum(r["row"].debit for r in rows)

    return render(request, "supplier_ledger/ledger_detail.html", {
        "supplier": supplier,
        "rows": rows,
        "total_debit": total_debit,
        "total_payment": total_payment, # Puthiya variable
        "total_return": total_return,   # Puthiya variable
        "final_balance": running
    })


# ==================================================
# 3️⃣ MANUAL LEDGER ENTRY
# ==================================================
def ledger_manual_add(request):

    suppliers = Supplier.objects.all()

    if request.method == "POST":

        supplier_id = request.POST.get("supplier")
        date_val = request.POST.get("date")
        entry_type = request.POST.get("entry_type")
        amount = float(request.POST.get("amount"))
        remark = request.POST.get("remark")

        debit = credit = 0

        if entry_type == "DEBIT":
            debit = amount
        else:
            credit = amount

        SupplierLedger.objects.create(
            supplier_id=supplier_id,
            date=date_val,
            particular=remark,
            debit=debit,
            credit=credit,
            source="MANUAL"
        )

        return redirect("supplier_ledger_summary")

    return render(request, "supplier_ledger/manual_entry.html", {
        "suppliers": suppliers
    })


# ==================================================
# 4️⃣ PAYMENT ENTRY
# ==================================================
def ledger_payment_add(request):

    suppliers = Supplier.objects.all()

    if request.method == "POST":

        SupplierLedger.objects.create(
            supplier_id=request.POST.get("supplier"),
            date=request.POST.get("date"),
            particular=f"{request.POST.get('mode')} Payment - {request.POST.get('remark')}",
            debit=0,
            credit=float(request.POST.get("amount")),
            source="PAYMENT"
        )

        return redirect("supplier_ledger_summary")

    return render(request, "supplier_ledger/payment_entry.html", {
        "suppliers": suppliers
    })


# ==================================================
# 5️⃣ DELETE LEDGER ENTRY
# ==================================================
def ledger_delete(request, pk):

    ledger = get_object_or_404(SupplierLedger, id=pk)

    if request.method == "POST":
        ledger.delete()
        return redirect("supplier_ledger_detail", supplier_id=ledger.supplier.id)

    return render(request, "supplier_ledger/ledger_delete.html", {
        "ledger": ledger
    })


# ==================================================
# 6️⃣ SUPPLIER LEDGER LIST (OPTIONAL DROPDOWN)
# ==================================================
def supplier_ledger_list(request):

    suppliers = Supplier.objects.all()
    selected_supplier = request.GET.get("supplier")

    ledger_entries = []

    if selected_supplier:
        supplier = Supplier.objects.get(id=selected_supplier)
        ledgers = SupplierLedger.objects.filter(
            supplier=supplier
        ).order_by("date", "id")

        running = 0
        for l in ledgers:
            running += l.debit - l.credit
            ledger_entries.append({
                "row": l,
                "balance": running
            })

    return render(request, "supplier_ledger/ledger_summary.html", {
        "suppliers": suppliers,
        "ledger_entries": ledger_entries,
        "selected_supplier": selected_supplier
    })


# ==================================================
# 7️⃣ SIMPLE LEDGER ADD (BASIC)
# ==================================================
def ledger_add(request):

    suppliers = Supplier.objects.all()

    if request.method == "POST":
        SupplierLedger.objects.create(
            supplier_id=request.POST.get("supplier"),
            date=request.POST.get("date"),
            particular=request.POST.get("particular"),
            debit=request.POST.get("debit") or 0,
            credit=request.POST.get("credit") or 0,
            source="MANUAL"
        )
        return redirect("supplier_ledger_summary")

    return render(request, "supplier_ledger/ledger_add.html", {
        "suppliers": suppliers
    })


from django.contrib import messages

def ledger_edit(request, pk):

    ledger = get_object_or_404(SupplierLedger, id=pk)

    # ❌ block non-manual entries
    if ledger.source != "MANUAL":
        messages.error(request, "Auto ledger entries cannot be edited.")
        return redirect('supplier_ledger_detail', supplier_id=ledger.supplier.id)

    if request.method == "POST":

        ledger.date = request.POST.get("date")
        ledger.particular = request.POST.get("particular")
        ledger.debit = request.POST.get("debit") or 0
        ledger.credit = request.POST.get("credit") or 0
        ledger.save()

        messages.success(request, "Ledger updated successfully")
        return redirect('supplier_ledger_detail', supplier_id=ledger.supplier.id)

    return render(request, "supplier_ledger/ledger_edit.html", {
        "ledger": ledger
    })



from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import SupplierLedger
from supplier_master.models import Supplier
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


def supplier_ledger_pdf(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    ledgers = SupplierLedger.objects.filter(supplier=supplier).order_by("date", "id")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{supplier.name}_ledger.pdf"'

    doc = SimpleDocTemplate(
        response, pagesize=A4,
        rightMargin=25, leftMargin=25, topMargin=30, bottomMargin=30
    )

    styles = getSampleStyleSheet()

    # --- Custom Times-Roman Styles ---
    title_style = ParagraphStyle(
        'MainTitle', parent=styles['Title'], fontName='Times-Bold',
        fontSize=18, textColor=colors.HexColor("#2C3E50"), alignment=TA_CENTER
    )
    normal_times = ParagraphStyle(
        'NormalTimes', parent=styles['Normal'], fontName='Times-Roman', fontSize=10
    )
    table_text_style = ParagraphStyle(
        'TableText', parent=styles['Normal'], fontName='Times-Roman', fontSize=9, alignment=TA_LEFT
    )

    elements = []

    # ---------------- HEADER SECTION ----------------
    elements.append(Paragraph("SUPPLIER LEDGER STATEMENT", title_style))
    elements.append(Spacer(1, 5))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#34495E")))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"<b>Supplier:</b> {supplier.name}", normal_times))
    elements.append(Paragraph(f"<b>Report Date:</b> {datetime.now().strftime('%d-%m-%Y %I:%M %p')}", normal_times))
    elements.append(Spacer(1, 15))

    # ---------------- TABLE PREPARATION ----------------
    # Particulars-il Paragraph use cheyyunnath kond text overlap aavilla
    table_data = [
        [
            Paragraph("<b>Date</b>", normal_times),
            Paragraph("<b>Particulars</b>", normal_times),
            Paragraph("<b>Debit (⬆)</b>", normal_times),
            Paragraph("<b>Paid (⬇)</b>", normal_times),
            Paragraph("<b>Return (📦)</b>", normal_times),
            Paragraph("<b>Balance</b>", normal_times)
        ]
    ]

    running_balance = 0
    total_debit = 0
    total_paid = 0
    total_return = 0

    for l in ledgers:
        running_balance += float(l.debit)
        running_balance -= float(l.credit)
        total_debit += float(l.debit)

        paid_val = return_val = "—"
        if l.source == 'PURCHASE' and l.credit > 0:
            return_val = f"{l.credit:,.2f}"
            total_return += float(l.credit)
        else:
            paid_val = f"{l.credit:,.2f}" if l.credit > 0 else "—"
            total_paid += float(l.credit)

        table_data.append([
            l.date.strftime("%d-%m-%Y"),
            Paragraph(l.particular, table_text_style),  # Automatic wrap
            f"{l.debit:,.2f}" if l.debit > 0 else "—",
            paid_val,
            return_val,
            f"{running_balance:,.2f}",
        ])

    # ---------------- TABLE STYLING ----------------
    # Column width properly balanced for A4
    table = Table(table_data, colWidths=[65, 180, 75, 75, 75, 75])

    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.2, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Amounts Right Align

        # Row Colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),

        # Conditional Text Colors
        ('TEXTCOLOR', (2, 1), (2, -1), colors.HexColor("#C0392B")),  # Debit Red
        ('TEXTCOLOR', (3, 1), (3, -1), colors.HexColor("#27AE60")),  # Paid Green
        ('TEXTCOLOR', (4, 1), (4, -1), colors.HexColor("#D35400")),  # Return Orange
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # ---------------- SUMMARY TILES (BEAUTIFUL) ----------------
    summary_data = [
        [
            Paragraph(f"<b>Total Purchase</b><br/>₹ {total_debit:,.2f}", normal_times),
            Paragraph(f"<b>Total Paid</b><br/>₹ {total_paid:,.2f}", normal_times),
            Paragraph(f"<b>Total Return</b><br/>₹ {total_return:,.2f}", normal_times),
            Paragraph(f"<b>Final Balance</b><br/>₹ {running_balance:,.2f}", normal_times)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[135, 135, 135, 135])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#FADBD8")),  # Light Red
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#D5F5E3")),  # Light Green
        ('BACKGROUND', (2, 0), (2, 0), colors.HexColor("#FCF3CF")),  # Light Yellow
        ('BACKGROUND', (3, 0), (3, 0), colors.HexColor("#D6EAF8")),  # Light Blue
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#34495E")),
    ]))

    elements.append(summary_table)

    # ---------------- BUILD PDF ----------------
    doc.build(elements)
    return response
