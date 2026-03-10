from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.sales_create, name='sales_create'),

    # SEARCH
    path('customer-search/', views.customer_search, name='customer_search'),
    path('product-search/', views.product_search, name='product_search'),

    # PREFIX UPDATE
    path('update-prefix/', views.update_invoice_prefix, name='update_invoice_prefix'),

    path('list/', views.sales_list, name='sales_list'),
    path('profit/', views.sales_profit, name='sales_profit'),
    path('return/', views.sales_return, name='sales_return'),

    path('delete/<int:pk>/', views.sales_delete, name='sales_delete'),
    # path('print/<int:pk>/', views.sales_print, name='sales_print'),

    # path('view/<int:pk>/', views.sales_view, name='sales_view'),
    path('edit/<int:pk>/', views.sales_edit, name='sales_edit'),
    path('settings/', views.invoice_settings, name='invoice_settings'),
    path('product-search-api/', views.product_search_api, name='product_search_api'),
    path('delete-confirm/<int:pk>/', views.sales_delete_confirm, name='sales_delete_confirm'),
    path('profit-update/<int:pk>/', views.profit_update, name='profit_update'),
    path('return-create/<int:pk>/', views.sales_return_create, name='sales_return_create'),
    path('return-view/<int:pk>/', views.sales_return_view, name='sales_return_view'),
    path('return/', views.sales_return, name='sales_return'),
    path('product-batch-info/<int:product_id>/',views.product_batch_info,name='product_batch_info'),
    # path('download/<int:pk>/', views.sales_download_pdf, name='sales_download_pdf'),
    path('sales/invoice/<int:pk>/<str:action>/', views.manage_sales_invoice, name='sales_invoice'),



]
