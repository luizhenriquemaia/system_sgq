from pathlib import Path
from csv import reader
from io import StringIO
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, reverse, redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from clie.forms import frmPesqCliente, formDadosCliente, frmLocalizacao, frmEscCliente, formDadosEmpresa
from clie.forms import frmPesqMunicip, frmPesqBairro, frmPesqLogradouro
from main.funcoes import numpurotelefone, format_list_telefone, nomesequencia
from main.models import a03Estados, a04Municipios, a05Bairros, a06Lograds, a07TiposEnd, a09TiposFone
from main.models import e01Cadastros, e02FonesCad, e03WebCad, e04EndCad, e06ContCad
 

# Pesquisa cliente por nome, telefone ou e-mail
def pesqcliente(request, sequencia):
    request.session['sequencia'] = sequencia
    request.session['marcador'] = 'clie:pesqcliente'
    if request.method == "POST":
        form = frmPesqCliente(request.POST)
        if form.is_valid():
            nomecliente = form.cleaned_data['nome']
            fonepesq = form.cleaned_data['fone']
            emailpesq = form.cleaned_data['email']
            # Procurar pelo dono do telefone na base de dados
            if len(fonepesq) > 0:
                # Verificar se o numero de telefone fornecido e valido
                fonepuro = numpurotelefone(fonepesq)
                if len(fonepuro) < 10:
                    messages.info(request, 'Numero de telefone inválido.')
                    form = frmPesqCliente(request.POST)
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
        # Metodo post nao verificado, ou formulario nao validado
        form = frmPesqCliente(request.POST)
    return render(request, "clie/formpesqcliente.html", {"form": form})


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
    request.session['marcador'] = 'clie:selecionar_cliente'
    filtro_cliente = request.session['filtroclie']
    lista_clientes = e01Cadastros.possiveisclientes(e01Cadastros, filtro_cliente)
    escolhas_clientes = [('0', 'Adicionar novo cliente')]
    for cliente in lista_clientes:
        escolhas_clientes.append(tuple((cliente.id, cliente.descricao)))
    if request.method == "POST":
        form = frmEscCliente(request.POST, escolhas_clientes=escolhas_clientes)
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
        form = frmEscCliente(escolhas_clientes=escolhas_clientes)
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
                # Seguir para inclusao do endereco
                request.session['regiao'] = 'Centro Oeste'
                request.session['siglauf'] = 'GO'
                request.session['codmuni'] = 94
                request.session['codbair'] = 100
                request.session['codlogr'] = 3
                return HttpResponseRedirect(reverse('clie:deflocal'))
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
                messages.info(request, "Empresa adicionada com sucesso, adicione um contato")
                return HttpResponseRedirect(
                    reverse('clie:pesqcliente', args=(1,)))
            # Se não for empresa, adicionar endereço
            # Verificar se deve cadastrar novo endereco
            cod_endereco = int(form.cleaned_data['endereco'])
            if cod_endereco == 0:
                # Seguir para inclusao do endereco
                request.session['regiao'] = 'Centro Oeste'
                request.session['siglauf'] = 'GO'
                request.session['codmuni'] = 94
                request.session['codbair'] = 100
                request.session['codlogr'] = 3
                return HttpResponseRedirect(reverse('clie:deflocal'))
            else:
                # Continua usando o endereco selecionado
                logrCli = e04EndCad.objetos.get(id=int(cod_endereco))
                codlogrclie = logrCli.lograd_id
                request.session['codendcliente'] = cod_endereco
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
                return HttpResponseRedirect(reverse('clie:prosseguir'))
    else:
        form = formDadosCliente()
        return render(request, "clie/dados-cliente.html", {"form": form, "dadosCliente": dados_cliente})



