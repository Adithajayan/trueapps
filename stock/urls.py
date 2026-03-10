from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_list, name='stock_list'),

    # opening stock
    path('opening/add/', views.opening_stock_add, name='opening_stock_add'),
    path('opening/history/', views.opening_stock_history, name='opening_stock_history'),
    path('opening/edit/<int:pk>/', views.opening_stock_edit, name='opening_stock_edit'),
    path('opening/delete/<int:pk>/', views.opening_stock_delete, name='opening_stock_delete'),
    path('register/detailed/', views.detailed_stock_register, name='detailed_stock_register'),
    path('update-selling-rate/', views.update_selling_rate, name='update_selling_rate'),


]
