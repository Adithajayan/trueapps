from django.shortcuts import render, redirect, get_object_or_404
from .models import Staff
from django.contrib.auth.decorators import login_required

# STAFF LIST


@login_required
def staff_list(request):
    staffs = Staff.objects.all()
    return render(request, 'staff/staff_list.html', {'staffs': staffs})


# =========================
# STAFF ADD
# =========================
from decimal import Decimal


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Staff


@login_required
def staff_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        designation = request.POST.get('designation')
        address = request.POST.get('address')
        daily_salary_raw = request.POST.get('daily_salary')
        daily_salary = Decimal(daily_salary_raw) if daily_salary_raw else Decimal('0.00')

        # Login credentials from form
        username = request.POST.get('username')
        password = request.POST.get('password')

        # ✅ SAFE STATUS LOGIC
        status = True if request.POST.get('status') else False

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another one.")
            return render(request, 'staff/staff_add.html')

        try:
            # 1. Create User for login
            new_user = User.objects.create_user(username=username, password=password)

            # 2. Link User to Staff model
            Staff.objects.create(
                user=new_user,
                name=name,
                designation=designation,
                address=address,
                daily_salary=daily_salary,
                status=status
            )

            messages.success(request, f"Staff {name} added successfully.")
            return redirect('staff_list')

        except Exception as e:
            messages.error(request, f"Error occurred: {e}")

    return render(request, 'staff/staff_add.html')





# STAFF EDIT
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from decimal import Decimal
from .models import Staff


@login_required
def staff_edit(request, pk):
    staff = get_object_or_404(Staff, pk=pk)

    if request.method == 'POST':
        # Basic Details
        staff.name = request.POST.get('name')
        staff.designation = request.POST.get('designation')
        staff.address = request.POST.get('address')
        staff.daily_salary = Decimal(request.POST.get('daily_salary'))
        staff.status = request.POST.get('status') == 'on'

        # Login Update Logic
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')

        if new_username:
            if staff.user:
                # Update existing user
                u = staff.user
                u.username = new_username
                if new_password:  # Password undo enkil mathram update cheyyuka
                    u.set_password(new_password)
                u.save()
            else:
                # Create new user for old staff
                if User.objects.filter(username=new_username).exists():
                    messages.error(request, "Username already taken!")
                    return render(request, 'staff/staff_edit.html', {'staff': staff})

                new_user = User.objects.create_user(username=new_username, password=new_password)
                staff.user = new_user

        staff.save()
        messages.success(request, "Staff updated successfully.")
        return redirect('staff_list')

    return render(request, 'staff/staff_edit.html', {'staff': staff})


@login_required
def staff_delete(request, id):
    staff = get_object_or_404(Staff, id=id)

    if request.method == 'POST':
        if staff.user:
            staff.user.delete()
        staff.delete()

        return redirect('staff_list')

    return render(request, 'staff/staff_delete.html', {'staff': staff})

