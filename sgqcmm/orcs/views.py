import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import HttpResponseRedirect, redirect, render, reverse
from django.http import HttpResponse
from django.db.models import Q

from main.funcoes import format_list_telefone, listacodigossup
from main.models import (a03Estados, a04Municipios, a05Bairros, a06Lograds,
                         a08TiposFrete, a10CatsInsumos, a11Insumos, a15AtvsPad,
                         a19PlsPgtos, a20StsOrcs, a31FaseOrc, b01Empresas, b04CCustos,
                         c01Usuarios, e01Cadastros, e02FonesCad, e04EndCad,
                         e06ContCad, g01Orcamento, g02ItOrc, g03EapOrc,
                         g04AtvEap, g05InsEAP, g09VisitasOrc)

from .calc.calculos_chapa_alveolar_e_compacto import (orc_poli_curvo,
                                                      orc_poli_plano)
from .calc.calculos_multi_click import orc_multi_click_plano
from .calc.calculos_telha_trap import orc_telha_trapezoidal
from .calc.calculos_veneziana import orc_venezianas
from .forms import (formAdicionarDesconto, formAlterarInsumoOrc,
                    formAlterarStatus, formAtualizarDadosInsumo, formCadInsumo,
                    formEditarContrato, formEditarProposta, formEditarEap,
                    formInserirDeslocamento, formInserirInsumoNaAtividade, formInserirServico,
                    formMarcarVisita, formMedidasVenezianas,
                    formOrcamentoMultiClickPlanoFixo,
                    formOrcamentoTelhaTrapezoidalFixo,
                    FormChapasPolicarbonato, FormEstruturaCobertura, FormMedidasCoberturaPlana,
                    FormCoberturaRetratil, FormMedidasCoberturaCurva, FormEstruturaCoberturaCurva)


# funções genéricas views
def formatar_custos_para_template(custo):
    return '{:,}'.format(round(custo, 2)).replace(
        '.', 'x').replace(',', '.').replace('x', ',')

def formatar_custos_para_bd(custo):
    return custo.replace(',', 'x').replace('.', '').replace('x', '.')

def formatar_com_duas_casas_string(string_valor):
    valor_separado = string_valor.split(",")
    if len(valor_separado[1]) < 2:
        return f"{valor_separado[0]},{valor_separado[1]}0"
    else:
        return string_valor

def obter_dados_gerais_orc(codorcam):
    orcEscolhido = g01Orcamento.objetos.get(pk=int(codorcam))
    codEndEsc = orcEscolhido.ender_id
    enderecoCompletoCad = e04EndCad.enderecocompletocad(e04EndCad, codEndEsc)
    codCliente = e04EndCad.objetos.get(pk=codEndEsc).cadastro_id
    cliente = e01Cadastros.objetos.get(id=codCliente)
    orcamento = {
        'codorcamento': codorcam,
        'codcliente': codCliente,
        'tratamento': cliente.fantasia,
        'nomecliente': cliente.razao,
        'desccliente': cliente.descrcad,
        'endereco': enderecoCompletoCad,
        'empresa': cliente.contempresa
    }
    return orcamento


def somar_custos_eap_editar_orcamento(eap_atividade, eap_entrega, eap_totalizador):
    # somar os custos das eaps para template de editar orcamento
    lista_eaps, lista_eaps_atividade, lista_eaps_entrega, lista_eaps_totalizador = [], [], [], []
    for item_totalizador in eap_totalizador:
        valor_totalizador = 0
        codigo_atual_totalizador = item_totalizador.codeap[0]
        for item_entrega in eap_entrega:
            codigo_atual_entrega = item_entrega.codeap[0]
            if codigo_atual_entrega == codigo_atual_totalizador:
                valor_entrega = 0
                if eap_atividade != []:
                    for item_atividade in eap_atividade:
                        codigo_atual_atividade = item_atividade.codeap[0]
                        if codigo_atual_atividade == codigo_atual_entrega:
                            try:
                                atividade_g04 = g04AtvEap.objetos.get(eap_id=item_atividade.id)
                                desconto = (item_atividade.vlrunit * atividade_g04.desconto / 100)
                            except ObjectDoesNotExist:
                                desconto = 0
                            item_atividade.qtdorc = round(item_atividade.qtdorc, 2)
                            item_atividade.vlrunit = round(item_atividade.vlrunit - desconto, 2)
                            valor_entrega += round(item_atividade.qtdorc * item_atividade.vlrunit, 2)
                            item_atividade.vlrtot = formatar_custos_para_template(item_atividade.vlrunit * item_atividade.qtdorc)
                            item_atividade.vlrunit_formatado = formatar_custos_para_template(item_atividade.vlrunit)
                            # Adicionar em uma lista temporária para organizar pro template
                            lista_eaps_atividade.append(item_atividade)
                else:
                    valor_entrega = item_entrega.vlrunit * item_entrega.qtdorc
                item_entrega.qtdorc = round(item_entrega.qtdorc, 2)
                item_entrega.vlrunit = round(valor_entrega / item_entrega.qtdorc, 2)
                valor_totalizador += round(item_entrega.qtdorc * item_entrega.vlrunit, 2)
                item_entrega.qtd_formatado = formatar_custos_para_template(item_entrega.qtdorc)
                item_entrega.vlrtot = formatar_custos_para_template(item_entrega.qtdorc * item_entrega.vlrunit)
                item_entrega.vlrunit_formatado = formatar_custos_para_template(item_entrega.vlrunit)
                # Adicionar em uma lista temporária para organizar pro template
                lista_eaps_entrega.append(item_entrega)
        item_totalizador.qtdorc = round(item_totalizador.qtdorc, 2)
        item_totalizador.vlrunit = round(valor_totalizador / item_totalizador.qtdorc, 2)
        item_totalizador.qtd_formatado = formatar_custos_para_template(item_totalizador.qtdorc)
        item_totalizador.vlrtot = formatar_custos_para_template(item_totalizador.vlrunit * item_totalizador.qtdorc)
        item_totalizador.vlrunit_formatado = formatar_custos_para_template(item_totalizador.vlrunit)
        lista_eaps_totalizador.append(item_totalizador)
        lista_eaps_totalizador += lista_eaps_entrega
        lista_eaps_entrega = []
        lista_eaps += lista_eaps_totalizador
        lista_eaps_totalizador = []
    return lista_eaps


def inserir_dados_eap(request, *eap_resultante):
    codigo_orcamento = request.session['codorcamento']
    novo_codigo_eap = g03EapOrc.proxnumeap(g03EapOrc)
    for linha in eap_resultante:
        if linha['Tipo'] > 0:
            nova_eap = g03EapOrc(
                id = novo_codigo_eap,
                orcamento_id = codigo_orcamento,
                codeap = linha['Ordenador'],
                coditem = linha['Ordenador'],
                descitem = linha['Descricao'],
                tipo = linha['Tipo'],
                qtdorc = linha['Quant'],
                unidade = linha['Unid'],
                vlrunit = 0
            )
            nova_eap.save()
            novo_codigo_eap += 1
            # atualmente só utilizamos os códigos 5 e 3
            # sem cadastrar atividades como insumos (estes possuem o tipo -1)
        elif linha['Tipo'] == -1:            
            novo_insumo = g05InsEAP(
                eap = nova_eap,
                insumo = a11Insumos.objetos.get(codigo=linha['CodInsumo']),
                qtdprod = linha['Quant'],
                qtdimpr = 0
            )
            novo_insumo.save()


