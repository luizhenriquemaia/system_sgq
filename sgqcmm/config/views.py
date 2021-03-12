from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from main.models import a03Estados, a04Municipios, a05Bairros, a06Lograds, a10CatsInsumos, b01Empresas, b04CCustos
from main.forms import formNovoEndereco

from config.forms import formCadastrarEmpresa, formCadastrarCentroDeCusto, formCategoriaInsumo, formEditarCategoriaInsumo



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
                    bairro = a05Bairros(
                        id=a05Bairros.objetos.latest('id').id + 1,
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
                    logradouro = a06Lograds(
                        id=a06Lograds.objetos.latest('id').id + 1,
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
