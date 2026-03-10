from django.urls import path
from . import views

urlpatterns = [
    path('', views.manual_backup, name='manual_backup'),
]