def atualizar_custos_orc(codorcam):
    eapAt = g03EapOrc.objetos.filter(orcamento_id=codorcam)
    eapAt.update(vlrunit=0, cstser=0, cstmat=0)
    for itEap in eapAt:
        cstServEap = 0
        cstMatEap = 0
        vlrUnEap = 0
        if itEap.tipo == 2:
            try:
                atvsAtEap = g04AtvEap.objetos.get(eap_id=itEap.id)
                insumosAt = g05InsEAP.objetos.filter(atividade_id=atvsAtEap.id)
                cstPrevMatAtv = 0
                cstPrevServAtv = 0
                for insumoAt in insumosAt:
                    # Atualizar custos unitarios dos insumos
                    # 15% de imposto em cima da estrutura
                    categoriaInsumo = a11Insumos.objetos.get(id=insumoAt.insumo_id).catins_id
                    list_acresc_15 = [ 37, 38, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
                    if categoriaInsumo in list_acresc_15:
                        insumoAt.cstunpr = float(a11Insumos.objetos.get(id=insumoAt.insumo_id).custo01)
                        insumoAt.cstunim = float(a11Insumos.objetos.get(id=insumoAt.insumo_id).custo02)
                    else:
                        # Não acrescentar 15% na mão de obra e no valor em dinheiro
                        list_nao_15 = [1, 209, 220]
                        insumoAt.cstunpr = float(a11Insumos.objetos.get(id=insumoAt.insumo_id).custo01) if insumoAt.insumo_id in list_nao_15 else float(a11Insumos.objetos.get(id=insumoAt.insumo_id).custo01) * 1.15
                        insumoAt.cstunim = float(a11Insumos.objetos.get(id=insumoAt.insumo_id).custo02) if insumoAt.insumo_id in list_nao_15 else float(a11Insumos.objetos.get(id=insumoAt.insumo_id).custo02) * 1.15
                    insumoAt.save()
                    if a10CatsInsumos.objetos.get(id=a11Insumos.objetos.get(id=insumoAt.insumo_id).catins_id).tipo == 3 or a10CatsInsumos.objetos.get(id=a11Insumos.objetos.get(id=insumoAt.insumo_id).catins_id).tipo == 10:
                        cstPrevMatAtv += (float(insumoAt.qtdprod) * insumoAt.cstunpr) + (float(insumoAt.qtdimpr) * insumoAt.cstunim)
                    else:
                        cstPrevServAtv += (float(insumoAt.qtdprod) * insumoAt.cstunpr) + (float(insumoAt.qtdimpr) * insumoAt.cstunim)
                # Atualizar custos das atividades
                atvsAtEap.cstprevser = cstPrevServAtv
                atvsAtEap.cstprevmat = cstPrevMatAtv
                atvsAtEap.cstprev = cstPrevMatAtv+cstPrevServAtv
                atvsAtEap.save()
                cstServEap += cstPrevServAtv
                cstMatEap += cstPrevMatAtv
            except:
                pass
        # Atualizar custo do item da EAP
        cstTotItEap = cstServEap + cstMatEap + float(itEap.cstdistindi) + float(itEap.cstdistrisc) + float(itEap.cstdistbdi)
        itEap.qtdorc = 1 if itEap.qtdorc == 0 else itEap.qtdorc
        itEap.vlrunit = cstTotItEap / float(itEap.qtdorc)
        itEap.cstser = cstServEap
        itEap.cstmat = cstMatEap
        itEap.save()
        # Somar custos nos itens superiores
        for codigo in listacodigossup(itEap.codeap):
            for itemSup in g03EapOrc.objetos.filter(codeap=codigo):
                itemSup.qtdorc = 1 if itemSup.qtdorc == 0 else itemSup.qtdorc
                itemSup.cstser = float(itemSup.cstser) + float(cstServEap)
                itemSup.cstmat = float(itemSup.cstmat) + float(cstMatEap)
                itemSup.vlrunit = float(itemSup.vlrunit) + (cstTotItEap / float(itemSup.qtdorc))
                itemSup.save()
    return eapAt


def atualizar_lista_insumos(codOrcam):
    # Limpar lista atual de itens
    orcamento = g01Orcamento.objetos.get(pk=codOrcam)
    g02ItOrc.objetos.filter(orcamento__id=codOrcam).delete()
    # Obter nova lista
    nova_lista_insumos = g01Orcamento.lista_atualizada_insumos(g01Orcamento, codOrcam)
    # Gravar nova lista
    for insumo in nova_lista_insumos:
        try:
            novo_item = g02ItOrc(
                orcamento=orcamento,
                insumo=a11Insumos.objetos.get(pk=insumo.insumo_id),
                qtdprod=insumo.totQtProd,
                qtdimpr=insumo.totQtImp,
                cstunpr=insumo.medCstProd,
                cstunim=insumo.medCstProd
            )
            novo_item.save(force_insert=True)
        # devido as mudanças no models os orçamentos anteriores a 22-07-2020 estão com erro
        # de atributo pois não tem mais atividade
        except AttributeError:
            pass


def atualizar_dados_insumo(request, codInsumo):
    codorcam = request.session['codorcamento']
    insumo_bd = a11Insumos.objetos.get(codigo=codInsumo)
    insumo_para_template = {
        "codigo": insumo_bd.codigo,
        "descricao": insumo_bd.descricao,
        "unidade": insumo_bd.undbas,
        "valor_unitario": insumo_bd.custo01,
        "espessura": insumo_bd.espessura,
        "comprimento": insumo_bd.comprimento,
        "largura": insumo_bd.largura,
        "categoria": insumo_bd.catins
        }
    categorias_select = a10CatsInsumos.get_all_categories(a10CatsInsumos)
    if request.method == 'POST':
        form = formAtualizarDadosInsumo(request.POST)
        if form.is_valid():
            insumo_bd.custo01 = form.cleaned_data['valor_unitario'] if form.cleaned_data['valor_unitario'] else insumo_bd.custo01
            insumo_bd.descricao = form.cleaned_data['descricao'] if form.cleaned_data['descricao'] else insumo_bd.descricao
            insumo_bd.undbas = form.cleaned_data['unidade'] if form.cleaned_data['unidade'] else insumo_bd.undbas
            insumo_bd.espessura = form.cleaned_data['espessura'] if form.cleaned_data['espessura'] else insumo_bd.espessura
            insumo_bd.comprimento = form.cleaned_data['comprimento'] if form.cleaned_data['comprimento'] else insumo_bd.comprimento
            insumo_bd.largura = form.cleaned_data['largura'] if form.cleaned_data['largura'] else insumo_bd.largura
            insumo_bd.catins_id = form.cleaned_data['categoria'] if form.cleaned_data['categoria'] else insumo_bd.catins_id
            insumo_bd.dataatualizacao = datetime.date.today()
            insumo_bd.save()
            messages.info(request, "Dados atualizados com sucesso")
            return HttpResponseRedirect(
                reverse('orcs:editar_orcamento', args=(codorcam,)))
        else:
            print(form.errors.as_data())
            messages.error(request, "Erro ao atualizar dados do insumo")
            return render(
            request, "orcs/atualizar-dados-insumo.html", {
                "insumo": insumo_para_template, "categoriasSelect": categorias_select})
    else:
        return render(
            request, "orcs/atualizar-dados-insumo.html", {
                "insumo": insumo_para_template, "categoriasSelect": categorias_select})


def view_para_atualizar_custos_orc(request, codorcam):
    strcodorc = str(codorcam)
    atualizar_custos_orc(codorcam)
    return HttpResponseRedirect(
            reverse(
                'orcs:editar_orcamento', args=(strcodorc,)))


def alterar_insumo_atividade(request, codorcam, idEap, idInsumo):
    codorcam = request.session['codorcamento']
    insumo_eap = g05InsEAP.objetos.get(id=idInsumo)
    if request.method == 'POST':
        form = formAlterarInsumoOrc(request.POST)
        if form.is_valid():
            novo_insumo = insumo_eap.insumo_id
            quantidade_insumo = insumo_eap.qtdprod
            if form.cleaned_data['quantidadeInsumo']:
                quantidade_insumo = formatar_custos_para_bd(form.cleaned_data['quantidadeInsumo'])
            valor_unitario = insumo_eap.cstunpr
            if form.cleaned_data['valorUnitarioInsumo']:
                valor_unitario = formatar_custos_para_bd(form.cleaned_data['valorUnitarioInsumo'])
            if form.cleaned_data['novoInsumoOrc']:
                novo_insumo = form.cleaned_data['novoInsumoOrc']
            g05InsEAP.objetos.filter(id=idInsumo).update(
                insumo_id=novo_insumo, qtdprod=quantidade_insumo, cstunpr=valor_unitario)
            messages.info(request, "Insumo alterado com sucesso")
            strcodorc = str(codorcam)
            #atualizar_custos_orc(codorcam)
            atualizar_lista_insumos(codorcam)
            return HttpResponseRedirect(reverse('orcs:detalhar_servico', args=(str(codorcam), str(idEap))))
        else:
            messages.error(request, "Erro ao alterar o insumo")
            return HttpResponseRedirect(reverse('orcs:alterar_insumo_atividade', args=(idInsumo,)))
    else:
        form = formAlterarInsumoOrc()
        insumo = a11Insumos.objetos.get(id=g05InsEAP.objetos.get(id=idInsumo).insumo_id)
        insumos = {
            "codigo": insumo.codigo,
            "descricao": insumo.descricao,
            "quantidade": round(insumo_eap.qtdprod, 2),
            "valor_unitario": round(insumo_eap.cstunpr, 2)
        }
        return render(request, "orcs/alterar-insumo-atividade.html", {"form": form, "insumo": insumos})


def novo_orcamento(request):
    if not a08TiposFrete.objetos.filter(id=5).exists():
        messages.error(request, "Sem tipos de fretes cadastrados, vá para config/add-seeds")
        return HttpResponseRedirect(reverse('main:inicio'))
    if not a19PlsPgtos.objetos.filter(id=1).exists():
        messages.error(request, "Sem planos de pagamentos cadastrados, vá para config/add-seeds")
        return HttpResponseRedirect(reverse('main:inicio'))
    if not a20StsOrcs.objetos.filter(id=1).exists():
        messages.error(request, "Sem planos de pagamentos cadastrados, vá para config/add-seeds")
        return HttpResponseRedirect(reverse('main:inicio'))
    if not a31FaseOrc.objetos.filter(id=1).exists():
        messages.error(request, "Sem fases de orçamentos cadastradas, vá para config/add-seeds")
        return HttpResponseRedirect(reverse('main:inicio'))
    # usuários adicionados pelo cmd porém não adicionados na tabela c01
    if not c01Usuarios.objetos.filter(nomeusr=request.user).exists():
        messages.error(request, "O cadastro do seu usuário está incompleto")
        return HttpResponseRedirect(reverse('main:inicio'))
    cod_centro_de_custo = request.session['cc_orcamento']
    cod_endereço_cliente = request.session['cod_endereço_cliente']
    novo_cod_orcamento = g01Orcamento.proxnumorc(g01Orcamento)
    novo_orcamento = g01Orcamento(
        id=novo_cod_orcamento,
        ccusto=b04CCustos.objetos.get(id=cod_centro_de_custo),
        vended=c01Usuarios.objetos.get(nomeusr=request.user),
        fase=a31FaseOrc.objetos.get(id=1),
        plpgto=a19PlsPgtos.objetos.get(id=1),
        ender=e04EndCad.objetos.get(id=cod_endereço_cliente),
        prazo=15,
        tipofrete=a08TiposFrete.objetos.get(id=5),
        distfrete=10,
        status=a20StsOrcs.objetos.get(id=1)
    )
    novo_orcamento.save()
    request.session['cod_orcamento'] = novo_cod_orcamento
    return HttpResponseRedirect(
        reverse('orcs:editar_orcamento', args=(novo_cod_orcamento,)))


def editar_orcamento(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    orcamento_escolhido = g01Orcamento.objetos.get(pk=int(codorcam))
    request.session['codorcamento'] = codorcam
    # se o orçamento for de antes de 23-03-2021 -> ir para antiga view
    if request.method == "GET":
        if orcamento_escolhido.dtorc <= datetime.date(2021, 3, 16):
            return HttpResponseRedirect(reverse('orcs:editar_orcamento_antigo', args=(codorcam,)))
        try:
            raw_query_eaps = """ 
                            SELECT id, codeap, descitem, CAST(qtdorc AS DECIMAL(12,2)), 
                            unidade, CAST(vlrunit AS DECIMAL(12,2)), tipo
                            FROM main_g03eaporc 
                            WHERE orcamento_id = %s AND (tipo = 1 or tipo = 3 or tipo = 5)
                            ORDER BY codeap
                            """
            eaps_do_orcamento = g03EapOrc.objetos.raw(raw_query_eaps, [orcamento_escolhido])
        except ObjectDoesNotExist:
            eaps_do_orcamento = []
        eap_orc_5 = [eap for eap in eaps_do_orcamento if eap.tipo == 5]
        eap_orc_3 = [eap for eap in eaps_do_orcamento if eap.tipo == 3]
        eap_orc_1 = [eap for eap in eaps_do_orcamento if eap.tipo == 1]
        lista_eaps = somar_custos_eap_editar_orcamento(eap_orc_1, eap_orc_3, eap_orc_5)
        # Obter Lista de Insumos do Orcamentos
        lista_insumos = []
        for eap in eap_orc_3:
            for insumo in g05InsEAP.objetos.filter(eap_id=eap.id):
                insumo_objeto_a11 = a11Insumos.objetos.get(id=insumo.insumo_id)
                index_existent_insumo = next((index for index, insumo_adicionado in enumerate(lista_insumos) if insumo_adicionado['descricao'] == insumo_objeto_a11.descricao), None)
                if index_existent_insumo != None:
                    lista_insumos[index_existent_insumo]['qtdProd'] += insumo.qtdprod
                else:
                    dados_insumo =  {
                        'id': insumo_objeto_a11.id,
                        'codigo':insumo_objeto_a11.codigo,
                        'descricao':insumo_objeto_a11.descricao,
                        'undBas':insumo_objeto_a11.undbas,
                        'qtdProd': round(insumo.qtdprod, 2),
                        'cstUnPr': round(insumo.cstunpr, 2),
                        'vlrTotal':  formatar_custos_para_template(round(insumo.qtdprod * insumo.cstunpr, 2))
                    }
                    lista_insumos.append(dados_insumo)
        return render(request, "orcs/editar-orcamento.html", {
            "orcamento": orcamento, "eaporcam": lista_eaps,
            "form": formInserirServico
            })
    else:
        return HttpResponse(status=405)


# orçamentos antes de 23-03-2021
def editar_orcamento_antigo(request, codorcam):
    # Obter dados gerais do orcamento
    orcamento = obter_dados_gerais_orc(codorcam)
    orcEscolhido = g01Orcamento.objetos.get(pk=int(codorcam))
    request.session['codorcamento'] = codorcam
    if request.method == "POST":
        form = formInserirServico(request.POST)
        if form.is_valid():
            descricao_servico = form.cleaned_data['descricao']
            tipo_servico = int(request.POST['tipo'])
            codigo_eap_servico = form.cleaned_data['codigo_eap']
            try:
                codigo_nova_eap = g03EapOrc.objetos.latest('id').id + 1
            except ObjectDoesNotExist:
                codigo_nova_eap = 0
            novo_servico = g03EapOrc(
                id=codigo_nova_eap,
                codeap=codigo_eap_servico,
                coditem=codigo_eap_servico,
                descitem=descricao_servico,
                tipo=tipo_servico,
                qtdorc=1,
                unidade='un',
                vlrunit=0,
                orcamento_id=orcEscolhido.id
            )
            novo_servico.save()
        else:
            messages.error(request, "Erro ao adicionar serviço")
    # Obter eap do orçamento divididas por tipo
    eap_orc_5 = g03EapOrc.objetos.filter(orcamento_id=orcEscolhido, tipo=5).order_by('codeap')
    eap_orc_3 = g03EapOrc.objetos.filter(orcamento_id=orcEscolhido, tipo=3).order_by('codeap')
    eap_orc_1 = g03EapOrc.objetos.filter(orcamento_id=orcEscolhido, tipo=1).order_by('codeap')
    list_eaps, list_eaps_1, list_eaps3 = [] , [], []
    if len(eap_orc_5) != 0:
        for item5 in eap_orc_5:
            valor_eap_5 = 0
            cod_atual_5 = item5.codeap[0]
            for item3 in eap_orc_3:
                cod_atual_3 = item3.codeap[0]
                # Se o início da eap é o mesmo pode somar no valor total
                if cod_atual_3 == cod_atual_5:
                    valor_eap_3 = 0
                    for item1 in eap_orc_1:
                        cod_atual_1 = item1.codeap[0]
                        # Se o início da eap é o mesmo pode somar no valor total
                        if cod_atual_1 == cod_atual_3:
                            try:
                                atividade_item = g04AtvEap.objetos.get(eap_id=item1.id)
                                desconto = (item1.vlrunit * atividade_item.desconto / 100)
                            except ObjectDoesNotExist:
                                desconto = 0
                            item1.qtdorc = round(item1.qtdorc, 2)
                            item1.vlrunit = round(item1.vlrunit - desconto, 2)
                            # Adicionar no valor da eap do tipo 3
                            valor_eap_3 += (item1.qtdorc * item1.vlrunit)
                            item1.vlrtot = '{:,}'.format(round(
                                float(item1.vlrunit) * float(item1.qtdorc), 2)
                            ).replace('.', 'x').replace(',', '.').replace('x', ',')
                            item1.vlrunit = '{:,}'.format(item1.vlrunit).replace('.', 'x').replace(',', '.').replace('x', ',')
                            # Adicionar em uma lista temporária para organizar pro template
                            list_eaps_1.append(item1)
                        else:
                            pass
                    item3.qtdorc = round(item3.qtdorc, 2)
                    item3.vlrunit = round(valor_eap_3 / item3.qtdorc, 2)
                    # Adicionar na eap do tipo 5
                    valor_eap_5 += (item3.qtdorc * item3.vlrunit)
                    item3.vlrtot = '{:,}'.format(
                        round(float(item3.vlrunit) * float(item3.qtdorc), 2)
                    ).replace('.', 'x').replace(',', '.').replace('x', ',')
                    item3.vlrunit = '{:,}'.format(
                        item3.vlrunit).replace('.', 'x').replace(',', '.').replace('x', ',')
                    # Adicionar em uma lista temporária para organizar pro template
                    list_eaps3.append(item3)
                    list_eaps3 += list_eaps_1
                    list_eaps_1 = []
                else:
                    pass
            item5.qtdorc = round(item5.qtdorc, 2)
            item5.vlrunit = round(valor_eap_5 / item5.qtdorc, 2)
            item5.vlrtot = '{:,}'.format(
                round(float(item5.vlrunit) * float(item5.qtdorc), 2)
            ).replace('.', 'x').replace(',', '.').replace('x', ',')
            item5.vlrunit = '{:,}'.format(item5.vlrunit
            ).replace('.', 'x').replace(',', '.').replace('x', ',')
            # Adicionar na lista para passar pro html
            list_eaps.append(item5)
            list_eaps += list_eaps3
            list_eaps3 = []
    # se não tiver eap do tipo 5 precisa começar pela eap 3
    # mudar futuramente essa função
    elif len(eap_orc_3) != 0:
        for item3 in eap_orc_3:
            cod_atual_3 = item3.codeap[0]
            valor_eap_3 = 0
            for item1 in eap_orc_1:
                cod_atual_1 = item1.codeap[0]
                # Se o início da eap é o mesmo pode somar no valor total
                if cod_atual_1 == cod_atual_3:                    
                    item1.qtdorc = round(item1.qtdorc, 2)
                    item1.vlrunit = round(item1.vlrunit, 2)
                    # Adicionar no valor da eap do tipo 3
                    valor_eap_3 += (item1.qtdorc * item1.vlrunit)
                    item1.vlrtot = formatar_custos_para_template(
                        float(item1.vlrunit) * float(item1.qtdorc)
                    ) 
                    item1.vlrunit = formatar_custos_para_template(item1.vlrunit)
                    # Adicionar em uma lista temporária para organizar pro template
                    list_eaps_1.append(item1)
            item3.qtdorc = round(item3.qtdorc, 2)
            item3.vlrunit = round(valor_eap_3 / item3.qtdorc, 2)
            item3.vlrtot = formatar_custos_para_template(
                float(item3.vlrunit) * float(item3.qtdorc)
            )
            item3.vlrunit = formatar_custos_para_template(item3.vlrunit)
            # Adicionar em uma lista temporária para organizar pro template
            list_eaps3.append(item3)
            list_eaps3 += list_eaps_1
            list_eaps_1 = []
        # Adicionar na lista para passar pro html
        list_eaps += list_eaps3
        list_eaps3 = []
    # Obter Lista de Insumos do Orcamentos
    lista_insumos = []
    for eap in g03EapOrc.objetos.filter(orcamento_id=orcEscolhido, tipo=1):
        for insumo in g05InsEAP.objetos.filter(eap_id=eap.id):
            insumo_objeto_a11 = a11Insumos.objetos.get(id=insumo.insumo_id)
            index_existent_insumo = next((index for index, insumo_adicionado in enumerate(lista_insumos) if insumo_adicionado['descricao'] == insumo['descricao']), None)
            if index_existent_insumo != None:
                lista_insumos[index_existent_insumo]['quantidade'] += insumo['quantidade']
            else:
                dados_insumo =  {
                    'id': insumo_objeto_a11.id,
                    'codigo':insumo_objeto_a11.codigo,
                    'descricao':insumo_objeto_a11.descricao,
                    'undBas':insumo_objeto_a11.undbas,
                    'qtdProd': round(insumo.qtdprod, 2),
                    'cstUnPr': round(insumo.cstunpr, 2),
                    'vlrTotal': '{:,}'.format(round(insumo.qtdprod * insumo.cstunpr, 2)).replace('.', 'x').replace(',', '.').replace('x', ',')
                }
                lista_insumos.append(dados_insumo)

    return render(request, "orcs/editar-orcamento-antigo.html", {
        "orcamento": orcamento, "eaporcam": list_eaps,
        "insumos": lista_insumos, "form": formInserirServico
        }
    )


def lista_de_insumo(request, codorcam):
    if request.method == "GET": 
        if request.user:
            orcamento = obter_dados_gerais_orc(codorcam)
            lista_insumos = []
            for eap in g03EapOrc.objetos.filter(orcamento_id=codorcam, tipo=3):
                for insumo in g05InsEAP.objetos.filter(eap_id=eap.id):
                    insumo_objeto_a11 = a11Insumos.objetos.get(id=insumo.insumo_id)
                    index_existent_insumo = next((index for index, insumo_adicionado in enumerate(lista_insumos) if insumo_adicionado['descricao'] == insumo_objeto_a11.descricao), None)
                    if index_existent_insumo != None:
                        lista_insumos[index_existent_insumo]['qtdProd'] += insumo.qtdprod
                    else:
                        dados_insumo =  {
                            'id': insumo_objeto_a11.id,
                            'codigo':insumo_objeto_a11.codigo,
                            'descricao':insumo_objeto_a11.descricao,
                            'undBas':insumo_objeto_a11.undbas,
                            'qtdProd': round(insumo.qtdprod, 2),
                            'cstUnPr': round(insumo.cstunpr, 2),
                            'vlrTotal':  formatar_custos_para_template(round(insumo.qtdprod * insumo.cstunpr, 2))
                        }
                        lista_insumos.append(dados_insumo)
            budget_inputs_list_ordered = sorted(lista_insumos, key=lambda k: k['descricao'])
            return render(request, "orcs/lista-de-insumos.html", {
                    "orcamento": orcamento, "insumos": budget_inputs_list_ordered})
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=405)


def excluir_orcamento(request, codorcam):
    if request.user.is_staff:
        g01Orcamento.objetos.get(id=int(codorcam)).delete()
    else:
        return HttpResponse(status=403)
    return HttpResponseRedirect(reverse('main:inicio'))


def inserir_deslocamento(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    codigo_orcamento_atual = request.session['codorcamento']
    id_orcamento_escolhido = g01Orcamento.objetos.get(pk=int(codorcam)).id
    raw_query_eaps = """ 
                        SELECT id, codeap, descitem, CAST(qtdorc AS DECIMAL(12,2)), 
                        unidade, CAST(vlrunit AS DECIMAL(12,2)), tipo
                        FROM main_g03eaporc 
                        WHERE orcamento_id = %s AND tipo = 3
                        ORDER BY codeap
                    """
    entregas_select = g03EapOrc.objetos.raw(raw_query_eaps, [id_orcamento_escolhido])
    form = formInserirDeslocamento()
    if request.method == "POST":
        form = formInserirDeslocamento(request.POST)
        if form.is_valid():
            distancia = form.cleaned_data['distancia'] if form.cleaned_data['distancia'] else 0
            tipo_veiculo = form.cleaned_data['tipo_veiculo'] if form.cleaned_data['tipo_veiculo'] else 0
            dias = form.cleaned_data['dias'] if form.cleaned_data['dias'] else 0
            hospedagem = form.cleaned_data['hospedagem'] if form.cleaned_data['hospedagem'] else 0
            passagem = form.cleaned_data['passagem'] if form.cleaned_data['passagem'] else 0
            try: 
                eap = g03EapOrc.objetos.get(id=request.POST['entrega'])
                if eap.tipo != 3:
                    message.error("Entrega inválida")
                    return render(request, "orcs/inserir-deslocamento.html", {"orcamento": orcamento, "form": form,
                        "entregasSelect": entregas_select})
            except ObjectDoesNotExist:
                message.error("Entrega inválida")
                return render(request, "orcs/inserir-deslocamento.html", {"orcamento": orcamento, "form": form,
                    "entregasSelect": entregas_select})
            # id insumos -> hospedagem = 135, gasolina = 142, diesel s10 = 147, diesel s500 = 146, passagem = 140
            insumos_para_adicionar = []
            if distancia != 0 and dias != 0:
                quantidade_combustivel = distancia * dias * 2 / 8
                if tipo_veiculo == 1:
                    tipo_combustivel = 142
                elif tipo_veiculo == 2:
                    tipo_combustivel = 147
                else:
                    tipo_combustivel = 146
                    quantidade_combustivel = distancia * dias * 2 / 2.2 if tipo_veiculo == 3 else distancia * dias * 2 / 4
                insumos_para_adicionar.append(
                    {"quantidade": quantidade_combustivel, "insumo": tipo_combustivel})
            if hospedagem != 0:
                insumos_para_adicionar.append(
                    {"quantidade": hospedagem, "insumo": 135})
            if passagem != 0:
                insumos_para_adicionar.append(
                    {"quantidade": passagem, "insumo": 140})
            for insumo in insumos_para_adicionar:
                novo_insumo = g05InsEAP(
                    qtdprod=insumo['quantidade'],
                    qtdimpr=0,
                    cstunpr=0,
                    cstunim=0,
                    insumo=a11Insumos.objetos.get(id=insumo['insumo']),
                    eap=eap)
                novo_insumo.save()
            # Atualizar custos do orcamento
            # A FUNÇÃO ESTÁ GERANDO O ERRO 504
            #atualizar_custos_orc(cod_orc_atual)
            atualizar_lista_insumos(codigo_orcamento_atual)
            return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
        else:
            return render(request, "orcs/inserir-deslocamento.html", {"orcamento": orcamento, "form": form,
                "entregasSelect": entregas_select})
    elif request.method == "GET":
        return render(request, "orcs/inserir-deslocamento.html", {"orcamento": orcamento, "form": form,
            "entregasSelect": entregas_select})
    else:
        return HttpResponse(status=405)


def cadastrar_insumo(request):
    # Obter dados gerais do orcamento
    codOrcAtual = request.session['codorcamento']
    codigo_servico_atual = request.session['eap_atividade']
    if request.method == "POST":
        form = formCadInsumo(request.POST)
        if form.is_valid():
            espessura = form.cleaned_data['espessura'] if form.cleaned_data['espessura'] else 0
            comprimento = form.cleaned_data['comprimento'] if form.cleaned_data['comprimento'] else 0
            largura = form.cleaned_data['largura'] if form.cleaned_data['largura'] else 0
            try:
                ultimo_insumo_adicionado = a11Insumos.objetos.latest('-id')
            except ObjectDoesNotExist:
                ultimo_insumo_adicionado = {"id": 0, "codigo": 0}
            novo_insumo = a11Insumos(id = ultimo_insumo_adicionado.id + 1,
                                    codigo = ultimo_insumo_adicionado.codigo + 1,
                                    descricao = form.cleaned_data['descricao'],
                                    undbas = form.cleaned_data['unidade'],
                                    undcompr = form.cleaned_data['unidade'],
                                    fatundcomp = 1,
                                    custo01 = form.cleaned_data['custo'],
                                    custo02 = form.cleaned_data['custo'],
                                    prvda = form.cleaned_data['custo'],
                                    pesunbas = 0,
                                    qtppal = 0,
                                    catins_id = form.cleaned_data['categoria_insumo'],
                                    espessura = espessura,
                                    comprimento = comprimento,
                                    largura = largura,
                                    dataatualizacao = datetime.date.today())
            novo_insumo.save()
            return HttpResponseRedirect(reverse('orcs:detalhar_servico', args=(codOrcAtual, codigo_servico_atual,)))
        else:
            print(form.errors.as_data())
            message.error("Dados incorretos")
            return render(request, "orcs/cad-insumo.html", {"form":form,})
    else:
        form = formCadInsumo()
        categorias_insumo = a10CatsInsumos.ordenadas(a10CatsInsumos)
    return render(request, "orcs/cad-insumo.html", {"form":form, "categoriasInsumos": categorias_insumo})


def detalhar_servico(request, codorcam, codeap):
    request.session['eap_atividade'] = codeap
    orcamento = obter_dados_gerais_orc(codorcam)
    orcamento_escolhido = g01Orcamento.objetos.get(pk=int(codorcam))
    form = formInserirInsumoNaAtividade()
    if request.method == "GET":
        insumos_atividade = []
        raw_query_insumo =  """
                            SELECT main_g05inseap.id, main_g05inseap.eap_id, CAST(main_g05inseap.qtdprod AS DECIMAL(12,2)) AS qtdprod, CAST(main_g05inseap.cstunpr AS DECIMAL(12,2)) AS cstunpr,
                                   main_a11insumos.descricao AS descricao, main_a11insumos.undbas AS undbas
                            FROM main_g05inseap 
                            INNER JOIN main_a11insumos ON main_a11insumos.id = main_g05inseap.insumo_id
                            WHERE main_g05inseap.eap_id = %s
                            ORDER BY main_g05inseap.eap_id
                            """
        insumos_entrega = g05InsEAP.objetos.raw(raw_query_insumo, [codeap])
        for item, insumo in enumerate(insumos_entrega):
            insumos_atividade.append(
                {
                    "id": insumo.id,
                    "item": item,
                    "descricao": insumo.descricao,
                    "quantidade": formatar_custos_para_template(insumo.qtdprod),
                    "unidade": insumo.undbas,
                    "custo": formatar_custos_para_template(insumo.cstunpr),
                    "valorTotal": formatar_custos_para_template(insumo.qtdprod * insumo.cstunpr)
                }
            )
        return render(
            request, "orcs/detalhar-servico.html", 
            {"orcamento": orcamento, "idEap": codeap,
            "insumos": insumos_atividade, "form": form})
    else:
        HttpResponse(status=405)


def ajax_editar_servico(request, codorcam, codeap):
    if request.user:
        if request.method == "GET":
            servico_eap = g03EapOrc.objetos.filter(orcamento__id=codorcam, codeap=codeap)[0]
            servico_eap.vlrunit = formatar_custos_para_template(servico_eap.vlrunit)
            servico_eap.qtdorc = formatar_custos_para_template(servico_eap.qtdorc)
            return render(request, 'orcs/ajax-editar-eap.html', {"eaporcam": servico_eap})
        elif request.method == "POST":
            form = formEditarEap(request.POST)
            if form.is_valid():
                try:
                    servico_eap = g03EapOrc.objetos.filter(orcamento__id=codorcam, codeap=codeap)[0]
                    servico_eap.codeap = form.cleaned_data['codigo_eap'] if form.cleaned_data['codigo_eap'] else servico_eap.codeap
                    servico_eap.descitem = form.cleaned_data['descricao'] if form.cleaned_data['descricao'] else servico_eap.descitem
                    servico_eap.qtdorc = formatar_custos_para_bd(form.cleaned_data['quantidade']) if form.cleaned_data['quantidade'] else servico_eap.qtdorc
                    servico_eap.unidade = form.cleaned_data['unidade'] if form.cleaned_data['unidade'] else servico_eap.unidade
                    servico_eap.vlrunit = formatar_custos_para_bd(form.cleaned_data['valor_unitario']) if form.cleaned_data['valor_unitario'] else servico_eap.vlrunit
                    servico_eap.save()
                    return HttpResponse(status=201)
                except:
                    return HttpResponse(status=500)
            else:
                return HttpResponse(status=400)
        else:
            return HttpResponse(status=405)
    else:
        return HttpResponse(status=403)


def ajax_excluir_servico(request, codorcam, codeap):
    if request.method == "DELETE":
        if request.user:
            objetos_do_servico = g03EapOrc.objetos.filter(orcamento__id=codorcam, codeap__startswith=codeap)
            if objetos_do_servico == []:
                return HttpResponse(status=400)
            else:
                objetos_do_servico.delete()
                return HttpResponse(status=200)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=405)


def ajax_inserir_servico(request, codorcam):
    if request.method == "POST":
        if request.user:
            form = formInserirServico(request.POST)
            if form.is_valid():
                orcamento_escolhido = g01Orcamento.objetos.get(id=codorcam)
                descricao_servico = form.cleaned_data['descricao']
                tipo_servico = int(request.POST['tipo'])
                codigo_eap_servico = form.cleaned_data['codigo_eap'] if form.cleaned_data['codigo_eap'][-1:] == '.' else form.cleaned_data['codigo_eap'] + '.'
                try:
                    codigo_nova_eap = g03EapOrc.objetos.latest('id').id + 1
                except ObjectDoesNotExist:
                    codigo_nova_eap = 0
                novo_servico = g03EapOrc(
                    id=codigo_nova_eap,
                    codeap=codigo_eap_servico,
                    coditem=codigo_eap_servico,
                    descitem=descricao_servico,
                    tipo=tipo_servico,
                    qtdorc=1,
                    unidade='un',
                    vlrunit=0,
                    orcamento_id=orcamento_escolhido.id
                )
                novo_servico.save()
                return HttpResponse(status=201)
            else:
                return HttpResponse(status=400)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=405)


