from django.urls import path

from . import views

app_name = "config"

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('empresas/', views.empresas, name='empresas'),
]