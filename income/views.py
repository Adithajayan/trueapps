from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Customer, CustomerWork, WorkPayment


# =========================
# CUSTOMER
# =========================



def customer_list(request):

    pending_only = request.GET.get("pending")

    customers = Customer.objects.all()
    data = []

    for customer in customers:

        works = CustomerWork.objects.filter(customer=customer)

        total_amount = works.aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        payments = WorkPayment.objects.filter(
            work__customer=customer
        )

        received_amount = payments.aggregate(
            total=Sum("amount")
        )["total"] or 0

        balance = total_amount - received_amount

        # ✅ CORRECT pending logic
        if pending_only == "1" and balance <= 0:
            continue

        data.append({
            "customer": customer,
            "total": total_amount,
            "received": received_amount,
            "balance": balance
        })

    return render(request, "income/customer_list.html", {
        "data": data,
        "pending": pending_only
    })


# =========================
# WORK
# =========================

def work_list(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    works = CustomerWork.objects.filter(customer=customer)

    return render(request, 'income/work_list.html', {
        'customer': customer,
        'works': works
    })


def work_add(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        CustomerWork.objects.create(
            customer=customer,
            title=request.POST['title'],
            total_amount=request.POST['total_amount'],
            work_date=request.POST['work_date']
        )
        return redirect('work_list', customer_id=customer.id)

    return render(request, 'income/work_add.html', {'customer': customer})


# =========================
# PAYMENT
# =========================


def payment_list(request, work_id):

    # work
    work = get_object_or_404(CustomerWork, id=work_id)

    # customer
    customer = work.customer

    # payments
    payments = WorkPayment.objects.filter(work=work)

    # received amount
    received = payments.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # balance
    balance = work.total_amount - received

    return render(request, 'income/payment_list.html', {
        'work': work,
        'customer': customer,
        'payments': payments,
        'received': received,
        'balance': balance
    })


def payment_add(request, work_id):
    work = get_object_or_404(CustomerWork, id=work_id)

    if request.method == 'POST':
        WorkPayment.objects.create(
            work=work,
            amount=request.POST['amount'],
            mode=request.POST['mode'],
            date=request.POST['date'],
            note=request.POST.get('note')
        )
        return redirect('payment_list', work_id=work.id)

    return render(request, 'income/payment_add.html', {'work': work})


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


from django.http import HttpResponse
from django.template.loader import get_template
from django.db.models import Sum
from datetime import date

from config.utils.pdf import generate_pdf


from datetime import date # ഇന്നത്തെ ഡേറ്റ് കിട്ടാൻ ഇത് വേണം
from django.db.models import Sum
from .models import Customer, CustomerWork, WorkPayment # മോഡലുകൾ ഇമ്പോർട്ട് ചെയ്യുന്നു
from config.utils.pdf import generate_pdf # നമ്മുടെ മാജിക് ടൂൾ

def pending_pdf(request):
    customers = Customer.objects.all()
    data = []
    total_pending = 0

    for customer in customers:
        works = CustomerWork.objects.filter(customer=customer)
        total = works.aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        payments = WorkPayment.objects.filter(
            work__customer=customer
        )
        received = payments.aggregate(
            total=Sum("amount")
        )["total"] or 0

        balance = total - received

        # ബാലൻസ് ഉള്ള കസ്റ്റമേഴ്സിനെ മാത്രം ലിസ്റ്റിൽ എടുക്കുന്നു
        if balance > 0:
            data.append({
                "customer": customer,
                "total": total,
                "received": received,
                "balance": balance
            })
            total_pending += balance

    # ഇവിടെയാണ് നമ്മൾ പുതിയ ടൂൾ ഉപയോഗിക്കുന്നത്
    context = {
        "data": data,
        "today": date.today(),
        "total_pending": total_pending
    }

    template_name = "income/pending_income_pdf.html"
    filename = "pending_income.pdf"

    return generate_pdf(template_name, context, filename)


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import WorkPayment


def payment_edit(request, payment_id):
    payment = get_object_or_404(WorkPayment, id=payment_id)

    if request.method == "POST":
        payment.date = request.POST.get("date")
        payment.mode = request.POST.get("mode")
        payment.amount = request.POST.get("amount")
        payment.note = request.POST.get("note")
        payment.save()

        messages.success(request, "Payment updated successfully")
        return redirect("payment_list", payment.work.id)

    return render(request, "income/payment_edit.html", {
        "payment": payment
    })


def payment_delete(request, payment_id):
    payment = get_object_or_404(WorkPayment, id=payment_id)
    work_id = payment.work.id

    if request.method == "POST":
        payment.delete()
        return redirect('payment_list', work_id)

    return render(request, 'income/payment_confirm_delete.html', {
        'payment': payment
    })




from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomerWork
from django.contrib import messages


def work_edit(request, work_id):
    work = get_object_or_404(CustomerWork, id=work_id)

    if request.method == "POST":
        work.title = request.POST.get("title")
        work.total_amount = request.POST.get("total_amount")
        work.work_date = request.POST.get("work_date")
        work.save()

        messages.success(request, "Work updated successfully")
        return redirect("work_list", work.customer.id)

    return render(request, "income/work_edit.html", {"work": work})


def work_delete(request, work_id):
    work = get_object_or_404(CustomerWork, id=work_id)
    customer_id = work.customer.id

    if request.method == "POST":
        work.delete()
        messages.success(request, "Work deleted successfully")
        return redirect("work_list", customer_id)

    return render(request, "income/work_delete.html", {"work": work})



from django.http import JsonResponse
from customer.models import Customer


def customer_search(request):
    q = request.GET.get("q", "").strip()

    # Query undenkil mathram filter cheyyuka
    if q:
        customers = Customer.objects.filter(
            Q(name__icontains=q) | Q(place__icontains=q)
        ).distinct()[:10]

        data = [
            {
                "id": c.id,
                "name": c.name,
                "place": c.place if c.place else ""  # Place empty aayal issue varathirikkaan
            } for c in customers
        ]
        return JsonResponse(data, safe=False)

    # Query illengil empty array ayakkuka
    return JsonResponse([], safe=False)