def ajax_carregar_servico(request, codorcam):
    if request.method == "GET":
        if request.user:
            orcamento_escolhido = g01Orcamento.objetos.get(id=codorcam)
            if orcamento_escolhido.dtorc <= datetime.date(2021, 3, 16):
                return HttpResponseRedirect(reverse('orcs:editar_orcamento_antigo', args=(codorcam,)))
            try:
                raw_query_eaps = """ 
                                SELECT id, codeap, descitem, CAST(qtdorc AS DECIMAL(12,2)), 
                                unidade, CAST(vlrunit AS DECIMAL(12,2)), tipo
                                FROM main_g03eaporc 
                                WHERE orcamento_id = %s AND (tipo = 1 or tipo = 3 or tipo = 5)
                                ORDER BY codeap
                                """
                eaps_do_orcamento = g03EapOrc.objetos.raw(raw_query_eaps, [orcamento_escolhido])
            except ObjectDoesNotExist:
                eaps_do_orcamento = []
            eap_orc_5 = [eap for eap in eaps_do_orcamento if eap.tipo == 5]
            eap_orc_3 = [eap for eap in eaps_do_orcamento if eap.tipo == 3]
            eap_orc_1 = [eap for eap in eaps_do_orcamento if eap.tipo == 1]
            lista_eaps = somar_custos_eap_editar_orcamento(eap_orc_1, eap_orc_3, eap_orc_5)
            return render(request, 'orcs/carregar-servicos.html', {"eaporcam": lista_eaps})
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=405)


