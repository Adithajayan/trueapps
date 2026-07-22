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
        gst_number = request.POST.get("gst_number")

        # 🔥 DUPLICATE NAME CHECK (case-insensitive)
        if Customer.objects.filter(name__iexact=name).exists():
            messages.error(
                request,
                f"Customer '{name}' already exists. Please add a second name."
            )
            return render(request, "customer/customer_add.html", {
                "name": name,
                "phone": phone,
                "place": place,
                "gst_number": gst_number
            })

        Customer.objects.create(
            name=name,
            phone=phone,
            place=place,
            gst_number=gst_number
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
        gst_number = request.POST.get("gst_number")

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
        customer.gst_number = gst_number
        customer.save()

        messages.success(request, "Customer updated successfully")
        return redirect("customers_list")

    return render(request, "customer/customer_add.html", {
        "customer": customer
    })



# -------------------------
# DELETE CUSTOMER
# -------------------------
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Customer


def customer_delete(request, pk):
    customer = get_object_or_404(Customer, id=pk)

    if request.method == "POST":
        # 1. Ee customer-kku sales undonnu check cheyyunnu
        if customer.salesmaster_set.exists():
            messages.error(request,
                           f"Cannot delete '{customer.name}' because sales records are linked with this customer. Please delete related sales first.")

            # 🛑 IMPORTANT CHANGE: Redirect-nu pakaram same delete page-ilekku render cheyyuka
            return render(request, 'customer/customer_delete.html', {
                'customer': customer
            })

        # Sales illengil mathram customer-ne delete cheyyuka
        customer.delete()
        messages.success(request, "Customer deleted successfully!")
        return redirect('customers_list')

    return render(request, 'customer/customer_delete.html', {
        'customer': customer
    })


