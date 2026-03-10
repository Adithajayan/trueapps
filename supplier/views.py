from django.shortcuts import render, get_object_or_404
from django.db.models import Sum

from .models import Supplier, SupplierPurchase, SupplierPayment


def supplier_list(request):

    pending_only = request.GET.get("pending")

    suppliers = Supplier.objects.all()
    data = []

    for supplier in suppliers:

        purchases = SupplierPurchase.objects.filter(supplier=supplier)

        total_amount = purchases.aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        payments = SupplierPayment.objects.filter(
            purchase__supplier=supplier
        )

        paid_amount = payments.aggregate(
            total=Sum("amount")
        )["total"] or 0

        balance = total_amount - paid_amount

        # pending filter
        if pending_only and balance <= 0:
            continue

        data.append({
            "supplier": supplier,
            "total": total_amount,
            "paid": paid_amount,
            "balance": balance
        })

    return render(request, "supplier/supplier_list.html", {
        "data": data,
        "pending": pending_only
    })


from django.shortcuts import render, redirect, get_object_or_404
from .models import Supplier, SupplierPurchase


def purchase_list(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    purchases = SupplierPurchase.objects.filter(supplier=supplier)

    return render(request, "supplier/purchase_list.html", {
        "supplier": supplier,
        "purchases": purchases
    })


def purchase_add(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == "POST":
        bill_no = request.POST.get("bill_no")
        total = request.POST.get("total_amount")
        date = request.POST.get("purchase_date")

        SupplierPurchase.objects.create(
            supplier=supplier,
            bill_no=bill_no,
            total_amount=total,
            purchase_date=date
        )

        return redirect("purchase_list", supplier.id)

    return render(request, "supplier/purchase_add.html", {
        "supplier": supplier
    })


from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from .models import SupplierPurchase, SupplierPayment


def payment_list(request, purchase_id):
    purchase = get_object_or_404(SupplierPurchase, id=purchase_id)

    payments = SupplierPayment.objects.filter(purchase=purchase)

    paid = payments.aggregate(
        total=Sum("amount")
    )["total"] or 0

    balance = purchase.total_amount - paid

    return render(request, "supplier/payment_list.html", {
        "purchase": purchase,
        "payments": payments,
        "paid": paid,
        "balance": balance
    })


def payment_add(request, purchase_id):
    purchase = get_object_or_404(SupplierPurchase, id=purchase_id)

    if request.method == "POST":
        SupplierPayment.objects.create(
            purchase=purchase,
            amount=request.POST.get("amount"),
            mode=request.POST.get("mode"),
            date=request.POST.get("date"),
            note=request.POST.get("note")
        )
        return redirect("supplier_payment_list", purchase.id)

    return render(request, "supplier/payment_add.html", {
        "purchase": purchase
    })


from django.shortcuts import render, redirect
from .models import Supplier

def supplier_add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        Supplier.objects.create(
            name=name,
            phone=phone,
            address=address
        )

        return redirect("supplier_list")

    return render(request, "supplier/supplier_add.html")
