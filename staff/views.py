from django.shortcuts import render, redirect, get_object_or_404
from .models import Staff
from django.contrib.auth.decorators import login_required

# STAFF LIST
@login_required
def staff_list(request):
    staffs = Staff.objects.all()
    return render(request, 'staff/staff_list.html', {'staffs': staffs})


from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Staff


# =========================
# STAFF ADD
# =========================
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Staff

@login_required
def staff_add(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        designation = request.POST.get('designation')
        address = request.POST.get('address')
        daily_salary = request.POST.get('daily_salary')

        # ✅ SAFE STATUS LOGIC
        status = True if request.POST.get('status') else False

        Staff.objects.create(
            name=name,
            designation=designation,
            address=address,
            daily_salary=daily_salary,
            status=status
        )

        return redirect('staff_list')

    return render(request, 'staff/staff_add.html')





# STAFF EDIT
@login_required
def staff_edit(request, pk):

    staff = get_object_or_404(Staff, pk=pk)

    if request.method == 'POST':

        staff.name = request.POST.get('name')
        staff.designation = request.POST.get('designation')
        staff.address = request.POST.get('address')

        staff.daily_salary = Decimal(
            request.POST.get('daily_salary')
        )

        staff.status = request.POST.get('status') == 'on'

        staff.save()

        return redirect('staff_list')

    return render(request, 'staff/staff_edit.html', {
        'staff': staff
    })

    return render(request, 'staff/staff_edit.html', {'staff': staff})


@login_required
def staff_delete(request, id):
    staff = get_object_or_404(Staff, id=id)

    if request.method == 'POST':
        staff.delete()
        return redirect('staff_list')

    return render(request, 'staff/staff_delete.html', {'staff': staff})

