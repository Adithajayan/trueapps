from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Max
from decimal import Decimal

# Corrected Imports from other apps
from .models import SalesMaster, SalesItem, InvoiceSetting
from customer.models import Customer
from product.models import Product
from stock.models import Stock


# ---------------- SALES CREATE ----------------
from django.db import transaction
from stock.models import StockHistory  # Opening stock-inu vendi
from sales.models import SalesItemBatch

from django.db import transaction
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from .models import SalesMaster, SalesItem, SalesItemBatch, InvoiceSetting
from purchase.models import PurchaseItem
from stock.models import Stock

from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from django.db.models import Max
from decimal import Decimal
from .models import SalesMaster, SalesItem, SalesItemBatch, InvoiceSetting
from purchase.models import PurchaseItem
from stock.models import Stock
from customer.models import Customer
from product.models import Product


@transaction.atomic
def sales_create(request):
    # Invoice setting fetch cheyyunnu
    setting, _ = InvoiceSetting.objects.get_or_create(name="SALES", defaults={'prefix': 'TBT-IN'})

    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        # 🔥 Puthiya Field: B2B/B2C select box-il ninnu edukkunnu
        sale_type = request.POST.get('sale_type', 'B2C')

        if not customer_id:
            messages.error(request, "Please select a customer.")
            return render(request, 'sales/sales_form.html')

        customer = get_object_or_404(Customer, id=customer_id)
        product_ids = request.POST.getlist('product_id[]')
        qtys = request.POST.getlist('qty[]')
        rates = request.POST.getlist('rate[]')
        cgsts = request.POST.getlist('cgst[]')
        sgsts = request.POST.getlist('sgst[]')

        # --- STEP 1: STOCK VALIDATION ---
        for i in range(len(product_ids)):
            if not product_ids[i]: continue
            prod_obj = Product.objects.get(id=product_ids[i])
            requested_qty = int(qtys[i])
            stock_obj = Stock.objects.filter(product=prod_obj).first()
            available = stock_obj.quantity if stock_obj else 0
            if available < requested_qty:
                messages.error(request, f"Insufficient stock for {prod_obj.name}. Available: {available}")
                # Form-ilekk thirichu vidumbol data nashpedatha reethiyil handle cheyyanam
                return render(request, 'sales/sales_form.html')

        # --- STEP 2: INVOICE MASTER ---
        prefix = setting.prefix
        last_invoice = SalesMaster.objects.filter(invoice_prefix=prefix).aggregate(Max('id'))['id__max']
        next_no = 1 if not last_invoice else last_invoice + 1
        invoice_no = f"{prefix}-{next_no:03d}"

        # 🔥 sale_type koodi ivide create cheyyunnu
        sale = SalesMaster.objects.create(
            invoice_prefix=prefix,
            invoice_no=invoice_no,
            customer=customer,
            sale_type=sale_type,
            total_amount=0
        )

        total_bill = Decimal(0)

        # --- STEP 3: ITEM SAVING & FIFO GST PROFIT ---
        for i in range(len(product_ids)):
            if not product_ids[i]: continue

            product = Product.objects.get(id=product_ids[i])
            requested_qty = int(qtys[i])
            sell_rate = Decimal(rates[i])
            s_cgst = Decimal(cgsts[i]) if (i < len(cgsts) and cgsts[i]) else Decimal(0)
            s_sgst = Decimal(sgsts[i]) if (i < len(sgsts) and sgsts[i]) else Decimal(0)

            # Selling price with GST
            sell_price_inc_gst = sell_rate + (sell_rate * (s_cgst + s_sgst) / 100)

            sales_item = SalesItem.objects.create(
                sales=sale, product=product, hsn_code=product.hsn_code,
                qty=requested_qty, purchase_price=0, selling_price=sell_rate,
                cgst=s_cgst, sgst=s_sgst, total=0
            )

            batches = PurchaseItem.objects.filter(
                product=product, quantity_at_hand__gt=0
            ).order_by('purchase__purchase_date')

            remaining_to_sell = requested_qty
            total_purchase_cost_no_gst = Decimal(0)

            for batch in batches:
                if remaining_to_sell <= 0: break
                qty_from_batch = min(batch.quantity_at_hand, remaining_to_sell)

                # Purchase price with GST from batch
                p_cgst = batch.cgst
                p_sgst = batch.sgst
                purchase_price_inc_gst = batch.rate + (batch.rate * (p_cgst + p_sgst) / 100)

                # 🔥 GST Inclusive Profit
                batch_profit = (sell_price_inc_gst - purchase_price_inc_gst) * Decimal(qty_from_batch)

                SalesItemBatch.objects.create(
                    sales_item=sales_item, purchase_item=batch, qty=qty_from_batch,
                    purchase_rate=batch.rate, selling_rate=sell_rate, profit=batch_profit
                )

                batch.quantity_at_hand -= qty_from_batch
                batch.save()
                total_purchase_cost_no_gst += (batch.rate * qty_from_batch)
                remaining_to_sell -= qty_from_batch

            # Final Item Calculations
            sales_item.purchase_price = total_purchase_cost_no_gst / requested_qty if requested_qty > 0 else 0
            base_amount = sell_rate * requested_qty
            item_total = base_amount + (base_amount * (s_cgst + s_sgst) / 100)
            sales_item.total = item_total
            sales_item.save()

            # Global Stock Update
            stock_obj = Stock.objects.filter(product=product).first()
            if stock_obj:
                stock_obj.quantity -= requested_qty
                stock_obj.save()

            total_bill += item_total

        sale.total_amount = total_bill
        sale.save()
        messages.success(request, f"Invoice {invoice_no} created successfully!")
        return redirect('sales_list')

    return render(request, 'sales/sales_form.html')


