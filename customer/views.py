from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer


# -------------------------
# CUSTOMER LIST
# -------------------------
from django.shortcuts import render
from django.db.models import Q
from .models import Customer
from django.db import connection

def customer_list(request):

    query = request.GET.get('q', '').strip()

    if query:

        customers = Customer.objects.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(place__icontains=query)
        ).order_by('-id')
    else:
        customers = Customer.objects.order_by('-id')

    return render(request, 'customer/customer_list.html', {
        'customers': customers,
        'search_query': query
    })


# -------------------------
# ADD CUSTOMER
# -------------------------
from django.contrib import messages
from .models import Customer

def customer_add(request):

    if request.method == "POST":
        name = request.POST.get("name").strip()
        phone = request.POST.get("phone")
        place = request.POST.get("place")

        # 🔥 DUPLICATE NAME CHECK (case-insensitive)
        if Customer.objects.filter(name__iexact=name).exists():
            messages.error(
                request,
                f"Customer '{name}' already exists. Please add a second name."
            )
            return render(request, "customer/customer_add.html", {
                "name": name,
                "phone": phone,
                "place": place
            })

        Customer.objects.create(
            name=name,
            phone=phone,
            place=place
        )

        messages.success(request, "Customer added successfully")
        return redirect("customers_list")

    return render(request, "customer/customer_add.html")



# -------------------------
# EDIT CUSTOMER
# -------------------------
def customer_edit(request, pk):

    customer = get_object_or_404(Customer, id=pk)

    if request.method == "POST":
        name = request.POST.get("name").strip()
        phone = request.POST.get("phone")
        place = request.POST.get("place")

        # 🔥 Duplicate check except current customer
        if Customer.objects.filter(name__iexact=name).exclude(id=customer.id).exists():
            messages.error(
                request,
                f"Customer '{name}' already exists. Please use a different name."
            )
            return render(request, "customer/customer_add.html", {
                "customer": customer
            })

        customer.name = name
        customer.phone = phone
        customer.place = place
        customer.save()

        messages.success(request, "Customer updated successfully")
        return redirect("customers_list")

    return render(request, "customer/customer_add.html", {
        "customer": customer
    })



# -------------------------
# DELETE CUSTOMER
# -------------------------
def customer_delete(request, pk):

    customer = get_object_or_404(Customer, id=pk)

    if request.method == "POST":
        customer.delete()
        return redirect('customers_list')

    return render(request, 'customer/customer_delete.html', {
        'customer': customer
    })


