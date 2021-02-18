import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import HttpResponseRedirect, redirect, render, reverse
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
                    formEditarContrato, formEditarProposta, formEditarTextoEAP,
                    formInserirDeslocamento, formInserirInsumo,
                    formInserirInsumoNaAtividade, formInserirServico,
                    formMarcarVisita, formMedidasVenezianas,
                    formOrcamentoMultiClickPlanoFixo,
                    formOrcamentoTelhaTrapezoidalFixo, formPoliCurvoFix,
                    formPoliCurvoRet, formPoliPlanFix, formPoliPlanRet)


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


def inserir_dados_eap(request, *eapResult):
    codOrcAtual = request.session['codorcamento']
    #atvEapAtual = 0
    novo_codigo_eap = g03EapOrc.proxnumeap(g03EapOrc)
    #nvCodAtvEap = g04AtvEap.proxnumatveap(g04AtvEap)
    for linha in eapResult:
        if linha['Tipo'] > 0:
            nova_eap = g03EapOrc(
                id = novo_codigo_eap,
                orcamento = g01Orcamento.objetos.get(pk=codOrcAtual),
                codeap = linha['Ordenador'],
                coditem = linha['Ordenador'],
                descitem = linha['Descricao'],
                tipo = linha['Tipo'],
                qtdorc = linha['Quant'],
                unidade = linha['Unid'],
                vlrunit = 0
            )
            nova_eap.save()
            if linha['Tipo'] == 1:
                # salvar o id da atividade para lançar insumos
                atividade_atual = novo_codigo_eap
            novo_codigo_eap += 1
        # colocar insumo como tipo -1 no calculos.py
        elif linha['Tipo'] == -1:
            novo_insumo = g05InsEAP(
                eap=g03EapOrc.objetos.get(id=atividade_atual),
                insumo = a11Insumos.objetos.get(codigo=linha['CodInsumo']),
                qtdprod = linha['Quant'],
                qtdimpr = 0
            )
            novo_insumo.save()
        # Quando for necessário, criar a parte de atividade para a eap
        # # Corrigir o erro na hora de adicionar um novo vão de veneziana
        # if linha['CodAtvEAP'] == 5:
        #     atvEapAtual = 0
        # else:
        #     novaEAP = g03EapOrc(
        #                         id = novo_codigo_eap,
        #                         orcamento = g01Orcamento.objetos.get(pk=codOrcAtual),
        #                         codeap = linha['Ordenador'],
        #                         coditem = linha['Ordenador'],
        #                         descitem = linha['Descricao'],
        #                         tipo = linha['Tipo'],
        #                         qtdorc = linha['Quant'],
        #                         unidade = linha['Unid'],
        #                         vlrunit = valor
        #                         )
        #     novaEAP.save()
        #     nvCodEap += 1
        #     if linha['CodAtvEAP'] and linha['CodAtvPad'] > 0:
        #         if linha['CodAtvEAP'] > atvEapAtual:
        #             # Criar atividade padrao para item da EAP
        #             novaAtvEAP = g04AtvEap(
        #                 id = nvCodAtvEap,
        #                 eap = novaEAP,
        #                 atvpadr = a15AtvsPad.objetos.get(pk=linha['CodAtvPad'])
        #             )
        #             novaAtvEAP.save()
        #             nvCodAtvEap += 1
        #             atvEapAtual = linha['CodAtvEAP']
        #         if linha['CodInsumo'] > 0:
        #             # Criar insumo para atividade padrao da EAP
        #             novoInsEAP = g05InsEAP(
        #                 atividade = novaAtvEAP,
        #                 insumo = a11Insumos.objetos.get(codigo=linha['CodInsumo']),
        #                 qtdprod = linha['Quant'],
        #                 qtdimpr=0
        #             )
        #             novoInsEAP.save()


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
    if request.method == 'POST':
        form = formAtualizarDadosInsumo(request.POST)
        if form.is_valid():
            insumo_bd = a11Insumos.objetos.filter(codigo=codInsumo)
            novo_preco = formatar_custos_para_bd(form.cleaned_data['novo_preco']) if form.cleaned_data['novo_preco'] else insumo_bd[0].custo01
            # if form.cleaned_data['novo_preco']:
            #     novo_preco = formatar_custos_para_bd(
            #         form.cleaned_data['novo_preco'])
            # else:
            #     novo_preco = insumo_bd[0].custo01
            nova_descricao = form.cleaned_data['nova_descricao'] if form.cleaned_data['nova_descricao'] else insumo_bd[0].descricao
            nova_unidade = form.cleaned_data['nova_unidade'] if form.cleaned_data['nova_unidade'] else insumo_bd[0].undbas
            nova_espessura = formatar_custos_para_bd(form.cleaned_data['nova_espessura']) if form.cleaned_data['nova_espessura'] else insumo_bd[0].espessura
            novo_comprimento = formatar_custos_para_bd(form.cleaned_data['novo_comprimento']) if form.cleaned_data['novo_comprimento'] else insumo_bd[0].comprimento
            nova_largura = formatar_custos_para_bd(form.cleaned_data['nova_largura']) if form.cleaned_data['nova_largura'] else insumo_bd[0].largura
            nova_categoria = request.POST['nova_cat_insumo'] if request.POST['nova_cat_insumo'] else insumo_bd[0].catins_id
            dataAtualizacao = datetime.date.today()
            a11Insumos.objetos.filter(codigo=codInsumo).update(
                descricao=nova_descricao, 
                undbas=nova_unidade,
                custo01=novo_preco,
                espessura=nova_espessura,
                comprimento=novo_comprimento,
                largura=nova_largura,
                dataatualizacao=dataAtualizacao
            )
            messages.info(request, "Dados atualizados com sucesso")
            strcodorc = str(codorcam)
            #atualizar_custos_orc(codorcam)
            atualizar_lista_insumos(codorcam)
            return HttpResponseRedirect(
                reverse(
                    'orcs:editar_orcamento', args=(strcodorc,)))
        else:
            messages.error(request, "Erro ao atualizar dados do insumo")
            return HttpResponseRedirect(
                reverse(
                    'orcs:atualizar-dados-insumo', 
                    args=(codInsumo,)))
    else:
        form = formAtualizarDadosInsumo()
        insumo = a11Insumos.objetos.get(codigo=codInsumo)
        dicInsumo = {
                     "codigo": insumo.codigo,
                     "antigaDescricao": insumo.descricao,
                     "antigaUnidade": insumo.undbas,
                     "antigoPreco": formatar_custos_para_template(insumo.custo01),
                     "antigaEspessura": insumo.espessura,
                     "antigoComprimento": insumo.comprimento,
                     "antigaLargura": insumo.largura,
                     "antigaCategoria": a10CatsInsumos.objetos.get(id=insumo.catins_id).descricao
                     }
        return render(
            request, "orcs/atualizar-dados-insumo.html", {
                "form": form, "insumo": dicInsumo})


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
    # Gravar marcador
    request.session['marcador'] = 'orcs:preorcamento/'
    # Obter endereco do cliente
    codendsel = int(request.session['codendcliente'])
    # Criar novo orcamento
    # try:
    #     # se o centro de custo não existir
    #     centro_de_custo_orcamento = b04CCustos.objetos.get(id=199)
    # except ObjectDoesNotExist:
    #     try:
    #         # se não existir empresa
    #         empresa_orcamento = b01Empresas.objetos.get(razao="CMM Comércio e Serviços EIRELI")
    #     except:
    #         try:
    #             logradouro_empresa = a06Lograds.objetos.filter(logradouro="Avenida C-104", ceplogr=74250030, bairro=)
    #         empresa_orcamento = b01Empresas(
    #             id=b01Empresas.objetos.latest(id) + 1,
    #             juridica=1,
    #             razao="CMM Comércio e Serviços EIRELI",
    #             fantasia="CAMAMAR",
    #             codemp="CM",
    #             complend="complemento - alterar posteriormente",
    #             cnpj="36186950000108",
    #             inscest="",
    #             lograd=
    #         )
    #     centro_de_custo_orcamento = b04CCustos(
    #         id=199,
    #         funccc=8,
    #         descricao="Orçamentos",
    #         ativo=1,
    #         seqmfhol=1,
    #         empresa=
    #     )
    nvcodorc = g01Orcamento.proxnumorc(g01Orcamento)
    novo_orcamento = g01Orcamento(
        id=nvcodorc,
        ccusto=centro_de_custo_orcamento,
        vended=c01Usuarios.objetos.get(nomeusr=request.user),
        fase=a31FaseOrc.objetos.get(id=1),
        plpgto=a19PlsPgtos.objetos.get(id=1),
        ender=e04EndCad.objetos.get(id=codendsel),
        prazo=15,
        tipofrete=a08TiposFrete.objetos.get(id=5),
        distfrete=10,
        status=a20StsOrcs.objetos.get(id=1)
    )
    novo_orcamento.save()
    request.session['codorcamento'] = nvcodorc
    # Editar orcamento criado
    strcodorc = int(nvcodorc)
    return HttpResponseRedirect(
        reverse('orcs:editar_orcamento', args=(strcodorc,)))