# ---------------- PRODUCT SEARCH (FIXED) ----------------
def product_search(request):
    term = request.GET.get('term', '')
    products = Product.objects.filter(name__icontains=term)[:10]

    data = []
    for p in products:
        stock_obj = Stock.objects.filter(product=p).first()
        qty = stock_obj.quantity if stock_obj else 0

        data.append({
            'id': p.id,
            'name': p.name,
            'stock': float(qty),
            'rate': float(p.sales_rate) if hasattr(p, 'sales_rate') else float(p.selling_rate),
            'cgst': float(p.cgst) if p.cgst else 0,
            'sgst': float(p.sgst) if p.sgst else 0
        })
    return JsonResponse(data, safe=False)

# ---------------- OTHERS ----------------
def customer_search(request):
    term = request.GET.get('term', '')
    # Customer name-il aa search term undo ennu nokkunnu
    customers = Customer.objects.filter(name__icontains=term)[:10]

    results = []
    for c in customers:
        results.append({
            'id': c.id,
            'name': c.name,
            'place': getattr(c, 'place', '')  # Place model-il undenkil athum koodi edukkum
        })
    return JsonResponse(results, safe=False)


def update_invoice_prefix(request):
    if request.method == 'POST':
        new_prefix = request.POST.get('prefix')
        # get_or_create upayogichal settings illenkil error varilla
        setting, created = InvoiceSetting.objects.get_or_create(
            name="SALES",
            defaults={'prefix': 'INV'}
        )
        setting.prefix = new_prefix
        setting.save()
    return redirect('sales_list')

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Max, Sum, F
from decimal import Decimal
from datetime import datetime

from .models import SalesMaster, SalesItem, InvoiceSetting
from customer.models import Customer
from product.models import Product
from stock.models import Stock


# ... (sales_create, product_search, customer_search functions stay the same) ...

# ---------------- SALES LIST WITH MONTHLY FILTER ----------------
def sales_list(request):
    # Get current year and month as default
    now = datetime.now()
    month = request.GET.get('month', now.month)
    year = request.GET.get('year', now.year)

    sales = SalesMaster.objects.filter(
        date__month=month,
        date__year=year
    ).order_by('-id')


    years = range(2024, 2031)
    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    return render(request, 'sales/sales_list.html', {
        'sales': sales,
        'current_month': int(month),
        'current_year': int(year),
        'months': months,
        'years': years,
    })


