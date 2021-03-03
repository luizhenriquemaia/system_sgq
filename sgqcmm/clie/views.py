from csv import reader
from decimal import Decimal
from io import StringIO
from pathlib import Path

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render, reverse)
from main.forms import formNovoEndereco
from main.funcoes import format_list_telefone, nomesequencia, numpurotelefone
from main.models import (a03Estados, a04Municipios, a05Bairros, a06Lograds,
                         a07TiposEnd, a09TiposFone, b01Empresas, e01Cadastros, e02FonesCad,
                         e03WebCad, e04EndCad, e06ContCad)

from clie.forms import (formDadosCliente, formDadosEmpresa, formEscCliente,
                        formPesqCliente, formSelecionarEmpresa)


# Pesquisa cliente por nome, telefone ou e-mail
def pesqcliente(request):
    if request.method == "POST":
        form = formPesqCliente(request.POST)
        if form.is_valid():
            nomecliente = form.cleaned_data['nome']
            fonepesq = form.cleaned_data['fone']
            emailpesq = form.cleaned_data['email']
            # Procurar pelo dono do telefone na base de dados
            if len(fonepesq) > 0:
                # Verificar se o numero de telefone fornecido e valido
                fonepuro = numpurotelefone(fonepesq)
                if len(fonepuro) < 10:
                    messages.error(request, 'Numero de telefone inválido.')
                    form = formPesqCliente(request.POST)
                    return render(request, "clie/formpesqcliente.html", {"form": form})
                cadfone = int(e02FonesCad.numjacadastrado(e02FonesCad, fonepuro))
            else:
                cadfone = 0
            # Procurar pelo dono do email na base de dados
            if len(emailpesq) > 0:
                cademail = int(e03WebCad.emailjacadastrado(e03WebCad, emailpesq))
            else:
                cademail = 0
            # Procurar pelo cliente na base de dados usando os dados fornecidos
            if cadfone > 0:
                # Prosseguir com o codigo do cadastro obtido pelo telefone
                request.session['codcliente'] = cadfone
                request.session['novofone'] = '0'
                if cademail == 0:
                    request.session['novoemail'] = emailpesq
                else:
                    request.session['novoemail'] = '@'
                return HttpResponseRedirect(reverse('clie:dados_cliente'))
            elif cademail > 0:
                # Prosseguir com o codigo do cadastro obtido pelo email
                request.session['codcliente'] = cademail
                request.session['novofone'] = fonepesq
                request.session['novoemail'] = '@'
                return HttpResponseRedirect(reverse('clie:dados_cliente'))
            else:
                # Nem telefone, nem email cadastrados, procurar apenas pelo nome
                clientesposs = e01Cadastros.possiveisclientes(e01Cadastros, nomecliente)
                qtdclientes = len(clientesposs)
                if qtdclientes == 1:
                    # Encontrado um unico cliente com o nome digitado, seguir com o seu codigo
                    clienteencontrado = clientesposs[0]
                    codcliente = clienteencontrado.id
                    if not fonepesq or fonepesq == '':
                        fonepesq = '0'
                    if not emailpesq or emailpesq == '':
                        emailpesq = '@'
                    request.session['codcliente'] = codcliente
                    request.session['novofone'] = fonepesq
                    request.session['novoemail'] = emailpesq
                    return HttpResponseRedirect(reverse('clie:dados_cliente'))
                elif qtdclientes > 0:
                    # Encontrado mais de um cliente com o nome digitado, escolher de uma lista:
                    if not fonepesq or fonepesq == '':
                        fonepesq = '0'
                    if not emailpesq or emailpesq == '':
                        emailpesq = '@'
                    request.session['filtroclie'] = nomecliente
                    request.session['novofone'] = fonepesq
                    request.session['novoemail'] = emailpesq
                    return HttpResponseRedirect(reverse('clie:selecionar_cliente'))
                else:
                    # Nao encontrado nenhum cliente com o nome digitado, criar um novo cliente
                    criar_novo_cliente(request, nomecliente, fonepesq, emailpesq)
                    return HttpResponseRedirect(reverse('clie:dados_cliente'))
    else:
        form = formPesqCliente()
    return render(request, "clie/pesquisar-cliente.html", {"form": form})