def ajax_carregar_insumo_servico(request, codorcam, codeap):
    if request.method == "GET":
        if request.user:
            raw_query_insumo =  """
                                SELECT main_g05inseap.id, main_g05inseap.eap_id, CAST(main_g05inseap.qtdprod AS DECIMAL(12,2)) AS qtdprod, CAST(main_g05inseap.cstunpr AS DECIMAL(12,2)) AS cstunpr,
                                        main_a11insumos.descricao AS descricao, main_a11insumos.undbas AS undbas
                                FROM main_g05inseap 
                                INNER JOIN main_a11insumos ON main_a11insumos.id = main_g05inseap.insumo_id
                                WHERE main_g05inseap.eap_id = %s
                                ORDER BY main_g05inseap.eap_id
                                """
            insumos_entrega = g05InsEAP.objetos.raw(raw_query_insumo, [codeap])
            insumos_atividade = []
            for item, insumo in enumerate(insumos_entrega):
                insumos_atividade.append(
                    {
                        "id": insumo.id,
                        "item": item,
                        "descricao": insumo.descricao,
                        "quantidade": formatar_custos_para_template(insumo.qtdprod),
                        "unidade": insumo.undbas,
                        "custo": formatar_custos_para_template(insumo.cstunpr),
                        "valorTotal": formatar_custos_para_template(insumo.qtdprod * insumo.cstunpr)
                    }
                )
            return render(request, "orcs/ajax-carregar-insumos-servico.html", 
                {"idEap": codeap, "insumos": insumos_atividade})
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=405)


def ajax_alterar_insumo_servico(request, codorcam, id_eap, id_insumo):
    if request.user:
        if request.method == "GET":
            form = formAlterarInsumoOrc()
            inputs_select = a11Insumos.objetos.all().only('id', 'descricao').order_by('descricao')
            service_input = g05InsEAP.objetos.get(id=id_insumo)
            service_input.qtdprod = str(service_input.qtdprod).replace(",", ".")
            service_input.cstunpr = str(service_input.cstunpr).replace(",", ".")
            return render(request, 'orcs/ajax-alterar-insumo-servico.html',
                {"serviceInput": service_input, "form": form, "insumosSelect": inputs_select})
        elif request.method == "POST":
            form = formAlterarInsumoOrc(request.POST)
            if form.is_valid():
                try:
                    service_input = g05InsEAP.objetos.get(id=id_insumo)
                    service_input.insumo_id = form.cleaned_data['insumo'] if form.cleaned_data['insumo'] else service_input.insumo_id
                    service_input.qtdprod = form.cleaned_data['quantidade'] if form.cleaned_data['quantidade'] else service_input.qtdprod
                    service_input.cstunpr = form.cleaned_data['valor_unitario'] if form.cleaned_data['valor_unitario'] or form.cleaned_data['valor_unitario'] >= 0 else service_input.cstunpr
                    service_input.save()
                    return HttpResponse(status=200)
                except:
                    return HttpResponse(status=500)
            else:
                print(form.errors.as_data())
                return HttpResponse(status=400)
        else:
            return HttpResponse(status=405)
    else:
        return HttpResponse(status=403)


def ajax_inserir_insumo_servico(request, codorcam, codeap):
    if request.method == "POST":
        if request.user:
            form = formInserirInsumoNaAtividade(request.POST)
            if form.is_valid():
                id_novo_insumo = int(request.POST['insumo'])
                quantidade_novo_insumo = formatar_custos_para_bd(form.cleaned_data['quant_insumo']) if form.cleaned_data['quant_insumo'] else 0
                valor_novo_insumo = formatar_custos_para_bd(form.cleaned_data['valor_insumo']) if form.cleaned_data['valor_insumo'] else 0                
                novo_insumo = g05InsEAP(
                    qtdprod=quantidade_novo_insumo,
                    qtdimpr=0,
                    cstunpr=valor_novo_insumo,
                    cstunim=0,
                    insumo=a11Insumos.objetos.get(id=id_novo_insumo),
                    eap_id=codeap
                )
                novo_insumo.save()
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=400)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=405)