def editar_orcamento(request, codorcam):	
    request.session['marcador'] = 'orcs:preorcamento/'
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
            novo_servico = g03EapOrc(
                id=g03EapOrc.objetos.order_by('id').last().id + 1,
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
    # CORRIGIR ERRO DE TIPO DE EAP PARA VENEZIANAS
    #try:
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
    return render(request, "orcs/editar-orcamento.html", {
        "orcamento": orcamento, "eaporcam": list_eaps,
        "insumos": lista_insumos, "form": formInserirServico
        }
    )


def excluir_orcamento(request, codorcam):
    if request.user.is_staff:
        g01Orcamento.objetos.get(id=int(codorcam)).delete()
    else:
        pass
    return HttpResponseRedirect(reverse('main:inicio'))


# 07-01-2020 -> Se não precisar dessa view até 3 meses apagar
# também apagar o template e a url 
# def inserir_insumo(request, codorcam):
#     # Obter dados gerais do orcamento
#     orcamento = obter_dados_gerais_orc(codorcam)
#     codOrcAtual = request.session['codorcamento']
#     if request.method == "POST":
#         form = formInserirInsumo(request.POST)
#         if 'btnInserir' in request.POST:
#             if form.is_valid():
#                 quantInsumo = float(form.cleaned_data['quantInsumo'])
#                 bdInsumo = a11Insumos.objetos.get(codigo=int(request.POST['combInsumo']))
#                 cod_atividade_padrao = int(request.POST['combAtvPad'])
#                 eaps_do_orcamento = g03EapOrc.objetos.filter(orcamento_id=codOrcAtual).order_by('id')
#                 # Se não tiver eap no orçamento
#                 # A descrição é genérica pois não se sabe o que está sendo orçado
#                 if not eaps_do_orcamento:
#                     primeira_eap = g03EapOrc(
#                                         id = g03EapOrc.proxnumeap(g03EapOrc),
#                                         orcamento = g01Orcamento.objetos.get(pk=codOrcAtual),
#                                         codeap = '1.',
#                                         coditem = '1.',
#                                         descitem = "Cobertura de policarbonato",
#                                         tipo = 5,
#                                         qtdorc = 1,
#                                         unidade = 'un',
#                                         vlrunit = 0
#                                         )
#                     primeira_eap.save()
#                     segunda_eap = g03EapOrc(
#                                        id = g03EapOrc.proxnumeap(g03EapOrc),
#                                        orcamento = g01Orcamento.objetos.get(pk=codOrcAtual),
#                                        codeap = '1.01.',
#                                        coditem = '1.01.',
#                                        descitem = "Cobertura de policarbonato",
#                                        tipo = 3,
#                                        qtdorc = 1,
#                                        unidade = 'un',
#                                        vlrunit = 0
#                                        )
#                     segunda_eap.save()
#                 eaps_do_orcamento = g03EapOrc.objetos.filter(orcamento_id=codOrcAtual).order_by('id')
#                 ultItemEap = eaps_do_orcamento[0].codeap
#                 listaEaps11 = []
#                 for eapOrc in eaps_do_orcamento:
#                     if cod_atividade_padrao == 35 or cod_atividade_padrao == 36 or cod_atividade_padrao == 55:
#                         if (len(eapOrc.codeap) >= 11) and (eapOrc.codeap[6] == '1') and (eapOrc.codeap[0] == ultItemEap[0]):
#                             listaEaps11.append(eapOrc.codeap)
#                         elif len(eapOrc.codeap) == 8 and (eapOrc.codeap[-2:] == '1.'):
#                             atividadeEap = g04AtvEap.objetos.get(eap_id=eapOrc.id)
#                         else:
#                             pass
#                         prefUltimaEap = eapOrc.codeap
#                     elif cod_atividade_padrao == 21 or cod_atividade_padrao == 56:
#                         if (len(eapOrc.codeap) >= 11) and (eapOrc.codeap[6] == '2') and (eapOrc.codeap[0] == ultItemEap[0]):
#                             listaEaps11.append(eapOrc.codeap)
#                         elif len(eapOrc.codeap) == 8 and (eapOrc.codeap[-2:] == '2.'):
#                             atividadeEap = g04AtvEap.objetos.get(eap_id=eapOrc.id)
#                         else:
#                             pass
#                         prefUltimaEap = eapOrc.codeap
#                 try:
#                     ultimaEap = listaEaps11[-1]
#                 except:
#                     if cod_atividade_padrao == 35 or cod_atividade_padrao == 36 or cod_atividade_padrao == 55:
#                         ultimaEap = f'{prefUltimaEap[:2]}01.01.00.'
#                         novaEAP = g03EapOrc(
#                                             id = g03EapOrc.proxnumeap(g03EapOrc),
#                                             orcamento = g01Orcamento.objetos.get(pk=codOrcAtual),
#                                             codeap = f'{prefUltimaEap[:2]}01.01.',
#                                             coditem = f'{prefUltimaEap[:2]}01.01.',
#                                             descitem = f"Policarbonato e acessórios",
#                                             tipo = 2,
#                                             qtdorc = 1,
#                                             unidade = 'un',
#                                             vlrunit = 0
#                                             )
#                         novaEAP.save()
#                     elif cod_atividade_padrao == 21 or cod_atividade_padrao == 56:
#                         ultimaEap = f'{prefUltimaEap[:2]}01.02.00.'
#                         novaEAP = g03EapOrc(
#                                             id = g03EapOrc.proxnumeap(g03EapOrc),
#                                             orcamento = g01Orcamento.objetos.get(pk=codOrcAtual),
#                                             codeap = f'{prefUltimaEap[:2]}01.02.',
#                                             coditem = f'{prefUltimaEap[:2]}01.02.',
#                                             descitem = f"Estrutura",
#                                             tipo = 2,
#                                             qtdorc = 1,
#                                             unidade = 'un',
#                                             vlrunit = 0
#                                             )
#                         novaEAP.save()
#                     eaps_do_orcamento = g03EapOrc.objetos.filter(orcamento_id=codOrcAtual).order_by('id')
#                 # Selecionar eaps do tipo 2
#                 eapAtv = []
#                 for eap in eaps_do_orcamento:
#                     if cod_atividade_padrao == 35 or cod_atividade_padrao == 36 or cod_atividade_padrao == 55:
#                         if eap.descitem == 'Policarbonato e acessórios': 
#                             if eap.tipo == 2: 
#                                 eapAtv.append(eap)
#                     else:
#                         if eap.descitem == 'Estrutura': 
#                             if eap.tipo == 2: 
#                                 eapAtv.append(eap)
#                 # Checkar se existe uma atividade já criada
#                 try:
#                     atvEAP = g04AtvEap.objetos.filter(eap_id=eapAtv[-1]).reverse()[0]
#                 except:
#                     if eapAtv == []: 
#                         pass
#                     else:
#                         # Criar atividade padrao para item da EAP
#                         atvEAP = g04AtvEap(
#                             id = g04AtvEap.proxnumatveap(g04AtvEap),
#                             eap = eapAtv[-1],
#                             atvpadr = a15AtvsPad.objetos.get(pk=cod_atividade_padrao)
#                         )
#                         atvEAP.save()
#                 # Criar EAP do tipo 1 para o insumo
#                 ordenador = f'{ultimaEap[:9]}{int(ultimaEap[9])+1}.'
#                 novaEAP = g03EapOrc(
#                                     id = g03EapOrc.proxnumeap(g03EapOrc),
#                                     orcamento = g01Orcamento.objetos.get(pk=codOrcAtual),
#                                     codeap = ordenador,
#                                     coditem = ordenador,
#                                     descitem = f"{quantInsumo} {bdInsumo.undcompr} de {bdInsumo.descricao}",
#                                     tipo = 1,
#                                     qtdorc = quantInsumo,
#                                     unidade = bdInsumo.undcompr,
#                                     vlrunit = bdInsumo.custo01
#                                     )
#                 novaEAP.save()
#                 try:
#                     # Se tiver a atividade já criada
#                     novoInsEap = g05InsEAP(atividade = atividadeEap,
#                                            insumo = a11Insumos.objetos.get(codigo=bdInsumo.codigo),
#                                            qtdprod = quantInsumo,
#                                            qtdimpr = 0,
#                                            cstunpr = a11Insumos.objetos.get(codigo=bdInsumo.codigo).custo01,
#                                            cstunim = 0)
#                 except:
#                     # Se não, pegar a atividade nova
#                     novoInsEap = g05InsEAP(atividade = atvEAP,
#                                            insumo = a11Insumos.objetos.get(codigo=bdInsumo.codigo),
#                                            qtdprod = quantInsumo,
#                                            qtdimpr = 0,
#                                            cstunpr = a11Insumos.objetos.get(codigo=bdInsumo.codigo).custo01,
#                                            cstunim = 0)
#                 novoInsEap.save()
#                 # A FUNÇÃO ESTÁ GERANDO O ERRO 504
#                 #atualizar_custos_orc(codOrcAtual)
#                 atualizar_lista_insumos(codOrcAtual)
#                 strCodOrc = int(codOrcAtual)
#                 return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
#     else:
#         form = formInserirInsumo()
#     return render(request, "orcs/inserir-insumo.html", {
#         "form":form, "orcamento":orcamento,
#     })


def inserir_deslocamento(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    codOrcAtual = request.session['codorcamento']
    if request.method == "POST":
        form = formInserirDeslocamento(request.POST)
        if form.is_valid():
            # id insumos -> hospedagem = 135, gasolina = 142, diesel s10 = 147, diesel s500 = 146, passagem = 140
            quantKm = form.cleaned_data['quantKm']
            codVeiculo = int(request.POST['combVeiculo'])
            quantDias = form.cleaned_data['quantDias']
            quantHosp = form.cleaned_data['quantHosp']
            quantPassagens = form.cleaned_data['quantPassagens']
            if quantKm != '' and quantDias != '':
                quantCombust = float(quantKm) * float(quantDias) * 2 / 10
                if codVeiculo == 1:
                    codInsumos = [142, 135, 140]
                elif codVeiculo == 2:
                    codInsumos = [147, 135, 140]
                else:
                    codInsumos = [146, 135, 140]
                    quantCombust = float(quantKm) * float(quantDias) * 2 / 2.2 if codVeiculo == 3 else float(quantKm) * float(quantDias) * 2 / 4
            else:
                quantCombust = 0
                codInsumos = [142, 135, 140]
            quantInsumos = [quantCombust, quantHosp, quantPassagens]

            if quantKm != '' or quantHosp != '' or quantPassagens != '':
                eapsOrcamento = g03EapOrc.objetos.filter(orcamento_id=codOrcAtual).order_by('-id')
                prefUltimaEap = eapsOrcamento[0].codeap
                # Verificar se já existe eap de deslocamento
                eapsOrcamento = g03EapOrc.objetos.filter(tipo=2)
                for eapOrcamento in eapsOrcamento:
                    idEap = eapOrcamento.id if eapOrcamento.codeap == f'{prefUltimaEap[:2]}01.04.' else g03EapOrc.proxnumeap(g03EapOrc)
                # Criar nova eap
                novaEAP = g03EapOrc(
                                    id = idEap,
                                    orcamento = g01Orcamento.objetos.get(pk=codOrcAtual),
                                    codeap = f'{prefUltimaEap[:2]}01.04.',
                                    coditem = f'{prefUltimaEap[:2]}01.04.',
                                    descitem = f"Deslocamento e Hospedagem",
                                    tipo = 2,
                                    qtdorc = 1,
                                    unidade = 'un',
                                    vlrunit = 0
                                    )
                novaEAP.save()
                # Verificar se já existe atividade
                try:
                    atividadeEap = g04AtvEap.objetos.get(eap_id=idEap)
                except:
                    # Criar atividade padrao para item da EAP
                    nvCodAtvEap = g04AtvEap.proxnumatveap(g04AtvEap)
                    atividadeEap = g04AtvEap(
                                        id = nvCodAtvEap,
                                        eap = novaEAP,
                                        atvpadr = a15AtvsPad.objetos.get(pk=5)
                                        )
                    atividadeEap.save()
                # Inserir insumos da eap
                i = 0
                for quantInsumo in quantInsumos:
                    if quantInsumo != '':
                        bdInsumo = a11Insumos.objetos.get(id=codInsumos[i])
                        # Criar insumos da eap
                        novoInsEap = g05InsEAP(atividade = atividadeEap,
                                               insumo = a11Insumos.objetos.get(codigo=bdInsumo.codigo),
                                               qtdprod = quantInsumo,
                                               qtdimpr = 0,
                                               cstunpr = a11Insumos.objetos.get(codigo=bdInsumo.codigo).custo01,
                                               cstunim = 0)
                        novoInsEap.save()
                    i += 1
                # Atualizar custos do orcamento
                # A FUNÇÃO ESTÁ GERANDO O ERRO 504
                #atualizar_custos_orc(cod_orc_atual)
                atualizar_lista_insumos(codOrcAtual)
                strCodOrc = int(codOrcAtual)
                return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
    else:
        form = formInserirDeslocamento()
        return render(request, "orcs/inserir-deslocamento.html", {"form": form})


def cadastrar_insumo(request):
    # Obter dados gerais do orcamento
    codOrcAtual = request.session['codorcamento']
    codigo_servico_atual = request.session['eap_atividade']
    if request.method == "POST":
        form = formCadInsumo(request.POST)
        if form.is_valid():
            catInsumo = int(request.POST['combcatInsumo'])
            descInsumo = form.cleaned_data['descInsumo']
            unidInsumo = form.cleaned_data['unidInsumo']
            custoInsumo = float(form.cleaned_data['custoInsumo'])
            espessura = formatar_custos_para_bd(form.cleaned_data['espessura']) if form.cleaned_data['espessura'] else 0
            comprimento = formatar_custos_para_bd(form.cleaned_data['comprimento']) if form.cleaned_data['comprimento'] else 0
            largura = formatar_custos_para_bd(form.cleaned_data['largura']) if form.cleaned_data['largura'] else 0
            ultimoCodigo = a11Insumos.objetos.all().values_list('codigo', flat=True)
            maiorCodigo = max(ultimoCodigo) if bool(ultimoCodigo) else maiorCodigo
            ultimoIdInsumo = int(a11Insumos.objetos.all().order_by('-id')[0].id)
            novoInsumo = a11Insumos(id=ultimoIdInsumo+1,
                                    codigo=maiorCodigo+1,
                                    descricao=descInsumo,
                                    undbas=unidInsumo,
                                    undcompr=unidInsumo,
                                    fatundcomp=1,
                                    custo01=custoInsumo,
                                    custo02=custoInsumo,
                                    prvda=custoInsumo,
                                    pesunbas=0,
                                    qtppal=0,
                                    catins_id=catInsumo,
                                    espessura=espessura,
                                    comprimento=comprimento,
                                    largura=largura)
            novoInsumo.save()
            return HttpResponseRedirect(reverse('orcs:detalhar_servico', args=(codOrcAtual, codigo_servico_atual,)))
    else:
        form = formCadInsumo()
    return render(request, "orcs/cad-insumo.html", {"form":form,})


def detalhar_servico(request, codorcam, id):
    request.session['eap_atividade'] = id
    idEap = id
    orcamento = obter_dados_gerais_orc(codorcam)
    form = formInserirInsumoNaAtividade()
    if request.method == "POST":
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
                eap_id=idEap
            )
            novo_insumo.save()
    insumos_eap = g05InsEAP.objetos.filter(eap_id=idEap)
    insumos_para_template = []
    for item, insumo in enumerate(insumos_eap, start=1):
        insumo_db = a11Insumos.objetos.get(id=insumo.insumo_id)
        insumo_objeto = {
            "id": insumo.id,
            "item": item,
            "descricao": insumo_db,
            "quantidade": round(insumo.qtdprod, 2),
            "unidade": insumo_db.undbas,
            "custo": formatar_custos_para_template(float(insumo.cstunpr)) if insumo.cstunpr else "0,00",
            "valorTotal": formatar_custos_para_template(float(insumo.qtdprod) * float(insumo.cstunpr)) if insumo.cstunpr else "0,00"
        }
        insumos_para_template.append(insumo_objeto)
    return render(
        request, "orcs/detalhar-servico.html", 
        {"orcamento": orcamento, "idEap": idEap,
        "insumos": insumos_para_template, "form": form})


def excluir_servico(request, codorcam, codeap):
    try:
        list_cod_eap = [eap.codeap for eap in g03EapOrc.objetos.filter(orcamento_id=codorcam, codeap__startswith=codeap[:-3], tipo=1)]
        cod_atv = request.session['eap_atividade']
        g05InsEAP.objetos.filter(atividade_id=g04AtvEap.objetos.get(eap_id=cod_atv).id)[list_cod_eap.index(codeap)].delete()
    # Quando o usuário tenta excluir mais do que só um item da eap
    except:
        pass
    # Deletar eap do orçamento na g03
    g03EapOrc.objetos.filter(orcamento__id=codorcam, codeap__startswith=codeap).delete()
    strcodorc = str(codorcam)
    # GERANDO O ERRO 504 PELA DEMORA, FAZER O PROCESSO SEPARADO
    #atualizar_custos_orc(codorcam)
    atualizar_lista_insumos(codorcam)
    return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(strcodorc,)))


