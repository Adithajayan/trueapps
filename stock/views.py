from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from product.models import Product
from .models import Stock, StockHistory


# -------------------------------------------------
# STOCK REGISTER
# -------------------------------------------------
from django.utils import timezone # Top-il import cheyyuka
from django.db.models import Q

from django.utils import timezone # Top-il import cheyyuka
from django.db.models import Q

def stock_list(request):
    stocks = Stock.objects.select_related('product')

    # Filter values edukkunnu
    q = request.GET.get('q', '').strip()
    selected_month = request.GET.get('month') # Format: YYYY-MM

    # Text search (Product Name)
    if q:
        stocks = stocks.filter(product__name__icontains=q)


    if selected_month:
        year, month = selected_month.split('-')
        # Stock update cheyyappetta month vechu filter cheyyunnu
        stocks = stocks.filter(updated_at__year=year, updated_at__month=month)

    return render(request, 'stock/stock_list.html', {
        'stocks': stocks,
        'query': q,
        'selected_month': selected_month
    })


# -------------------------------------------------
# OPENING STOCK ADD
# -------------------------------------------------
@transaction.atomic
@transaction.atomic
def opening_stock_add(request):
    products = Product.objects.all()

    if request.method == "POST":
        product_id = request.POST.get("product")
        hsn_code = request.POST.get("hsn_code")
        qty = Decimal(request.POST.get("quantity") or 0)

        # NEW: Purchase Rate (Profit correct aakan)
        p_rate = Decimal(request.POST.get("purchase_rate") or 0)

        s_rate = Decimal(request.POST.get("selling_rate") or 0)
        cgst_val = Decimal(request.POST.get("cgst") or 0)
        sgst_val = Decimal(request.POST.get("sgst") or 0)

        product = get_object_or_404(Product, id=product_id)

        # 1. HSN Code Product model-il update cheyyunnu
        if hsn_code:
            product.hsn_code = hsn_code
            product.save()

        # 2. Main Stock Table update cheyyunnu
        stock, created = Stock.objects.get_or_create(
            product_id=product_id,
            defaults={'quantity': Decimal("0")}
        )
        stock.quantity += qty
        stock.save()

        # 3. Stock History entry (Audit trail-inu vendi)
        StockHistory.objects.create(
            product_id=product_id,
            qty=qty,
            selling_rate=s_rate,
            cgst=cgst_val,
            sgst=sgst_val,
            type='OPENING'
        )


        opening_purchase, _ = Purchase.objects.get_or_create(
            bill_number="OPENING",
            defaults={
                'vendor_name': 'OPENING STOCK',
                'total_amount': 0,
            }
        )


        PurchaseItem.objects.create(
            purchase=opening_purchase, # <--- THE FIX
            product=product,
            qty=qty,
            quantity_at_hand=qty,
            rate=p_rate,
            selling_rate=s_rate,
            cgst=cgst_val,
            sgst=sgst_val,
            total=qty * p_rate
        )

        return redirect("stock_list")

    return render(request, "stock/opening_stock_add.html", {"products": products})


# -------------------------------------------------
# OPENING STOCK EDIT
# -------------------------------------------------
@transaction.atomic
def opening_stock_edit(request, pk):
    # Old data fetch cheyyunnu
    history = get_object_or_404(StockHistory, id=pk, type='OPENING')
    stock = Stock.objects.get(product=history.product)

    if request.method == "POST":

        new_qty = Decimal(request.POST.get("quantity") or 0)
        new_selling_rate = Decimal(request.POST.get("selling_rate") or 0)
        new_cgst = Decimal(request.POST.get("cgst") or 0)
        new_sgst = Decimal(request.POST.get("sgst") or 0)


        stock.quantity = (stock.quantity - history.qty) + new_qty
        stock.save()


        history.qty = new_qty
        history.selling_rate = new_selling_rate
        history.cgst = new_cgst
        history.sgst = new_sgst
        history.save()

        return redirect('opening_stock_history')

    return render(request, 'stock/opening_stock_edit.html', {
        'history': history
    })


# -------------------------------------------------
# OPENING STOCK DELETE
# -------------------------------------------------
def opening_stock_delete(request, pk):

    history = get_object_or_404(StockHistory, id=pk, type='OPENING')
    stock = Stock.objects.get(product=history.product)

    if request.method == "POST":
        stock.quantity -= history.qty
        stock.save()

        history.delete()
        return redirect('opening_stock_history')

    return render(request, 'stock/opening_stock_delete.html', {
        'history': history
    })


