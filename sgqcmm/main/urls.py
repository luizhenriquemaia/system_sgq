from django.urls import path
from . import views


app_name = 'main'

urlpatterns = [
     path('', views.login_request, name='login'),
     path('inicio/', views.inicio, name='inicio'),
     path('apps-disponiveis/', views.apps_disponiveis, name='apps_disponiveis'),
     path('logout/', views.logout_request, name='logout'),
     path('add-user/', views.add_user, name='add_user'),
     path('edit-profile/', views.edit_profile, name='edit_profile'),
     path('change-password/', views.change_password, name='change_password'),
     path('listas-offline/', views.listas_offline, name='listas_offline'),
     path('listas-insumos/', views.listas_insumos, name='listas_insumos'),
     path('listas-empresas/', views.listas_empresas, name='listas_empresas'),
     path('listas-caixas/', views.listas_caixas, name='listas_caixas'),
     path('listas-ccustos/', views.listas_ccustos, name='listas_ccustos'),
     path('listas-ativs/', views.listas_ativs, name='listas_ativs'),
     path('listas-patrs/', views.listas_patrs, name='listas_patrs'),
     path('listas-colabs/', views.listas_colabs, name='listas_colabs'),
     path('ajax/carregar-estados/<regiao>', views.carregar_estados,
          name='ajax_carregar_estados'),
     path('ajax/carregar-cidades/<estado>', views.carregar_cidades,
          name='ajax_carregar_cidades'),
     path('ajax/carregar-bairros/<cidade>', views.carregar_bairros,
          name='ajax_carregar_bairros'),
     path('ajax/carregar-logradouros/<bairro>', views.carregar_logradouros,
          name='ajax_carregar_logradouros'),
     path('ajax/verificar-empresa/<codigo>', views.verificar_empresa,
         name='ajax_verificar_empresa'),
]