def criar_novo_cliente(request, nome, telefone, email):
    # Se não tiver nenhum cliente adicionado ainda
    try:
        cod_cliente = e01Cadastros.objetos.latest('id').id + 1
    except ObjectDoesNotExist:
        cod_cliente = 1
    # Caso seja o primeiro cadastro de cliente
    try:
        # teste para ver se existem estados cadastrados
        a03Estados.objetos.get(id=1)
    except:
        # cadastrar estados do seeds_db
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
    try:
        #teste para ver se existem cidades cadastradas
        a04Municipios.objetos.get(id=1)
    except:
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
    try:
        #teste para ver se existem tipos de telefones cadastrados
        a09TiposFone.objetos.get(id=1)
    except:
        csv_file = Path.cwd().joinpath("seeds_db", 'main_a09tiposfone.csv')
        data_set = csv_file.read_text(encoding='UTF-8')
        io_string = StringIO(data_set)
        for count, column in enumerate(reader(io_string, delimiter=',', quotechar="|")):
            phone = a09TiposFone(
                id=count + 1,
                tfone=column[1].strip(' "'),
            )
            phone.save()
    cliente = e01Cadastros(
        id=cod_cliente,
        usrcad=request.user,
        juridica=False,
        descrcad=nome,
        razao=nome,
        tipo=1
    )
    cliente.save()
    # Cadastrar telefone do cliente
    if telefone:
        e02FonesCad.novofonecad(e02FonesCad, cod_cliente, telefone)
    # Cadastrar email do cliente
    if email == '' or email == '@':
        pass
    else:
        e03WebCad.novoemail(e03WebCad, cod_cliente, email)
    # Requerer nome completo do cliente e tratamento (Sr., Sra., etc.)
    request.session['codcliente'] = cod_cliente
    request.session['novofone'] = '0'
    request.session['novoemail'] = '@'
    return


def selecionar_cliente(request):
    filtro_cliente = request.session['filtroclie']
    lista_clientes = e01Cadastros.possiveisclientes(e01Cadastros, filtro_cliente)
    escolhas_clientes = [('0', 'Adicionar novo cliente')]
    for cliente in lista_clientes:
        escolhas_clientes.append(tuple((cliente.id, cliente.descricao)))
    if request.method == "POST":
        form = formEscCliente(request.POST, escolhas_clientes=escolhas_clientes)
        if form.is_valid():
            cod_cliente = int(request.POST['clientes'])
            if cod_cliente == 0:
                # Adicionar novo cliente
                telefone = request.session['novofone']
                email = request.session['novoemail']
                criar_novo_cliente(request, filtro_cliente, telefone, email)
            elif cod_cliente > 0:
                # Atualizacao simplificada do cliente escolhido
                request.session['codcliente'] = cod_cliente
            return HttpResponseRedirect(reverse('clie:dados_cliente'))
    else:
        form = formEscCliente(escolhas_clientes=escolhas_clientes)
    return render(request, "clie/selecionar-cliente.html", {"form": form, "listaClientes": lista_clientes})


def dados_empresa(request, codempresa):
    empresa = get_object_or_404(e01Cadastros, id=codempresa)
    telefones = e02FonesCad.objetos.filter(cadastro_id=codempresa)
    emails = e03WebCad.objetos.filter(cadastro_id=codempresa)
    enderecos = e04EndCad.enderecoscad(e04EndCad, codempresa)
    if request.method == "POST":
        form = formDadosEmpresa(request.POST)
        if form.is_valid():
            empresa.razao = form.cleaned_data['nome']
            empresa.cnpj = form.cleaned_data['cnpj']
            empresa.genero = request.POST['genero']
            cod_endereco = int(form.cleaned_data['endereco'])
            if cod_endereco == 0:
                return HttpResponseRedirect(reverse('clie:cadastrar_novo_endereco'))
            else:
                # Continua usando o endereco selecionado
                lograd_empresa = e04EndCad.objetos.get(id=int(cod_endereco))
                cod_logr_empresa = lograd_empresa.lograd_id
                request.session['codendcliente'] = cod_endereco
                request.session['codlogr'] = cod_logr_empresa
                cod_bairro = a06Lograds.objetos.get(pk=cod_logr_empresa).bairro_id
                request.session['codbair'] = cod_bairro
                bairro = a05Bairros.objetos.get(pk=cod_bairro)
                munic = a04Municipios.objetos.get(pk=bairro.municipio_id)
                cod_municipio = munic.id
                request.session['codmuni'] = cod_municipio
                sigla_uf = munic.estado_id
                request.session['siglauf'] = sigla_uf
                request.session['regiao'] = a03Estados.objetos.get(
                    pk=sigla_uf).regiao
                # cliente != de empresa
                codorcam = request.session['codorcam']
                return HttpResponseRedirect(reverse('orcs:editar_contrato', args=(codorcam, )))
    else:
        dados_empresa = {
            "nome": empresa.razao,
            "cnpj": empresa.cnpj,
            "genero": empresa.genero,
            "telefones": telefones,
            "emails": emails,
            "enderecos": enderecos
        }
        form = formDadosEmpresa()
    return render(request, "clie/dados-empresa.html", {"form": form, "dadosEmpresa": dados_empresa})