def deflocal(request):
    form = frmLocalizacao(request.POST)
    seqorc = request.session['sequencia']
    nomeseq = nomesequencia(seqorc)
    codcliente = request.session['codcliente']
    nomecliente = e01Cadastros.nometratcliente(e01Cadastros, codcliente)
    siglauf = request.session['siglauf']
    nomeuf = a03Estados.nomeestado(a03Estados, siglauf)
    codmunic = request.session['codmuni']
    nomemunic = a04Municipios.nomemuncipio(a04Municipios, codmunic)
    codbairro = request.session['codbair']
    nomebairro = a05Bairros.nomebairro(a05Bairros, codbairro)
    codlograd = request.session['codlogr']
    nomelograd = a06Lograds.nomelogradouro(a06Lograds, codlograd)
    parametros = {
        'sequencia': seqorc,
        'nomeseq': nomeseq,
        'codcliente': codcliente,
        'nomecliente': nomecliente,
        'regiao': request.session['regiao'],
        'siglauf': siglauf,
        'nomeuf': nomeuf,
        'codmuni': codmunic,
        'nomemuni': nomemunic,
        'codbair': codbairro,
        'nomebair': nomebairro,
        'codlogr': codlograd,
        'nomelogr': nomelograd
    }
    if codmunic == 0:
        return HttpResponseRedirect(reverse('clie:mudamunicipio', args=['A-B-C.1']))
    if codbairro == 0:
        return HttpResponseRedirect(reverse('clie:mudabairro', args=['A-B-C.1']))
    if codlograd == 0:
        return HttpResponseRedirect(reverse('clie:mudalogradouro'))
    if request.method == "POST":
        if form.is_valid():
            if codlograd > 0 and form.cleaned_data['complemento']:
                # Cadastrar novo endereco para cliente
                complend = form.cleaned_data['complemento']
                nvcodend = e04EndCad.proxnumcad(e04EndCad)
                nvendclie = e04EndCad(
                    id=nvcodend,
                    cadastro=e01Cadastros.objetos.get(pk=codcliente),
                    tipend=a07TiposEnd.objetos.get(pk=1),
                    lograd=a06Lograds.objetos.get(pk=codlograd),
                    complend=complend
                )
                nvendclie.save()
                request.session['codendcliente'] = nvcodend

            if e01Cadastros.objetos.get(id=codcliente).juridica == 1:
                # cliente != de empresa
                codorcam = request.session['codorcam']
                return HttpResponseRedirect(reverse('orcs:editar_contrato', args=(codorcam, )))
            else:
                request.session['marcador'] = 'clie:deflocal'
                return HttpResponseRedirect(reverse('clie:prosseguir'))
    else:
        form = frmPesqBairro(request.POST)
        request.session['marcador'] = 'clie:deflocal'
    return render(request, "clie/formescendereco.html", {"form": form, "parametros": parametros})


def mudaregiao(request):
    request.session['marcador'] = 'clie:deflocal/mudaregiao'
    seqorc = request.session['sequencia']
    nomeseq = nomesequencia(seqorc)
    codcliente = request.session['codcliente']
    nomecliente = e01Cadastros.nometratcliente(e01Cadastros, codcliente)
    parametros = {
        'sequencia': seqorc,
        'nomeseq': nomeseq,
        'codcliente': codcliente,
        'nomecliente': nomecliente,
        'regiao': '',
        'siglauf': '',
        'codmuni': 0,
        'codbair': 0,
        'codlogr': 0
    }
    return render(request, "clie/formmudaregiao.html", {"parametros": parametros})


def mudaestado(request, regiao):
    request.session['marcador'] = 'clie:deflocal/mudaestado/' + regiao
    regiaoform = regiao.replace("_", " ")
    seqorc = request.session['sequencia']
    nomeseq = nomesequencia(seqorc)
    codcliente = request.session['codcliente']
    request.session['regiao'] = regiaoform
    nomecliente = e01Cadastros.nometratcliente(e01Cadastros, codcliente)
    parametros = {
        'sequencia': seqorc,
        'nomeseq': nomeseq,
        'codcliente': codcliente,
        'nomecliente': nomecliente,
        'regiao': regiaoform,
        'siglauf': '',
        'codmuni': 0,
        'codbair': 0,
        'codlogr': 0
    }
    listaestado = a03Estados.objetos.filter(regiao=regiaoform)
    return render(request, "clie/formmudaestado.html", {"parametros": parametros, "listaestado": listaestado})


def estadoescolhido(request, estadoesc):
    request.session['marcador'] = 'clie:estado/' + estadoesc
    # Seguir com o municipio selecionado
    request.session['siglauf'] = estadoesc
    request.session['codmuni'] = 0
    request.session['codbair'] = 0
    request.session['codlogr'] = 0
    return HttpResponseRedirect(reverse('clie:deflocal'))


