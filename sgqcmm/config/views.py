from csv import reader
from decimal import Decimal
from io import StringIO
from pathlib import Path

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from main.forms import formNovoEndereco
from main.models import (a03Estados, a04Municipios, a05Bairros, a06Lograds,
                         a07TiposEnd, a08TiposFrete, a09TiposFone,
                         a10CatsInsumos, a11Insumos, a19PlsPgtos, a20StsOrcs,
                         a31FaseOrc, b01Empresas, b04CCustos)

from config.forms import (formCadastrarCentroDeCusto, formCadastrarEmpresa,
                          formCategoriaInsumo, formEditarCategoriaInsumo, formCadastroInsumo,
                          formEditarPlanoPagamento, formPlanoPagamento)


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



def inicio(request):
    if not request.user.is_staff:
        messages.error(request, "Não permitido, o usuário deve ser administrador para acessar esta seção")
        return redirect("main:inicio")
    else:
        return render(request, "config/inicio.html")

def empresas(request):
    if not request.user.is_staff:
        messages.error(request, "Negado, o usuário deve ser administrador para acessar esta seção")
        return redirect("main:inicio")
    else:
        empresas_bd = b01Empresas.objetos.all()
        empresas_cadastradas = []
        for empresa in empresas_bd:
            log_empresa = a06Lograds.objetos.get(id=empresa.lograd_id)
            bairro_empresa = a05Bairros.objetos.get(id=log_empresa.bairro_id)
            municipio_empresa = a04Municipios.objetos.get(id=bairro_empresa.municipio_id)
            endereco_empresa = f"{municipio_empresa.municipio}-{municipio_empresa.estado_id}, {bairro_empresa.bairro}, {log_empresa.logradouro}, {empresa.complend}"
            dic_empresa = {
                "id": empresa.id,
                "razao": empresa.razao,
                "cnpj": empresa.cnpj,
                "inscest": empresa.inscest,
                "endereco": endereco_empresa
            }
            empresas_cadastradas.append(dic_empresa)
        if request.method == "POST":
            form_cad_empresa = formCadastrarEmpresa(request.POST)
            if form_cad_empresa.is_valid():
                regiao = request.POST['regiao']
                estado = request.POST['estado']
                cidade = request.POST['cidade']
                if form_cad_empresa.cleaned_data['novo_bairro']:
                    try:
                        ultimo_id_bairro = a05Bairros.objetos.latest('id').id
                    except:
                        ultimo_id_bairro = -1
                    bairro = a05Bairros(
                        id=ultimo_id_bairro + 1,
                        bairro=form_cad_empresa.cleaned_data['novo_bairro'],
                        cepini=0,
                        cepfin=0,
                        distfab=0,
                        municipio=a04Municipios.objetos.get(id=cidade)
                    )
                    bairro.save()
                else:
                    if request.POST['bairro'] != "":
                        bairro = a05Bairros.objetos.get(id=request.POST['bairro'])
                if form_cad_empresa.cleaned_data['novo_logradouro']:
                    try:
                        ultimo_id_logradouro = a06Lograds.objetos.latest('id').id
                    except:
                        ultimo_id_logradouro = -1
                    logradouro = a06Lograds(
                        id=ultimo_id_logradouro + 1,
                        logradouro=form_cad_empresa.cleaned_data['novo_logradouro'],
                        ceplogr="",
                        distfab=0,
                        bairro=bairro
                    )
                    logradouro.save()
                else:
                    if request.POST['logradouro'] != "":
                        logradouro = a06Lograds.objetos.get(id=request.POST['logradouro'])
                complemento = form_cad_empresa.cleaned_data['complemento']
                try:
                    id_nova_empresa = b01Empresas.objetos.latest('id').id + 1
                except:
                    id_nova_empresa = 0
                if len(b01Empresas.objetos.filter(Q(razao=form_cad_empresa.cleaned_data['razao'])|Q(cnpj=form_cad_empresa.cleaned_data['cnpj'])|Q(codemp=form_cad_empresa.cleaned_data['codigo_empresa'])|Q(inscest=form_cad_empresa.cleaned_data['inscricao_estadual']))) > 0:
                    messages.error(request, "Empresa com dados semelhantes já cadastrada, verifique os dados")
                else: 
                    nova_empresa = b01Empresas(
                        id=id_nova_empresa,
                        juridica=form_cad_empresa.cleaned_data['juridica'],
                        razao=form_cad_empresa.cleaned_data['razao'],
                        fantasia=form_cad_empresa.cleaned_data['fantasia'],
                        codemp=form_cad_empresa.cleaned_data['codigo_empresa'],
                        lograd=logradouro,
                        complend=form_cad_empresa.cleaned_data['complemento'],
                        cnpj=form_cad_empresa.cleaned_data['cnpj'],
                        inscest=form_cad_empresa.cleaned_data['inscricao_estadual'],
                        observs=form_cad_empresa.cleaned_data['observacao']
                    )
                    nova_empresa.save()
                    messages.success(request, "Empresa Cadastrada")
                return render(request, "config/empresas.html", {"empresasCadastradas": empresas_cadastradas, "formCadEmpresa": formCadastrarEmpresa()})
            else:
                print(f"\n\n\n{form_cad_empresa.errors.as_data()}\n\n\n")
                messages.error(request, "Erro nos dados do formulário")
        return render(request, "config/empresas.html", {"empresasCadastradas": empresas_cadastradas, "formCadEmpresa": formCadastrarEmpresa()})


