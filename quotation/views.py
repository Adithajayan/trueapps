import json
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum

from .models import (
    Quotation,
    QuotationItem,
    QuotationTemplate,
    QuotationTemplateItem
)

from product.models import Product
from customer.models import Customer


# =====================================================
# CREATE QUOTATION
# =====================================================

import json
from datetime import date
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Customer, Product, Quotation, QuotationItem, QuotationTemplate

import json
from datetime import date
from django.shortcuts import render, redirect
from .models import Customer, Product, Quotation, QuotationItem, QuotationTemplate

def quotation_add(request):
    customers = Customer.objects.all().order_by('name')
    templates = QuotationTemplate.objects.all()
    products = Product.objects.all().order_by('name')

    if request.method == "POST":
        customer_id = request.POST.get("customer")
        quotation_date = request.POST.get("quotation_date")

        if not customer_id:
            return redirect("quotation_add")

        quotation = Quotation.objects.create(
            customer_id=customer_id,
            quotation_date=quotation_date
        )

        product_ids = request.POST.getlist("product[]")
        qtys = request.POST.getlist("qty[]")
        rates = request.POST.getlist("rate[]")
        totals = request.POST.getlist("total[]")

        total_amount = 0
        total_profit = 0

        for pid, qty, rate, total in zip(product_ids, qtys, rates, totals):
            if not pid or not qty: continue

            product = Product.objects.get(id=pid)
            cost_rate = float(product.purchase_rate or 0)
            selling_rate = float(rate or 0)
            quantity = float(qty or 0)
            item_total = float(total or 0)

            profit = (selling_rate - cost_rate) * quantity

            QuotationItem.objects.create(
                quotation=quotation,
                product=product,
                quantity=quantity,
                selling_rate=selling_rate,
                cost_rate=cost_rate,
                total_price=item_total,
                profit=profit
            )
            total_amount += item_total
            total_profit += profit

        advance = float(request.POST.get("advance_amount") or 0)
        quotation.total_amount = total_amount
        quotation.advance_amount = advance
        quotation.balance_amount = total_amount - advance
        quotation.total_profit = total_profit
        quotation.save()

        return redirect("quotation_list")

    return render(request, "quotation/quotation_add.html", {
        "customers": customers,
        "templates": templates,
        "products": products,
        "today": date.today().strftime('%Y-%m-%d')
    })



# =====================================================
# LOAD TEMPLATE ITEMS (AJAX)
# =====================================================

def load_template_items(request):
    template_id = request.GET.get("template_id")
    items = QuotationTemplateItem.objects.filter(template_id=template_id)
    data = []
    for item in items:
        data.append({
            "product_id": item.product.id,
            "product_name": item.product.name,  # Template load cheyyan ithu nirbandham aanu
            "qty": float(item.default_qty),
            "rate": float(item.product.sales_rate)
        })
    return JsonResponse(data, safe=False)


# =====================================================
# QUOTATION LIST
# =====================================================

from datetime import datetime

def quotation_list(request):

    quotations = Quotation.objects.all().order_by("-id")

    selected_month = request.GET.get("month")

    if selected_month:
        year, month = selected_month.split("-")

        quotations = quotations.filter(
            quotation_date__year=year,
            quotation_date__month=month
        )

    return render(request, "quotation/quotation_list.html", {
        "quotations": quotations,
        "selected_month": selected_month
    })



from .utils.pdf import generate_pdf


def quotation_pdf(request, pk):
    quotation = get_object_or_404(Quotation, id=pk)
    items = quotation.items.all()


    context = {
        "quotation": quotation,
        "items": items,
        "logo": request.build_absolute_uri("/static/company/logo.png")
    }


    filename = f"quotation_{quotation.id}.pdf"


    template_path = "quotation/quotation_pdf.html"


    return generate_pdf(template_path, context, filename)







from .utils.pdf import generate_pdf


def quotation_pdf_view(request, pk):


    quotation = get_object_or_404(Quotation, id=pk)
    items = quotation.items.all()


    heading = ""
    if items.exists():
        heading = items.first().product.name


    logo_url = request.build_absolute_uri(settings.STATIC_URL + "company/logo.jpeg")

    # ✅ ഡാറ്റാ പാക്കറ്റ് (Context)
    context = {
        "quotation": quotation,
        "items": items,
        "heading": heading,
        "logo": logo_url,
    }


    filename = f"quotation_{pk}.pdf"


    template_path = "quotation/quotation_pdf.html"

    return generate_pdf(template_path, context, filename)

