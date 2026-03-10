from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from django.db.models import Q


def product_list(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(product_code__icontains=query) |
            Q(hsn_code__icontains=query)
        )

    return render(request, 'product/product_list.html', {
        'products': products,
        'query': query
    })


from django.contrib import messages

def product_add(request):
    if request.method == 'POST':

        hsn_code = request.POST.get('hsn_code')
        name = request.POST.get('name')

        # ✅ DUPLICATE CHECK
        if Product.objects.filter(name=name, hsn_code=hsn_code).exists():
            messages.error(request, "⚠ This product already exists.")
            return redirect('product_add')

        Product.objects.create(
            hsn_code=hsn_code,
            name=name,
            description=request.POST.get('description'),
            purchase_rate=request.POST.get('purchase_rate', 0),
            sales_rate=request.POST.get('sales_rate', 0),
            mrp=request.POST.get('mrp', 0),
            discount=request.POST.get('discount', 0),
            cgst=request.POST.get('cgst', 0),
            sgst=request.POST.get('sgst', 0),
            unit=request.POST.get('unit'),
            image=request.FILES.get('image')
        )

        messages.success(request, "✅ Product added successfully.")
        return redirect('product_list')

    return render(request, 'product/product_form.html')


def product_edit(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        product.hsn_code = request.POST.get('hsn_code')
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.purchase_rate = request.POST.get('purchase_rate')
        product.sales_rate = request.POST.get('sales_rate')
        product.mrp = request.POST.get('mrp')
        product.discount = request.POST.get('discount', 0)
        product.cgst = request.POST.get('cgst', 0)
        product.sgst = request.POST.get('sgst', 0)
        product.unit = request.POST.get('unit')

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()
        return redirect('product_list')

    return render(request, 'product/product_form.html', {'product': product})



def product_delete(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.delete()
        return redirect('product_list')

    return render(request, 'product/product_delete.html', {
        'product': product
    })