def ajax_excluir_insumo_servico(request, codorcam, idInsumo):
    if request.method == "DELETE":
        if request.user:
            try:
                g05InsEAP.objetos.get(id=idInsumo).delete()
            except:
                return HttpResponse(status=400)
            atualizar_lista_insumos(codorcam)
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=405)


def marcar_visita(request, codorcam):
    request.session['marcador'] = 'orcs:marcarvisita/'
    orcamento = obter_dados_gerais_orc(codorcam)
    request.session['codorcamento'] = codorcam
    telefones = e02FonesCad.fonescad(e02FonesCad, orcamento['codcliente'])
    telefones = format_list_telefone(telefones)
    if request.method == "POST":
        form = formMarcarVisita(request.POST)
        if form.is_valid():
            dataVisita = form.cleaned_data['dataVisita']
            horaVisita = form.cleaned_data['horaVisita']
            tipoVisita = int(request.POST['combTiposVisita'])
            visitas = g09VisitasOrc.objetos.all().order_by('-id')[:1]
            ultimaVisita = int(visitas[0].id) if visitas else 0
            novaVisita = g09VisitasOrc(id=ultimaVisita+1,
                                       orcamento=g01Orcamento.objetos.get(id=codorcam),
                                       data=dataVisita,
                                       hora=horaVisita,
                                       tipovisita=tipoVisita,
                                       pendente=True)
            novaVisita.save()
            g01Orcamento.objetos.filter(id=codorcam).update(fase=2)
            messages.info(request, "Visita marcada com sucesso")
            if tipoVisita == 0:
                messages.error(request, "Erro ao marcar a visita")
                return HttpResponseRedirect(reverse('orcs:marcar_visita', args=(codorcam,)))
            else:
                return redirect("orcs:cronog_visitas")
        else:
            messages.error(request, "Erro ao marcar a visita")
            return HttpResponseRedirect(reverse('orcs:marcar_visita', args=(codorcam,)))
    else:
        form = formMarcarVisita()
        return render(request, "orcs/marcar-visita.html", {"form": form,"orcamento": orcamento,"telefones": telefones})


def imp_visita(request, codorcam):
    # Gravar marcador
    request.session['marcador'] = 'orcs:imp_visita/'
    # Obter dados gerais do orcamento
    orcamento = obter_dados_gerais_orc(codorcam)
    request.session['codorcamento'] = codorcam
    # Obter contatos do cliente
    telefones = e02FonesCad.fonescad(e02FonesCad, orcamento['codcliente'])
    telefones = format_list_telefone(telefones)
    tipoVisita = g09VisitasOrc.objetos.filter(orcamento__id=codorcam).order_by('-id')[0].tipovisita
    vendedor = c01Usuarios.objetos.get(id=g01Orcamento.objetos.get(id=codorcam).vended_id).nomeusr
    if tipoVisita == 1:
        return render(request, "orcs/imp-visita-coberturas.html", {"orcamento": orcamento, "telefones": telefones, "vendedor": vendedor})
    elif tipoVisita == 2:
        return render(request, "orcs/imp-visita-veneziana.html", {"orcamento": orcamento, "telefones": telefones, "vendedor": vendedor})
    else:
        messages.error(request, "Erro ao abrir formulário de visita")
        return HttpResponseRedirect(reverse('orcs:marcar_visita', args=(codorcam,)))


def cronog_visitas(request):
    visitas = g09VisitasOrc.objetos.filter(pendente=True).order_by('data')
    listVisitas = []
    for visita in visitas:
        dicVisitas = {"codVisita": visita.id,
                      "data": visita.data,
                      "hora": visita.hora,
                      "orcamento": visita.orcamento,
                      "cliente": e01Cadastros.objetos.get(id=e04EndCad.objetos.get(id=g01Orcamento.objetos.get(id=visita.orcamento_id).ender_id).cadastro_id).descrcad,
                      "tipovisita": visita.tipovisita}
        listVisitas.append(dicVisitas)
    return render(request, "orcs/cronog-visitas.html", {"visitas": listVisitas})


def remarcar_visita(request, codVisita):
    codorcam = g09VisitasOrc.objetos.get(id=codVisita).orcamento_id
    g09VisitasOrc.objetos.filter(id=codVisita).delete()
    messages.info(request, "Defina os novos dados da visita")
    return HttpResponseRedirect(reverse('orcs:marcar_visita', args=(codorcam,)))


def obra_visitada(request, codVisita):
    visitaEf = g09VisitasOrc.objetos.filter(id=codVisita).update(pendente=False)
    messages.info(request, "Baixa em visita efetuada com sucesso")
    g01Orcamento.objetos.filter(id=g09VisitasOrc.objetos.get(id=codVisita).orcamento_id).update(fase_id=3)
    return redirect("orcs:cronog_visitas")


def contratos_pendentes(request):
    contratos = g01Orcamento.objetos.filter(fase_id=4) if request.user.is_staff else g01Orcamento.objetos.filter(fase_id=4, vended_id=request.user.id)
    list_contratos = []
    for contrato in contratos:
        cod_endereco = contrato.ender_id
        cliente = e01Cadastros.objetos.get(
            id=e04EndCad.objetos.get(pk=cod_endereco).cadastro_id)
        dic_contrato = {
            "numero_orc": contrato.id,
            "data_orc": contrato.dtorc,
            "cliente": cliente,
            "pagamento": a19PlsPgtos.objetos.get(id=contrato.plpgto_id).descricao,
            "vendedor": c01Usuarios.objetos.get(id=contrato.vended_id).nomeusr
        }
        list_contratos.append(dic_contrato)
    return render(request, "orcs/contratos-pendentes.html", {"contratos": list_contratos})


def contrato_assinado(request, codorcam):
    if request.user.is_staff:
        orcamento = g01Orcamento.objetos.get(id=codorcam)
        orcamento.fase_id = 5
        orcamento.save()
    else:
        messages.info(request, "usuário não autorizado")
    return redirect("orcs:contratos_pendentes")


def info_obras(request):
    obras = g01Orcamento.objetos.filter(fase_id=5) if request.user.is_staff else g01Orcamento.objetos.filter(fase_id=4, vended_id=request.user.id)
    list_obras = []
    for obra in obras:
        cod_endereco = obra.ender_id
        cliente = e01Cadastros.objetos.get(
            id=e04EndCad.objetos.get(pk=cod_endereco).cadastro_id)
        dic_obra = {
            "numero_orc": obra.id,
            "data_orc": obra.dtorc,
            "cliente": cliente,
            "pagamento": a19PlsPgtos.objetos.get(id=obra.plpgto_id).descricao,
            "vendedor": c01Usuarios.objetos.get(id=obra.vended_id).nomeusr
        }
        list_obras.append(dic_obra)
    return render(request, "orcs/info-obras.html", {"obras": list_obras})


