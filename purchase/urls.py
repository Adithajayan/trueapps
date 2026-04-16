from django.urls import path
from . import views

urlpatterns = [
    path('', views.purchase_list, name='purchase_list'),
    path('add/', views.purchase_add, name='purchase_add'),
    path('edit/<int:pk>/', views.purchase_edit, name='purchase_edit'),
    path('delete/<int:pk>/', views.purchase_delete, name='purchase_delete'),

    # SAME TEMPLATE
    path('view/<int:pk>/', views.purchase_invoice_print, name='purchase_view'),
    path('print/<int:pk>/', views.purchase_invoice_print, name='purchase_print'),
    path('pdf/<int:pk>/', views.purchase_invoice_pdf, name='purchase_pdf'),

    path('invoice-settings/', views.invoice_settings, name='invoice_settings'),
    path('returns/', views.purchase_return_list, name='purchase_return_list'),
    path('returns/add/<int:purchase_id>/', views.purchase_return_add, name='purchase_return_add'),
    path('check-supplier-invoice/', views.check_supplier_invoice, name='check_supplier_invoice'),
]

