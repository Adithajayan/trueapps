from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone

from .models import Supplier
from supplier_ledger.models import SupplierLedger


# ================= LIST =================
def supplier_list(request):
    search = request.GET.get('search')

    suppliers = Supplier.objects.all().order_by('-id')

    if search:
        suppliers = suppliers.filter(
            Q(name__icontains=search) |
            Q(supplier_code__icontains=search) |
            Q(contact_number__icontains=search)
        )

    return render(request, 'supplier_master/supplier_list.html', {
        'suppliers': suppliers,
        'search': search
    })


# ================= ADD =================
def supplier_add(request):

    if request.method == 'POST':

        opening_balance = float(request.POST.get('opening_balance') or 0)

        supplier = Supplier.objects.create(
            name=request.POST.get('name'),
            contact_number=request.POST.get('contact_number'),
            email=request.POST.get('email'),
            gstin=request.POST.get('gstin'),
            address=request.POST.get('address'),   # 🔥 ADDRESS
            opening_balance=opening_balance,
            image=request.FILES.get('image')
        )

        # 🔥 OPENING BALANCE → LEDGER ENTRY
        if opening_balance > 0:
            SupplierLedger.objects.create(
                supplier=supplier,
                date=timezone.now().date(),
                particular="Opening Balance",
                debit=opening_balance,
                credit=0,
                source="OPENING",
                reference_id=supplier.id
            )

        return redirect('supplier_master_list')

    return render(request, 'supplier_master/supplier_form.html')


# ================= EDIT =================
def supplier_edit(request, id):

    supplier = get_object_or_404(Supplier, id=id)

    opening_ledger = SupplierLedger.objects.filter(
        supplier=supplier,
        source='OPENING'
    ).first()

    if request.method == 'POST':

        new_opening = float(request.POST.get('opening_balance') or 0)

        supplier.name = request.POST.get('name')
        supplier.contact_number = request.POST.get('contact_number')
        supplier.email = request.POST.get('email')
        supplier.gstin = request.POST.get('gstin')
        supplier.address = request.POST.get('address')   # 🔥 ADDRESS
        supplier.opening_balance = new_opening

        if request.FILES.get('image'):
            supplier.image = request.FILES.get('image')

        supplier.save()

        # 🔥 LEDGER UPDATE
        if new_opening > 0:
            if opening_ledger:
                opening_ledger.debit = new_opening
                opening_ledger.date = timezone.now().date()
                opening_ledger.save()
            else:
                SupplierLedger.objects.create(
                    supplier=supplier,
                    date=timezone.now().date(),
                    particular="Opening Balance",
                    debit=new_opening,
                    credit=0,
                    source="OPENING",
                    reference_id=supplier.id
                )
        else:
            if opening_ledger:
                opening_ledger.delete()

        return redirect('supplier_master_list')

    return render(request, 'supplier_master/supplier_form.html', {
        'supplier': supplier
    })


# ================= DELETE =================
def supplier_delete(request, id):
    supplier = get_object_or_404(Supplier, id=id)

    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier_master_list')

    return render(request, 'supplier_master/supplier_delete.html', {
        'supplier': supplier
    })