def quotation_pdf_download(request, pk):

    quotation = get_object_or_404(Quotation, id=pk)
    items = quotation.items.all()

    # ✅ HEADING LOGIC (UNCHANGED)
    heading = ""
    if items.exists():
        heading = items.first().product.name

    # ✅ LOGO ABSOLUTE PATH
    logo_path = os.path.join(settings.BASE_DIR, "static", "company", "logo.jpeg")
    logo_url = f"file:///{logo_path.replace(os.sep, '/')}"

    # ✅ HTML RENDER
    html_string = render_to_string(
        "quotation/quotation_pdf.html",
        {
            "quotation": quotation,
            "items": items,
            "heading": heading,
            "logo": logo_url,
        }
    )

    pdf = HTML(string=html_string).write_pdf()

    # ✅ SAFE CUSTOMER NAME
    customer_name = quotation.customer.name
    safe_name = re.sub(r'[^A-Za-z0-9]+', '_', customer_name).strip('_')

    filename = f"{safe_name}_Quotation.pdf"

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response




# =====================================================
# QUOTATION PROFIT
# =====================================================





# =====================================================
# TEMPLATE LIST
# =====================================================

# =====================================================
# TEMPLATE LIST (Views)
# =====================================================
def template_list(request):
    templates = QuotationTemplate.objects.all()
    return render(request, "quotation/template_list.html", {"templates": templates})


# =====================================================
# TEMPLATE EDIT (Puthiya View)
# =====================================================
#
def template_edit(request, pk):
    template = get_object_or_404(QuotationTemplate, id=pk)
    if request.method == "POST":
        template.name = request.POST.get("name")
        template.save()
        return redirect('template_list')
    return render(request, "quotation/template_add.html", {"template": template}) # Same add page use cheyyam

# Template Delete cheyyan
def template_delete(request, pk):
    template = get_object_or_404(QuotationTemplate, id=pk)

    # POST request aanel maathram delete nadathuka
    if request.method == "POST":
        template.delete()
        return redirect('template_list')

    # GET request aayittaanu varunnathenkil confirmation HTML page kaanikkuka
    return render(request, "quotation/template_confirm_delete.html", {"template": template})


# ITEM DELETE CONFIRMATION PAGE
def template_item_delete(request, item_id):
    item = get_object_or_404(QuotationTemplateItem, id=item_id)
    if request.method == "POST":
        template_id = item.template.id
        item.delete()
        return redirect('template_items', template_id=template_id)

    # Browser alert-inu pakaram ee HTML render cheyyum
    return render(request, "quotation/template_item_confirm_delete.html", {"item": item})


# ITEM EDIT (INLINE UPDATE)
def template_item_edit(request, item_id):
    item = get_object_or_404(QuotationTemplateItem, id=item_id)

    if request.method == "POST":
        item.default_qty = request.POST.get('qty')
        item.save()
        return redirect('template_items', item.template.id)

    # GET request aanel edit page render cheyyunnu
    return render(request, "quotation/template_item_edit.html", {"item": item})


# =====================================================
# TEMPLATE ADD
# =====================================================

def template_add(request):

    if request.method == "POST":
        name = request.POST.get("name")
        template = QuotationTemplate.objects.create(name=name)
        return redirect("template_items", template.id)

    return render(request, "quotation/template_add.html")


# =====================================================
# TEMPLATE ITEMS
# =====================================================

def template_items(request, template_id):

    template = get_object_or_404(QuotationTemplate, id=template_id)
    products = Product.objects.all()
    items = template.items.all()

    if request.method == "POST":

        product_id = request.POST.get("product")
        qty = request.POST.get("qty")

        QuotationTemplateItem.objects.create(
            template=template,
            product_id=product_id,
            default_qty=qty
        )

        return redirect("template_items", template_id)

    return render(request, "quotation/template_items.html", {
        "template": template,
        "products": products,
        "items": items
    })


# =====================================================
# PRODUCT SEARCH
# =====================================================

from django.http import JsonResponse
from .models import Product

def product_search(request):

    q = request.GET.get("q") or request.GET.get("term") or ""


    products = Product.objects.filter(name__icontains=q).order_by('name')[:20]


    data = [
        {
            "id": p.id,
            "text": p.name,
            "price": float(p.sales_rate) if p.sales_rate else 0.0
        }
        for p in products
    ]

    return JsonResponse({"results": data})


