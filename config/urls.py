from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('accounts.urls')),
    path('', include('staff.urls')),
    path('', include('attendance.urls')),
    path('income/', include('income.urls')),
    path('product/', include('product.urls')),
    path('supplier/', include('supplier_master.urls')),
    path('purchase/', include('purchase.urls')),
    path('supplier-ledger/', include('supplier_ledger.urls')),
    path('stock/', include('stock.urls')),
    path('quotation/', include('quotation.urls')),
    path('customers/', include('customer.urls')),
    path('expense/', include('expense.urls')),
    path('sales/', include('sales.urls')),
    path('reports/', include('reports.urls')),
    path('jobs/', include('job_management.urls')),
    path('backup/', include('backup.urls')),


]

