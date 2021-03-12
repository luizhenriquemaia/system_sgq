from django.urls import path

from . import views

app_name = "config"

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('empresas/', views.empresas, name='empresas'),
    path('empresas/<int:cod_empresa>/centro-de-custos/', views.centro_de_custos, name='centro_de_custos'),
    path('orcamento/', views.orcamento, name='orcamento'),
    path('orcamento/categoria-insumo/', views.categoria_insumo, name='categoria_insumo'),
    path('orcamento/categoria-insumo/<int:cod_categoria>/', views.editar_categoria_insumo, name='editar_categoria_insumo'),
    path('orcamento/categoria-insumo/ajax/carregar-categorias-insumos/', views.carregar_categorias_insumo, name='carregar_categorias_insumo'),
]