# =====================================================
# CUSTOMER SEARCH
# =====================================================

from django.http import JsonResponse
from .models import Customer

def customer_search(request):
    # 'q' അല്ലെങ്കിൽ 'term' എടുക്കുന്നു
    query = request.GET.get("q") or request.GET.get("term") or ""

    # query ഉണ്ടെങ്കിൽ മാത്രം ഫിൽട്ടർ ചെയ്യുക, അല്ലെങ്കിൽ വെറുതെ ഒഴിഞ്ഞ ലിസ്റ്റ് നൽകുക
    if query:
        customers = Customer.objects.filter(name__icontains=query).order_by('name')[:20]
    else:
        # ആദ്യമേ കുറച്ച് കസ്റ്റമേഴ്സിനെ കാണിക്കണമെന്നുണ്ടെങ്കിൽ ഇത് മാറ്റാം
        customers = Customer.objects.all().order_by('name')[:10]

    # 'id', 'text' എന്നിവ കറക്റ്റ് ആയി മാപ്പ് ചെയ്യുന്നു
    data = [{"id": c.id, "text": c.name} for c in customers]

    return JsonResponse({"results": data})

def quotation_detail(request, pk):
    quotation = get_object_or_404(Quotation, id=pk)
    items = quotation.items.all()

    return render(request, "quotation/quotation_detail.html", {
        "quotation": quotation,
        "items": items
    })


def quotation_delete(request, pk):
    quotation = get_object_or_404(Quotation, id=pk)

    if request.method == "POST":
        quotation.delete()
        return redirect("quotation_list")

    return render(request, "quotation/quotation_delete.html", {
        "quotation": quotation
    })

def quotation_edit(request, pk):
    quotation = get_object_or_404(Quotation, id=pk)
    items = quotation.items.all()

    customers = Customer.objects.all()
    products = Product.objects.all()

    if request.method == "POST":

        quotation.customer_id = request.POST.get("customer")
        quotation.quotation_date = request.POST.get("quotation_date")

        quotation.items.all().delete()

        product_ids = request.POST.getlist("product[]")
        qtys = request.POST.getlist("qty[]")
        rates = request.POST.getlist("rate[]")
        totals = request.POST.getlist("total[]")

        total_amount = 0
        total_profit = 0

        for pid, qty, rate, total in zip(product_ids, qtys, rates, totals):

            product = Product.objects.get(id=pid)

            cost_rate = float(product.purchase_rate)
            selling_rate = float(rate)
            quantity = float(qty)
            item_total = float(total)

            profit = (selling_rate - cost_rate) * quantity

            QuotationItem.objects.create(
                quotation=quotation,
                product=product,
                quantity=quantity,
                selling_rate=selling_rate,
                cost_rate=cost_rate,
                total_price=item_total,
                profit=profit
            )

            total_amount += item_total
            total_profit += profit

        advance = float(request.POST.get("advance_amount") or 0)
        quotation.advance_amount = advance
        quotation.total_amount = total_amount
        quotation.balance_amount = total_amount - advance
        quotation.total_profit = total_profit
        quotation.save()

        return redirect("quotation_list")

    return render(request, "quotation/quotation_edit.html", {
        "quotation": quotation,
        "items": items,
        "customers": customers,
        "products": products
    })

import os
import re
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

import re
import os
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .utils.pdf import generate_pdf


def invoice_pdf_download(request, pk):

    quotation = get_object_or_404(Quotation, id=pk)
    items = quotation.items.all()


    logo_url = request.build_absolute_uri(settings.STATIC_URL + "company/logo.jpeg")


    context = {
        "quotation": quotation,
        "items": items,
        "logo": logo_url,
    }


    customer_name = quotation.customer.name
    safe_name = re.sub(r'[^A-Za-z0-9]+', '_', customer_name).strip('_')
    filename = f"{safe_name}_Invoice.pdf"

    template_path = "quotation/invoice_pdf.html"

    return generate_pdf(template_path, context, filename)





from django.shortcuts import redirect, get_object_or_404

def quotation_convert_invoice(request, pk):

    quotation = get_object_or_404(Quotation, id=pk)

    quotation.status = "INVOICE"
    quotation.save()

    return redirect("quotation_list")

