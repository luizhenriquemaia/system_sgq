from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q

from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import redirect, render
from main.models import (a03Estados, a04Municipios, a05Bairros, a06Lograds,
                         a10CatsInsumos, a11Insumos, a19PlsPgtos, a20StsOrcs,
                         b01Empresas, b03CtasCaixa, b04CCustos, d01Patrim,
                         e01Cadastros, e04EndCad, g01Orcamento, h01ContrPServ,
                         h03EapContr)

from .forms import addUserForm, editProfileForm, formPesqPorCliente


def inicio(request):
    # caso for pesquisa por nome de cliente
    if request.method == "POST":
        form = formPesqPorCliente(request.POST)
        if form.is_valid():
            nome_cliente = form.cleaned_data['nome_cliente']
            possiveis_clientes = e01Cadastros.possiveisclientes(e01Cadastros, nome_cliente)
            lista_preorcamentos_pendentes, lista_visitas_pendentes = [], []
            lista_orcamentos_pendentes, lista_contratos_pendentes = [], []
            lista_obras_pendentes, lista_obras_finalizadas = [], []
            if request.user.is_staff:
                for possivel_cliente in possiveis_clientes:
                    for endereco in e04EndCad.objetos.filter(cadastro_id=possivel_cliente.id):    
                        orcamentos_por_cliente = g01Orcamento.objetos.filter(ender_id=endereco.id)
                        for orcamento_cliente in orcamentos_por_cliente:
                            dic_orcamentos = {
                                "numero": orcamento_cliente.id,
                                "data": orcamento_cliente.dtorc,
                                "cliente": possivel_cliente.descrcad,
                                "pagamento": a19PlsPgtos.objetos.get(id=orcamento_cliente.plpgto_id).descricao,
                                "status": a20StsOrcs.objetos.get(id=orcamento_cliente.status_id).descricao}
                            if orcamento_cliente.fase_id == 1:
                                lista_preorcamentos_pendentes.append(dic_orcamentos)
                            elif orcamento_cliente.fase_id == 2:
                                lista_visitas_pendentes.append(dic_orcamentos)
                            elif orcamento_cliente.fase_id == 3:
                                lista_orcamentos_pendentes.append(dic_orcamentos)
                            elif orcamento_cliente.fase_id == 4:
                                lista_contratos_pendentes.append(dic_orcamentos)
                            elif orcamento_cliente.fase_id == 5:
                                lista_obras_pendentes.append(dic_orcamentos)
                            elif orcamento_cliente.fase_id == 6:
                                lista_obras_finalizadas.append(dic_orcamentos)
            # listar somente os clientes do vendedor quando não for staff
            else:
                for possivel_cliente in possiveis_clientes:
                    for endereco in e04EndCad.objetos.filter(cadastro_id=possivel_cliente.id):
                        orcamentos_por_cliente = g01Orcamento.objetos.filter(
                            ender_id=endereco.id, vended_id=request.user.id)
                        for orcamento_cliente in orcamentos_por_cliente:
                            dic_orcamentos = {
                                "numero": orcamento_cliente.id,
                                "data": orcamento_cliente.dtorc,
                                "cliente": possivel_cliente.descrcad,
                                "pagamento": a19PlsPgtos.objetos.get(id=orcamento_cliente.plpgto_id).descricao,
                                "status": a20StsOrcs.objetos.get(id=orcamento_cliente.status_id).descricao}
                            if orcamento_cliente.fase_id == 1:
                                lista_preorcamentos_pendentes.append(dic_orcamentos)
                            elif orcamento_cliente.fase_id == 2:
                                lista_visitas_pendentes.append(dic_orcamentos)
                            elif orcamento_cliente.fase_id == 3:
                                lista_orcamentos_pendentes.append(
                                    dic_orcamentos)
                            elif orcamento_cliente.fase_id == 4:
                                lista_contratos_pendentes.append(
                                    dic_orcamentos)
                            elif orcamento_cliente.fase_id == 5:
                                lista_obras_pendentes.append(dic_orcamentos)
                            elif orcamento_cliente.fase_id == 6:
                                lista_obras_finalizadas.append(dic_orcamentos)
        # Caso ocorra algum erro no formulário
        else:
            messages.error(request, "Erro ao listar orçamentos")
        numeros_pendencias = [len(lista_preorcamentos_pendentes), len(lista_visitas_pendentes), len(lista_orcamentos_pendentes), len(lista_contratos_pendentes)]
        return render(request, "main/inicio.html", {"preOrcPend": lista_preorcamentos_pendentes, "visitasPend": lista_visitas_pendentes,
                                                    "orcamPend": lista_orcamentos_pendentes, "contrPend": lista_contratos_pendentes,
                                                    "obraPend": lista_obras_pendentes, "obraAFinal": lista_obras_finalizadas,
                                                    "form": formPesqPorCliente, "numerosPendencias":numeros_pendencias})
    elif request.method == "GET":
        # querys para usuário staff e usuário comum
        ids_status_orcamento_ativos = [status.id for status in a20StsOrcs.objetos.filter(ativo=1)]
        if request.user.is_staff:
            pendencias_para_listar = g01Orcamento.objetos.filter(
                status_id__in=ids_status_orcamento_ativos
            ).order_by('-id')[:200]
        else:
            pendencias_para_listar = g01Orcamento.objetos.filter(
                vended_id=request.user.id, 
                status_id__in=ids_status_orcamento_ativos
            ).order_by('-id')[:200]
        lista_preorcamentos_pendentes, lista_visitas_pendentes = [], []
        lista_orcamentos_pendentes, lista_contratos_pendentes = [], []
        lista_obras_pendentes, lista_obras_finalizadas = [], []
        # separar as pendencias por fase de orçamento
        for pendencia in pendencias_para_listar:
            dic_pendencias = {
                "numero": pendencia.id,
                "data": pendencia.dtorc,
                "cliente": e01Cadastros.objetos.get(id=e04EndCad.objetos.get(id=pendencia.ender_id).cadastro_id).descrcad,
                "pagamento": a19PlsPgtos.objetos.get(id=pendencia.plpgto_id).descricao,
                "status": a20StsOrcs.objetos.get(id=pendencia.status_id).descricao}
            if pendencia.fase_id == 1:
                lista_preorcamentos_pendentes.append(dic_pendencias)
            elif pendencia.fase_id == 2:
                lista_visitas_pendentes.append(dic_pendencias)
            elif pendencia.fase_id == 3:
                lista_orcamentos_pendentes.append(dic_pendencias)
            elif pendencia.fase_id == 4:
                lista_contratos_pendentes.append(dic_pendencias)
        numeros_pendencias = [len(lista_preorcamentos_pendentes), len(lista_visitas_pendentes), len(lista_orcamentos_pendentes), len(lista_contratos_pendentes)]
        return render(request, "main/inicio.html", {"preOrcPend": lista_preorcamentos_pendentes, "visitasPend": lista_visitas_pendentes,
                                                    "orcamPend": lista_orcamentos_pendentes, "contrPend": lista_contratos_pendentes,
                                                    "obraPend": lista_obras_pendentes, "obraAFinal": lista_obras_finalizadas,
                                                    "form": formPesqPorCliente, "numerosPendencias":numeros_pendencias})
    else:
        return HttpResponse(405)