def invoice_settings(request):
    setting, created = InvoiceSetting.objects.get_or_create(name="SALES", defaults={'prefix': 'INV'})
    if request.method == 'POST':
        setting.prefix = request.POST.get('prefix')
        setting.save()
        return redirect('sales_list')
    return render(request, 'sales/invoice_settings_form.html', {'setting': setting})

    return render(request, 'sales/invoice_settings.html', {'setting': setting})

# ---------------- SALES PROFIT (MONTHLY) ----------------



# ---------------- DELETE SALE ----------------
@transaction.atomic
def sales_delete(request, pk):
    sale = get_object_or_404(SalesMaster, pk=pk)

    for item in sale.items.all():
        # Global stock
        stock_obj = Stock.objects.filter(product=item.product).first()
        if stock_obj:
            stock_obj.quantity += item.qty
            stock_obj.save()

        # Batch Stock Restore (Critical Fix)
        for ib in item.batches.all():
            pi = ib.purchase_item
            pi.quantity_at_hand += ib.qty
            pi.save()

    sale.delete()
    return redirect('sales_list')





# ---------------- SALES RETURN HISTORY (LIST) ----------------
def sales_return(request):
    # Ella return records-um latest date-il aadyam varunna reethiyil fetch cheyyunnu
    returns = SalesReturn.objects.all().order_by('-id').select_related('sale', 'sale__customer')

    return render(request, 'sales/sales_return.html', {
        'returns': returns
    })

# def sales_view(request, pk):
#     sale = get_object_or_404(SalesMaster, pk=pk)
#     return render(request, 'sales/sales_view.html', {'sale': sale})


from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from decimal import Decimal
from .models import SalesMaster, SalesItem, SalesItemBatch
from purchase.models import PurchaseItem
from stock.models import Stock
from product.models import Product