def centro_de_custos(request, cod_empresa):
    if not request.user.is_staff:
        messages.error(request, "Negado, o usuário deve ser administrador para acessar esta seção")
        return redirect("main:inicio")
    else:
        empresa = b01Empresas.objetos.get(id=cod_empresa)
        if request.method == "POST":
            form = formCadastrarCentroDeCusto(request.POST)
            if form.is_valid():
                descricao = f"{empresa.codemp} {form.cleaned_data['descricao']}"
                funcionamento = form.cleaned_data['funcionamento']
                sequencia_holerite = form.cleaned_data['sequencia_holerite']
                ativo = form.cleaned_data['ativo']
                if len(b04CCustos.objetos.filter(descricao=descricao, funccc=funcionamento, seqmfhol=sequencia_holerite, empresa=empresa)) > 0:
                    messages.error(request, "Centro de custo já cadastrado")
                else:
                    try:
                        last_id = b04CCustos.objetos.latest('id').id + 1
                    except:
                        last_id = -1
                    novo_centro_de_custo = b04CCustos(
                        id=last_id + 1,
                        funccc=funcionamento,
                        descricao=descricao,
                        ativo=ativo,
                        seqmfhol=sequencia_holerite,
                        empresa=empresa
                    )
                    novo_centro_de_custo.save()                
                    messages.success(request, "Centro de custo adicionado")
        centro_de_custos_empresa = b04CCustos.objetos.filter(empresa=empresa)
        list_centro_de_custos = []
        for centro in centro_de_custos_empresa:
            dic_centro = {
                "id": centro.id,
                "funccc": centro.funccc,
                "descricao": centro.descricao,
                "ativo": centro.ativo
            }
            list_centro_de_custos.append(dic_centro)
    return render(request, "config/centro-de-custos.html", {"centrosDeCusto": list_centro_de_custos, "empresa": empresa, "formCadastrarCentroDeCusto": formCadastrarCentroDeCusto()})

def orcamento(request):
    if not request.user.is_staff:
        messages.error(request, "Negado, o usuário deve ser administrador para acessar esta seção")
        return redirect("main:inicio")
    else:        
        return render(request, "config/orcamento.html")

