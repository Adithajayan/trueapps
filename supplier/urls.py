from django.urls import path
from . import views

urlpatterns = [
    path("", views.supplier_list, name="supplier_list"),
    path("purchases/<int:supplier_id>/", views.purchase_list, name="purchase_list"),
    path("purchases/add/<int:supplier_id>/", views.purchase_add, name="purchase_add"),
    path("payments/<int:purchase_id>/", views.payment_list, name="supplier_payment_list"),
    path("payments/add/<int:purchase_id>/", views.payment_add, name="supplier_payment_add"),
    path('add/', views.supplier_add, name='supplier_add'),

]