@transaction.atomic
def sales_edit(request, pk):
    sale = get_object_or_404(SalesMaster, pk=pk)
    items = sale.items.all()

    if request.method == 'POST':
        product_ids = request.POST.getlist('product_id[]')
        qtys = request.POST.getlist('qty[]')
        rates = request.POST.getlist('rate[]')
        cgsts = request.POST.getlist('cgst[]')
        sgsts = request.POST.getlist('sgst[]')
        # 🔥 Puthiya Field: Form-il ninnu B2B/B2C type edukkunnu
        new_sale_type = request.POST.get('sale_type', 'B2C')

        # --- STEP 1: VALIDATE STOCK ---
        for i in range(len(product_ids)):
            if not product_ids[i]: continue
            prod_obj = Product.objects.get(id=product_ids[i])
            new_qty = int(qtys[i])
            old_item = items.filter(product=prod_obj).first()
            old_qty = old_item.qty if old_item else 0
            stock_obj = Stock.objects.filter(product=prod_obj).first()
            current_available = stock_obj.quantity if stock_obj else 0
            if (current_available + old_qty) < new_qty:
                messages.error(request, f"Insufficient stock for {prod_obj.name}.")
                return render(request, 'sales/sales_edit.html', {'sale': sale, 'items': items})

        # --- STEP 2: RESTORE OLD STOCK (Before updating) ---
        for item in items:
            stock_obj = Stock.objects.filter(product=item.product).first()
            if stock_obj:
                stock_obj.quantity += item.qty
                stock_obj.save()
            for ib in item.batches.all():
                pi = ib.purchase_item
                pi.quantity_at_hand += ib.qty
                pi.save()

        # Pazhaya items delete cheyyunnu (Re-creation logic)
        items.delete()

        # --- STEP 3: RE-CREATE ITEMS WITH NEW DATA ---
        total_bill = Decimal(0)
        for i in range(len(product_ids)):
            if not product_ids[i]: continue
            product = Product.objects.get(id=product_ids[i])
            req_qty = int(qtys[i])
            sell_rate = Decimal(rates[i])
            s_cgst = Decimal(cgsts[i]) if (i < len(cgsts) and cgsts[i]) else Decimal(0)
            s_sgst = Decimal(sgsts[i]) if (i < len(sgsts) and sgsts[i]) else Decimal(0)

            # Selling price with GST (Profit calculation-u vendi)
            sell_price_inc_gst = sell_rate + (sell_rate * (s_cgst + s_sgst) / 100)

            new_item = SalesItem.objects.create(
                sales=sale, product=product, hsn_code=product.hsn_code,
                qty=req_qty, selling_price=sell_rate, purchase_price=0,
                cgst=s_cgst, sgst=s_sgst, total=0
            )

            remaining = req_qty
            total_purchase_cost = Decimal(0)
            # FIFO: Oldest batches first
            batches = PurchaseItem.objects.filter(product=product, quantity_at_hand__gt=0).order_by(
                'purchase__purchase_date')

            for b in batches:
                if remaining <= 0: break
                take = min(b.quantity_at_hand, remaining)

                p_inc_gst = b.rate + (b.rate * (b.cgst + b.sgst) / 100)
                batch_profit = (sell_price_inc_gst - p_inc_gst) * Decimal(take)

                SalesItemBatch.objects.create(
                    sales_item=new_item, purchase_item=b, qty=take,
                    purchase_rate=b.rate, selling_rate=sell_rate, profit=batch_profit
                )
                b.quantity_at_hand -= take
                b.save()
                total_purchase_cost += (b.rate * take)
                remaining -= take

            # Final Item-wise Calculations
            new_item.purchase_price = total_purchase_cost / req_qty if req_qty > 0 else 0
            item_total = (sell_rate * req_qty) * (1 + (s_cgst + s_sgst) / 100)
            new_item.total = item_total
            new_item.save()

            # Global Stock Update (New Qty subtract cheyyunnu)
            stock_obj = Stock.objects.filter(product=product).first()
            if stock_obj:
                stock_obj.quantity -= req_qty
                stock_obj.save()

            total_bill += item_total

        # --- STEP 4: UPDATE SALES MASTER ---
        sale.total_amount = total_bill
        sale.date = request.POST.get('date') or sale.date
        sale.sale_type = new_sale_type  # 🔥 Puthiya Sale Type ivide save cheyyunnu
        sale.save()

        messages.success(request, "Invoice updated successfully!")
        return redirect('sales_list')

    return render(request, 'sales/sales_edit.html', {'sale': sale, 'items': items})

from django.http import JsonResponse
from product.models import Product


def product_search_api(request):
    query = request.GET.get('term', '')
    products = Product.objects.filter(name__icontains=query)[:10]
    results = []
    for p in products:
        # Stock model-il ninnu current quantity edukkyunnu
        stock_obj = Stock.objects.filter(product=p).first()
        qty = stock_obj.quantity if stock_obj else 0

        results.append({
            'id': p.id,
            'name': p.name,
            'price': float(p.selling_rate),
            'cgst': float(p.cgst),
            'sgst': float(p.sgst),
            'stock': float(qty)  # Stock value ivide pass cheyyunnu
        })
    return JsonResponse(results, safe=False)


@transaction.atomic
def sales_delete_confirm(request, pk):
    sale = get_object_or_404(SalesMaster, pk=pk)

    if request.method == 'POST':
        for item in sale.items.all():
            # 1. Global stock restore
            stock_obj = Stock.objects.filter(product=item.product).first()
            if stock_obj:
                stock_obj.quantity += item.qty
                stock_obj.save()

            # 2. Batch Stock Restore (FIFO batches-ilekk thirichu idunnu)
            for ib in item.batches.all():
                pi = ib.purchase_item
                pi.quantity_at_hand += ib.qty
                pi.save()

        sale.delete()
        return redirect('sales_list')

    return render(request, 'sales/sales_delete_confirm.html', {'sale': sale})


from django.db.models import Sum
from decimal import Decimal
from datetime import datetime


