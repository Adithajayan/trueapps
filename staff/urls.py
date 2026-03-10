from django.urls import path
from . import views

urlpatterns = [
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.staff_add, name='staff_add'),
    path('staff/edit/<int:pk>/', views.staff_edit, name='staff_edit'),
    path('staff/delete/<int:id>/', views.staff_delete, name='staff_delete'),
]