def dados_cliente(request):
    cod_cliente = request.session['codcliente']
    cliente = get_object_or_404(e01Cadastros, id=cod_cliente)
    novo_telefone = request.session['novofone']
    novo_email = request.session['novoemail']
    telefones = e02FonesCad.fonescad(e02FonesCad, cod_cliente)
    telefones = format_list_telefone(telefones)
    emails = e03WebCad.objetos.filter(cadastro_id=cod_cliente)
    enderecos = e04EndCad.enderecoscad(e04EndCad, cod_cliente)
    if cliente.cnpj == None:
        cliente.cnpj = ""
    dados_cliente = {
        "tratamento": cliente.fantasia,
        "nome": cliente.razao,
        "cnpj": cliente.cnpj,
        "descricao": cliente.descrcad,
        "juridica": cliente.juridica,
        "genero": cliente.genero,
        "telefones": telefones,
        "emails": emails,
        "enderecos": enderecos
    }
    if request.method == "POST":
        form = formDadosCliente(request.POST)
        if form.is_valid():
            # Alterar dados do cliente
            cliente.fantasia = form.cleaned_data['tratamento']
            cliente.nome = form.cleaned_data['nome']
            cliente.cnpj = form.cleaned_data['cnpj']
            cliente.descrcad = form.cleaned_data['descricao']
            cliente.juridica = int(request.POST['juridica'])
            cliente.genero = int(request.POST['genero'])
            try:
                empresa = int(request.POST['empresa'])
            except ValueError:
                empresa = 0
            cliente.ativo = 1
            cliente.usrcad_id = request.user.id
            # Verificar se é empresa
            # Se for empresa, adicionar contato
            if empresa != 0:
                obj_contato = e06ContCad(
                    id=e06ContCad.objetos.latest('id').id + 1,
                    titulo='contato',
                    cargo='contato',
                    contato=cod_cliente,
                    empresa_id=empresa)
                cliente.contempresa = obj_contato.id
                obj_contato.save()
            cliente.save()
            # Cadastrar novo telefone
            novo_telefone = form.cleaned_data['telefone']
            if novo_telefone:
                if novo_telefone != '0':
                    e02FonesCad.novofonecad(e02FonesCad, cod_cliente, novo_telefone)
            # Cadastrar novo email
            email = form.cleaned_data['email']
            if email != '':
                emails_existentes = e03WebCad.objetos.filter(cadastro_id=cod_cliente)
                if emails_existentes.count() == 0:
                    novo_email = e03WebCad(
                        id=e03WebCad.objetos.latest('id').id + 1,
                        tipo=1,
                        endweb=email,
                        cadastro_id=cod_cliente
                    )
                    novo_email.save()
                elif emails_existentes.count() >= 1:
                    emails_existentes[0].endweb = email
                    emails_existentes[0].save()
            # Se for empresa, adicionar contato
            if cliente.juridica == 1:
                messages.success(request, "Empresa adicionada com sucesso, adicione um contato")
                return HttpResponseRedirect(
                    reverse('clie:pesqcliente', args=(1,)))
            # Se não for empresa, adicionar endereço
            # Verificar se deve cadastrar novo endereco
            cod_endereco = int(form.cleaned_data['endereco'])
            if cod_endereco == 0:
                return HttpResponseRedirect(reverse('clie:cadastrar_novo_endereco'))
            else:
                # Continua usando o endereco selecionado
                logrCli = e04EndCad.objetos.get(id=int(cod_endereco))
                codlogrclie = logrCli.lograd_id
                request.session['cod_endereço_cliente'] = cod_endereco
                request.session['codlogr'] = codlogrclie
                codbairro = a06Lograds.objetos.get(pk=codlogrclie).bairro_id
                request.session['codbair'] = codbairro
                bairro = a05Bairros.objetos.get(pk=codbairro)
                munic = a04Municipios.objetos.get(pk=bairro.municipio_id)
                codmunic = munic.id
                request.session['codmuni'] = codmunic
                siglaUf = munic.estado_id
                request.session['siglauf'] = siglaUf
                request.session['regiao'] = a03Estados.objetos.get(
                    pk=siglaUf).regiao
                return HttpResponseRedirect(reverse('orcs:novo_orcamento'))
    else:
        form = formDadosCliente()
        form_selecionar_empresa = formSelecionarEmpresa()
        return render(request, "clie/dados-cliente.html", {"form": form, "dadosCliente": dados_cliente,
                                                            "formSelecionarEmpresa": form_selecionar_empresa})