def profit_update(request, pk):
    sale = get_object_or_404(SalesMaster, pk=pk)
    batch_data = []
    total_invoice_profit = Decimal('0')

    product_returns = {}
    for ret in sale.returns.all():
        for ret_item in ret.return_items.all():
            p_id = ret_item.product.id
            product_returns[p_id] = product_returns.get(p_id, Decimal('0')) + ret_item.qty_returned

    batches = SalesItemBatch.objects.filter(sales_item__sales=sale).select_related(
        'sales_item', 'sales_item__product', 'purchase_item'
    )

    returned_tracked = set()

    for batch in batches:
        net_qty = batch.qty
        prod_id = batch.sales_item.product.id
        total_ret_for_prod = product_returns.get(prod_id, Decimal('0'))

        if prod_id not in returned_tracked:
            display_returned = total_ret_for_prod
            display_sold = net_qty + total_ret_for_prod
            returned_tracked.add(prod_id)
        else:
            display_returned = Decimal('0')
            display_sold = net_qty

        # 🔥 GST INCLUSIVE CALCULATION FOR DISPLAY
        p_inc_gst = batch.purchase_rate * (1 + (batch.purchase_item.cgst + batch.purchase_item.sgst) / 100)
        s_inc_gst = batch.selling_rate * (1 + (batch.sales_item.cgst + batch.sales_item.sgst) / 100)

        # Batch profit is already saved as GST inclusive in create/edit/return
        # But we re-calculate here to ensure display is 100% sync with Net Qty
        batch_profit = (s_inc_gst - p_inc_gst) * net_qty
        total_invoice_profit += batch_profit

        batch_data.append({
            'product_name': batch.sales_item.product.name,
            'sold_qty': display_sold,
            'returned_qty': display_returned,
            'net_qty': net_qty,
            'purchase_rate': p_inc_gst,
            'selling_rate': s_inc_gst,
            'profit': batch_profit,
            'is_returned': total_ret_for_prod > 0
        })

    return render(request, 'sales/profit_update_form.html', {
        'sale': sale,
        'batch_data': batch_data,
        'total_invoice_profit': total_invoice_profit
    })




from .models import SalesMaster, SalesItem, InvoiceSetting, SalesReturn, SalesReturnItem

from django.db import transaction  # Import this for safety

from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from .models import SalesMaster, SalesReturn, SalesReturnItem, SalesItemBatch
from stock.models import Stock
from product.models import Product

from decimal import Decimal
from django.db import transaction


from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
# Ninte model names anusarichu import check cheyyuka




def sales_return_view(request, pk):
    # SalesReturn model-il ninnu data edukkyunnu
    return_obj = get_object_or_404(SalesReturn, pk=pk)
    # Athile items (return_items) fetch cheyyunnu
    return_items = return_obj.return_items.all()

    return render(request, 'sales/sales_return_view.html', {
        'return_obj': return_obj,
        'return_items': return_items
    })

from django.http import JsonResponse
from django.db.models import Sum
from purchase.models import PurchaseItem
from sales.models import SalesItemBatch

from django.http import JsonResponse
from django.db.models import Sum
from purchase.models import PurchaseItem
from sales.models import SalesItem


def product_batch_info(request, product_id):
    # Oldest batches with stock first (FIFO)
    batches = PurchaseItem.objects.filter(
        product_id=product_id,
        quantity_at_hand__gt=0
    ).order_by('purchase__purchase_date')

    batch_list = []
    total_stock = 0

    for b in batches:
        total_stock += b.quantity_at_hand
        batch_list.append({
            'available_qty': float(b.quantity_at_hand),
            'purchase_rate': float(b.rate),
            'selling_rate': float(b.selling_rate) if b.selling_rate else 0,
            'cgst': float(b.cgst),
            'sgst': float(b.sgst),
        })

    return JsonResponse({
        'total_stock': float(total_stock),
        'batches': batch_list
    })



from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.http import HttpResponse
from config.utils.pdf import generate_pdf
from .models import SalesMaster


