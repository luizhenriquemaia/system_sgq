from django.urls import path
from . import views


app_name = 'orcs'

urlpatterns = [
    path(
        'contratos-pendentes/',
        views.contratos_pendentes,
        name='contratos_pendentes'),
    path(
        'contrato-assinado/<int:codorcam>/',
        views.contrato_assinado,
        name='contrato_assinado'),
    path(
        'info-obras/',
        views.info_obras,
        name='info_obras'),
    path(
        'preorcamento/', 
        views.novo_orcamento, 
        name='novo_orcamento'),
    path(
        'preorcamento/<int:codorcam>/', 
        views.editar_orcamento,
        name='editar_orcamento'),
    path(
        'preorcamento-antigo/<int:codorcam>/', 
        views.editar_orcamento_antigo,
        name='editar_orcamento_antigo'),
    path(
        'preorcamento/<int:codorcam>/atualizar-custos/',
        views.view_para_atualizar_custos_orc,
        name='atualizar_custos_orc'),
    path(
        'preorcamento/<int:codorcam>/adicionar-desconto/<str:codeap>',
        views.adicionar_desconto,
        name='adicionar_desconto'),
    path(
        'excluir-orcamento/<int:codorcam>/',
        views.excluir_orcamento,
        name='excluir_orcamento'),
    path(
        'preorcamento/<int:codorcam>/ajax/excluir-serv/<str:codeap>',
        views.ajax_excluir_servico, 
        name='ajax_excluir_servico'),
    path(
        'preorcamento/<int:codorcam>/ajax/inserir-serv/',
        views.ajax_inserir_servico, 
        name='ajax_inserir_servico'),
    path(
        'preorcamento/<int:codorcam>/ajax/carregar-servico/',
        views.ajax_carregar_servico, 
        name='ajax_carregar_servico'),
    path(
        'preorcamento/<int:codorcam>/detalhar-serv/<int:codeap>/ajax/carregar-insumo-servico/',
        views.ajax_carregar_insumo_servico, 
        name='ajax_carregar_insumo_servico'),
    path(
        'preorcamento/<int:codorcam>/detalhar-serv/<int:codeap>/ajax/inserir-insumo-servico/',
        views.ajax_inserir_insumo_servico, 
        name='ajax_inserir_insumo_servico'),
    path(
        'preorcamento/<int:codorcam>/detalhar-serv/ajax/excluir-insumo-servico/<int:idInsumo>',
        views.ajax_excluir_insumo_servico, 
        name='ajax_excluir_insumo_servico'),
    path(
        'preorcamento/<int:codorcam>/detalhar-serv/<int:codeap>',
        views.detalhar_servico, 
        name='detalhar_servico'),
    path(
        'preorcamento/<int:codorcam>/detalhar-serv/<int:idEap>/alterar-insumo-atividade/<int:idInsumo>',
        views.alterar_insumo_atividade, 
        name='alterar_insumo_atividade'),
    path(
        'preorcamento/<int:codorcam>/editar-eap/<int:id>',
        views.editar_eap,
        name='editar_eap'),
    path(
        'marcar-visita/<int:codorcam>/', 
        views.marcar_visita, 
        name='marcar_visita'),
    path(
        'remarcar-visita/<int:codVisita>/', 
        views.remarcar_visita, 
        name='remarcar_visita'),
    path(
        'imp-visita/<int:codorcam>/', 
        views.imp_visita, 
        name='imp_visita'),
    path(
        'visita-efetuada/<int:codVisita>/', 
        views.obra_visitada, 
        name='obra_visitada'),
    path(
        'imp-proposta/<int:codorcam>/',
        views.imp_proposta,
        name='imp_proposta'),
    path(
        'imp-proposta-so-material/<int:codorcam>/',
        views.imp_proposta_so_material,
        name='imp_proposta_so_material'),
    path(
        'imp-proposta-outros-servicos/<int:codorcam>/',
        views.imp_proposta_outros_servicos,
        name='imp_proposta_outros_servicos'),
    path(
        'editar-proposta/<int:codorcam>/', 
        views.editar_proposta, 
        name='editar_proposta'),
    path(
        'alterar-status/<int:codorcam>/', 
        views.alterar_status_orc, 
        name='alterar_status_orc'),
    path(
        'imp-contrato/<int:codorcam>/',
        views.imp_contrato, 
        name='imp_contrato'),
    path(
        'editar-contrato/<int:codorcam>/',
        views.editar_contrato,
        name='editar_contrato'),
    path(
        'inserir-deslocamento/<int:codorcam>/', 
        views.inserir_deslocamento,
        name='inserir_deslocamento'),
    path(
        'atualizar-dados-insumo/<int:codInsumo>/', 
        views.atualizar_dados_insumo, 
        name='atualizar_dados_insumo'),
    path(
        'cad-insumo/', 
        views.cadastrar_insumo, 
        name='cadastrar_insumo'),
    path(
        'cronog-visitas/', 
        views.cronog_visitas, 
        name='cronog_visitas'),
    path(
        'venezianas/<int:codigo_orcamento>/', 
        views.venezianas, 
        name='venezianas'),
    path(
        'venezianas/ajax/adicionar-mais-vaos/<int:numberOfRows>/', 
        views.adicionar_mais_vaos_veneziana, 
        name='adicionar_mais_vaos_veneziana'),
    path(
        'poli-plano-fix/<int:codorcam>/', 
        views.poli_plano_fix, 
        name='poli_plano_fix'),
    path(
        'multi-click-plano-fixo/<int:codorcam>/',
        views.orc_multi_click_plano_fixo,
        name='orc_multi_click_plano_fixo'),
    path(
        'telha-trap-fixo/<int:codorcam>/',
        views.orc_telha_trapezoidal_fixo,
        name='orc_telha_trapezoidal_fixo'),
    path(
        'poli-plano-ret/<int:codorcam>/', 
        views.poli_plano_ret, 
        name='poli_plano_ret'),
    path(
        'poli-curvo-fix/<int:codorcam>/', 
        views.poli_curvo_fix, 
        name='poli_curvo_fix'),
    path(
        'poli-curvo-ret/<int:codorcam>/', 
        views.poli_curvo_ret, 
        name='poli_curvo_ret'),
]
