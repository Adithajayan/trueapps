from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_list, name='customers_list'),
    path('add/', views.customer_add, name='customers_add'),
    path('edit/<int:pk>/', views.customer_edit, name='customers_edit'),
    path('delete/<int:pk>/', views.customer_delete, name='customers_delete'),
]

