from django.urls import path
from . import views

urlpatterns = [

    path('enquiry/add/', views.add_enquiry, name='add_enquiry'),
    path('maintenance/add/', views.add_maintenance, name='add_maintenance'),
    path('service/add/', views.add_service, name='add_service'),
    path('enquiry/delete/<int:id>/', views.delete_enquiry, name='delete_enquiry'),

    path('enquiry/list/', views.enquiry_list, name='enquiry_list'),
    path('maintenance/list/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/delete/<int:id>/',views.delete_maintenance,name='delete_maintenance'),
    path('maintenance/edit/<int:id>/',views.edit_maintenance,name='edit_maintenance'),
    path('maintenance/view/<int:id>/',views.view_maintenance,name='view_maintenance'),

    path('service/list/', views.service_list, name='service_list'),
    path('service/view/<int:id>/', views.view_service, name='view_service'),
    path('service/edit/<int:id>/', views.edit_service, name='edit_service'),
    path('service/delete/<int:id>/', views.delete_service, name='delete_service'),

    path('complete/<int:id>/', views.mark_completed, name='mark_completed'),
    path('', views.job_dashboard, name='job_dashboard'),
    path('toggle-status/<int:id>/', views.toggle_status, name='toggle_status'),
    path('edit/<int:id>/', views.edit_job, name='edit_job'),
    path('reminders/', views.reminder_list, name='reminders'),
    path('reminders/today/', views.today_reminders, name='today_reminders'),
    path('reminder/add/', views.add_reminder, name='add_reminder'),
    path('reminder/complete/<int:id>/', views.complete_reminder, name='complete_reminder'),
    path('reminder/edit/<int:id>/', views.edit_reminder, name='edit_reminder'),
    path('reminder/delete/<int:id>/', views.delete_reminder, name='delete_reminder'),
    path('reminder/toggle/<int:id>/', views.toggle_reminder_status,name='toggle_reminder_status'),




]