def apps_disponiveis(request):
    return render(request, "main/apps-disponiveis.html")


def logout_request(request):
    logout(request)
    messages.info(request, "Logout realizado com sucesso")
    return redirect("main:login")


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, "Login realizado com sucesso")
                return redirect("main:apps_disponiveis")
            else:
                messages.error(request, "Usuário ou senha invalido")
        else:
            messages.error(request, "Usuário ou senha invalido")
    form = AuthenticationForm()
    return render(request,
                  "main/login.html",
                  {"form": form})


def add_user(request):
    if request.method == "POST":
        form = addUserForm(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            if password1 and password2 and password1 != password2:
                messages.error(request, "Erro na conferência de senhas")
                return redirect("main:add_user")
            else:
                form.save()
                messages.info(request, "Usuário criado com sucesso")
                return redirect("main:inicio")
        else:
            messages.error(request, "Dados Inválidos")
            return redirect("main:add_user")
    else:
        form = addUserForm()
        return render(request, "main/add-user.html", {'form': form})


def edit_profile(request):
    if request.method == "POST":
        form = editProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.info(request, "Dados alterados com sucesso")
            return redirect("main:inicio")
        else:
            messages.error(request, "Dados Inválidos")
            return redirect("main:edit_profile")
    else:
        form = editProfileForm(instance=request.user)
        return render(request, "main/edit-profile.html", {'form': form})


def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.info(request, "Senha alterada com sucesso")
            update_session_auth_hash(request, form.user)
            return redirect("main:edit_profile")
        else:
            messages.error(request, "Senha inválida")
            return redirect("main:change_password")
    else:
        form = PasswordChangeForm(user=request.user)
        return render(request, "main/change-password.html", {'form': form})


def listas_offline(request):
    lstCategs = []
    nocat = 0
    tabCategs = a10CatsInsumos.ordenadas(a10CatsInsumos)
    txtcateg = "[]"
    for categ in tabCategs:
        txtcateg = f"[{chr(34)}{categ.ordenador}{chr(34)}, {categ.tipo}, {chr(34)}{categ.descricao}{chr(34)}, {categ.id}, "
        #txtcateg = "[" + chr(34) + str(categ.ordenador) + chr(34) + ", " + str(categ.tipo) + ", " + chr(34) + \
        #           categ.descricao + chr(34) + ", " + str(categ.id) + ", "
        tabInsumos = a11Insumos.objetos.filter(catins_id=categ.id)
        txtins = "["
        for insumo in tabInsumos:
            if txtins != "[":
                txtins += ", "
            txtins += f" [{insumo.id}, {chr(34)}{insumo.descricao}{chr(34)}, {chr(34)}{insumo.undbas}{chr(34)}]"
            #txtins += " [" + str(insumo.id) + ", " + chr(34) + insumo.descricao + chr(34) + ", " + chr(34) + \
            #          insumo.undbas + chr(34) + "]"
        txtins += "]"
        txtcateg += txtins + "]"
        itemlst = {"texto": txtcateg, "continua": ", "}
        lstCategs.append(itemlst)
        nocat += 1
    if nocat > 0:
        lstCategs[nocat-1] = {"texto": txtcateg, "continua": ""}
    return render(request, "main/listas.html", {'tipolista': "de Categorias", 'nomearq': "arqcategs",
                                                'itenslista': lstCategs})


def listas_insumos(request):
    lstInsumos = []
    noins = 0
    tabInsumos = a11Insumos.objetos.all()
    for insumo in tabInsumos:
        txtins = f"[{insumo.id}, {chr(34)}{insumo.descricao}{chr(34)}, {chr(34)}{insumo.undbas}{chr(34)}]"
        #txtins = "[" + str(insumo.id) + ", " + chr(34) + insumo.descricao + chr(34) + ", " + chr(34) + insumo.undbas + \
        #         chr(34) + "]"
        itemlst = {"texto": txtins, "continua": ", "}
        lstInsumos.append(itemlst)
        noins += 1
    if noins > 0:
        lstInsumos[noins - 1] = {"texto": txtins, "continua": ""}
    return render(request, "main/listas.html", {'tipolista': "de Insumos", 'nomearq': "arqinsum",
                                                'itenslista': lstInsumos})


def listas_empresas(request):
    codUsuario = request.user.id
    lstEmpresas = []
    noemp = 0
    tabEmpresas = b01Empresas.permitidas(b01Empresas, codUsuario)
    for empresa in tabEmpresas:
        txtins = f"[{empresa.id}, {chr(34)}{empresa.razao}{chr(34)}, {empresa.juridica}]"
        #txtins = "[" + str(empresa.id) + ", " + chr(34) + empresa.razao + chr(34) + ", " + str(empresa.juridica) + "]"
        itemlst = {"texto": txtins, "continua": ", "}
        lstEmpresas.append(itemlst)
        noemp += 1
    if noemp > 0:
        lstEmpresas[noemp - 1] = {"texto": txtins, "continua": ""}
    return render(request, "main/listas.html", {'tipolista': "de Empresas", 'nomearq': "arqemps",
                                                'itenslista': lstEmpresas})


def listas_caixas(request):
    codUsuario = request.user.id
    lstCaixas = []
    nocxas = 0
    tabCaixas = b03CtasCaixa.permitidos(b03CtasCaixa, codUsuario)
    for caixa in tabCaixas:
        txtins = f"[{caixa.id}, {chr(34)}{caixa.descricao}{chr(34)}, {caixa.tipo}]"
        #txtins = "[" + str(caixa.id) + ", " + chr(34) + caixa.descricao + chr(34) + ", " + str(caixa.tipo) + "]"
        itemlst = {"texto": txtins, "continua": ", "}
        lstCaixas.append(itemlst)
        nocxas += 1
    if nocxas > 0:
        lstCaixas[nocxas - 1] = {"texto": txtins, "continua": ""}
    return render(request, "main/listas.html", {'tipolista': "de Contas Caixas", 'nomearq': "arqcaixas",
                                                'itenslista': lstCaixas})


def listas_ccustos(request):
    codUsuario = request.user.id
    lstCCustos = []
    noins = 0 
    tabCCustos = b04CCustos.permitidos(b04CCustos, codUsuario, 1)
    for ccusto in tabCCustos:
        txtcc = f"[{ccusto.empresa_id}, {ccusto.id}, {chr(34)}{ccusto.descricao}{chr(34)}, {ccusto.funccc}, "
        #txtcc = "[" + str(ccusto.empresa_id) + ", " + str(ccusto.id) + ", " + chr(34) + ccusto.descricao + chr(34) + ", " + str(ccusto.funccc) + ", "
        tabContratos = h01ContrPServ.objetos.filter(ccustvinc_id=ccusto.id)
        txtconts = "["
        for contrato in tabContratos:
            if txtconts != "[":
                txtconts += ", "
            txtconts += " [" + str(contrato.id) + ", " + chr(34) + contrato.codprojet + chr(34) + ", " + chr(34) + \
                        str(contrato.tipservic) + chr(34) + "]"
        txtconts += "]"
        txtcc += txtconts + "]"
        itemlst = {"texto": txtcc, "continua": ", "}
        lstCCustos.append(itemlst)
        noins += 1
    if noins > 0:
        lstCCustos[noins - 1] = {"texto": txtcc, "continua": ""}
    return render(request, "main/listas.html", {'tipolista': "de Centros de Custos", 'nomearq': "arqcctos",
                                                'itenslista': lstCCustos})


def listas_ativs(request):
    codUsuario = request.user.id
    lstAtivs = []
    noatvs = 0
    tabAtivs = h03EapContr.permitidos(h03EapContr, codUsuario, 1)
    for atividade in tabAtivs:
        txtins = f"[{atividade.ccustvinc_id}, {atividade.id}, {chr(34)}{atividade.codeap}{chr(34)}, {chr(34)}{atividade.descitem}{chr(34)}, {atividade.tipo}]"
        #txtins = "[" + str(atividade.ccustvinc_id) + ", " + str(atividade.id) + ", " + chr(34) + atividade.codeap + \
        #         chr(34) + ", " + chr(34) + atividade.descitem + chr(34) + ", " + str(atividade.tipo) + "]"
        itemlst = {"texto": txtins, "continua": ", "}
        lstAtivs.append(itemlst)
        noatvs += 1
    if noatvs > 0:
        lstAtivs[noatvs - 1] = {"texto": txtins, "continua": ""}
    return render(request, "main/listas.html", {'tipolista': "de Atividades", 'nomearq': "arqativs",
                                                'itenslista': lstAtivs})


def listas_patrs(request):
    codUsuario = request.user.id
    lstPatrs = []
    nopats = 0
    tabPatrs = d01Patrim.permitidos(d01Patrim, codUsuario, 1)
    for patrim in tabPatrs:
        txtins = f"[{patrim.ccusto_id}, {patrim.id}, {chr(34)}{patrim.codigo}{chr(34)}, {chr(34)}{patrim.descres}{chr(34)}, {patrim.tipo}]"
        #txtins = "[" + str(patrim.ccusto_id) + ", " + str(patrim.id) + ", " + chr(34) + patrim.codigo + \
        #         chr(34) + ", " + chr(34) + patrim.descres + chr(34) + ", " + str(patrim.tipo) + "]"
        itemlst = {"texto": txtins, "continua": ", "}
        lstPatrs.append(itemlst)
        nopats += 1
    if nopats > 0:
        lstPatrs[nopats - 1] = {"texto": txtins, "continua": ""}
    return render(request, "main/listas.html", {'tipolista': "de Patrimônios", 'nomearq': "arqpatrs",
                                                'itenslista': lstPatrs})


def listas_colabs(request):
    codUsuario = request.user.id
    lstColabs = []
    nocols = 0
    tabColabs = e01Cadastros.colabspermitidos(e01Cadastros, codUsuario, 1)
    for colab in tabColabs:
        txtins = f"[{colab.ccusto_id}, {colab.id}, {chr(34)}{colab.descrcad}{chr(34)}]"
        #txtins = "[" + str(colab.ccusto_id) + ", " + str(colab.id) + ", " + chr(34) + colab.descrcad + chr(34) + "]"
        itemlst = {"texto": txtins, "continua": ", "}
        lstColabs.append(itemlst)
        nocols += 1
    if nocols > 0:
        lstColabs[nocols - 1] = {"texto": txtins, "continua": ""}
    return render(request, "main/listas.html", {'tipolista': "de Colaboradores", 'nomearq': "arqcolabs",
                                                'itenslista': lstColabs})


def carregar_estados(request, regiao):
    estados = a03Estados.objetos.filter(regiao=regiao).order_by('estado')
    return render(request, 'clie/carregar-estados.html', {'estados': estados})

def carregar_cidades(request, estado):
    cidades = a04Municipios.objetos.filter(estado_id=estado).order_by('municipio')
    return render(request, 'clie/carregar-cidades.html', {'cidades': cidades})

def carregar_bairros(request, cidade):
    bairros = a05Bairros.objetos.filter(municipio_id=cidade).order_by('bairro')
    return render(request, 'clie/carregar-bairros.html', {'bairros': bairros})

def carregar_logradouros(request, bairro):
    logradouros = a06Lograds.objetos.filter(bairro_id=bairro).order_by('logradouro')
    return render(request, 'clie/carregar-logradouros.html', {'logradouros': logradouros})

def verificar_empresa_e_cc(request, cod_empresa, cod_cc):
    if request.method == "POST":
        try:
            empresa = b01Empresas.objetos.get(id=cod_empresa)
            centro_de_custo = b04CCustos.objetos.filter(id=cod_cc, empresa=empresa)
            if len(centro_de_custo) == 0:
                return HttpResponse(content="", status=400)
        except:
            return HttpResponse(content="", status=400)
        request.session['empresa_orcamento'] = cod_empresa
        request.session['cc_orcamento'] = cod_cc
        return HttpResponse(content="", status=200)
    else:
        return HttpResponse(content="", status=405)

def carregar_centros_de_custo(request, cod_empresa):
    try:
        empresa = b01Empresas.objetos.get(id=cod_empresa)
    except:
        return HttpResponse(content="Empresa não válida", status=400)
    centros_de_custo = b04CCustos.objetos.filter(empresa=empresa, ativo=True).order_by('descricao')
    return render(request, 'clie/carregar-centro-de-custo.html', {'centrosDeCusto': centros_de_custo})