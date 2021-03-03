from django.urls import path

from . import views

app_name = "clie"

urlpatterns = [
    path('', views.pesqcliente, name='pesqcliente'),
    path('selecionar-cliente/', views.selecionar_cliente,
         name='selecionar_cliente'),
    path('dados-cliente/', views.dados_cliente, name='dados_cliente'),
    path('dados-empresa/<int:codempresa>',
         views.dados_empresa, name='dados_empresa'),
    path('cadastrar-novo-endereco/', views.cadastrar_novo_endereco,
         name='cadastrar_novo_endereco')
]