def mudamunicipio(request, filtro):
    request.session['marcador'] = 'clie:mudamunicipio/' + filtro
    form = frmPesqMunicip(request.POST)
    seqorc = request.session['sequencia']
    nomeseq = nomesequencia(seqorc)
    codcliente = request.session['codcliente']
    nomecliente = e01Cadastros.nometratcliente(e01Cadastros, codcliente)
    siglauf = request.session['siglauf']
    nomeuf = a03Estados.nomeestado(a03Estados, siglauf)
    codmunic = request.session['codmuni']
    nomemunic = a04Municipios.nomemuncipio(a04Municipios, codmunic)
    listamunicip = a04Municipios.municipiosestado(a04Municipios, siglauf, filtro)
    parametros = {
        'sequencia': seqorc,
        'nomeseq': nomeseq,
        'codcliente': codcliente,
        'nomecliente': nomecliente,
        'regiao': request.session['regiao'],
        'siglauf': siglauf,
        'nomeuf': nomeuf,
        'codmuni': codmunic,
        'nomemuni': nomemunic,
        'filtro': filtro,
    }
    if request.method == "POST":
        # Metodo POST Ok
        if form.is_valid():
            if form.cleaned_data['pesqmunicip']:
                pesqmunicip = form.cleaned_data['pesqmunicip']
                request.session['pesqmunicip'] = pesqmunicip
                parametros['nomemuni'] = pesqmunicip
                request.session['nomemuni'] = pesqmunicip
                parametros['codmuni'] = 0
                listamunicip = a04Municipios.municipiosestado(a04Municipios, siglauf, 'like.' + pesqmunicip)
    else:
        form = frmPesqMunicip(request.POST)
    return render(request, "clie/formmudamunicipio.html", {"form": form, "parametros": parametros,
                                                           "listamunicip": listamunicip})


def municipioescolhido(request, municipesc):
    request.session['marcador'] = 'clie:municipio/' + str(municipesc)
    if municipesc == 0:
        # Incluir municipio
        siglauf = request.session['siglauf']
        nvcodmun = a04Municipios.proxnumcad(a04Municipios)
        novomun = a04Municipios(
            id=nvcodmun,
            estado=a03Estados.objetos.get(pk=siglauf),
            municipio=request.session['nomemuni'],
            distfab=0
        )
        novomun.save()
        request.session['codmuni'] = nvcodmun
        request.session['codbair'] = 0
        request.session['codlogr'] = 0
        return HttpResponseRedirect(reverse('clie:deflocal'))
    else:
        # Seguir com o municipio selecionado
        request.session['codmuni'] = municipesc
        request.session['codbair'] = 0
        request.session['codlogr'] = 0
        return HttpResponseRedirect(reverse('clie:deflocal'))


def mudabairro(request, filtro):
    request.session['marcador'] = 'clie:mudabairro/' + filtro
    form = frmPesqBairro(request.POST)
    seqorc = request.session['sequencia']
    nomeseq = nomesequencia(seqorc)
    codcliente = request.session['codcliente']
    nomecliente = e01Cadastros.nometratcliente(e01Cadastros, codcliente)
    siglauf = request.session['siglauf']
    nomeuf = a03Estados.nomeestado(a03Estados, siglauf)
    codmunic = request.session['codmuni']
    nomemunic = a04Municipios.nomemuncipio(a04Municipios, codmunic)
    codbairro = request.session['codbair']
    nomebairro = a05Bairros.nomebairro(a05Bairros, codbairro)
    listabairros = a05Bairros.bairrosmunicipio(a05Bairros, codmunic, filtro)
    parametros = {
        'sequencia': seqorc,
        'nomeseq': nomeseq,
        'codcliente': codcliente,
        'nomecliente': nomecliente,
        'regiao': request.session['regiao'],
        'siglauf': siglauf,
        'nomeuf': nomeuf,
        'codmuni': codmunic,
        'nomemuni': nomemunic,
        'codbair': codbairro,
        'nomebair': nomebairro,
        'filtro': filtro,
    }
    if request.method == "POST":
        # Metodo POST Ok
        if form.is_valid():
            if form.cleaned_data['pesqbairro']:
                pesqbairro = form.cleaned_data['pesqbairro']
                request.session['pesqbairro'] = pesqbairro
                parametros['nomebair'] = pesqbairro
                request.session['nomebair'] = pesqbairro
                parametros['codbair'] = 0
                listabairros = a05Bairros.bairrosmunicipio(a05Bairros, codmunic, 'like.' + pesqbairro)
    else:
        form = frmPesqBairro(request.POST)
    return render(request, "clie/formmudabairro.html", {"form": form,
                                                        "parametros": parametros,
                                                        "listabairros": listabairros})


def bairroescolhido(request, bairroesc):
    request.session['marcador'] = 'clie:bairro/' + str(bairroesc)
    if bairroesc == 0:
        # Incluir bairro
        codmuni = request.session['codmuni']
        nvcodbair = a05Bairros.proxnumcad(a05Bairros)
        novobairro = a05Bairros(
            id=nvcodbair,
            municipio=a04Municipios.objetos.get(pk=codmuni),
            bairro=request.session['nomebair'],
            distfab=0
        )
        novobairro.save()
        request.session['codbair'] = nvcodbair
        request.session['codlogr'] = 0
        return HttpResponseRedirect(reverse('clie:deflocal'))
    else:
        # Seguir com o bairro selecionado
        request.session['codbair'] = bairroesc
        request.session['codlogr'] = 0
        return HttpResponseRedirect(reverse('clie:deflocal'))


