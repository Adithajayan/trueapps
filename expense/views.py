from django.shortcuts import render, redirect, get_object_or_404
from .models import ExpenseType, ExpenseCategory




def expense_home(request):
    expense_types = ExpenseType.objects.filter(is_active=True)
    return render(request, 'expense/expense_home.html', {
        'expense_types': expense_types
    })

def expense_type_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            ExpenseType.objects.create(name=name)
        return redirect('expense_home')

    return render(request, 'expense/expense_type_form.html', {
        'title': 'Add Expense Type'
    })

def expense_type_edit(request, pk):
    expense_type = get_object_or_404(ExpenseType, pk=pk)

    if request.method == 'POST':
        expense_type.name = request.POST.get('name')
        expense_type.save()
        return redirect('expense_home')

    return render(request, 'expense/expense_type_form.html', {
        'title': 'Edit Expense Type',
        'expense_type': expense_type
    })


def expense_type_delete(request, pk):
    expense_type = get_object_or_404(ExpenseType, pk=pk)
    expense_type.is_active = False   # soft delete
    expense_type.save()
    return redirect('expense_home')


def expense_category_grid(request, type_id):
    expense_type = ExpenseType.objects.get(id=type_id)
    categories = ExpenseCategory.objects.filter(
        expense_type=expense_type,
        is_active=True
    )

    return render(request, 'expense/expense_category_grid.html', {
        'expense_type': expense_type,
        'categories': categories
    })