def alterar_status_orc(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    request.session['codorcamento'] = codorcam
    if request.method == "POST":
        form = formAlterarStatus(request.POST)
        if form.is_valid():
            orcamento = g01Orcamento.objetos.get(pk=int(codorcam))
            orcamento.status_id = int(request.POST['combStatus'])
            orcamento.save()
            messages.info(request, "Status alterado com sucesso")
            return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
        else:
            messages.error(request, "Status inválido")
            return redirect("orcs:alterar_status_orc")
    else:
        form = formAlterarStatus()
        return render(request, "orcs/alterar-status-orc.html", {"form": form, "orcamento": orcamento})


def adicionar_desconto(request, codorcam, codeap):
    orcamento = obter_dados_gerais_orc(codorcam)
    atividade = g04AtvEap.objetos.get(eap_id=int(codeap))
    if request.method == "POST":
        if request.user.is_staff:
            form = formAdicionarDesconto(request.POST)
            if form.is_valid():
                atividade.desconto = form.cleaned_data['valor_desconto']
                atividade.save()
                messages.info(request, "Desconto aplicado")
                return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
            else:
                messages.error(request, "Formulário inválido")
        else:
            messages.error(request, "Usuário não autorizado")
    else:
        form = formAdicionarDesconto()
        return render(request, "orcs/adicionar-desconto.html", {"form": form, "orcamento": orcamento, "desconto_ant": atividade})


def editar_proposta(request, codorcam):
    detalhes_orcamento = obter_dados_gerais_orc(codorcam)
    orcamento = g01Orcamento.objetos.get(pk=int(codorcam))
    empresas_contato = e06ContCad.objetos.filter(
        contato=detalhes_orcamento['codcliente']).order_by('empresa_id')
    # Tuple das escolhas do campo empresa do formulário
    nomes_empresas = [(empresa.id, e01Cadastros.objetos.get(
        id=empresa.empresa_id).descrcad) for empresa in empresas_contato]
    # Caso o usuário não escolha nenhuma empresa
    escolhas_empresas_list = [('0', '')]
    for empresa in nomes_empresas:
        escolhas_empresas_list.append(tuple(empresa))
    escolhas_empresas_tup = tuple(escolhas_empresas_list)
    form = formEditarProposta(escolhas_empresas=escolhas_empresas_tup)
    if request.method == "POST":
        #atualizar_custos_orc(codorcam)
        form = formEditarProposta(request.POST, escolhas_empresas=escolhas_empresas_tup)
        if form.is_valid():
            orcamento = g01Orcamento.objetos.get(pk=int(codorcam))
            cliente = e01Cadastros.objetos.get(id=e04EndCad.objetos.get(id=orcamento.ender_id).cadastro_id)
            cliente.fantasia = form.cleaned_data['tratamento']
            cliente.descrcad = form.cleaned_data['nomeCliente']
            if int(request.POST['empresa']) != 0: cliente.empresa = int(request.POST['empresa'])
            cliente.save()
            try:
                orcamento.prazo = int(form.cleaned_data['prazoObra'])
                prazoValidade = int(form.cleaned_data['prazoValidade'])
            except:
                messages.info(request, "Erro, Certifique que os prazos são válidos")
                return render(request,"orcs/editar-proposta.html",
                              {"orcamento": orcamento, "form": form, "codorcam": codorcam})
            today = datetime.date.today()
            orcamento.dtval = datetime.date.today() + datetime.timedelta(days=prazoValidade)
            if request.POST['vendedor']:
                orcamento.vended_id = request.POST['vendedor']
            if request.POST['condPgto']:
                orcamento.plpgto_id = request.POST['condPgto']
            orcamento.save()
            strcodorc = str(codorcam)
            tipo_proposta = int(request.POST['tipo_proposta'])
            show_index = int(request.POST['show_index'])
            return HttpResponseRedirect(reverse('orcs:imp_proposta', args=(strcodorc, tipo_proposta, show_index)))
        else:
            orcamento_template = {
                "prazoObra": orcamento.prazo,
                "prazoValidade": abs(datetime.date.today() - orcamento.dtval).days
            }
            messages.info(request, "Erro ao validar os dados do formulário")
            return render(request,"orcs/editar-proposta.html",
                          {"orcamento": detalhes_orcamento, "form": form, "codorcam": codorcam})
    else:
        orcamento_template = {
            "prazoObra": orcamento.prazo,
            "prazoValidade": abs(datetime.date.today() - orcamento.dtval).days}
        return render(request,"orcs/editar-proposta.html", {
            "orcamento": detalhes_orcamento, "dadosOrcamento": orcamento_template, 
            "form": form, "codorcam": codorcam})


def imp_proposta(request, codorcam, tipo_proposta, show_index):
    orcamento = obter_dados_gerais_orc(codorcam)
    bd_orc = g01Orcamento.objetos.get(id=codorcam)
    cliente = e01Cadastros.objetos.get(id=orcamento['codcliente'])
    vendedor = c01Usuarios.objetos.get(id=bd_orc.vended_id)
    usuario_vendedor = User.objects.get(username=vendedor.nomeusr)
    nome_vendedor = f"{usuario_vendedor.first_name} {usuario_vendedor.last_name}"
    email_vendedor = usuario_vendedor.email
    telefone_vendedor = vendedor.fone
    telefone_vendedor = f"({telefone_vendedor[:2]}) {telefone_vendedor[2:7]}-{telefone_vendedor[-4:]}"
    if cliente.contempresa == None:
        dados_proposta = {
            "tratamento": cliente.fantasia,
            "cliente": cliente.descrcad,
            "genero": cliente.genero,
            "enderecoObra": orcamento['endereco'],
            "condPgto": a19PlsPgtos.objetos.get(id=bd_orc.plpgto_id).descricaoexterna,
            "prazoObra": bd_orc.prazo,
            "prazoValidade": bd_orc.dtval,
            "vendedor": nome_vendedor,
            "telefoneVendedor": telefone_vendedor,
            "email_vendedor": email_vendedor
        }
    else:
        empresa_contato = e06ContCad.objetos.get(id=int(cliente.contempresa)).empresa_id
        empresa = e01Cadastros.objetos.get(id=empresa_contato)
        dados_proposta = {
            "tratamento": cliente.fantasia,
            "cliente": cliente.descrcad,
            "genero": cliente.genero,
            "genero_empresa": empresa.genero,
            "empresa": empresa.descrcad,
            "enderecoObra": orcamento['endereco'],
            "condPgto": a19PlsPgtos.objetos.get(id=bd_orc.plpgto_id).descricao,
            "prazoObra": bd_orc.prazo,
            "prazoValidade": bd_orc.dtval,
            "vendedor": nome_vendedor,
            "telefoneVendedor": telefone_vendedor,
            "email_vendedor": email_vendedor
        }
    # Obter EAP do Orcamento
    eaps_budget = g03EapOrc.objetos.filter(orcamento_id=bd_orc.id).only('codeap', 'descitem', 'qtdorc', 'vlrunit').order_by('codeap')
    budget_deliveries = []
    budget_services = []
    total_budget_amount = 0
    for eap in eaps_budget:
        if eap.tipo == 5:
            budget_deliveries.append(
                {
                    "codEap": eap.codeap,
                    "descricao": str(eap.descitem).lower()
                }
            )
        elif eap.tipo == 3:
            eap.qtdorc = round(eap.qtdorc, 2)
            eap.vlrunit = round(eap.vlrunit, 2)
            eap.vlrtot = round(float(eap.vlrunit) * float(eap.qtdorc), 2)
            eap.vlrtot_formated = formatar_com_duas_casas_string(formatar_custos_para_template(eap.vlrtot))
            budget_services.append(eap)
            total_budget_amount += eap.vlrtot
    total_budget_amount = formatar_com_duas_casas_string(formatar_custos_para_template(total_budget_amount))
    budget_inputs_list = []
    raw_query_insumo =  """
                        SELECT main_g05inseap.id, main_g05inseap.eap_id,
                                main_a11insumos.descricao AS descricao, main_a11insumos.codigo AS codigo,
                                main_a10catsinsumos.id AS categoria
                        FROM main_g05inseap 
                        INNER JOIN main_a11insumos ON main_a11insumos.id = main_g05inseap.insumo_id
                        INNER JOIN main_a10catsinsumos ON main_a10catsinsumos.id = main_a11insumos.catins_id
                        WHERE main_g05inseap.eap_id = %s
                        ORDER BY main_g05inseap.eap_id
                        """
    budget_inputs = [g05InsEAP.objetos.raw(raw_query_insumo, [eap.id]) for eap in budget_services]
    # Não listar valor em dinheiro, gasolina, serralheiro e etc.
    insumos_nao_mostrar = [1, 405, 1152, 1163, 400, 6164, 6201, 6300, 6302, 6306, 6307, 6308, 6309,
                           6325, 6326, 6327, 6328, 6329, 14217]
    chapas_zincadas = False
    for query_inputs in budget_inputs:
        for insumo in query_inputs:
            if not insumo.codigo in insumos_nao_mostrar:
                # Não mostrar insumos repetidos
                insumos_nao_mostrar.append(insumo.codigo)
                budget_inputs_list.append(
                    {
                        'codigo': insumo.codigo,
                        'descricao': insumo.descricao})
                if insumo.categoria == 63:
                    chapas_zincadas = True
    budget_inputs_list_ordered = sorted(budget_inputs_list, key=lambda k: k['descricao'])
    meses = [0, "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    mesHoje = meses[int(datetime.date.today().strftime("%m"))]
    today = datetime.date.today().strftime(f"%d de {mesHoje} de %Y")
    # Alterar status do orçamento
    bd_orc.fase_id = 3
    bd_orc.save()
    return render(request, "orcs/imp-proposta.html",
                {"dadosProposta": dados_proposta, "eapProp": budget_services,
                 "insumos": budget_inputs_list_ordered, "totalProposta": total_budget_amount, "today": today,
                "listDescricoesOrc": budget_deliveries, "tipoProposta": tipo_proposta, "chapasZincadas": chapas_zincadas,
                "showIndex": show_index})


def editar_contrato(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    request.session['codorcam'] = codorcam
    empresas_contato = e06ContCad.objetos.filter(
        contato=orcamento['codcliente']).order_by('empresa_id')
    # Tuple das escolhas do campo empresa do formulário
    nomes_empresas = [(empresa.id, e01Cadastros.objetos.get(
        id=empresa.empresa_id).descrcad) for empresa in empresas_contato]
    # Caso o usuário não escolha nenhuma empresa
    escolhas_empresas_list = [('0', '')]
    for empresa in nomes_empresas:
        escolhas_empresas_list.append(tuple(empresa))
    escolhas_empresas_tup = tuple(escolhas_empresas_list)
    form = formEditarContrato(escolhas_empresas=escolhas_empresas_tup)
    # Dados do Orçamento
    list_telefones = e02FonesCad.objetos.filter(
        cadastro_id=orcamento['codcliente'])
    telefone = '' if list_telefones.count() == 0 else list_telefones[0].numero
    obj_orcamento = g01Orcamento.objetos.get(id=codorcam)
    obj_cliente = e01Cadastros.objetos.get(id=orcamento['codcliente'])
    # Dicionário de dados
    dic_dados_orcamento = {
        "codCliente": orcamento['codcliente'],
        "nome": orcamento['nomecliente'],
        "cnpj": obj_cliente.cnpj,
        "telefone": telefone,
        "endereco": orcamento['endereco'],
        "prazoObra": obj_orcamento.prazo
    }
    if request.method == "POST":
        form = formEditarContrato(
            request.POST, escolhas_empresas=escolhas_empresas_tup)
        if form.is_valid():
            orcamento = g01Orcamento.objetos.get(pk=int(codorcam))
            cliente = e01Cadastros.objetos.get(
                id=e04EndCad.objetos.get(id=orcamento.ender_id).cadastro_id)
            cliente.descrcad = form.cleaned_data['nomeCliente']
            cliente.cnpj = form.cleaned_data['cnpj']
            if int(request.POST['empresa']) != 0: cliente.empresa = int(request.POST['empresa'])
            cliente.save()
            # Listar os telefones e alterar 1 deles para o novo número
            list_telefones = e02FonesCad.objetos.filter(cadastro_id=cliente.id)
            telefone = form.cleaned_data['telefone']
            # Conferir se o telefone está no formato correto
            telefone_filters = filter(lambda character: character.isdigit(), telefone)
            telefone_numbers = [tel for tel in telefone_filters]
            telefone_bd = "".join(telefone_numbers)
            if list_telefones.count() >= 1:
                mudar_telefone = list_telefones[0]
                mudar_telefone.numero = telefone_bd
                mudar_telefone.save()
            else:
                e02FonesCad.novofonecad(
                    e02FonesCad, cliente.id, telefone_bd)
            try:
                orcamento.prazo = int(form.cleaned_data['prazoObra'])
            except:
                messages.info(
                    request, "Erro, Certifique se o prazo da obra é valido")
                return render(request, "orcs/editar-contrato.html",
                              {"orcamento": dic_dados_orcamento, "form": form, "codorcam": codorcam})
            orcamento.plpgto_id = request.POST['condPgto']
            orcamento.vended_id = request.POST['vendedor']
            orcamento.save()
            strcodorc = str(codorcam)
            return HttpResponseRedirect(reverse('orcs:imp_contrato', args=(strcodorc,)))
        else:
            messages.info(request, "Erro ao validar os dados do formulário")
            return render(request, "orcs/editar-contrato.html",
                          {"orcamento": dic_dados_orcamento, "form": form, "codorcam": codorcam})
    return render(request,"orcs/editar-contrato.html",
                  {"orcamento": dic_dados_orcamento, "form": form, "codorcam": codorcam})


def imp_contrato(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    bd_orc = g01Orcamento.objetos.get(id=codorcam)
    desc_orc = g03EapOrc.objetos.filter(
        orcamento_id=bd_orc.id).order_by('codeap')
    # Títulos e subtítulos da eap do orcamento
    list_desc_orc = []
    for descricao in desc_orc:
        if len(descricao.codeap) <= 5:
            dic_eap_orc = {
                "codEap": descricao.codeap,
                "descricao": str(descricao.descitem).lower()
            }
            list_desc_orc.append(dic_eap_orc)
    pular_pagina_obj = 'sim' if len(list_desc_orc) > 4 else 'nao'
    cliente = e01Cadastros.objetos.get(id=orcamento['codcliente'])
    if cliente.contempresa == '':
        # telefones pessoa física
        obj_telefones = e02FonesCad.objetos.filter(cadastro_id=cliente.id)
        list_telefones = [telefone.numero for telefone in obj_telefones]
        if list_telefones == []:
            list_telefones = [0]
        dados_proposta = {
            "tratamento": cliente.fantasia,
            "cliente": cliente.descrcad,
            "cpf": cliente.cnpj,
            "genero": cliente.genero,
            "enderecoObra": orcamento['endereco'],
            "telefone": list_telefones[0],
            "condPgto": a19PlsPgtos.objetos.get(id=bd_orc.plpgto_id).descricao,
            "prazoObra": bd_orc.prazo,
            "prazoValidade": bd_orc.dtval,
            "vendedor": c01Usuarios.objetos.get(id=bd_orc.vended_id).nomeusr,
        }
    else:
        empresa_contato = e06ContCad.objetos.get(
            id=int(cliente.contempresa)).empresa_id
        empresa = e01Cadastros.objetos.get(id=empresa_contato)
        # telefones da empresa
        obj_telefones = e02FonesCad.objetos.filter(cadastro_id=empresa.id)
        list_telefones = [telefone.numero for telefone in obj_telefones]
        if list_telefones == []: list_telefones = [0]
        telefone = list_telefones[0]
        telefone_str = f"({telefone[:2]}){telefone[2:6]}-{telefone[6:]}" if len(telefone) == 10 else f"({telefone[:2]}){telefone[2:7]}-{telefone[7:]}"
        # endereço da empresa
        obj_enderecos = e04EndCad.objetos.filter(cadastro_id=empresa.id)
        list_complementos = [endereco.complend for endereco in obj_enderecos]
        list_id_logradoros = [endereco.lograd_id for endereco in obj_enderecos]
        list_logradoros = [a06Lograds.objetos.filter(id=id_logradoro).logradouro for id_logradoro in list_id_logradoros]
        list_id_bairros = [a06Lograds.objetos.filter(id=id_logradoro).bairro_id for id_logradoro in list_id_logradoros]
        list_bairros = [a05Bairros.objetos.filter(id=id_bairro).bairro for id_bairro in list_id_bairros]
        list_id_municipios = [a05Bairros.objetos.filter(id=id_bairro).municipio_id for id_bairro in list_id_bairros]
        list_municipios = [a04Municipios.objetos.filter(id=id_municipio).municipio for id_municipio in list_id_municipios]
        list_id_estados = [a04Municipios.objetos.filter(id=id_municipio).estado_id for id_municipio in list_id_municipios]
        list_estados = [a03Estados.objetos.filter(id=id_estado).uf for id_estado in list_id_estados]
        # montar a string do endereço, pegar somente o primeiro endereço
        # talvez mais tarde implementar um choice field para selecionar o endereço
        try:
            endereco_empresa = f"{list_logradoros[0]}, {list_complementos[0]} - {list_bairros[0]} {list_municipios[0]} - {list_estados[0]}"
        except IndexError:
            endereco_empresa = ""
        # montar a string do cnpj -> 00.000.000/0000-00
        cnpj = str(empresa.cnpj)
        string_cnpj = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"
        dados_proposta = {
            "tratamento": cliente.fantasia,
            "cliente": cliente.descrcad,
            "genero": cliente.genero,
            "empresa": empresa.descrcad,
            "cnpj": string_cnpj,
            "enderecoEmpresa": endereco_empresa,
            "telefone": list_telefones[0],
            "enderecoObra": orcamento['endereco'],
            "condPgto": a19PlsPgtos.objetos.get(id=bd_orc.plpgto_id).descricao,
            "prazoObra": bd_orc.prazo,
            "prazoValidade": bd_orc.dtval,
            "vendedor": c01Usuarios.objetos.get(id=bd_orc.vended_id).nomeusr,
        }
    # Identificar o número de parcelas
    numero_parcelas = 6
    if numero_parcelas > 5 and numero_parcelas < 7:
        pular_pagina_parc = 'sim1'
    elif numero_parcelas >= 7 and numero_parcelas <= 8:
        pular_pagina_parc = 'sim2'
    elif numero_parcelas > 8 and numero_parcelas < 11:
        pular_pagina_parc = 'sim3'
    else:
        pular_pagina_parc = 'nao'
    meses = [0, "janeiro", "fevereiro", "março", "abril", "maio", "junho",
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    mesHoje = meses[int(datetime.date.today().strftime("%m"))]
    today = datetime.date.today().strftime(f"%d de {mesHoje} de %Y")
    # Alterar status do orçamento
    bd_orc.fase_id = 4
    bd_orc.save()
    return render(request, "orcs/imp-contrato.html", 
                {"dadosProposta":dados_proposta, "today": today,
                 "listDescricoesOrc": list_desc_orc, "pularPaginaObj": pular_pagina_obj,
                 "pularPaginaParc": pular_pagina_parc,
                 })


def venezianas(request, codigo_orcamento):
    if request.method == "POST":
        forms = [formMedidasVenezianas(request.POST, prefix=i) for i in range(1, int(request.POST['totalVaos']) + 1)]
        if all((form.is_valid() for form in forms)):
            venezianas = []
            for index, form  in enumerate(forms):
                if form.cleaned_data['base'] != "" and form.cleaned_data['altura'] != "" and form.cleaned_data['repeticoes'] != "" and form.cleaned_data['rebite'] != "":
                    dict_veneziana = {
                        'vao': index + 1,
                        'base': form.cleaned_data['base'],
                        'altura': form.cleaned_data['altura'],
                        'repeticoes': form.cleaned_data['repeticoes'],
                        'rebite': form.cleaned_data['rebite'],
                    }
                    venezianas.append(dict_veneziana)
            codigo_aleta = request.POST['aleta']
            codigo_selante = request.POST['1-selante']

            if venezianas == [] or codigo_aleta == "":
                return HttpResponse(status=400)
            try:
                ultimo_numero_eap = int(g03EapOrc.objetos.filter(orcamento_id=codigo_orcamento).only("id", "codeap").order_by('-id')[0].codeap[:1])
            except IndexError:
                ultimo_numero_eap = 0
            quantitativo = orc_venezianas(codigo_aleta, codigo_selante, ultimo_numero_eap + 1, *venezianas)
            inserir_dados_eap(request, *quantitativo)
            atualizar_lista_insumos(codigo_orcamento)
            # # Atualizar custos do orcamento
            # #atualizar_custos_orc(cod_orc_atual)
            return HttpResponse(status=201)
        else:
            for form in forms:
                print(f"\n\n{form.errors.as_data}\n\n")
            return HttpResponse(status=400)
    elif request.method == "GET":
        form = formMedidasVenezianas(prefix=1)
        orcamento = obter_dados_gerais_orc(codigo_orcamento)
        aletas = a11Insumos.objetos.filter(catins_id=48)
        return render(request, "orcs/orcamento-venezianas.html", {"orcamento": orcamento,
                                                            "aletas": aletas, "form": form})
    else:
        return HttpResponse(status=405)


def adicionar_mais_vaos_veneziana(request, numberOfRows):
    form = formMedidasVenezianas(prefix=numberOfRows)
    return render(request, 'orcs/orcamento-venezianas-vaos.html',
        {"form": form})


def orc_telha_trapezoidal_fixo(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    codOrcAtual = request.session['codorcamento']
    if request.POST:
        form = formOrcamentoTelhaTrapezoidalFixo(request.POST)
        if form.is_valid():
            dados_para_calculos = {
                'codigo_telha': request.POST['telha'],
                'codigo_parafuso_costura': request.POST['parafuso_costura'],
                'codigo_parafuso_fixacao': request.POST['parafuso_fixacao'],
                'codigo_selante': request.POST['selante'],
                'codigo_perfil_estrutural_externo': request.POST['perfil_estrutural_externo'],
                'codigo_perfil_estrutural_interno': request.POST['perfil_estrutural_interno'],
                'codigo_rufo': request.POST['rufo'],
                'codigo_calha': request.POST['calha'],
                'codigo_pintura': request.POST['tipo_pintura'],
                'quantidade_pintura': form.cleaned_data['quantidade_pintura'] if form.cleaned_data['quantidade_pintura'] else 0,
                'quantidade_modulos': 1,
                'comprimento': form.cleaned_data['comprimento'],
                'largura': form.cleaned_data['largura'],
                'declividade': form.cleaned_data['declividade'],
                'repeticoes': form.cleaned_data['repeticoes'],
                'distancia_entre_apoios': form.cleaned_data['distancia_entre_apoios'],
                'distancia_entre_maos_f': form.cleaned_data['distancia_entre_maos_f'] if form.cleaned_data['distancia_entre_maos_f'] else 0,
                'montante': form.cleaned_data['montante'],
                'jusante': form.cleaned_data['jusante'],
                'lateral_esquerda': form.cleaned_data['lateral_esquerda'],
                'lateral_direita': form.cleaned_data['lateral_direita'],
                'dias_serralheiro': form.cleaned_data['dias_serralheiro'],
                'quantidade_serralheiro': form.cleaned_data['quantidade_serralheiro'],
                'dias_auxiliar': form.cleaned_data['dias_auxiliar'],
                'quantidade_auxiliar': form.cleaned_data['quantidade_auxiliar'],
                'dificuldade': form.cleaned_data['dificuldade'],
                'aproveitar_estrutura': form.cleaned_data['aproveitar_estrutura'],
                'estrutura': 0}
            try:
                ultNumItemEAP = int((
                    g03EapOrc.objetos.filter(orcamento_id=codOrcAtual).order_by('-id')[0].codeap
                    )[:1])
            except:
                ultNumItemEAP = 0
            resultados = orc_telha_trapezoidal(
                f'{ultNumItemEAP+1}.', **dados_para_calculos)
            inserir_dados_eap(request, *resultados)
            atualizar_lista_insumos(codOrcAtual)
            return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
        else:
            messages.info(request, "Erro ao validar os dados do formulário")
            return render(request, "orcs/orcamento-telha-trap-fixo.html", {"form": form, "orcamento": orcamento, })

    else:
        form = formOrcamentoTelhaTrapezoidalFixo()
        return render(request, "orcs/orcamento-telha-trap-fixo.html", {"form":form, "orcamento": orcamento,})


def orc_multi_click_plano_fixo(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    codOrcAtual = request.session['codorcamento']
    if request.POST:
        form = formOrcamentoMultiClickPlanoFixo(request.POST)
        if form.is_valid():
            codigo_perfil_multi_click = request.POST['chapa']
            dados_para_calculos = {
                'codigo_perfil_multi_click': request.POST['chapa'],
                'codigo_perfil_arremate': request.POST['perfil_arremate'],
                'codigo_tampa': request.POST['tampa'],
                'codigo_garra': request.POST['garra'],
                'codigo_fita': request.POST['fita'],
                'codigo_selante': request.POST['selante'],
                'codigo_parafuso_arremate': request.POST['parafuso_arremate'],
                'codigo_parafuso_terca': request.POST['parafuso_terca'],
                'codigo_perfil_estrutural_externo': request.POST['perfil_estrutural_externo'],
                'codigo_perfil_estrutural_interno': request.POST['perfil_estrutural_interno'],
                'codigo_rufo': request.POST['rufo'],
                'codigo_calha': request.POST['calha'],
                'quantidade_modulos': 1,
                'codigo_pintura': request.POST['tipo_pintura'],
                'quantidade_pintura': form.cleaned_data['quantidade_pintura'] if form.cleaned_data['quantidade_pintura'] else 0,
                'comprimento': form.cleaned_data['comprimento'],
                'largura': form.cleaned_data['largura'],
                'declividade': form.cleaned_data['declividade'],
                'repeticoes': form.cleaned_data['repeticoes'],
                'distancia_entre_apoios': form.cleaned_data['distancia_entre_apoios'],
                'distancia_entre_maos_f': form.cleaned_data['distancia_entre_maos_f'] if form.cleaned_data['distancia_entre_maos_f'] else 0,
                'montante': form.cleaned_data['montante'],
                'jusante': form.cleaned_data['jusante'],
                'lateral_esquerda': form.cleaned_data['lateral_esquerda'],
                'lateral_direita': form.cleaned_data['lateral_direita'],
                'dias_serralheiro': form.cleaned_data['dias_serralheiro'],
                'quantidade_serralheiro': form.cleaned_data['quantidade_serralheiro'],
                'dias_auxiliar': form.cleaned_data['dias_auxiliar'],
                'quantidade_auxiliar': form.cleaned_data['quantidade_auxiliar'],
                'dificuldade': form.cleaned_data['dificuldade'],
                'aproveitar_estrutura': form.cleaned_data['aproveitar_estrutura'],
                'estrutura': 0}
            try:
                ultNumItemEAP = int((
                    g03EapOrc.objetos.filter(orcamento_id=codOrcAtual).order_by('-id')[0].codeap
                    )[:1])
            except:
                ultNumItemEAP = 0
            resultados = orc_multi_click_plano(
                f'{ultNumItemEAP+1}.', **dados_para_calculos)
            inserir_dados_eap(request, *resultados)
            atualizar_lista_insumos(codOrcAtual)
            return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
        else:
            messages.info(request, "Erro ao validar os dados do formulário")
            return render(request, "orcs/orcamento-multi-click-plano-fixo.html", {"form": form, "orcamento": orcamento, })

    else:
        form = formOrcamentoMultiClickPlanoFixo()
        return render(request, "orcs/orcamento-multi-click-plano-fixo.html", {"form":form, "orcamento": orcamento,})


def dicionario_de_policarbonato(form):
    dados_policarbonato = {
        'cod_policarbonato': form.cleaned_data['tipo_policarbonato'].codigo,
        'cod_perfil_uniao': form.cleaned_data['tipo_perfil_uniao'].codigo,
        'cod_perfil_arremate': form.cleaned_data['tipo_perfil_arremate'].codigo,
        'cod_perfil_u': form.cleaned_data['tipo_perfil_u'].codigo,
        'cod_guarnicao': form.cleaned_data['tipo_guarnicao'].codigo,
        'cod_gaxeta': form.cleaned_data['tipo_gaxeta'].codigo,
        'cod_fita_vent': form.cleaned_data['tipo_fita_vent'].codigo,
        'cod_fita_aluminio': form.cleaned_data['tipo_fita_aluminio'].codigo,
        'cod_selante': form.cleaned_data['tipo_selante'].codigo,
    }
    return dados_policarbonato


def dicionario_de_estrutura(form):
    dados_estrutura = {
        'cod_perfil_estrutural_externo': form.cleaned_data['tipo_perfil_externo'].codigo,
        'cod_perfil_estrutural_interno': form.cleaned_data['tipo_perfil_interno'].codigo,
        'cod_chapa_rufo': form.cleaned_data['chapa_rufo'].codigo,
        'cod_chapa_calha': form.cleaned_data['chapa_calha'].codigo,
        'cod_pintura': form.cleaned_data['tipo_pintura'].codigo,
        'quantidade_pintura': form.cleaned_data['quantidade_pintura'] if form.cleaned_data['quantidade_pintura'] else 0,
        'montante': form.cleaned_data['montante'],
        'jusante': form.cleaned_data['jusante'],
        'lateral_esquerda': form.cleaned_data['lateral_esquerda'],
        'lateral_direita': form.cleaned_data['lateral_direita'],
        'dias_serralheiro': form.cleaned_data['dias_serralheiro'],
        'quantidade_serralheiro': form.cleaned_data['quantidade_serralheiro'],
        'dias_auxiliar': form.cleaned_data['dias_auxiliar'],
        'quantidade_auxiliar': form.cleaned_data['quantidade_auxiliar'],
        'dificuldade': form.cleaned_data['dificuldade'],
        'aproveitar_estrutura': form.cleaned_data['aproveitar_estrutura'],
    }
    return dados_estrutura


def dicionario_de_estrutura_curva(form):
    dados_estrutura_curva = {
        'cod_calandra': form.cleaned_data['tipo_calandra'].codigo
    }
    return dados_estrutura_curva


def dicionario_de_dimensoes_planas(form):
    dados_dimensoes = {
        'comprimento_cobertura': form.cleaned_data['comprimento_cobertura'],
        'largura_cobertura': form.cleaned_data['largura_cobertura'],
        'declividade_cobertura': form.cleaned_data['declividade_cobertura'],
        'repeticoes_cobertura': form.cleaned_data['repeticoes_cobertura'] if form.cleaned_data['repeticoes_cobertura'] > 0 else 1,
        'distancia_apoios_cobertura': form.cleaned_data['distancia_apoios_cobertura'],
        'quantidade_maos_francesas': form.cleaned_data['quantidade_maos_francesas'] if form.cleaned_data['quantidade_maos_francesas'] else 0,
    }
    return dados_dimensoes


def dicionario_de_dimensoes_curvas(form):
    dados_dimensoes = {
        'corda_cobertura': form.cleaned_data['corda_cobertura'],
        'flecha_cobertura': form.cleaned_data['flecha_cobertura'],
        'largura_cobertura': form.cleaned_data['largura_cobertura'],
        'repeticoes_cobertura': form.cleaned_data['repeticoes_cobertura'] if form.cleaned_data['repeticoes_cobertura'] > 0 else 1,
        'distancia_apoios_cobertura': form.cleaned_data['distancia_apoios_cobertura'],
        'quantidade_maos_francesas': form.cleaned_data['quantidade_maos_francesas'] if form.cleaned_data['quantidade_maos_francesas'] else 0,
    }
    return dados_dimensoes


def dicionario_cobertura_retratil(form):
    dados_retratil = {
        'cod_motor': form.cleaned_data['tipo_motor'].codigo,
        'quantidade_motor': form.cleaned_data['quantidade_motor'],
        'quantidade_modulos': form.cleaned_data['quantidade_modulos'],
        'quantidade_modulos_moveis': form.cleaned_data['quantidade_modulos_moveis'],
        'direcao_movimento': form.cleaned_data['direcao_movimento'],
        'cod_cantoneira': form.cleaned_data['tipo_cantoneira'].codigo,
        'cod_perfil_cantoneira': form.cleaned_data['tipo_perfil_cantoneira'].codigo,
        'cod_roldana': form.cleaned_data['tipo_roldana'].codigo
    }
    return dados_retratil


def poli_plano_fix(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    if request.method == "POST":
        form_policarbonato = FormChapasPolicarbonato(request.POST)
        form_estrutura = FormEstruturaCobertura(request.POST)
        form_dimensoes = FormMedidasCoberturaPlana(request.POST)
        forms = [form_policarbonato, form_estrutura, form_dimensoes]
        if all(form.is_valid() for form in forms):
            dados_orcamento = {
                'dados_policarbonato': dicionario_de_policarbonato(form_policarbonato),
                'dados_estrutura': dicionario_de_estrutura(form_estrutura),
                'dados_dimensoes': dicionario_de_dimensoes_planas(form_dimensoes)
            }
            try:
              ultNumItemEAP = int((g03EapOrc.objetos.filter(orcamento_id=codorcam).order_by('-id')[0].codeap)[:1])
            except:
              ultNumItemEAP = 0
            resultados = orc_poli_plano(f'{ultNumItemEAP+1}.', **dados_orcamento)
            inserir_dados_eap(request, *resultados)
            ##Atualizar custos do orcamento
            ##GERANDO O ERRO 504 PELA DEMORA, FAZER O PROCESSO SEPARADO
            #atualizar_custos_orc(codorcam)
            atualizar_lista_insumos(codorcam)
            return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
        else:
            for form in forms:
                print(f"\n {form.errors.as_data} \n")
            return HttpResponse(status=400)
    elif request.method == "GET":
        form_policarbonato = FormChapasPolicarbonato()
        form_estrutura = FormEstruturaCobertura()
        form_dimensoes = FormMedidasCoberturaPlana()
        return render(request, "orcs/orcamento-chapa-policarbonato.html", {
            "formPolicarbonato": form_policarbonato,
            "formEstrutura": form_estrutura,
            "formDimensoes": form_dimensoes,
            "orcamento": orcamento,})
    else:
        HttpResponse(status=405)


def poli_plano_ret(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    if request.method == "POST":
        form_policarbonato = FormChapasPolicarbonato(request.POST)
        form_estrutura = FormEstruturaCobertura(request.POST)
        form_dimensoes = FormMedidasCoberturaPlana(request.POST)
        form_retratil = FormCoberturaRetratil(request.POST)
        forms = [form_policarbonato, form_estrutura, form_dimensoes, form_retratil]
        if all(form.is_valid() for form in forms):
            dados_orcamento = {
                'dados_policarbonato': dicionario_de_policarbonato(form_policarbonato),
                'dados_estrutura': dicionario_de_estrutura(form_estrutura),
                'dados_dimensoes': dicionario_de_dimensoes_planas(form_dimensoes),
                'dados_retratil': dicionario_cobertura_retratil(form_retratil)
            }
            try:
              ultNumItemEAP = int((g03EapOrc.objetos.filter(orcamento_id=codorcam).order_by('-id')[0].codeap)[:1])
            except:
              ultNumItemEAP = 0
            resultados = orc_poli_plano(f'{ultNumItemEAP+1}.', **dados_orcamento)
            inserir_dados_eap(request, *resultados)
            ##Atualizar custos do orcamento
            ##GERANDO O ERRO 504 PELA DEMORA, FAZER O PROCESSO SEPARADO
            #atualizar_custos_orc(codorcam)
            atualizar_lista_insumos(codorcam)
            return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
        else:
            for form in forms:
                print(f"\n {form.errors.as_data} \n")
            return HttpResponse(status=400)
    elif request.method == "GET":
        form_policarbonato = FormChapasPolicarbonato()
        form_estrutura = FormEstruturaCobertura()
        form_dimensoes = FormMedidasCoberturaPlana()
        form_retratil = FormCoberturaRetratil()
        return render(request, "orcs/orcamento-chapa-policarbonato.html", {
            "formPolicarbonato": form_policarbonato,
            "formEstrutura": form_estrutura,
            "formDimensoes": form_dimensoes,
            "formRetratil": form_retratil,
            "orcamento": orcamento,})
    else:
        HttpResponse(status=405)


def poli_curvo_fix(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    if request.method == "POST":
        form_policarbonato = FormChapasPolicarbonato(request.POST)
        form_estrutura = FormEstruturaCobertura(request.POST)
        form_estrutura_curva = FormEstruturaCoberturaCurva(request.POST)
        form_dimensoes = FormMedidasCoberturaCurva(request.POST)
        forms = [form_policarbonato, form_estrutura, form_estrutura_curva, form_dimensoes]
        if all(form.is_valid() for form in forms):
            dados_orcamento = {
                'dados_policarbonato': dicionario_de_policarbonato(form_policarbonato),
                'dados_estrutura': dicionario_de_estrutura(form_estrutura),
                'dados_estrutura_curva': dicionario_de_estrutura_curva(form_estrutura_curva),
                'dados_dimensoes': dicionario_de_dimensoes_curvas(form_dimensoes)
            }
            try:
              ultNumItemEAP = int((g03EapOrc.objetos.filter(orcamento_id=codorcam).order_by('-id')[0].codeap)[:1])
            except:
              ultNumItemEAP = 0
            resultados = orc_poli_curvo(f'{ultNumItemEAP+1}.', **dados_orcamento)
            inserir_dados_eap(request, *resultados)
            ##Atualizar custos do orcamento
            ##GERANDO O ERRO 504 PELA DEMORA, FAZER O PROCESSO SEPARADO
            #atualizar_custos_orc(codorcam)
            atualizar_lista_insumos(codorcam)
            return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
        else:
            for form in forms:
                print(f"\n {form.errors.as_data} \n")
            return HttpResponse(status=400)
    elif request.method == "GET":
        form_policarbonato = FormChapasPolicarbonato()
        form_estrutura = FormEstruturaCobertura()
        form_estrutura_curva = FormEstruturaCoberturaCurva()
        form_dimensoes = FormMedidasCoberturaCurva()
        return render(request, "orcs/orcamento-chapa-policarbonato.html", {
            "formPolicarbonato": form_policarbonato,
            "formEstrutura": form_estrutura,
            "formEstruturaCurva": form_estrutura_curva,
            "formDimensoes": form_dimensoes,
            "orcamento": orcamento})
    else:
        HttpResponse(status=405)


def poli_curvo_ret(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    if request.method == "POST":
        form_policarbonato = FormChapasPolicarbonato(request.POST)
        form_estrutura = FormEstruturaCobertura(request.POST)
        form_estrutura_curva = FormEstruturaCoberturaCurva(request.POST)
        form_dimensoes = FormMedidasCoberturaCurva(request.POST)
        form_retratil = FormCoberturaRetratil(request.POST)
        forms = [form_policarbonato, form_estrutura, form_estrutura_curva, form_dimensoes, form_retratil]
        if all(form.is_valid() for form in forms):
            dados_orcamento = {
                'dados_policarbonato': dicionario_de_policarbonato(form_policarbonato),
                'dados_estrutura': dicionario_de_estrutura(form_estrutura),
                'dados_estrutura_curva': dicionario_de_estrutura_curva(form_estrutura_curva),
                'dados_dimensoes': dicionario_de_dimensoes_curvas(form_dimensoes),
                'dados_retratil': dicionario_cobertura_retratil(form_retratil)
            }
            try:
              ultNumItemEAP = int((g03EapOrc.objetos.filter(orcamento_id=codorcam).order_by('-id')[0].codeap)[:1])
            except:
              ultNumItemEAP = 0
            resultados = orc_poli_curvo(f'{ultNumItemEAP+1}.', **dados_orcamento)
            inserir_dados_eap(request, *resultados)
            ##Atualizar custos do orcamento
            ##GERANDO O ERRO 504 PELA DEMORA, FAZER O PROCESSO SEPARADO
            #atualizar_custos_orc(codorcam)
            atualizar_lista_insumos(codorcam)
            return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
        else:
            for form in forms:
                print(f"\n {form.errors.as_data} \n")
            return HttpResponse(status=400)
    elif request.method == "GET":
        form_policarbonato = FormChapasPolicarbonato()
        form_estrutura = FormEstruturaCobertura()
        form_estrutura_curva = FormEstruturaCoberturaCurva()
        form_dimensoes = FormMedidasCoberturaCurva()
        form_retratil = FormCoberturaRetratil()
        return render(request, "orcs/orcamento-chapa-policarbonato.html", {
            "formPolicarbonato": form_policarbonato,
            "formEstrutura": form_estrutura,
            "formEstruturaCurva": form_estrutura_curva,
            "formDimensoes": form_dimensoes,
            "formRetratil": form_retratil,
            "orcamento": orcamento})
    else:
        HttpResponse(status=405)