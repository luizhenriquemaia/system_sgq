from django.contrib import messages
from django.shortcuts import render

from main.models import a03Estados, a04Municipios, a05Bairros, a06Lograds, b01Empresas
from main.forms import formNovoEndereco

from config.forms import formCadastrarEmpresa



def inicio(request):
    if not request.user.is_staff:
        messages.error(request, "Não permitido, o usuário deve ser administrativo para acessar esta seção")
        return redirect("main:inicio")
    else:
        return render(request, "config/inicio.html")

def empresas(request):
    if not request.user.is_staff:
        messages.error(request, "Negado, o usuário deve ser administrativo para acessar esta seção")
        return redirect("main:inicio")
    else:
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
            else:
                print(f"\n\n\n{form_cad_empresa.errors.as_data()}\n\n\n")
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
        return render(request, "config/empresas.html", {"empresasCadastradas": empresas_cadastradas, "formCadEmpresa": formCadastrarEmpresa()})
