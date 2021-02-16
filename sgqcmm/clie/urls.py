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
         name='cadastrar_novo_endereco'),
    path('ajax/carregar-estados/<regiao>', views.carregar_estados,
         name='ajax_carregar_estados'),
    path('ajax/carregar-cidades/<estado>', views.carregar_cidades,
         name='ajax_carregar_cidades'),
    path('ajax/carregar-bairros/<cidade>', views.carregar_bairros,
         name='ajax_carregar_bairros'),
    path('ajax/carregar-logradouros/<bairro>', views.carregar_logradouros,
         name='ajax_carregar_logradouros'),
]
