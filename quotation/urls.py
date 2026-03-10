from django.urls import path
from . import views

urlpatterns = [

    path("add/", views.quotation_add, name="quotation_add"),
    path("", views.quotation_list, name="quotation_list"),


    path("templates/", views.template_list, name="template_list"),
    path("templates/add/", views.template_add, name="template_add"),
    path("templates/items/<int:template_id>/", views.template_items, name="template_items"),

    path("load-template/", views.load_template_items, name="load_template_items"),

    path("product-search/", views.product_search, name="product_search"),
    path("customer-search/", views.customer_search, name="customer_search"),
    path("templates/edit/<int:pk>/", views.template_edit, name="template_edit"),
    path("templates/delete/<int:pk>/", views.template_delete, name="template_delete"),
    path("templates/item/delete/<int:item_id>/", views.template_item_delete, name="template_item_delete"),
    path("templates/item/edit/<int:item_id>/", views.template_item_edit, name="template_item_edit"),
    path("detail/<int:pk>/", views.quotation_detail, name="quotation_detail"),
    path("delete/<int:pk>/", views.quotation_delete, name="quotation_delete"),
    path("edit/<int:pk>/", views.quotation_edit, name="quotation_edit"),
    path("pdf/<int:pk>/", views.quotation_pdf, name="quotation_pdf"),
    path("pdf/view/<int:pk>/", views.quotation_pdf_view, name="quotation_pdf_view"),
    path("pdf/download/<int:pk>/", views.quotation_pdf_download, name="quotation_pdf_download"),
    path("convert-invoice/<int:pk>/",views.quotation_convert_invoice,name="quotation_convert_invoice"),
    path("invoice-download/<int:pk>/",views.invoice_pdf_download,name="invoice_pdf_download"),



]
