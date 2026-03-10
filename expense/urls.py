from django.urls import path
from . import views

urlpatterns = [

    # HOME
    path('', views.expense_home, name='expense_home'),

    # EXPENSE TYPE
    path('type/add/', views.expense_type_add, name='expense_type_add'),
    path('type/edit/<int:pk>/', views.expense_type_edit, name='expense_type_edit'),
    path('type/delete/<int:pk>/', views.expense_type_delete, name='expense_type_delete'),

    # CATEGORY
    path('type/<int:type_id>/categories/', views.expense_category_grid, name='expense_category_grid'),
    path('type/<int:type_id>/category/add/', views.expense_category_add, name='expense_category_add'),
    path('category/edit/<int:pk>/', views.expense_category_edit, name='expense_category_edit'),
    path('category/delete/<int:pk>/',views.expense_category_delete,name='expense_category_delete'),


    # EXPENSE CRUD
    path('type/<int:type_id>/add-expense/', views.expense_add, name='expense_add'),
    path('edit/<int:pk>/', views.expense_edit, name='expense_edit'),
    path('delete/<int:pk>/', views.expense_delete, name='expense_delete'),

    # TYPE WISE LIST (ONLY LIST WE USE)
    path('type/<int:type_id>/list/', views.expense_type_list, name='expense_type_list'),

    # PARTNERS
    path('partners/', views.partner_list, name='partner_list'),
    path('partners/add/', views.partner_add, name='partner_add'),
    path('partners/edit/<int:pk>/', views.partner_edit, name='partner_edit'),
    path('partners/delete/<int:pk>/', views.partner_delete, name='partner_delete'),
    # SUMMARY PAGES
    path('summary/', views.expense_summary, name='expense_summary'),
    path('summary/pdf/', views.expense_summary_pdf, name='expense_summary_pdf'),






]
