from django.urls import path

from . import views

app_name = "config"

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('add-seeds/', views.adicionar_seeds, name='adicionar_seeds'),
    path('add-seeds/ajax/estados/', views.adicionar_seeds_estados, name='adicionar_seeds_estados'),
    path('add-seeds/ajax/municipios/', views.adicionar_seeds_municipios, name='adicionar_seeds_municipios'),
    path('add-seeds/ajax/tipos-endereco/', views.adicionar_seeds_tipos_endereco, name='adicionar_seeds_tipos_endereco'),
    path('add-seeds/ajax/tipos-frete/', views.adicionar_seeds_tipos_frete, name='adicionar_seeds_tipos_frete'),
    path('add-seeds/ajax/tipos-telefone/', views.adicionar_seeds_tipos_telefones, name='adicionar_seeds_tipos_telefones'),
    path('add-seeds/ajax/planos-de-pagamentos/', views.adicionar_seeds_planos_pagamento, name='adicionar_seeds_planos_pagamento'),
    path('add-seeds/ajax/status-do-orcamento/', views.adicionar_seeds_status_orcamento, name='adicionar_seeds_status_orcamento'),
    path('add-seeds/ajax/fases-do-orcamento/', views.adicionar_seeds, name='adicionar_seeds'),
    path('empresas/', views.empresas, name='empresas'),
    path('empresas/<int:cod_empresa>/centro-de-custos/', views.centro_de_custos, name='centro_de_custos'),
    path('orcamento/', views.orcamento, name='orcamento'),
    path('orcamento/insumo/', views.insumos_orcamento, name='insumos_orcamento'),
    path('orcamento/insumo/ajax/carregar-insumos/', views.carregar_insumos, name='carregar_insumos'),
    path('orcamento/categoria-insumo/', views.categoria_insumo, name='categoria_insumo'),
    path('orcamento/categoria-insumo/<int:cod_categoria>/', views.editar_categoria_insumo, name='editar_categoria_insumo'),
    path('orcamento/categoria-insumo/ajax/carregar-categorias-insumos/', views.carregar_categorias_insumo, name='carregar_categorias_insumo'),
]