def categoria_insumo(request):
    if not request.user.is_staff:
        messages.error(request, "Negado, o usuário deve ser administrador para acessar esta seção")
        return redirect("main:inicio")
    else:
        if request.method == "POST":
            form = formCategoriaInsumo(request.POST)
            if form.is_valid():
                tipo = request.POST['tipo']
                hierarquia = form.cleaned_data['hierarquia']
                ordenador = form.cleaned_data['ordenador']
                descricao = form.cleaned_data['descricao']
                if a10CatsInsumos.objetos.filter(Q(ordenador=ordenador)|Q(descricao=descricao)).exists():
                    return HttpResponse(status=400)
                else:
                    try:
                        ultimo_id_categoria = a10CatsInsumos.objetos.latest('id').id
                    except:
                        ultimo_id_categoria = -1
                    nova_categoria_insumo = a10CatsInsumos(
                        id=ultimo_id_categoria + 1,
                        hierarquia=hierarquia,
                        ordenador=ordenador,
                        tipo=tipo,
                        descricao=descricao
                    )
                    nova_categoria_insumo.save()
                    messages.success(request, "Categoria de insumo cadastrada")
            else:
                print("\nERROR FORM\n")
                print(form.errors.as_data())
        categorias_insumo_cadastradas = a10CatsInsumos.get_all_categories(a10CatsInsumos)
        form = formCategoriaInsumo()
        return render(request, "config/categoria-insumo.html", 
            {'formCadCategoria': form, 'categoriasCadastradas': categorias_insumo_cadastradas})