def manage_sales_invoice(request, pk, action='view'):
    sale = get_object_or_404(SalesMaster, pk=pk)

    # DOWNLOAD ACTION
    if action == 'download':


        context = {'sale': sale}
        filename = f"{sale.invoice_no}.pdf"
        template_path = 'sales/sales_print.html'

        # Using the new PDF generation machine
        return generate_pdf(template_path, context, filename)

    # PRINT ACTION
    if action == 'print':
        return render(request, 'sales/sales_print.html', {'sale': sale})

    # VIEW ACTION (Default)
    return render(request, 'sales/sales_view.html', {'sale': sale})



# ---------------- SALES RETURN CREATE (EDITED) ----------------
@transaction.atomic
def sales_return_create(request, pk):
    sale = get_object_or_404(SalesMaster, pk=pk)
    items = sale.items.all()

    if request.method == 'POST':
        product_ids = request.POST.getlist('product_id[]')
        return_qtys = request.POST.getlist('return_qty[]')
        rates = request.POST.getlist('rate[]')

        with transaction.atomic():
            res = SalesReturn.objects.create(sale=sale, total_return_amount=0)
            total_ret_amt = 0

            for i in range(len(product_ids)):
                qty_ret = Decimal(return_qtys[i]) if return_qtys[i] else Decimal('0')

                if qty_ret > 0:
                    prod = Product.objects.get(id=product_ids[i])
                    rate = Decimal(rates[i])
                    line_total = qty_ret * rate

                    # 1. Return Record Create
                    SalesReturnItem.objects.create(
                        sales_return=res, product=prod,
                        qty_returned=qty_ret, rate=rate, total=line_total
                    )

                    # 2. BATCH ADJUSTMENT (FIFO logic for returning to batches)
                    item_batches = SalesItemBatch.objects.filter(
                        sales_item__sales=sale,
                        sales_item__product=prod
                    ).order_by('-id')

                    remaining_to_restock = qty_ret
                    for ib in item_batches:
                        if remaining_to_restock <= 0: break

                        current_batch_qty = ib.qty
                        restore_qty = min(current_batch_qty, remaining_to_restock)

                        # A. Detailed Stock-ilekku (PurchaseItem) stock thirichu idunnu
                        pi = ib.purchase_item
                        pi.quantity_at_hand += restore_qty
                        pi.save()

                        # B. Sales Batch Record-ile qty & profit update cheyyunnu 🔥
                        ib.qty -= restore_qty
                        # 🔥 Ithaanu puthiya line: Qty kurayumbol profit-um recalculate cheyyanam
                        ib.profit = (ib.selling_rate - ib.purchase_rate) * ib.qty
                        ib.save()

                        remaining_to_restock -= restore_qty

                    # 3. Global Stock Update
                    stock_obj = Stock.objects.filter(product=prod).first()
                    if stock_obj:
                        stock_obj.quantity += qty_ret
                        stock_obj.save()

                    total_ret_amt += line_total

            res.total_return_amount = total_ret_amt
            res.save()
            return redirect('sales_return')

    return render(request, 'sales/sales_return_form.html', {'sale': sale, 'items': items})


def sales_profit(request):
    now = datetime.now()
    month = int(request.GET.get('month', now.month))
    year = int(request.GET.get('year', now.year))

    sales = SalesMaster.objects.filter(date__month=month, date__year=year).order_by('-id')

    sales_data = []
    total_monthly_profit = Decimal('0')

    for sale in sales:
        # Sum profit from batches (already saved as GST inclusive)
        invoice_profit = SalesItemBatch.objects.filter(
            sales_item__sales=sale
        ).aggregate(total=Sum('profit'))['total'] or Decimal('0')

        # Add service and material charges
        invoice_profit += (sale.service_charge + sale.material_charge)
        total_monthly_profit += invoice_profit

        sales_data.append({
            'sale': sale,
            'profit': invoice_profit,
            'has_return': sale.returns.exists()
        })

    months = [(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]
    years = range(2024, 2031)

    return render(request, 'sales/sales_profit.html', {
        'sales_data': sales_data,
        'total_monthly_profit': total_monthly_profit,
        'month': month, 'year': year, 'months': months, 'years': years,
    })