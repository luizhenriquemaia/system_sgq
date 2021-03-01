from django.urls import path

from . import views

app_name = "config"

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('empresas/', views.empresas, name='empresas'),
    path('empresas/<int:cod_empresa>/centro-de-custos/', views.centro_de_custos, name='centro_de_custos'),
]