from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from .models import Stock, StockHistory
from product.models import Product


# ----------------------------------
# OPENING STOCK HISTORY LIST
# ----------------------------------
def opening_stock_history(request):

    histories = StockHistory.objects.filter(
        type='OPENING'
    ).select_related('product').order_by('-created_at')

    return render(request, 'stock/opening_stock_history.html', {
        'histories': histories
    })

from purchase.models import PurchaseItem
from sales.models import SalesItem
from django.db.models import Sum

from purchase.models import PurchaseItem
from sales.models import SalesItem
from django.db.models import Sum
from product.models import Product
from supplier_master.models import Supplier

from django.shortcuts import render
from django.db.models import Sum
from product.models import Product
from supplier_master.models import Supplier
from purchase.models import PurchaseItem
from sales.models import SalesItem


def detailed_stock_register(request):
    product_id = request.GET.get('product')
    supplier_id = request.GET.get('supplier')
    only_available = request.GET.get('available')

    stock_rows = []

    # 1. --- OPENING STOCK ENTRIES ---
    # Opening stock-inu specific supplier illathathukond supplier filter illekil mathram kaanikunnu
    if not supplier_id:
        opening_stocks = StockHistory.objects.filter(type='OPENING').select_related('product')
        if product_id:
            opening_stocks = opening_stocks.filter(product_id=product_id)

        for oh in opening_stocks:
            # Opening stock-inu ippozhathe ninte setup-il batch tracking illekil
            # product-wise sales minus cheyyendi varum.
            total_sold = SalesItem.objects.filter(product=oh.product).aggregate(total=Sum('qty'))['total'] or 0

            # Note: Return handle cheyyan Opening Stock-inum batch system varanam.
            # Ennalum ippol ninte logic anusarichu balance ingane set cheyyam:
            balance_qty = oh.qty - total_sold

            if only_available and balance_qty <= 0:
                continue

            stock_rows.append({
                'item_id': f"OP-{oh.id}",
                'product': oh.product,
                'supplier': None,  # HTML-il "OPENING STOCK" ennu varan
                'date': oh.created_at,
                'rate': 0,
                'purchased_qty': oh.qty,
                'sold_qty': total_sold,
                'returned_qty': 0,  # Opening-inu batch illathathond 0 aayi idunnu
                'balance_qty': balance_qty,
                'selling_rate': oh.selling_rate,
            })

    # 2. --- PURCHASE ENTRIES (BATCH-WISE) ---
    purchase_items = PurchaseItem.objects.select_related('product', 'purchase', 'purchase__supplier')

    if product_id:
        purchase_items = purchase_items.filter(product_id=product_id)
    if supplier_id:
        purchase_items = purchase_items.filter(purchase__supplier_id=supplier_id)

    for item in purchase_items.order_by('-purchase__purchase_date'):
        # 🔥 FIX: Batch-wise functions call cheyyunnu
        # Ithaanu return vannal detailed register update aakanulla vazhi
        sold_qty = item.get_total_sold()
        returned_qty = item.get_total_returned()

        # Net Sold = Poyath - Thirichu Vannath
        net_sold = sold_qty - returned_qty

        # Balance is directly from our quantity_at_hand field
        balance_qty = item.quantity_at_hand

        if only_available and balance_qty <= 0:
            continue

        stock_rows.append({
            'item_id': item.id,
            'product': item.product,
            'supplier': item.purchase.supplier,
            'date': item.purchase.purchase_date,
            'rate': item.rate,
            'purchased_qty': item.qty,
            'sold_qty': net_sold,
            'returned_qty': returned_qty,
            'balance_qty': balance_qty,
            'selling_rate': item.selling_rate or 0,
        })

    return render(request, 'stock/stock_register_detailed.html', {
        'stock_rows': stock_rows,
        'products': Product.objects.all(),
        'suppliers': Supplier.objects.all(),
        'selected_product': product_id,
        'selected_supplier': supplier_id,
        'only_available': only_available,
    })


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
from purchase.models import PurchaseItem


@require_POST
def update_selling_rate(request):
    item_id = request.POST.get('item_id')
    rate = request.POST.get('selling_rate')

    if not item_id:
        return JsonResponse({'status': 'error', 'msg': 'Invalid item'})

    try:
        item = PurchaseItem.objects.get(id=item_id)
        item.selling_rate = Decimal(rate) if rate else None
        item.save()
        return JsonResponse({'status': 'success'})
    except PurchaseItem.DoesNotExist:
        return JsonResponse({'status': 'error', 'msg': 'Item not found'})


