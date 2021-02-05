from django.urls import path
from . import views


app_name = "clie"

urlpatterns = [
    path('<int:sequencia>', views.pesqcliente, name='pesqcliente'),
    path('selecionar-cliente/', views.selecionar_cliente,
         name='selecionar_cliente'),
    path('dados-cliente/', views.dados_cliente, name='dados_cliente'),
    path('dados-empresa/<int:codempresa>',
         views.dados_empresa, name='dados_empresa'),
    path('deflocal/', views.deflocal, name='deflocal'),
    path('deflocal/mudalogradouro/', views.mudalogradouro, name='mudalogradouro'),
    path('deflocal/mudabairro/<str:filtro>',
         views.mudabairro, name='mudabairro'),
    path('deflocal/bairro/<int:bairroesc>',
         views.bairroescolhido, name='bairroescolhido'),
    path('deflocal/mudamunicipio/<str:filtro>',
         views.mudamunicipio, name='mudamunicipio'),
    path('deflocal/municipio/<int:municipesc>',
         views.municipioescolhido, name='municipioescolhido'),
    path('deflocal/mudaestado/<str:regiao>',
         views.mudaestado, name='mudaestado'),
    path('deflocal/estado/<str:estadoesc>',
         views.estadoescolhido, name='estadoescolhido'),
    path('deflocal/mudaregiao', views.mudaregiao, name='mudaregiao'),
    path('prosseguir/', views.prosseguir, name='prosseguir')
]