def cadastrar_novo_endereco(request):
    codigo_cliente = request.session['codcliente']
    nome_cliente = e01Cadastros.objetos.get(id=codigo_cliente).descrcad
    if request.POST:
        form = formNovoEndereco(request.POST)
        if form.is_valid():
            regiao = request.POST['regiao']
            estado = request.POST['estado']
            cidade = request.POST['cidade']
            if form.cleaned_data['novo_bairro']:
                if len(a05Bairros.objetos.filter(bairro=form.cleaned_data['novo_bairro'])) > 0:
                    bairro = a05Bairros.objetos.filter(bairro=form.cleaned_data['novo_bairro'])[0]
                else:
                    bairro = a05Bairros(
                        id=a05Bairros.objetos.latest('id').id + 1,
                        bairro=form.cleaned_data['novo_bairro'],
                        cepini=0,
                        cepfin=0,
                        distfab=0,
                        municipio=a04Municipios.objetos.get(id=cidade)
                    )
                    bairro.save()
            else:
                if request.POST['bairro'] != "":
                    bairro = a05Bairros.objetos.get(id=request.POST['bairro'])
            if form.cleaned_data['novo_logradouro']:
                if len(a06Lograds.objetos.filter(logradouro=form.cleaned_data['novo_logradouro'])) > 0:
                    logradouro = a06Lograds.objetos.filter(logradouro=form.cleaned_data['novo_logradouro'])[0]
                else:
                    logradouro = a06Lograds(
                        id=a06Lograds.objetos.latest('id').id + 1,
                        logradouro=form.cleaned_data['novo_logradouro'],
                        ceplogr="",
                        distfab=0,
                        bairro=bairro
                    )
                    logradouro.save()
            else:
                if request.POST['logradouro'] != "":
                    logradouro = a06Lograds.objetos.get(id=request.POST['logradouro'])
            complemento = form.cleaned_data['complemento']
            if len(e04EndCad.objetos.filter(complend=form.cleaned_data['complemento'], cadastro=e01Cadastros.objetos.get(id=codigo_cliente), lograd=logradouro)) > 0:
                novo_endereco_cliente = e04EndCad.objetos.filter(complend=form.cleaned_data['complemento'], cadastro=e01Cadastros.objetos.get(id=codigo_cliente), lograd=logradouro)[0]
            else:
                novo_endereco_cliente = e04EndCad(
                    id=e04EndCad.proxnumcad(e04EndCad),
                    cadastro=e01Cadastros.objetos.get(id=codigo_cliente),
                    tipend=a07TiposEnd.objetos.get(id=1),
                    lograd=logradouro,
                    complend=complemento
                )
                novo_endereco_cliente.save()
            request.session['cod_endereço_cliente'] = novo_endereco_cliente.id
            messages.success(request, "Endereço cadastrado")
            return HttpResponseRedirect(reverse('orcs:novo_orcamento'))
        else:
            print(form.errors.as_data())
            messages.error(request, "Erro ao validar os dados do formulário")
            return render(request, "clie/cadastrar-novo-endereco.html", 
                {"form": form, "cliente": nome_cliente, "formSelecionarEmpresa": form_selecionar_empresa})
    else:
        form = formNovoEndereco()
        form_selecionar_empresa = formSelecionarEmpresa()
        return render(request,"clie/cadastrar-novo-endereco.html", 
            {"form": form, "cliente": nome_cliente, "formSelecionarEmpresa": form_selecionar_empresa})