def mudalogradouro(request):
    request.session['marcador'] = 'clie:mudalogradouro'
    form = frmPesqLogradouro(request.POST)
    seqorc = request.session['sequencia']
    nomeseq = nomesequencia(seqorc)
    codcliente = request.session['codcliente']
    nomecliente = e01Cadastros.nometratcliente(e01Cadastros, codcliente)
    siglauf = request.session['siglauf']
    nomeuf = a03Estados.nomeestado(a03Estados, siglauf)
    codmunic = request.session['codmuni']
    nomemunic = a04Municipios.nomemuncipio(a04Municipios, codmunic)
    codbairro = request.session['codbair']
    nomebairro = a05Bairros.nomebairro(a05Bairros, codbairro)
    codlograd = request.session['codlogr']
    nomelograd = a06Lograds.nomelogradouro(a06Lograds, codlograd)
    listalograd = a06Lograds.logrsbairro(a06Lograds, codbairro)
    parametros = {
        'sequencia': seqorc,
        'nomeseq': nomeseq,
        'codcliente': codcliente,
        'nomecliente': nomecliente,
        'regiao': request.session['regiao'],
        'siglauf': siglauf,
        'nomeuf': nomeuf,
        'codmuni': codmunic,
        'nomemuni': nomemunic,
        'codbair': codbairro,
        'nomebair': nomebairro,
        'codlogr': codlograd,
        'nomelogr': nomelograd,
        'listalograd': listalograd
    }
    if request.method == "POST":
        # Metodo POST Ok
        if form.is_valid():
            logradform = int(form.cleaned_data['codlograd'])
            if logradform == 0 and form.cleaned_data['novolograd']:
                # Cadastrar novo logradouro
                nvcodlogr = a06Lograds.proxnumcad(a06Lograds)
                nvlograd = a06Lograds(
                    id=nvcodlogr,
                    bairro=a05Bairros.objetos.get(pk=codbairro),
                    logradouro=form.cleaned_data['novolograd'],
                    distfab=0
                )
                nvlograd.save()
                codlograd = nvcodlogr
                request.session['codlogr'] = nvcodlogr
                parametros['codlogr'] = nvcodlogr
                parametros['nomelogr'] = nvlograd.logradouro
            if codlograd > 0 and form.cleaned_data['complemento']:
                try:
                    # se não tiver tipos de endereços cadastrados
                    a07TiposEnd.objetos.get(pk=1)
                except:
                    csv_file = Path.cwd().joinpath("seeds_db", 'main_a07tiposend.csv')
                    data_set = csv_file.read_text(encoding='UTF-8')
                    io_string = StringIO(data_set)
                    for count, column in enumerate(reader(io_string, delimiter=',', quotechar="|")):
                        tipo_endereço = a07TiposEnd(
                            id=count + 1,
                            tend=column[1].strip(' "'),
                        )
                        tipo_endereço.save()
                # Cadastrar novo endereco para cliente
                complend = form.cleaned_data['complemento']
                nvcodend = e04EndCad.proxnumcad(e04EndCad)
                nvendclie = e04EndCad(
                    id=nvcodend,
                    cadastro=e01Cadastros.objetos.get(pk=codcliente),
                    tipend=a07TiposEnd.objetos.get(pk=1),
                    lograd=a06Lograds.objetos.get(pk=codlograd),
                    complend=complend
                )
                nvendclie.save()
                request.session['codendcliente'] = nvcodend
            if e01Cadastros.objetos.get(id=codcliente).juridica == 1:
                # cliente != de empresa
                codorcam = request.session['codorcam']
                return HttpResponseRedirect(reverse('orcs:editar_contrato', args=(codorcam, )))
            else:
                request.session['marcador'] = 'clie:deflocal'
                return HttpResponseRedirect(reverse('clie:prosseguir'))
    else:
        form = frmPesqLogradouro(request.POST)
    return render(request, "clie/formmudalograd.html", {"form": form, "parametros": parametros})


def prosseguir(request):
    seqorc = request.session['sequencia']
    if seqorc == 1:
        return HttpResponseRedirect(reverse('orcs:novo_orcamento'))
    return HttpResponseRedirect(reverse('main:inicio'))
