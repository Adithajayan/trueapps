from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('sales/', views.sales_report, name='sales_report'),
    path('sales/pdf/', views.sales_report_pdf, name='sales_report_pdf'),
    path('low-stock/', views.low_stock_report, name='low_stock_report'),
    path('purchase/', views.purchase_report, name='purchase_report'),
    path('purchase/pdf/', views.purchase_report_pdf, name='purchase_report_pdf'),
    path('profit-loss/', views.profit_loss_report, name='profit_loss_report'),
    path('profit-loss/pdf/',views.profit_loss_pdf,name='profit_loss_pdf'),
    path('export-all-excel/', views.export_all_excel, name='export_all_excel'),

]