def expense_category_add(request, type_id):
    expense_type = get_object_or_404(ExpenseType, id=type_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            ExpenseCategory.objects.create(
                expense_type=expense_type,
                name=name
            )
        return redirect('expense_category_grid', type_id=type_id)

    return render(request, 'expense/expense_category_form.html', {
        'title': 'Add Category',
        'expense_type': expense_type
    })


def expense_category_edit(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)
    expense_type = category.expense_type

    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.save()
        return redirect('expense_category_grid', type_id=expense_type.id)

    return render(request, 'expense/expense_category_form.html', {
        'title': 'Edit Category',
        'category': category,
        'expense_type': expense_type
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import ExpenseType, ExpenseCategory, Expense, Partner


def expense_add(request, type_id):
    expense_type = get_object_or_404(ExpenseType, id=type_id)

    categories = ExpenseCategory.objects.filter(
        expense_type=expense_type,
        is_active=True
    )

    partners = Partner.objects.filter(is_active=True)

    if request.method == 'POST':
        Expense.objects.create(
            expense_type=expense_type,
            category_id=request.POST.get('category') or None,
            partner_id=request.POST.get('partner') or None,
            amount=request.POST.get('amount'),
            note=request.POST.get('note'),
            date=request.POST.get('date'),
            status=request.POST.get('status', 'PAID')
        )

        # 🔥 IMPORTANT FIX
        return redirect('expense_type_list', expense_type.id)

    return render(request, 'expense/expense_add.html', {
        'expense_type': expense_type,
        'categories': categories,
        'partners': partners,
        'today': timezone.now().date()
    })



from django.shortcuts import render, redirect, get_object_or_404
from .models import Partner


def partner_list(request):
    partners = Partner.objects.filter(is_active=True)
    return render(request, 'expense/partner_list.html', {
        'partners': partners
    })
def partner_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Partner.objects.create(name=name)
        return redirect('partner_list')

    return render(request, 'expense/partner_form.html', {
        'title': 'Add Partner'
    })

def partner_edit(request, pk):
    partner = get_object_or_404(Partner, pk=pk)

    if request.method == 'POST':
        partner.name = request.POST.get('name')
        partner.save()
        return redirect('partner_list')

    return render(request, 'expense/partner_form.html', {
        'title': 'Edit Partner',
        'partner': partner
    })

def partner_delete(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    partner.is_active = False
    partner.save()
    return redirect('partner_list')


from .models import Expense

def expense_list(request):
    expenses = Expense.objects.select_related(
        'expense_type',
        'category',
        'partner'
    ).order_by('-date')

    context = {
        'expenses': expenses
    }
    return render(request, 'expense/expense_list.html', context)


def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)

    categories = ExpenseCategory.objects.filter(
        expense_type=expense.expense_type,
        is_active=True
    )
    partners = Partner.objects.filter(is_active=True)

    if request.method == 'POST':
        expense.date = request.POST.get('date')
        expense.amount = request.POST.get('amount')
        expense.status = request.POST.get('status')
        expense.note = request.POST.get('note')

        category_id = request.POST.get('category')
        partner_id = request.POST.get('partner')

        expense.category = ExpenseCategory.objects.get(id=category_id) if category_id else None
        expense.partner = Partner.objects.get(id=partner_id) if partner_id else None

        expense.save()

        # 🔥 IMPORTANT FIX
        return redirect('expense_type_list', expense.expense_type.id)

    context = {
        'expense': expense,
        'categories': categories,
        'partners': partners,
    }
    return render(request, 'expense/expense_edit.html', context)


def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense_type_id = expense.expense_type.id
    expense.delete()

    return redirect('expense_type_list', expense_type_id)



from django.shortcuts import render, get_object_or_404
from .models import Expense, ExpenseType

from django.db.models import Sum

def expense_type_list(request, type_id):
    expense_type = get_object_or_404(ExpenseType, id=type_id)

    expenses = Expense.objects.filter(
        expense_type=expense_type
    ).order_by('-date')

    # FILTER VALUES
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    partner_id = request.GET.get('partner')

    # DATE FILTER
    if from_date and to_date:
        expenses = expenses.filter(date__range=[from_date, to_date])

    # PARTNER FILTER
    if partner_id:
        expenses = expenses.filter(partner_id=partner_id)

    # TOTAL SUM
    total_amount = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0

    partners = Partner.objects.filter(is_active=True)

    context = {
        'expense_type': expense_type,
        'expenses': expenses,
        'partners': partners,
        'from_date': from_date,
        'to_date': to_date,
        'selected_partner': partner_id,
        'total_amount': total_amount,
    }
    return render(request, 'expense/expense_type_list.html', context)


from django.db.models import Sum
from .models import Expense, ExpenseType

from django.db.models import Sum
import json

import json
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from .models import Expense, ExpenseType


# views.py

import json
from django.db.models import Sum
from .models import Expense, ExpenseType

import json
from decimal import Decimal
from django.db.models import Sum
from .models import Expense, ExpenseType

def expense_summary(request):

    expense_types = ExpenseType.objects.filter(is_active=True)

    expenses = (
        Expense.objects
        .select_related('expense_type', 'category', 'partner')
        .filter(expense_type__is_active=True)
        .order_by('-date')
    )

    type_id = request.GET.get('type')
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')

    selected_type = "All Expenses"

    if type_id and type_id != 'all':
        expenses = expenses.filter(expense_type_id=type_id)
        selected_type = ExpenseType.objects.get(
            id=type_id, is_active=True
        ).name

    if from_date:
        expenses = expenses.filter(date__gte=from_date)

    if to_date:
        expenses = expenses.filter(date__lte=to_date)

    total_amount = expenses.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')

    # =====================
    # CATEGORY SUMMARY
    # =====================
    raw_summary = (
        expenses
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    category_summary = []
    chart_labels = []
    chart_values = []

    for row in raw_summary:
        category = row['category__name'] or 'Others'
        total = row['total'] or Decimal('0')

        percentage = (
            (total / total_amount * Decimal('100')).quantize(Decimal('0.1'))
            if total_amount else Decimal('0.0')
        )

        category_summary.append({
            'category__name': category,
            'total': total,
            'percentage': percentage
        })

        chart_labels.append(category)
        chart_values.append(float(total))  # chart.js needs float

    context = {
        'expenses': expenses,
        'expense_types': expense_types,
        'total_amount': total_amount,
        'selected_type': selected_type,
        'category_summary': category_summary,
        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),
    }

    return render(request, 'expense/expense_summary.html', context)







# views.py




from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Sum
from django.utils.text import slugify
from config.utils.pdf import generate_pdf

def expense_summary_pdf(request):

    expenses = (
        Expense.objects
        .select_related('expense_type', 'category', 'partner')
        .filter(expense_type__is_active=True)
        .order_by('-date')
    )

    type_id = request.GET.get('type')
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')

    selected_type = "All Expenses"

    if type_id and type_id != 'all':
        expenses = expenses.filter(expense_type_id=type_id)
        selected_type = ExpenseType.objects.get(
            id=type_id, is_active=True
        ).name

    if from_date:
        expenses = expenses.filter(date__gte=from_date)

    if to_date:
        expenses = expenses.filter(date__lte=to_date)

    total_amount = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # CATEGORY SUMMARY
    raw_summary = (
        expenses
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    category_summary = []
    for row in raw_summary:
        category = row['category__name'] or 'Others'
        total = row['total']
        percentage = round((total / total_amount) * 100, 1) if total_amount else 0

        category_summary.append({
            'category': category,
            'total': total,
            'percentage': percentage
        })




        context = {
            'total_amount': total_amount,
            'selected_type': selected_type,
            'from_date': from_date,
            'to_date': to_date,
            'category_summary': category_summary,
            'expenses': expenses,
        }


        final_filename = f"{slugify(selected_type)}_summary.pdf"


        return generate_pdf('expense/expense_summary_pdf.html', context, final_filename)



from django.shortcuts import get_object_or_404, redirect

def expense_category_delete(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)

    category.is_active = False   # 🔥 soft delete
    category.save()

    return redirect(
        'expense_category_grid',
        type_id=category.expense_type.id
    )

