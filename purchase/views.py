from django.shortcuts import render, redirect, get_object_or_404
from .models import Purchase, PurchaseItem
from supplier_master.models import Supplier
from product.models import Product
from django.db import transaction
from supplier_ledger.models import SupplierLedger
from django.db import transaction


# ---------------- LIST ----------------
from django.db.models import Q  # <--- Ithu top-il undo ennu urappu varuthuka

def purchase_list(request):
    # 1. Base Queryset (Ellaa purchases-um edukkunnu)
    purchases = Purchase.objects.all().order_by('-id')

    # 2. URL-il ninnu filter values edukkunnu (eg: ?q=INV001&start_date=2024-01-01)
    query = request.GET.get('q', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # 3. Invoice Number-o Supplier Name-o vechu search cheyyaan
    if query:
        purchases = purchases.filter(
            Q(invoice_no__icontains=query) |
            Q(supplier__name__icontains=query)
        )

    # 4. Date range filter
    if start_date:
        purchases = purchases.filter(purchase_date__gte=start_date)
    if end_date:
        purchases = purchases.filter(purchase_date__lte=end_date)

    return render(request, 'purchase/purchase_list.html', {
        'purchases': purchases,
        'query': query,        # Template-il box-il value retain cheyyaan
        'start_date': start_date,
        'end_date': end_date
    })




# ---------------- ADD ----------------
from stock.models import Stock

from decimal import Decimal
from django.db import transaction
from decimal import Decimal



from django.shortcuts import render, redirect
from decimal import Decimal
from django.db import transaction
from .models import Purchase, PurchaseItem
from supplier_master.models import Supplier
from product.models import Product
from stock.models import Stock
from supplier_ledger.models import SupplierLedger

from decimal import Decimal
from django.db import transaction
from django.shortcuts import render, redirect
from supplier_master.models import Supplier
from product.models import Product
from .models import Purchase, PurchaseItem
from stock.models import Stock

from supplier_ledger.models import SupplierLedger



@transaction.atomic
def purchase_add(request):

    suppliers = Supplier.objects.all()
    products = Product.objects.all()

    if request.method == "POST":

        supplier = Supplier.objects.get(id=request.POST.get('supplier'))
        date = request.POST.get('purchase_date')
        payment_type = request.POST.get('payment_type')
        tax_type = request.POST.get('tax_type')

        purchase = Purchase.objects.create(
            supplier=supplier,
            purchase_date=date,
            payment_type=payment_type,
            tax_type=tax_type
        )

        grand_total = Decimal('0')

        product_ids = request.POST.getlist('product[]')
        qtys = request.POST.getlist('qty[]')
        rates = request.POST.getlist('rate[]')
        selling_rates = request.POST.getlist('selling_rate[]')  # ✅ NEW
        cgsts = request.POST.getlist('cgst[]')
        sgsts = request.POST.getlist('sgst[]')

        for i in range(len(product_ids)):

            pid = product_ids[i]
            if not pid:
                continue

            qty = Decimal(qtys[i])
            rate = Decimal(rates[i])
            cgst = Decimal(cgsts[i])
            sgst = Decimal(sgsts[i])

            selling_rate = selling_rates[i].strip()
            selling_rate = Decimal(selling_rate) if selling_rate else None

            base = qty * rate
            gst_amount = base * (cgst + sgst) / 100
            total = base + gst_amount

            PurchaseItem.objects.create(
                purchase=purchase,
                product_id=pid,
                qty=qty,
                rate=rate,
                cgst=cgst,
                sgst=sgst,
                gst_amount=gst_amount,
                selling_rate=selling_rate,  # ✅ SAVED
                total=total
            )

            stock, _ = Stock.objects.get_or_create(product_id=pid)
            stock.quantity += qty
            stock.save()

            grand_total += total

        purchase.total_amount = grand_total
        purchase.save()

        if payment_type == "CREDIT":
            SupplierLedger.objects.create(
                supplier=purchase.supplier,
                date=purchase.purchase_date,
                particular=f"Purchase {purchase.invoice_no}",
                debit=grand_total,
                credit=0,
                source='PURCHASE',
                reference_id=purchase.id
            )

        return redirect('purchase_list')

    return render(request, 'purchase/purchase_add.html', {
        'suppliers': suppliers,
        'products': products
    })









# ---------------- EDIT ----------------
from stock.models import Stock

from decimal import Decimal
from stock.models import Stock
from django.db import transaction

from decimal import Decimal
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .models import Purchase, PurchaseItem
from supplier_master.models import Supplier
from product.models import Product
from stock.models import Stock
from supplier_ledger.models import SupplierLedger


@transaction.atomic
def purchase_edit(request, pk):
    purchase = get_object_or_404(Purchase, id=pk)
    suppliers = Supplier.objects.all()
    products = Product.objects.all()
    items = purchase.items.all()

    if request.method == "POST":
        # 🔴 STEP 1: REVERSE OLD STOCK
        for item in items:
            stock = Stock.objects.filter(product=item.product).first()
            if stock:
                stock.quantity -= item.qty
                stock.save()

        # 🔴 STEP 2: DELETE OLD ITEMS
        purchase.items.all().delete()

        # 🔴 STEP 3: DELETE OLD LEDGER
        SupplierLedger.objects.filter(
            source='PURCHASE',
            reference_id=purchase.id
        ).delete()

        # 🔴 STEP 4: UPDATE PURCHASE MASTER
        purchase.supplier_id = request.POST.get('supplier')
        purchase.purchase_date = request.POST.get('purchase_date')
        purchase.payment_type = request.POST.get('payment_type')
        purchase.tax_type = request.POST.get('tax_type')
        purchase.save()

        grand_total = Decimal('0')

        product_ids = request.POST.getlist('product[]')
        qtys = request.POST.getlist('qty[]')
        rates = request.POST.getlist('rate[]')
        # ✅ FIX: Edit view-ilum selling_rate list edukkanam
        selling_rates = request.POST.getlist('selling_rate[]')
        cgsts = request.POST.getlist('cgst[]')
        sgsts = request.POST.getlist('sgst[]')

        # 🔴 STEP 5: RE-CREATE ITEMS
        for i in range(len(product_ids)):
            pid = product_ids[i]
            if not pid:
                continue

            qty = Decimal(qtys[i])
            rate = Decimal(rates[i])
            cgst = Decimal(cgsts[i])
            sgst = Decimal(sgsts[i])

            # ✅ FIX: Selling rate list-il ninnu value edukkanam
            s_rate = selling_rates[i].strip() if i < len(selling_rates) else None
            selling_rate = Decimal(s_rate) if s_rate else None

            base = qty * rate
            gst_amount = base * (cgst + sgst) / 100
            total = base + gst_amount

            PurchaseItem.objects.create(
                purchase=purchase,
                product_id=pid,
                qty=qty,
                rate=rate,
                cgst=cgst,
                sgst=sgst,
                gst_amount=gst_amount,
                selling_rate=selling_rate,  # ✅ Ippo edit cheyyumpol save aagum
                total=total
            )

            # 🔴 ADD STOCK AGAIN
            stock, _ = Stock.objects.get_or_create(product_id=pid)
            stock.quantity += qty
            stock.save()

            grand_total += total

        # 🔴 STEP 6: UPDATE PURCHASE TOTAL
        purchase.total_amount = grand_total
        purchase.save()

        # 🔴 STEP 7: LEDGER ONLY IF CREDIT
        if purchase.payment_type == "CREDIT":
            SupplierLedger.objects.create(
                supplier=purchase.supplier,
                date=purchase.purchase_date,
                particular=f"Purchase {purchase.invoice_no}",
                debit=grand_total,
                credit=0,
                source='PURCHASE',
                reference_id=purchase.id
            )

        return redirect('purchase_list')

    return render(request, 'purchase/purchase_add.html', {
        'purchase': purchase,
        'items': items,
        'suppliers': suppliers,
        'products': products
    })






from django.contrib import messages
from .models import InvoiceSettings

def invoice_settings(request):

    settings, created = InvoiceSettings.objects.get_or_create(id=1)

    if request.method == "POST":
        settings.purchase_prefix = request.POST.get("purchase_prefix")
        settings.save()

        messages.success(request, "✅ Invoice prefix updated successfully")
        return redirect("invoice_settings")

    return render(request, "purchase/invoice_settings.html", {
        "settings": settings
    })





# ---------------- VIEW INVOICE ----------------
# def purchase_view(request, pk):
#     purchase = get_object_or_404(Purchase, id=pk)
#     return render(request, 'purchase/purchase_invoice.html', {
#         'purchase': purchase
#     })


# ---------------- DELETE ----------------
from django.db import transaction
from stock.models import Stock
from supplier_ledger.models import SupplierLedger

@transaction.atomic
def purchase_delete(request, pk):
    purchase = get_object_or_404(Purchase, id=pk)

    if request.method == "POST":

        # 🔁 STEP 1: REVERSE STOCK
        for item in purchase.items.all():
            stock = Stock.objects.filter(product=item.product).first()
            if stock:
                stock.quantity -= item.qty
                stock.save()

        # 🔁 STEP 2: DELETE LEDGER ENTRY
        SupplierLedger.objects.filter(
            source='PURCHASE',
            reference_id=purchase.id
        ).delete()

        # 🔁 STEP 3: DELETE PURCHASE (items auto delete)
        purchase.delete()

        return redirect('purchase_list')

    return render(request, 'purchase/purchase_delete.html', {
        'purchase': purchase
    })



# ---------------- PRINT ----------------
from decimal import Decimal

from django.shortcuts import render, get_object_or_404
from decimal import Decimal


# VIEW / PRINT (same page)
def purchase_invoice_print(request, pk):
    purchase = get_object_or_404(Purchase, id=pk)

    total_sgst = 0
    total_cgst = 0
    taxable_total = 0

    for item in purchase.items.all():
        base = item.qty * item.rate
        taxable_total += base
        total_sgst += base * item.sgst / 100
        total_cgst += base * item.cgst / 100

    discount = 0  # future use

    return render(request, 'purchase/purchase_invoice_print.html', {
        'purchase': purchase,
        'taxable_total': round(taxable_total, 2),
        'total_sgst': round(total_sgst, 2),
        'total_cgst': round(total_cgst, 2),
        'discount': discount
    })





from django.shortcuts import get_object_or_404

from .utils.pdf import generate_pdf
from .models import Purchase


def purchase_invoice_pdf(request, pk):


    purchase = get_object_or_404(Purchase, id=pk)

    total_sgst = 0
    total_cgst = 0
    taxable_total = 0


    for item in purchase.items.all():
        base = item.qty * item.rate
        taxable_total += base
        total_sgst += base * item.sgst / 100
        total_cgst += base * item.cgst / 100


    context = {
        "purchase": purchase,
        "taxable_total": round(taxable_total, 2),
        "total_sgst": round(total_sgst, 2),
        "total_cgst": round(total_cgst, 2),
        "discount": 0,
    }


    filename = f"{purchase.invoice_no}.pdf"


    template_path = "purchase/purchase_invoice_print.html"

    return generate_pdf(template_path, context, filename)


from .models import PurchaseReturn, PurchaseReturnItem


# 1. Return cheytha list kaanan
def purchase_return_list(request):
    returns = PurchaseReturn.objects.order_by('-id')
    return render(request, 'purchase/return_list.html', {'returns': returns})


# 2. Puthiya return save cheyyan
@transaction.atomic
def purchase_return_add(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)

    if request.method == "POST":
        return_date = request.POST.get('return_date')
        reason = request.POST.get('reason')

        # Create Return Master
        p_return = PurchaseReturn.objects.create(
            purchase=purchase,
            return_date=return_date,
            reason=reason
        )

        grand_return_total = Decimal('0')
        item_ids = request.POST.getlist('item_id[]')  # PurchaseItem IDs
        return_qtys = request.POST.getlist('return_qty[]')

        for i in range(len(item_ids)):
            qty_to_return = Decimal(return_qtys[i] or 0)

            if qty_to_return > 0:
                p_item = PurchaseItem.objects.get(id=item_ids[i])

                # Row calculations (Purchase rate-il thanne return cheyyunnu)
                base = qty_to_return * p_item.rate
                gst = base * (p_item.cgst + p_item.sgst) / 100
                row_total = base + gst

                # Create Return Item
                PurchaseReturnItem.objects.create(
                    purchase_return=p_return,
                    purchase_item=p_item,
                    qty=qty_to_return,
                    rate=p_item.rate,
                    total=row_total
                )

                # 📉 STOCK KURAYKKANAM (Return poyille...)
                # Batch update
                p_item.quantity_at_hand -= qty_to_return
                p_item.save()

                # Overall stock update
                stock = Stock.objects.get(product=p_item.product)
                stock.quantity -= qty_to_return
                stock.save()

                grand_return_total += row_total

        p_return.total_return_amount = grand_return_total
        p_return.save()

        # 📉 LEDGER UPDATE (Supplier-nu nammal kodukkanulla debt kurayunnu)
        # Purchase-il debit aayirunnu (payment_type credit aayappol)
        # Appol return-il nammal athu CREDIT column-ilaanu idukka (Balance kurayaan)
        SupplierLedger.objects.create(
            supplier=purchase.supplier,
            date=return_date,
            particular=f"Purchase Return {p_return.return_no} (Inv: {purchase.invoice_no})",
            debit=0,
            credit=grand_return_total,  # Balance kuraykkan credit-il idunnu
            source='PURCHASE',  # Or 'RETURN' choice models-il undengil athu
            reference_id=p_return.id
        )

        return redirect('purchase_return_list')

    # GET request: Purchase items list cheyyanulla page kaanikkanam
    return render(request, 'purchase/purchase_return_add.html', {
        'purchase': purchase,
        'items': purchase.items.all()
    })