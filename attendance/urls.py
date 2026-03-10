from django.urls import path
from . import views

urlpatterns = [
    path('attendance/', views.attendance_mark, name='attendance_mark'),
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
    path('attendance/summary/', views.attendance_summary, name='attendance_summary'),
    path('advance/add/', views.add_advance, name='add_advance'),
    # ADVANCE
    path('advance/', views.advance_list, name='advance_list'),
    path('advance/add/', views.advance_add, name='advance_add'),
    path('advance/edit/<int:id>/', views.advance_edit, name='advance_edit'),
    path('advance/delete/<int:id>/', views.advance_delete, name='advance_delete'),
    path('advance/', views.advance_list, name='advance_list'),
    path('salary/', views.salary_sheet, name='salary_sheet'),
    #salary total
    path('salary-total/', views.salary_total, name='salary_total'),
    path("salary-pdf/<int:staff_id>/",views.staff_salary_pdf,name="staff_salary_pdf"),
    path('salary-total-pdf/', views.export_salary_total_pdf, name='export_salary_total_pdf'),


]