def excluir_insumo_atividade(request, codorcam, idEap, idInsumo):
    try:
        g05InsEAP.objetos.get(id=idInsumo).delete()
        messages.info(request, "Insumo deletado com sucesso")
    except:
        messages.error(request, "Erro ao tentar deletar insumo")
    # GERANDO O ERRO 504 PELA DEMORA, FAZER O PROCESSO SEPARADO
    #atualizar_custos_orc(codorcam)
    atualizar_lista_insumos(codorcam)
    return HttpResponseRedirect(reverse('orcs:detalhar_servico', args=(str(codorcam), str(idEap), )))


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


def editar_eap(request, codorcam, id):
    orcamento = obter_dados_gerais_orc(codorcam)
    codOrcAtual = request.session['codorcamento']
    eap = g03EapOrc.objetos.get(id=id)
    if request.method == "POST":
        form = formEditarTextoEAP(request.POST)
        if form.is_valid():
            try:
                eap.descitem = form.cleaned_data['texto_novo'] if form.cleaned_data['texto_novo'] else eap.descitem
                eap.codeap = form.cleaned_data['codigo_eap_novo'] if form.cleaned_data['codigo_eap_novo'] else eap.codeap
                eap.coditem = eap.codeap
                eap.vlrunit = formatar_custos_para_bd(form.cleaned_data['valor_unitario_novo']) if form.cleaned_data['valor_unitario_novo'] else eap.vlrunit
                eap.qtdorc = formatar_custos_para_bd(form.cleaned_data['quantidade_nova']) if form.cleaned_data['quantidade_nova'] else eap.qtdorc
                eap.save()
                messages.info(request, "EAP alterada com sucesso")
            except:
                messages.error(request, "Erro ao alterar eap")
            strCodOrc = int(codOrcAtual)
            return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
    form = formEditarTextoEAP()
    return render(request, "orcs/editar-eap.html", {"eap": eap})


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
            tipo_proposta = request.POST['tipo_proposta']
            if tipo_proposta == '2':
                return HttpResponseRedirect(reverse('orcs:imp_proposta_so_material', args=(strcodorc,)))
            elif tipo_proposta == '3':
                return HttpResponseRedirect(reverse('orcs:imp_proposta_outros_servicos', args=(strcodorc,)))
            # Para orcamentos anteriores a 22-07-2020 utilizar a view de proposta antiga
            if orcamento.dtorc <= datetime.date(2020, 7, 22):
                return HttpResponseRedirect(reverse('orcs:imp_proposta_antiga', args=(strcodorc,)))
            else:
                return HttpResponseRedirect(reverse('orcs:imp_proposta', args=(strcodorc,)))
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
            "prazoValidade": abs(datetime.date.today() - orcamento.dtval).days
        }
        return render(request,"orcs/editar-proposta.html", {
            "orcamento": detalhes_orcamento, "dadosOrcamento": orcamento_template, 
            "form": form, "codorcam": codorcam
        })


