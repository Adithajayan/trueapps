from django.urls import path
from . import views

urlpatterns = [

    # MAIN DASHBOARD

    path('list/', views.supplier_ledger_summary, name='supplier_ledger_summary'),

    # DETAIL PAGE
    path('detail/<int:supplier_id>/', views.supplier_ledger_detail, name='supplier_ledger_detail'),

    # MANUAL ENTRY
    path('manual/add/', views.ledger_manual_add, name='ledger_manual_add'),

    # PAYMENT ENTRY
    path('payment/add/', views.ledger_payment_add, name='ledger_payment_add'),

    # DELETE
    path('delete/<int:pk>/', views.ledger_delete, name='ledger_delete'),

    #edit
    path('edit/<int:pk>/', views.ledger_edit, name='ledger_edit'),

    # PDF
    path('pdf/<int:supplier_id>/', views.supplier_ledger_pdf, name='supplier_ledger_pdf'),



    # OPTIONAL
    path('list/', views.supplier_ledger_list, name='supplier_ledger_list'),
    path('basic/add/', views.ledger_add, name='ledger_add'),
]
