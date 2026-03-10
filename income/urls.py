from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_list, name='customer_list'),

    path('works/<int:customer_id>/', views.work_list, name='work_list'),
    path('works/add/<int:customer_id>/', views.work_add, name='work_add'),
    path('works/edit/<int:work_id>/', views.work_edit, name='work_edit'),
    path('works/delete/<int:work_id>/', views.work_delete, name='work_delete'),

    path('payments/<int:work_id>/', views.payment_list, name='payment_list'),
    path('payments/add/<int:work_id>/', views.payment_add, name='payment_add'),
    path("pending/pdf/", views.pending_pdf, name="pending_pdf"),
    path('payments/edit/<int:payment_id>/', views.payment_edit, name='payment_edit'),
    path('payments/delete/<int:payment_id>/', views.payment_delete, name='payment_delete'),
    path('customer/search/', views.customer_search, name='customer_search'),


]