# Essa versão foi descontinuada no dia 22-07-2020 devido a alteração no banco de dados
def imp_proposta_antiga(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    bd_orc = g01Orcamento.objetos.get(id=codorcam)
    desc_orc = g03EapOrc.objetos.filter(orcamento_id=bd_orc.id).order_by('codeap')
    # Títulos e subtítulos da eap do orcamento
    list_desc_orc = []
    for descricao in desc_orc:
        if len(descricao.codeap) <= 5:
            dic_eap_orc = {
                          "codEap": descricao.codeap,
                          "descricao": str(descricao.descitem).lower()
                          }
            list_desc_orc.append(dic_eap_orc)
    cliente = e01Cadastros.objetos.get(id=orcamento['codcliente'])
    vendedor = c01Usuarios.objetos.get(id=bd_orc.vended_id)
    usuario_vendedor = User.objects.get(username=vendedor.nomeusr)
    nome_vendedor = f"{usuario_vendedor.first_name} {usuario_vendedor.last_name}"
    email_vendedor = usuario_vendedor.email
    telefone_vendedor = vendedor.fone
    telefone_vendedor = f"{telefone_vendedor[:5]}-{telefone_vendedor[-4:]}"
    if cliente.contempresa == None:
        dados_proposta = {
                        "tratamento": cliente.fantasia,
                        "cliente": cliente.descrcad,
                        "genero": cliente.genero,
                        "enderecoObra": orcamento['endereco'],
                        "condPgto": a19PlsPgtos.objetos.get(id=bd_orc.plpgto_id).descricao,
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
    eap_orc = g03EapOrc.objetos.filter(orcamento_id=codorcam, tipo=2).order_by('-codeap')
    list_eap_prop = []
    valor_restante_orc = 0
    #Somar os valores de diferentes eaps
    itensEap = [0, 1, 2, 3, 4]
    for item_eap in eap_orc:
        item_eap.qtdorc = round(item_eap.qtdorc, 2)
        item_eap.vlrunit = round(item_eap.vlrunit, 2)
        item_eap.vlrtot = round(float(item_eap.vlrunit) * float(item_eap.qtdorc), 2)
        # Haverá só 2 itens na carta proposta, policarbonato e estrutura
        if len(item_eap.codeap) == 8:
            if item_eap.codeap[-2:] != "1." and item_eap.codeap[-2:] != "2.":
                valor_restante_orc += item_eap.vlrtot
            else:
                if item_eap.codeap[-2:] == "1.":
                    itensEap[0] = item_eap.descitem
                    itensEap[1] += item_eap.vlrtot
                elif item_eap.codeap[-2:] == "2.":
                    # alteração no texto da estrutura
                    # itensEap[3] = item_eap.descitem
                    itensEap[3] = "Fabricação e Instalação da Cobertura"
                    itensEap[2] += item_eap.vlrtot
        else:
            pass
    # O valor da mão de obra, riscos e lucro serão somados na estrutura somente
    itensEap[1] = round(itensEap[1], 2)
    itensEap[2] = round(itensEap[2] + valor_restante_orc, 2)
    totalProposta = '{:,}'.format(
        round(itensEap[1] + itensEap[2], 2)).replace('.', 'x').replace(',', '.').replace('x', ',')
    itensEap[1] = '{:,}'.format(
        round(itensEap[1], 2)).replace('.', 'x').replace(',', '.').replace('x', ',')
    itensEap[2] = '{:,}'.format(
        round(itensEap[2], 2)).replace('.', 'x').replace(',', '.').replace('x', ',')
    dic_eap_prop = {
                        'descricao': itensEap[0],
                        'valor': itensEap[1]
                       }
    list_eap_prop.append(dic_eap_prop)
    dic_eap_prop = {
                        'descricao': itensEap[3],
                        'valor': itensEap[2],
                       }
    list_eap_prop.append(dic_eap_prop)
    # Obter lista de insumos dos orçamentos
    # Mudança no banco de dados dia 22/07/2020 - Se não der nenhum problema pode apagar
    ### list_atividades = [g04AtvEap.objetos.get(eap_id=eap.id) for eap in eap_orc]
    ### list_insumos = [g05InsEAP.objetos.filter(atividade_id=atividade.id) for atividade in list_atividades]
    list_insumos = [g05InsEAP.objetos.filter(eap_id=eap.id) for eap in eap_orc]
    list_dic_insumos = []
    # Não listar valor em dinheiro, gasolina, serralheiro e etc.
    insumos_nao_mostrar = [1, 405, 1152, 1163, 400, 6164, 6201, 6300, 6302, 6306, 6307, 6308, 6309,
                           6325, 6326, 6327, 6328, 6329, 14217]
    for query_insumo in list_insumos:
        for insumo in query_insumo:
            bd_insumo = a11Insumos.objetos.get(id=insumo.insumo_id)
            if bd_insumo.codigo in insumos_nao_mostrar:
                pass
            else:
                dic_insumo =  {
                    'codigo': bd_insumo.codigo, 
                    'descricao': str(bd_insumo.descricao).lower(),
                    }
                # Não mostrar insumos repetidos
                insumos_nao_mostrar.append(bd_insumo.codigo)
                list_dic_insumos.append(dic_insumo)
    list_dic_insumos_order = sorted(list_dic_insumos, key=lambda k: k['descricao'])
    meses = [0, "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    mesHoje = meses[int(datetime.date.today().strftime("%m"))]
    today = datetime.date.today().strftime(f"%d de {mesHoje} de %Y")
    # Alterar status do orçamento
    bd_orc.fase_id = 3
    bd_orc.save()
    return render(request, "orcs/imp-proposta.html",
                {"dadosProposta": dados_proposta, "eapProp": list_eap_prop,
                 "insumos": list_dic_insumos_order, "totalProposta": totalProposta, "today": today,
                "listDescricoesOrc": list_desc_orc})


def imp_proposta(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    bd_orc = g01Orcamento.objetos.get(id=codorcam)
    desc_orc = g03EapOrc.objetos.filter(orcamento_id=bd_orc.id).order_by('codeap')
    # Títulos e subtítulos da eap do orcamento
    list_desc_orc = []
    for descricao in desc_orc:
        if len(descricao.codeap) <= 3:
            dic_eap_orc = {
                "codEap": descricao.codeap,
                "descricao": str(descricao.descitem).lower()
            }
            list_desc_orc.append(dic_eap_orc)
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
            "condPgto": a19PlsPgtos.objetos.get(id=bd_orc.plpgto_id).descricao,
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
    eap_orc = g03EapOrc.objetos.filter(orcamento_id=codorcam, tipo=1).order_by('-codeap')
    list_eap_prop = []
    valor_restante_orc = 0
    #Somar os valores de diferentes eaps
    itensEap = [0.00, 0.00, 0.00, 0.00, 0.00]
    for item_eap in eap_orc:
        item_eap.qtdorc = round(item_eap.qtdorc, 2)
        item_eap.vlrunit = round(item_eap.vlrunit, 2)
        item_eap.vlrtot = round(float(item_eap.vlrunit) * float(item_eap.qtdorc), 2)
        # Haverá só 2 itens na carta proposta, policarbonato e estrutura
        if len(item_eap.codeap) == 5:
            if item_eap.codeap[-2:] != "1." and item_eap.codeap[-2:] != "2.":
                valor_restante_orc =+ item_eap.vlrtot
            else:
                if item_eap.codeap[-2:] == "1.":
                    itensEap[0] = item_eap.descitem
                    itensEap[1] =+ item_eap.vlrtot
                elif item_eap.codeap[-2:] == "2.":
                    # alteração no texto da estrutura
                    # itensEap[3] = item_eap.descitem
                    itensEap[3] = "Fabricação e Instalação da Cobertura"
                    itensEap[2] =+ item_eap.vlrtot
        else:
            pass
    # O valor da mão de obra, riscos e lucro serão somados na estrutura somente
    itensEap[1] = round(itensEap[1], 2)
    itensEap[2] = round(itensEap[2] + valor_restante_orc, 2)
    totalProposta = formatar_custos_para_template(itensEap[1] + itensEap[2])
    itensEap[1] = formatar_custos_para_template(itensEap[1])
    itensEap[2] = formatar_custos_para_template(itensEap[2])
    # escrever valor com 2 casas decimais
    itensEap[1] = formatar_com_duas_casas_string(itensEap[1])
    itensEap[2] = formatar_com_duas_casas_string(itensEap[2])
    totalProposta = formatar_com_duas_casas_string(totalProposta)
    list_eap_prop = [{
        'descricao': itensEap[0],
        'valor': itensEap[1]
    }]
    list_eap_prop.append({
        'descricao': itensEap[3],
        'valor': itensEap[2]
    })
    list_insumos = [g05InsEAP.objetos.filter(eap_id=eap.id) for eap in eap_orc]
    list_dic_insumos = []
    # Não listar valor em dinheiro, gasolina, serralheiro e etc.
    insumos_nao_mostrar = [1, 405, 1152, 1163, 400, 6164, 6201, 6300, 6302, 6306, 6307, 6308, 6309,
                           6325, 6326, 6327, 6328, 6329, 14217]
    for query_insumo in list_insumos:
        for insumo in query_insumo:
            bd_insumo = a11Insumos.objetos.get(id=insumo.insumo_id)
            if not bd_insumo.codigo in insumos_nao_mostrar:
                dic_insumo =  {
                    'codigo': bd_insumo.codigo, 
                    'descricao': str(bd_insumo.descricao).lower(),
                }
                # Não mostrar insumos repetidos
                insumos_nao_mostrar.append(bd_insumo.codigo)
                list_dic_insumos.append(dic_insumo)
    list_dic_insumos_order = sorted(list_dic_insumos, key=lambda k: k['descricao'])
    meses = [0, "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    mesHoje = meses[int(datetime.date.today().strftime("%m"))]
    today = datetime.date.today().strftime(f"%d de {mesHoje} de %Y")
    # Alterar status do orçamento
    bd_orc.fase_id = 3
    bd_orc.save()
    return render(request, "orcs/imp-proposta.html",
                {"dadosProposta": dados_proposta, "eapProp": list_eap_prop,
                 "insumos": list_dic_insumos_order, "totalProposta": totalProposta, "today": today,
                "listDescricoesOrc": list_desc_orc})


def imp_proposta_so_material(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    bd_orc = g01Orcamento.objetos.get(id=codorcam)
    desc_orc = g03EapOrc.objetos.filter(orcamento_id=bd_orc.id).order_by('codeap')
    # Títulos e subtítulos da eap do orcamento
    list_desc_orc = []
    for descricao in desc_orc:
        if len(descricao.codeap) <= 3:
            dic_eap_orc = {
                "codEap": descricao.codeap,
                "descricao": str(descricao.descitem).lower()
            }
            list_desc_orc.append(dic_eap_orc)
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
            "condPgto": a19PlsPgtos.objetos.get(id=bd_orc.plpgto_id).descricao,
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
    eap_orc = g03EapOrc.objetos.filter(orcamento_id=codorcam, tipo=1).order_by('-codeap')
    list_eap_prop = []
    valor_restante_orc = 0
    #Somar os valores de diferentes eaps
    itensEap = [0.00, 0.00, 0.00, 0.00, 0.00]
    for item_eap in eap_orc:
        item_eap.qtdorc = round(item_eap.qtdorc, 2)
        item_eap.vlrunit = round(item_eap.vlrunit, 2)
        item_eap.vlrtot = round(float(item_eap.vlrunit) * float(item_eap.qtdorc), 2)
        # Haverá só 2 itens na carta proposta, policarbonato e estrutura
        if len(item_eap.codeap) == 5:
            if item_eap.codeap[-2:] != "1." and item_eap.codeap[-2:] != "2.":
                valor_restante_orc =+ item_eap.vlrtot
            else:
                if item_eap.codeap[-2:] == "1.":
                    itensEap[0] = item_eap.descitem
                    itensEap[1] =+ item_eap.vlrtot
                elif item_eap.codeap[-2:] == "2.":
                    # alteração no texto da estrutura
                    # itensEap[3] = item_eap.descitem
                    itensEap[3] = "Estrutura"
                    itensEap[2] =+ item_eap.vlrtot
        else:
            pass
    # O valor da mão de obra, riscos e lucro serão somados na estrutura somente
    itensEap[1] = round(itensEap[1], 2)
    itensEap[2] = round(itensEap[2] + valor_restante_orc, 2)
    totalProposta = formatar_custos_para_template(itensEap[1] + itensEap[2])
    itensEap[1] = formatar_custos_para_template(itensEap[1])
    itensEap[2] = formatar_custos_para_template(itensEap[2])
    # escrever valor com 2 casas decimais
    itensEap[1] = formatar_com_duas_casas_string(itensEap[1])
    itensEap[2] = formatar_com_duas_casas_string(itensEap[2])
    totalProposta = formatar_com_duas_casas_string(totalProposta)
    list_eap_prop = [{
        'descricao': itensEap[0],
        'valor': itensEap[1]
    }]
    # sem estrutura
    if not itensEap[3] == 0.0:
        list_eap_prop.append({
            'descricao': itensEap[3],
            'valor': itensEap[2]
        })
    list_insumos = [g05InsEAP.objetos.filter(eap_id=eap.id) for eap in eap_orc]
    list_dic_insumos = []
    # Não listar valor em dinheiro, gasolina, serralheiro e etc.
    insumos_nao_mostrar = [1, 405, 1152, 1163, 400, 6164, 6201, 6300, 6302, 6306, 6307, 6308, 6309,
                           6325, 6326, 6327, 6328, 6329, 14217]
    for query_insumo in list_insumos:
        for insumo in query_insumo:
            bd_insumo = a11Insumos.objetos.get(id=insumo.insumo_id)
            if not bd_insumo.codigo in insumos_nao_mostrar:
                dic_insumo =  {
                    'codigo': bd_insumo.codigo, 
                    'descricao': str(bd_insumo.descricao).lower(),
                }
                # Não mostrar insumos repetidos
                insumos_nao_mostrar.append(bd_insumo.codigo)
                list_dic_insumos.append(dic_insumo)
    list_dic_insumos_order = sorted(list_dic_insumos, key=lambda k: k['descricao'])
    meses = [0, "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    mesHoje = meses[int(datetime.date.today().strftime("%m"))]
    today = datetime.date.today().strftime(f"%d de {mesHoje} de %Y")
    # Alterar status do orçamento
    bd_orc.fase_id = 3
    bd_orc.save()
    return render(request, "orcs/imp-proposta-so-material.html",
                {"dadosProposta": dados_proposta, "eapProp": list_eap_prop,
                 "insumos": list_dic_insumos_order, "totalProposta": totalProposta, "today": today,
                "listDescricoesOrc": list_desc_orc})


def imp_proposta_outros_servicos(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    bd_orc = g01Orcamento.objetos.get(id=codorcam)
    desc_orc = g03EapOrc.objetos.filter(orcamento_id=bd_orc.id).order_by('codeap')
    # Títulos e subtítulos da eap do orcamento
    list_desc_orc = []
    for descricao in desc_orc:
        if len(descricao.codeap) <= 3:
            dic_eap_orc = {
                "codEap": descricao.codeap,
                "descricao": str(descricao.descitem).lower()
            }
            list_desc_orc.append(dic_eap_orc)
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
            "condPgto": a19PlsPgtos.objetos.get(id=bd_orc.plpgto_id).descricao,
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
    eap_orc = g03EapOrc.objetos.filter(orcamento_id=codorcam, tipo=1).order_by('codeap')
    list_eap_prop = []
    totalProposta = 0
    for item_eap in eap_orc:
        item_eap.qtdorc = round(item_eap.qtdorc, 2)
        item_eap.vlrunit = round(item_eap.vlrunit, 2)
        item_eap.vlrtot = round(float(item_eap.vlrunit) * float(item_eap.qtdorc), 2)
        if len(item_eap.codeap) == 5:
            objeto_item_eap = {
                "descricao": item_eap.descitem,
                "valor": formatar_com_duas_casas_string(formatar_custos_para_template(item_eap.vlrtot))
            }
            totalProposta += item_eap.vlrtot
            list_eap_prop.append(objeto_item_eap)
    totalProposta = formatar_com_duas_casas_string(formatar_custos_para_template(totalProposta))
    list_insumos = [g05InsEAP.objetos.filter(eap_id=eap.id) for eap in eap_orc]
    list_dic_insumos = []
    # Não listar valor em dinheiro, gasolina, serralheiro e etc.
    insumos_nao_mostrar = [1, 405, 1152, 1163, 400, 6164, 6201, 6300, 6302, 6306, 6307, 6308, 6309,
                           6325, 6326, 6327, 6328, 6329, 14217]
    for query_insumo in list_insumos:
        for insumo in query_insumo:
            bd_insumo = a11Insumos.objetos.get(id=insumo.insumo_id)
            if not bd_insumo.codigo in insumos_nao_mostrar:
                dic_insumo =  {
                    'codigo': bd_insumo.codigo, 
                    'descricao': str(bd_insumo.descricao).lower(),
                }
                # Não mostrar insumos repetidos
                insumos_nao_mostrar.append(bd_insumo.codigo)
                list_dic_insumos.append(dic_insumo)
    list_dic_insumos_order = sorted(list_dic_insumos, key=lambda k: k['descricao'])
    meses = [0, "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    mesHoje = meses[int(datetime.date.today().strftime("%m"))]
    today = datetime.date.today().strftime(f"%d de {mesHoje} de %Y")
    # Alterar status do orçamento
    bd_orc.fase_id = 3
    bd_orc.save()
    
    return render(request, "orcs/imp-proposta-outros-servicos.html", {
        "dadosProposta": dados_proposta, 
        "eapProp": list_eap_prop,
        "insumos": list_dic_insumos_order, 
        "totalProposta": totalProposta,
        "today": today,
        "listDescricoesOrc": list_desc_orc})



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


def venezianas(request, codorcam):
    if request.method == "POST":
        form = formMedidasVenezianas(request.POST)
        if form.is_valid():
            codAleta = request.POST['tipAleta']
            # Obter dados dos vaos
            venezianas = {'veneziana1': {'base': form.cleaned_data['base1'],
                                         'altura': form.cleaned_data['altura1'],
                                         'repeticoes': form.cleaned_data['repet1'],
                                         'rebitesAleta': form.cleaned_data['rebite1']},
                          'veneziana2': {'base': form.cleaned_data['base2'],
                                         'altura': form.cleaned_data['altura2'],
                                         'repeticoes': form.cleaned_data['repet2'],
                                         'rebitesAleta': form.cleaned_data['rebite2']},
                          'veneziana3': {'base': form.cleaned_data['base3'],
                                         'altura': form.cleaned_data['altura3'],
                                         'repeticoes': form.cleaned_data['repet3'],
                                         'rebitesAleta': form.cleaned_data['rebite3']},
                          'veneziana4': {'base': form.cleaned_data['base4'],
                                         'altura': form.cleaned_data['altura4'],
                                         'repeticoes': form.cleaned_data['repet4'],
                                         'rebitesAleta': form.cleaned_data['rebite4']},
                          'veneziana5': {'base': form.cleaned_data['base5'],
                                         'altura': form.cleaned_data['altura5'],
                                         'repeticoes': form.cleaned_data['repet5'],
                                         'rebitesAleta': form.cleaned_data['rebite5']}}
            #  Eliminar vaos com dimensoes em branco
            for veneziana, valores in venezianas.copy().items():
                if (valores['base'] or valores['altura'] or valores['repeticoes']) == '':
                    try:
                        del venezianas[veneziana]
                    except:
                        pass
            cod_orc_atual = request.session['codorcamento']
            try:
                ult_num_item_eap = int((g03EapOrc.objetos.filter(orcamento_id=cod_orc_atual).order_by('-id')[0].codeap)[:1])
            except:
                ult_num_item_eap = 0
            esp_ven = a11Insumos.objetos.get(codigo=codAleta).espessura
            ##### RETIRAR ESSE IF ASSIM QUE FOR DECIDIDO COMO SERÁ CALCULADA AS ESPESSURAS 3,6 E 4
            if esp_ven == 3:
                # Criar EAP para 3mm
                resultVen3 = orc_venezianas(3, f'{ult_num_item_eap+1}.',
                                                           codAleta, **venezianas)
                inserir_dados_eap(request, *resultVen3)
            else:
                # Criar EAP para 5mm
                resultVen5 = orc_venezianas(5, f'{ult_num_item_eap+1}.',
                                                           codAleta, **venezianas)
                inserir_dados_eap(request, *resultVen5)
            # Atualizar custos do orcamento
            #atualizar_custos_orc(cod_orc_atual)
            atualizar_lista_insumos(cod_orc_atual)
            # Editar orcamento atual
            str_cod_orc = int(cod_orc_atual)
            return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(str_cod_orc,)))
    else:
        form = formMedidasVenezianas()
        orcamento = obter_dados_gerais_orc(codorcam)
        aletas = a11Insumos.objetos.filter(catins_id=48)
        return render(request, "orcs/medidas-venezianas.html", {"orcamento": orcamento,
                                                            "aletas": aletas, "form": form})


def orc_telha_trapezoidal_fixo(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    codOrcAtual = request.session['codorcamento']
    if request.POST:
        form = formOrcamentoTelhaTrapezoidalFixo(request.POST)
        if form.is_valid():
            dados_para_calculos = {
                'codigo_telha': int(request.POST['telha']),
                'codigo_parafuso_costura': int(request.POST['parafuso_costura']),
                'codigo_parafuso_fixacao': int(request.POST['parafuso_fixacao']),
                'codigo_selante': int(request.POST['selante']),
                'codigo_perfil_estrutural_externo': int(request.POST['perfil_estrutural_externo']),
                'codigo_perfil_estrutural_interno': int(request.POST['perfil_estrutural_interno']),
                'codigo_rufo': int(request.POST['rufo']),
                'codigo_calha': int(request.POST['calha']),
                'codigo_pintura': int(request.POST['tipo_pintura']),
                'quantidade_pintura': float(formatar_custos_para_bd(request.POST['quantidade_pintura'])) if form.cleaned_data['quantidade_pintura'] else 0,
                'quantidade_modulos': 1,
                'comprimento': float(formatar_custos_para_bd(form.cleaned_data['comprimento'])),
                'largura': float(formatar_custos_para_bd(form.cleaned_data['largura'])),
                'declividade': float(formatar_custos_para_bd(form.cleaned_data['declividade'])),
                'repeticoes': float(formatar_custos_para_bd(form.cleaned_data['repeticoes'])),
                'distancia_entre_apoios': float(formatar_custos_para_bd(form.cleaned_data['distancia_entre_apoios'])),
                'distancia_entre_maos_f': float(formatar_custos_para_bd(request.POST['distancia_entre_maos_f'])) if form.cleaned_data['distancia_entre_maos_f'] else 0,
                'montante': form.cleaned_data['montante'],
                'jusante': form.cleaned_data['jusante'],
                'lateral_esquerda': form.cleaned_data['lateral_esquerda'],
                'lateral_direita': form.cleaned_data['lateral_direita'],
                'dias_serralheiro': int(form.cleaned_data['dias_serralheiro']),
                'quantidade_serralheiro': int(form.cleaned_data['quantidade_serralheiro']),                
                'dias_auxiliar': int(form.cleaned_data['dias_auxiliar']),
                'quantidade_auxiliar': int(form.cleaned_data['quantidade_auxiliar']),
                'dificuldade': int(form.cleaned_data['dificuldade']),
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
                'codigo_perfil_multi_click': int(request.POST['chapa']),
                'codigo_perfil_arremate': int(request.POST['perfil_arremate']),
                'codigo_tampa': int(request.POST['tampa']),
                'codigo_garra': int(request.POST['garra']),
                'codigo_fita': int(request.POST['fita']),
                'codigo_selante': int(request.POST['selante']),
                'codigo_parafuso_arremate': int(request.POST['parafuso_arremate']),
                'codigo_parafuso_terca': int(request.POST['parafuso_terca']),
                'codigo_perfil_estrutural_externo': int(request.POST['perfil_estrutural_externo']),
                'codigo_perfil_estrutural_interno': int(request.POST['perfil_estrutural_interno']),
                'codigo_rufo': int(request.POST['rufo']),
                'codigo_calha': int(request.POST['calha']),
                'quantidade_modulos': 1,
                'codigo_pintura': int(request.POST['tipo_pintura']),
                'quantidade_pintura': float(formatar_custos_para_bd(request.POST['quantidade_pintura'])) if form.cleaned_data['quantidade_pintura'] else 0,
                'comprimento': float(formatar_custos_para_bd(form.cleaned_data['comprimento'])),
                'largura': float(formatar_custos_para_bd(form.cleaned_data['largura'])),
                'declividade': float(formatar_custos_para_bd(form.cleaned_data['declividade'])),
                'repeticoes': float(formatar_custos_para_bd(form.cleaned_data['repeticoes'])),
                'distancia_entre_apoios': float(formatar_custos_para_bd(form.cleaned_data['distancia_entre_apoios'])),
                'distancia_entre_maos_f': float(formatar_custos_para_bd(request.POST['distancia_entre_maos_f'])) if form.cleaned_data['distancia_entre_maos_f'] else 0,
                'montante': form.cleaned_data['montante'],
                'jusante': form.cleaned_data['jusante'],
                'lateral_esquerda': form.cleaned_data['lateral_esquerda'],
                'lateral_direita': form.cleaned_data['lateral_direita'],
                'dias_serralheiro': int(form.cleaned_data['dias_serralheiro']),
                'quantidade_serralheiro': int(form.cleaned_data['quantidade_serralheiro']),                
                'dias_auxiliar': int(form.cleaned_data['dias_auxiliar']),
                'quantidade_auxiliar': int(form.cleaned_data['quantidade_auxiliar']),
                'dificuldade': int(form.cleaned_data['dificuldade']),
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


def poli_plano_fix(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    codOrcAtual = request.session['codorcamento']
    if request.POST:
        form = formPoliPlanFix(request.POST)
        if "btnProximo" in request.POST:
            if form.is_valid():
                #Obter dados para calculos
                dadosOrcPoliPlano = {'codPoli': int(request.POST['combPolicarbonato']),
                                     'codPerfUn': int(request.POST['combPerfUn']),
                                     'codPerfAr': int(request.POST['combPerfAr']),
                                     'codPerfU': int(request.POST['combPerfU']),
                                     'codPerfEsExterno': int(request.POST['combPerfEsExterno']),
                                     'codPerfEsInterno': int(request.POST['combPerfEsInterno']),
                                     'cod_selante': int(request.POST['comb_selante']),
                                     'codRufo': int(request.POST['combRufo']),
                                     'codCalha': int(request.POST['combCalha']),
                                     'codPerfGuar': int(request.POST['combPerfGuar']),
                                     'codPerfGax': int(request.POST['combPerfGax']),
                                     'codFitaVent': int(request.POST['combFitaVent']),
                                     'codFitaAlum': int(request.POST['combFitaAlum']),
                                     'quantModulos': 1,
                                     'codPintura': int(request.POST['combPintura']),
                                     'quantPintura': float(formatar_custos_para_bd(request.POST['quantPintura'])) if form.cleaned_data['quantPintura'] else 0,
                                     'compPoli': float(formatar_custos_para_bd(form.cleaned_data['compPoli'])),
                                     'largPoli': float(formatar_custos_para_bd(form.cleaned_data['largPoli'])),
                                     'declPoli': float(formatar_custos_para_bd(form.cleaned_data['declPoli'])),
                                     'repetPoli': float(formatar_custos_para_bd(form.cleaned_data['repetPoli'])) if float(form.cleaned_data['repetPoli']) > 0 else 1,
                                     'distApoios': float(formatar_custos_para_bd(form.cleaned_data['distApoios'])),
                                     'distMaosF': float(formatar_custos_para_bd(request.POST['distMaosF'])) if form.cleaned_data['distMaosF'] else 0,
                                     'montante': form.cleaned_data['montante'],
                                     'jusante': form.cleaned_data['jusante'],
                                     'latEsq': form.cleaned_data['latEsq'],
                                     'latDir': form.cleaned_data['latDir'],
                                     'diasSerralheiro': int(form.cleaned_data['diasSerralheiro']),
                                     'quantSerralheiros': int(form.cleaned_data['quantSerralheiros']),
                                     'diasAuxiliar': int(form.cleaned_data['diasAuxiliar']),
                                     'quantAuxiliares': int(form.cleaned_data['quantAuxiliares']),
                                     'dificuldade': int(form.cleaned_data['dificuldade']),
                                     'apEstr': form.cleaned_data['apEstr'],
                                     'estrutura': 0
                                    }
                try:
                    ultNumItemEAP = int((g03EapOrc.objetos.filter(orcamento_id=codOrcAtual).order_by('-id')[0].codeap)[:1])
                except:
                    ultNumItemEAP = 0
                resultados = orc_poli_plano(
                    f'{ultNumItemEAP+1}.', **dadosOrcPoliPlano)
                inserir_dados_eap(request, *resultados)
                # Atualizar custos do orcamento
                # GERANDO O ERRO 504 PELA DEMORA, FAZER O PROCESSO SEPARADO
                #atualizar_custos_orc(codOrcAtual)
                atualizar_lista_insumos(codOrcAtual)
                # Editar orcamento atual
                strCodOrc = int(codOrcAtual)
                return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
    else:
        form = formPoliPlanFix()
        return render(request, "orcs/poli-plano-fixo.html", {"form":form, "orcamento": orcamento,})


def poli_plano_ret(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    codOrcAtual = request.session['codorcamento']
    if request.POST:
        form = formPoliPlanRet(request.POST)
        if "btnProximo" in request.POST:
            if form.is_valid():
                #Obter dados para calculos
                dadosOrcPoliPlano = {'codPoli': int(request.POST['combPolicarbonato']),
                                     'codPerfUn': int(request.POST['combPerfUn']),
                                     'codPerfAr': int(request.POST['combPerfAr']),
                                     'codPerfU': int(request.POST['combPerfU']),
                                     'cod_selante': int(request.POST['comb_selante']),
                                     'codPerfEsExterno': int(request.POST['combPerfEsExterno']),
                                     'codPerfEsInterno': int(request.POST['combPerfEsInterno']),
                                     'codRufo': int(request.POST['combRufo']),
                                     'codCalha': int(request.POST['combCalha']),
                                     'codPerfGuar': int(request.POST['combPerfGuar']),
                                     'codPerfGax': int(request.POST['combPerfGax']),
                                     'codFitaVent': int(request.POST['combFitaVent']),
                                     'codFitaAlum': int(request.POST['combFitaAlum']),
                                     'codMotor': int(request.POST['combMotores']),
                                     'quantMotor': int(form.cleaned_data['quantMotores']),
                                     'quantModulos': float(form.cleaned_data['quantModulos']),
                                     'quantModMoveis': float(form.cleaned_data['quantModMoveis']),
                                     'codCantoneira': int(request.POST['combCantoneira']),
                                     'codPerfCant': int(request.POST['combPerfCant']),
                                     'codRoldanas': int(request.POST['combRoldanas']),
                                     'direcMovimento': int(form.cleaned_data['direcMovimento']),
                                     'codPintura': int(request.POST['combPintura']),
                                     'quantPintura': float(formatar_custos_para_bd(request.POST['quantPintura'])) if form.cleaned_data['quantPintura'] else 0,
                                     'compPoli': float(formatar_custos_para_bd(form.cleaned_data['compPoli'])),
                                     'largPoli': float(formatar_custos_para_bd(form.cleaned_data['largPoli'])),
                                     'declPoli': float(formatar_custos_para_bd(form.cleaned_data['declPoli'])),
                                     'repetPoli': float(formatar_custos_para_bd(form.cleaned_data['repetPoli'])) if float(form.cleaned_data['repetPoli']) > 0 else 1,
                                     'distApoios': float(formatar_custos_para_bd(form.cleaned_data['distApoios'])),
                                     'distMaosF': 0,
                                     'montante': form.cleaned_data['montante'],
                                     'jusante': form.cleaned_data['jusante'],
                                     'latEsq': form.cleaned_data['latEsq'],
                                     'latDir': form.cleaned_data['latDir'],
                                     'diasSerralheiro': int(form.cleaned_data['diasSerralheiro']),
                                     'quantSerralheiros': int(form.cleaned_data['quantSerralheiros']),
                                     'diasAuxiliar': int(form.cleaned_data['diasAuxiliar']),
                                     'quantAuxiliares': int(form.cleaned_data['quantAuxiliares']),
                                     'dificuldade': int(form.cleaned_data['dificuldade']),
                                     'apEstr': form.cleaned_data['apEstr'],
                                     'estrutura': 1
                                    }
                try:
                    ultNumItemEAP = int((g03EapOrc.objetos.filter(orcamento_id=codOrcAtual).order_by('-id')[0].codeap)[:1])
                except:
                    ultNumItemEAP = 0
            resultados = orc_poli_plano(
                f'{ultNumItemEAP+1}.', **dadosOrcPoliPlano)
            inserir_dados_eap(request, *resultados)
            # Atualizar custos do orcamento
            # GERANDO O ERRO 504 PELA DEMORA, FAZER O PROCESSO SEPARADO
            #atualizar_custos_orc(codOrcAtual)
            atualizar_lista_insumos(codOrcAtual)
            # Editar orcamento atual
            strCodOrc = int(codOrcAtual)
        return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
    else:
        form = formPoliPlanRet()
        return render(request, "orcs/poli-plano-ret.html", {"form":form, "orcamento": orcamento,})


def poli_curvo_fix(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    codOrcAtual = request.session['codorcamento']
    if request.POST:
        form = formPoliCurvoFix(request.POST)
        if "btnProximo" in request.POST:
            if form.is_valid():
                #Obter dados para calculos
                dadosOrcPoliPlano = {'codPoli': int(request.POST['combPolicarbonato']),
                                     'codPerfUn': int(request.POST['combPerfUn']),
                                     'codPerfAr': int(request.POST['combPerfAr']),
                                     'codPerfU': int(request.POST['combPerfU']),
                                     'cod_selante': int(request.POST['comb_selante']),
                                     'codPerfEsEx': int(request.POST['combPerfEsExterno']),
                                     'codPerfEsIn': int(request.POST['combPerfEsInterno']),
                                     'codCalandra': int(request.POST['combCalandra']),
                                     'codRufo': int(request.POST['combRufo']),
                                     'codCalha': int(request.POST['combCalha']),
                                     'codPerfGuar': int(request.POST['combPerfGuar']),
                                     'codPerfGax': int(request.POST['combPerfGax']),
                                     'codFitaVent': int(request.POST['combFitaVent']),
                                     'quantModulos': 1,
                                     'codPintura': int(request.POST['combPintura']),
                                     'quantPintura': float(formatar_custos_para_bd(request.POST['quantPintura'])) if form.cleaned_data['quantPintura'] else 0,
                                     'cordaPoli': float(formatar_custos_para_bd(form.cleaned_data['cordaPoli'])),
                                     'flechaPoli': float(formatar_custos_para_bd(form.cleaned_data['flechaPoli'])),
                                     'largPoli': float(formatar_custos_para_bd(form.cleaned_data['largPoli'])),
                                     'repetPoli': float(formatar_custos_para_bd(form.cleaned_data['repetPoli'])) if float(form.cleaned_data['repetPoli']) > 0 else 1,
                                     'distApoios': float(formatar_custos_para_bd(form.cleaned_data['distApoios'])),
                                     'distMaosF': float(formatar_custos_para_bd(request.POST['distMaosF'])) if form.cleaned_data['distMaosF'] else 0,
                                     'montante': form.cleaned_data['montante'],
                                     'jusante': form.cleaned_data['jusante'],
                                     'latEsq': form.cleaned_data['latEsq'],
                                     'latDir': form.cleaned_data['latDir'],
                                     'diasSerralheiro': int(form.cleaned_data['diasSerralheiro']),
                                     'quantSerralheiros': int(form.cleaned_data['quantSerralheiros']),
                                     'diasAuxiliar': int(form.cleaned_data['diasAuxiliar']),
                                     'quantAuxiliares': int(form.cleaned_data['quantAuxiliares']),
                                     'dificuldade': int(form.cleaned_data['dificuldade']),
                                     'apEstr': form.cleaned_data['apEstr'],
                                     'estrutura': 0
                                    }
                try:
                    ultNumItemEAP = int((g03EapOrc.objetos.filter(orcamento_id=codOrcAtual).order_by('-id')[0].codeap)[:1])
                except:
                    ultNumItemEAP = 0
                resultados = orc_poli_curvo(
                    f'{ultNumItemEAP+1}.', **dadosOrcPoliPlano)
                inserir_dados_eap(request, *resultados)
                # Atualizar custos do orcamento
                # GERANDO O ERRO 504 PELA DEMORA, FAZER O PROCESSO SEPARADO
                #atualizar_custos_orc(codOrcAtual)
                atualizar_lista_insumos(codOrcAtual)
                # Editar orcamento atual
                strCodOrc = int(codOrcAtual)
                return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
    else:
        form = formPoliCurvoFix()
        return render(request, "orcs/poli-curvo-fix.html", {"form": form, "orcamento": orcamento, })


def poli_curvo_ret(request, codorcam):
    orcamento = obter_dados_gerais_orc(codorcam)
    codOrcAtual = request.session['codorcamento']
    if request.POST:
        form = formPoliCurvoRet(request.POST)
        if "btnProximo" in request.POST:
            if form.is_valid():
                #Obter dados para calculos
                dadosOrcPoliPlano = {'codPoli': int(request.POST['combPolicarbonato']),
                                     'codPerfUn': int(request.POST['combPerfUn']),
                                     'codPerfAr': int(request.POST['combPerfAr']),
                                     'codPerfU': int(request.POST['combPerfU']),
                                     'cod_selante': int(request.POST['comb_selante']),
                                     'codPerfEsEx': int(request.POST['combPerfEsExterno']),
                                     'codPerfEsIn': int(request.POST['combPerfEsInterno']),
                                     'codCalandra': int(request.POST['combCalandra']),
                                     'codRufo': int(request.POST['combRufo']),
                                     'codCalha': int(request.POST['combCalha']),
                                     'codPerfGuar': int(request.POST['combPerfGuar']),
                                     'codPerfGax': int(request.POST['combPerfGax']),
                                     'codFitaVent': int(request.POST['combFitaVent']),
                                     'codMotor': int(request.POST['combMotores']),
                                     'quantMotor': int(form.cleaned_data['quantMotores']),
                                     'quantModulos': float(form.cleaned_data['quantModulos']),
                                     'quantModMoveis': float(form.cleaned_data['quantModMoveis']),
                                     'codCantoneira': int(request.POST['combCantoneira']),
                                     'codPerfCant': int(request.POST['combPerfCant']),
                                     'codRoldanas': int(request.POST['combRoldanas']),
                                     'direcMovimento': int(form.cleaned_data['direcMovimento']),
                                     'codPintura': int(request.POST['combPintura']),
                                     'quantPintura': float(formatar_custos_para_bd(request.POST['quantPintura'])) if form.cleaned_data['quantPintura'] else 0,
                                     'cordaPoli': float(formatar_custos_para_bd(form.cleaned_data['cordaPoli'])),
                                     'flechaPoli': float(formatar_custos_para_bd(form.cleaned_data['flechaPoli'])),
                                     'largPoli': float(formatar_custos_para_bd(form.cleaned_data['largPoli'])),
                                     'repetPoli': float(formatar_custos_para_bd(form.cleaned_data['repetPoli'])) if float(form.cleaned_data['repetPoli']) > 0 else 1,
                                     'distApoios': float(formatar_custos_para_bd(form.cleaned_data['distApoios'])),
                                     'distMaosF': 0,
                                     'montante': form.cleaned_data['montante'],
                                     'jusante': form.cleaned_data['jusante'],
                                     'latEsq': form.cleaned_data['latEsq'],
                                     'latDir': form.cleaned_data['latDir'],
                                     'diasSerralheiro': int(form.cleaned_data['diasSerralheiro']),
                                     'quantSerralheiros': int(form.cleaned_data['quantSerralheiros']),
                                     'diasAuxiliar': int(form.cleaned_data['diasAuxiliar']),
                                     'quantAuxiliares': int(form.cleaned_data['quantAuxiliares']),
                                     'dificuldade': int(form.cleaned_data['dificuldade']),
                                     'apEstr': form.cleaned_data['apEstr'],
                                     'estrutura': 1
                                    }
                try:
                    ultNumItemEAP = int((g03EapOrc.objetos.filter(orcamento_id=codOrcAtual).order_by('-id')[0].codeap)[:1])
                except:
                    ultNumItemEAP = 0
            resultados = orc_poli_curvo(
                f'{ultNumItemEAP+1}.', **dadosOrcPoliPlano)
            inserir_dados_eap(request, *resultados)
            # Atualizar custos do orcamento
            # GERANDO O ERRO 504 PELA DEMORA, FAZER O PROCESSO SEPARADO
            #atualizar_custos_orc(codOrcAtual)
            atualizar_lista_insumos(codOrcAtual)
            # Editar orcamento atual
            strCodOrc = int(codOrcAtual)
        return HttpResponseRedirect(reverse('orcs:editar_orcamento', args=(codorcam,)))
    else:
        form = formPoliCurvoRet()
        return render(request, "orcs/poli-curvo-ret.html", {"form": form, "orcamento": orcamento, })