def carregar_categorias_insumo(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    else:
        categorias_insumo = a10CatsInsumos.get_all_categories(a10CatsInsumos)
        return render(request, 'config/carregar-categorias-insumos.html',
            {"categoriasCadastradas": categorias_insumo})

def editar_categoria_insumo(request, cod_categoria):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    else:
        categoria_insumo = a10CatsInsumos.objetos.get(id=cod_categoria)
        if request.method == "POST":
            form = formEditarCategoriaInsumo(request.POST)
            if form.is_valid():
                categoria_insumo.tipo = request.POST['tipo'] if request.POST['tipo'] != '' else  categoria_insumo.tipo
                categoria_insumo.hierarquia = form.cleaned_data['hierarquia'] if form.cleaned_data['hierarquia'] else categoria_insumo.hierarquia
                categoria_insumo.ordenador = form.cleaned_data['ordenador'] if form.cleaned_data['ordenador'] else categoria_insumo.ordenador
                categoria_insumo.descricao = form.cleaned_data['descricao'] if form.cleaned_data['descricao'] else categoria_insumo.descricao
                categoria_insumo.save()
                messages.success(request, "Categoria alterada com sucesso")
                return redirect("config:categoria_insumo")
            else:
                messages.error(request, "Dados inválidos")
                return render(request, 'config/editar-categoria-insumo.html',
                    {'form': form, "categoria": categoria_insumo})        
        form = formEditarCategoriaInsumo()
        return render(request, 'config/editar-categoria-insumo.html',
            {'form': form, "categoria": categoria_insumo})


def insumos_orcamento(request):
    if not request.user.is_staff:
        messages.error(request, "Negado, o usuário deve ser administrador para acessar esta seção")
        return redirect("main:inicio")
    else:
        if request.method == "POST":
            form = formCadastroInsumo(request.POST)
            if form.is_valid():
                categoria = request.POST['categoria']
                descricao = form.cleaned_data['descricao']
                unidade_base = form.cleaned_data['unidade_base']
                unidade_compra = form.cleaned_data['unidade_compra'] if form.cleaned_data['unidade_compra'] else form.cleaned_data['unidade_base']
                fator_conversao = form.cleaned_data['fator_conversao'] if form.cleaned_data['fator_conversao'] else 1
                custo_1 = form.cleaned_data['custo_1']
                custo_2 = form.cleaned_data['custo_2'] if form.cleaned_data['custo_2'] else form.cleaned_data['custo_1']
                preco_unitario_venda = form.cleaned_data['preco_unitario_venda'] if form.cleaned_data['preco_unitario_venda'] else form.cleaned_data['custo_1']
                peso_unidade_basica = form.cleaned_data['peso_unidade_basica'] if form.cleaned_data['peso_unidade_basica'] else 0
                quantidade_unidade_palete = form.cleaned_data['quantidade_unidade_palete'] if form.cleaned_data['quantidade_unidade_palete'] else 0
                comprimento = form.cleaned_data['comprimento'] if form.cleaned_data['comprimento'] else 0
                largura = form.cleaned_data['largura'] if form.cleaned_data['largura'] else 0
                espessura = form.cleaned_data['espessura'] if form.cleaned_data['espessura'] else 0
                try:
                    ultimo_insumo = a11Insumos.objetos.latest('id')
                    id_novo_insumo = ultimo_insumo.id + 1
                    codigo_novo_insumo = ultimo_insumo.codigo + 1
                except ObjectDoesNotExist:
                    id_novo_insumo = 0
                    codigo_novo_insumo = 0
                try:
                    novo_insumo = a11Insumos(
                        id = id_novo_insumo,
                        catins = a10CatsInsumos.objetos.get(id=categoria),
                        codigo = codigo_novo_insumo,
                        descricao = descricao,
                        undbas = unidade_base,
                        undcompr = unidade_compra,
                        fatundcomp = fator_conversao,
                        custo01 = custo_1,
                        custo02 = custo_2,
                        prvda = preco_unitario_venda,
                        pesunbas = peso_unidade_basica,
                        qtppal = quantidade_unidade_palete,
                        comprimento = comprimento,
                        largura = largura,
                        espessura = espessura
                    )
                    novo_insumo.save()
                    return HttpResponse(status=201)
                except:
                    return HttpResponse(status=400)
        form = formCadastroInsumo()
        insumos_cadastrados = a11Insumos.objetos.all().only('id', 'codigo', 'descricao', 'catins')
        return render(request, "config/insumo-orcamento.html", 
            {'formCadInsumo': form, 'insumosCadastrados': insumos_cadastrados})


def carregar_insumos(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    else:
        insumos_cadastrados = a11Insumos.objetos.all().only('id', 'codigo', 'descricao', 'catins')
        return render(request, 'config/carregar-insumos.html',
            {"insumosCadastrados": insumos_cadastrados})


def planos_pagamento(request):
    if not request.user.is_staff:
        messages.error(request, "Negado, o usuário deve ser administrador para acessar esta seção")
        return redirect("main:inicio")
    else:
        if request.method == "POST":
            form = formPlanoPagamento(request.POST)
            if form.is_valid():
                tipo = form.cleaned_data['tipo']
                forma_pgto = form.cleaned_data['forma_pgto']
                descricao = form.cleaned_data['descricao']
                descricao_externa = form.cleaned_data['descricao_externa']
                if a19PlsPgtos.objetos.filter(Q(formapgto=forma_pgto)|Q(descricao=descricao)|Q(descricaoexterna=descricao_externa)).exists():
                    return HttpResponse(status=400)
                else:
                    try:
                        ultimo_id_categoria = a19PlsPgtos.objetos.latest('id').id
                    except:
                        ultimo_id_categoria = -1
                    novo_plano_pgto = a19PlsPgtos(
                        id=ultimo_id_categoria + 1,
                        tipo=tipo,
                        formapgto=forma_pgto,
                        descricao=descricao,
                        descricaoexterna=descricao_externa
                    )
                    novo_plano_pgto.save()
                    messages.success(request, "Plano de pagamento cadastrado")
                    return HttpResponse(status=201)
            else:
                print("\nERROR FORM\n")
                print(form.errors.as_data())
                return HttpResponse(status=400)
        elif request.method == "GET":
            planos_pgto_cadastrados = a19PlsPgtos.objetos.all()
            form = formPlanoPagamento()
            return render(request, "config/plano-pagamento.html", 
                {'planosCadastrados': planos_pgto_cadastrados, "formCadastroPlanoPgto": form})
        else:
            return HttpResponse(status=405)

def editar_plano_pagamento(request, id_plano):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    else:
        plano_pagamento = a19PlsPgtos.objetos.get(id=id_plano)
        if request.method == "POST":
            form = formEditarPlanoPagamento(request.POST)
            if form.is_valid():
                plano_pagamento.tipo = request.POST['tipo'] if request.POST['tipo'] != '' else  plano_pagamento.tipo
                plano_pagamento.formapgto = form.cleaned_data['forma_pgto'] if form.cleaned_data['forma_pgto'] else plano_pagamento.formapgto
                plano_pagamento.descricao = form.cleaned_data['descricao'] if form.cleaned_data['descricao'] else plano_pagamento.descricao
                plano_pagamento.descricaoexterna = form.cleaned_data['descricao_externa'] if form.cleaned_data['descricao_externa'] else plano_pagamento.descricaoexterna
                plano_pagamento.save()
                messages.success(request, "Plano de pagamento alterado com sucesso")
                return redirect("config:planos_pagamento")
            else:
                messages.error(request, "Dados inválidos")
                return render(request, 'config/editar-plano-pagamento.html',
                    {'form': form, "plano": plano_pagamento})
        elif request.method == "GET":
            form = formEditarPlanoPagamento()
            return render(request, 'config/editar-plano-pagamento.html',
                {'form': form, "plano": plano_pagamento})

def ajax_carregar_planos_pgto(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    else:
        planos_pgto_cadastrados = a19PlsPgtos.objetos.all()
        return render(request, 'config/ajax-carregar-planos-pgto.html',
            {'planosCadastrados': planos_pgto_cadastrados})


def adicionar_seeds(request):
    return render(request, 'config/adicionar-seeds.html')


def adicionar_seeds_estados(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    else:
        if a03Estados.objetos.filter(uf="GO").exists():
            return HttpResponse(content="Dados já adicionados", status=400)
        else:
            try:
                csv_file = Path.cwd().joinpath("seeds_db", 'main_a03estados.csv')
                data_set = csv_file.read_text(encoding='UTF-8')
                io_string = StringIO(data_set)
                for column in reader(io_string, delimiter=',', quotechar="|"):
                    country = a03Estados(
                        uf=column[0].strip(' "'),
                        estado=column[1].strip(' "'),
                        regiao=column[2].strip(' "'),
                        distfab=Decimal(column[3].strip(' "')),
                        cepfin=column[4].strip(' "'),
                        cepini=column[5].strip(' "'),
                    )
                    country.save()
                return HttpResponse(content="Dados adicionados", status=201)
            except:
                return HttpResponse(content="Erro ao interno ao adicionar estados", status=500)


def adicionar_seeds_municipios(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    else:
        if a04Municipios.objetos.filter(id=1).exists():
            return HttpResponse(content="Dados já adicionados", status=400)
        else:
            try:
                csv_file = Path.cwd().joinpath("seeds_db", 'main_a04municipios.csv')
                data_set = csv_file.read_text(encoding='UTF-8')
                io_string = StringIO(data_set)
                for count, column in enumerate(reader(io_string, delimiter=',', quotechar="|")):
                    city = a04Municipios(
                        id=count,
                        municipio=column[1].strip(' "'),
                        cepini=column[2].strip(' "'),
                        cepfin=column[3].strip(' "'),
                        distfab=Decimal(column[4].strip(' "')),
                        estado_id=column[5].strip(' "')
                    )
                    city.save()
                return HttpResponse(content="Dados adicionados", status=201)
            except:
                return HttpResponse(content="Erro ao interno ao adicionar estados", status=500)


def adicionar_seeds_tipos_endereco(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    else:
        if a07TiposEnd.objetos.filter(id=1).exists():
            return HttpResponse(content="Dados já adicionados", status=400)
        else:
            try:
                csv_file = Path.cwd().joinpath("seeds_db", 'main_a07tiposend.csv')
                data_set = csv_file.read_text(encoding='UTF-8')
                io_string = StringIO(data_set)
                for count, column in enumerate(reader(io_string, delimiter=',', quotechar="|")):
                    tipo_endereco = a07TiposEnd(
                        id=column[0].strip(' "'),
                        tend=column[1].strip(' "'),
                    )
                    tipo_endereco.save()
                return HttpResponse(content="Dados adicionados", status=201)
            except:
                return HttpResponse(content="Erro ao interno ao adicionar estados", status=500)


def adicionar_seeds_tipos_frete(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    else:
        if a08TiposFrete.objetos.filter(id=1).exists():
            return HttpResponse(content="Dados já adicionados", status=400)
        else:
            try:
                csv_file = Path.cwd().joinpath("seeds_db", 'main_a08tiposfrete.csv')
                data_set = csv_file.read_text(encoding='UTF-8')
                io_string = StringIO(data_set)
                for column in reader(io_string, delimiter=';', quotechar='|'):
                    novo_tipo_frete = a08TiposFrete(
                        id=column[0].strip(' "'),
                        descsing=column[1].strip(' "'),
                        descplur=column[2].strip(' "'),
                        desccomp=column[3].strip(' "'),
                        pesomax=column[4].strip(' "'),
                        volmax=column[5].strip(' "'),
                        vlrkm=column[6].strip(' "'),
                    )
                    novo_tipo_frete.save()
                return HttpResponse(content="Dados adicionados", status=201)
            except:
                return HttpResponse(content="Erro ao interno ao adicionar estados", status=500)


def adicionar_seeds_tipos_telefones(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    else:
        if a09TiposFone.objetos.filter(id=1).exists():
            return HttpResponse(content="Dados já adicionados", status=400)
        else:
            try:
                csv_file = Path.cwd().joinpath("seeds_db", 'main_a09tiposfone.csv')
                data_set = csv_file.read_text(encoding='UTF-8')
                io_string = StringIO(data_set)
                for count, column in enumerate(reader(io_string, delimiter=',', quotechar="|")):
                    phone = a09TiposFone(
                        id=count + 1,
                        tfone=column[1].strip(' "'),
                    )
                    phone.save()
                return HttpResponse(content="Dados adicionados", status=201)
            except:
                return HttpResponse(content="Erro ao interno ao adicionar estados", status=500)


def adicionar_seeds_planos_pagamento(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    else:
        if a19PlsPgtos.objetos.filter(id=1).exists():
            return HttpResponse(content="Dados já adicionados", status=400)
        else:
            try:
                csv_file = Path.cwd().joinpath("seeds_db", 'main_a19plspgtos.csv')
                data_set = csv_file.read_text(encoding='UTF-8')
                io_string = StringIO(data_set)
                for column in reader(io_string, delimiter=';', quotechar='|'):
                    novo_plano = a19PlsPgtos(
                        id=column[0].strip(' "'),
                        tipo=column[1].strip(' "'),
                        formapgto=column[2].strip(' "'),
                        descricao=column[3].strip(' "'),
                        
                    )
                    novo_plano.save()
                return HttpResponse(content="Dados adicionados", status=201)
            except:
                return HttpResponse(content="Erro ao interno ao adicionar estados", status=500)


def adicionar_seeds_status_orcamento(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    else:
        if a20StsOrcs.objetos.filter(id=1).exists():
            return HttpResponse(content="Dados já adicionados", status=400)
        else:
            try:
                csv_file = Path.cwd().joinpath("seeds_db", 'main_a20stsorcs.csv')
                data_set = csv_file.read_text(encoding='UTF-8')
                io_string = StringIO(data_set)
                for column in reader(io_string, delimiter=',', quotechar='|'):
                    novo_status = a20StsOrcs(
                        id=column[0].strip(' "'),
                        descricao=column[1].strip(' "'),
                        alerta=column[2].strip(' "'), 
                        ativo=column[3].strip(' "'),
                        transfoe=column[4].strip(' "'),
                    )
                    novo_status.save()
                return HttpResponse(content="Dados adicionados", status=201)
            except:
                return HttpResponse(content="Erro ao interno ao adicionar estados", status=500)


def adicionar_seeds_fases_orcamento(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    else:
        if a31FaseOrc.objetos.filter(id=1).exists():
            return HttpResponse(content="Dados já adicionados", status=400)
        else:
            try:
                csv_file = Path.cwd().joinpath("seeds_db", 'main_a31faseorc.csv')
                data_set = csv_file.read_text(encoding='UTF-8')
                io_string = StringIO(data_set)
                for column in reader(io_string, delimiter=',', quotechar='|'):
                    new_fase = a31FaseOrc(
                        id=column[0].strip(' "'),
                        descricao=column[1].strip(' "')
                    )
                    new_fase.save()
                return HttpResponse(content="Dados adicionados", status=201)
            except:
                return HttpResponse(content="Erro ao interno ao adicionar estados", status=500)


def adicionar_seeds_categorias_insumos(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    else:
        if a10CatsInsumos.objetos.filter(id=1).exists():
            return HttpResponse(content="Dados já adicionados", status=400)
        else:
            try:
                csv_file = Path.cwd().joinpath("seeds_db", 'main_a10catsinsumos.csv')
                data_set = csv_file.read_text(encoding='UTF-8')
                io_string = StringIO(data_set)
                for column in reader(io_string, delimiter=';', quotechar='|'):
                    nova_categoria = a10CatsInsumos(
                        id=column[0].strip(' "'),
                        hierarquia=column[1].strip(' "'),
                        ordenador=column[2].strip(' "'),
                        descricao=column[3].strip(' "'),
                        tipo=column[4].strip(' "')
                    )
                    nova_categoria.save()
                return HttpResponse(content="Dados adicionados", status=201)
            except:
                return HttpResponse(content="Erro ao interno ao adicionar estados", status=500)


def adicionar_seeds_insumos(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    else:
        if a11Insumos.objetos.filter(id=1).exists():
            return HttpResponse(content="Dados já adicionados", status=400)
        else:
            try:
                csv_file = Path.cwd().joinpath("seeds_db", 'main_a11insumos.csv')
                data_set = csv_file.read_text(encoding='UTF-8')
                io_string = StringIO(data_set)
                for column in reader(io_string, delimiter=';', quotechar='|'):
                    nova_categoria = a11Insumos(
                        id=column[0].strip(' "'),
                        codigo=column[1].strip(' "'),
                        descricao=column[2].strip(' "'),
                        undbas=column[3].strip(' "'),
                        undcompr=column[4].strip(' "'),
                        fatundcomp=column[5].strip(' "'),
                        custo01=column[6].strip(' "'),
                        custo02=column[7].strip(' "'),
                        prvda=column[8].strip(' "'),
                        pesunbas=column[9].strip(' "'),
                        qtppal=column[10].strip(' "'),
                        catins=a10CatsInsumos.objetos.get(id=column[11].strip(' "')),
                        espessura=column[12].strip(' "'),
                        dataatualizacao=column[13].strip(' "'),
                        comprimento=column[14].strip(' "'),
                        largura=column[15].strip(' "'),
                    )
                    nova_categoria.save()
                return HttpResponse(content="Dados adicionados", status=201)
            except:
                return HttpResponse(content="Erro ao interno ao adicionar estados", status=500)

