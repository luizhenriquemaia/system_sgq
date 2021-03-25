# Orçamentos de chapa de policarbonato
from math import asin, pi, sqrt

from main.models import a11Insumos
from numpy import arange

from .utils.funcoes_calculos import (arrend_cima, escrever_linha_eap,
                                     tot_peca_juncao)
from .utils.materiais_orcamento import (
    Calha, ChapaPolicarbonato, DiscoCorte, Eletrodo, FitaAluminio,
    FitaVentTape, Gaxeta, Guarnicao, ParafusosPolicarbonato, PerfilArremate,
    PerfilU, PerfilUniao, PerfisEstruturaisDiferentes, PerfisEstruturaisIguais,
    Roldana, Rufo, Selante)


############ Conferencia Distancia Apoios ########################
def conf_dist_apoios(esp_chapas, dist_apoios, tipo, raio_circulo, chapa_compacta):
    # estrutura plana
    if tipo == 1:
        # se a chapa for de 10mm não é necessária a adição de apoio a cada 0,525
        # Se a distância dos apoios for maior do que 0.71 necessita de apoio no meio
        if chapa_compacta:
            dist_apoios = dist_apoios / \
                2 if int(esp_chapas) != 10 and dist_apoios > 0.71 else dist_apoios
        # Se for chapa compacta
        else:
            if int(esp_chapas) == 6:
                dist_apoios = dist_apoios / 2 if dist_apoios > 1.06 else dist_apoios
            elif int(esp_chapas) == 4:
                dist_apoios = dist_apoios / 2 if dist_apoios > 0.81 else dist_apoios
            elif int(esp_chapas) == 3:
                dist_apoios = dist_apoios / 2 if dist_apoios > 0.69 else dist_apoios
    # estrutura em arco
    elif tipo == 2:
        if chapa_compacta:
            if int(esp_chapas) != 10 and dist_apoios > 0.71:
                # Segundo o catálogo da replaex
                if int(esp_chapas) == 6:
                    dist_apoios = 1.06 if raio_circulo >= 1.05 and raio_circulo <= 1.75 else dist_apoios / 2
                elif int(esp_chapas) == 8:
                    dist_apoios = 1.06 if raio_circulo >= 1.04 and raio_circulo <= 2.20 else dist_apoios / 2
        # Se for chapa compacta
        else:
            if int(esp_chapas) == 6:
                dist_apoios = dist_apoios / 2 if dist_apoios > 1.06 else dist_apoios
            elif int(esp_chapas) == 4:
                dist_apoios = dist_apoios / 2 if dist_apoios > 0.81 else dist_apoios
            elif int(esp_chapas) == 3:
                dist_apoios = dist_apoios / 2 if dist_apoios > 0.69 else dist_apoios
    return dist_apoios

# escrever "eap" para os insumos de orçamentos de policarbonato
def escrever_eap_insumos(self):
    linha_eap = escrever_linha_eap(
            '', '', -1, arrend_cima(self.quantidade, 2), '', 0, 0, self.codigo
        )
    return linha_eap

############ Calculo de  Orelinhas, Parafusos e Buchas ########################
# quantidade de parafusos é igual a quantidade de orelinhas e a de buchas
def calc_orelinhas(comprimento, largura, repeticoes):
    quant_orelinhas = arrend_cima(2.5 * (comprimento + largura) * repeticoes / 1 , 0)
    quant_orelinhas = quant_orelinhas + 10 - quant_orelinhas % 10 if quant_orelinhas % 10 != 0 else quant_orelinhas
    return quant_orelinhas


############ Calculo de  Riscos e Bonificações ########################
def calc_riscos_bonificacoes(custo_total, dificuldade):
    riscos = custo_total * dificuldade * 0.1
    bonificacoes = (custo_total * 0.3) + riscos
    return bonificacoes


################# Policarbonato Plano com Inclinação ################
#####################################################################
#####################################################################
def orc_poli_plano(prefEap, **valores):
    ################# Cálculos ###########################
    altura = valores['compPoli'] * (valores['declPoli'] / 100)
    comp_real = sqrt(pow(valores['compPoli'], 2) + pow(altura, 2))
    ##### Limite para não haver erro na hora de quantificar chapa #####
    ##### Até 2cm pode-se completar a chapa com fita #####
    if comp_real - valores['compPoli'] <= 0.02:
            comp_real = valores['compPoli']
    # definir booleans para ifs futuros
    perfil_uniao_igual_ao_arremate = True if valores['codPerfUn'] == valores['codPerfAr'] else False
    orcamento_com_chapa_compacta = True if a11Insumos.objetos.get(codigo=valores['codPoli']).catins_id == 55 else False
    comprimento_orcamento = comp_real
    largura_orcamento = valores['largPoli']
    estrutura_retratil = True if valores['estrutura'] == 1 else False
    if estrutura_retratil:
        estrutura_retratil_direcao_largura = True if valores['direcMovimento'] == 1 else False
        estrutura_retratil_direcao_comprimento = True if valores['direcMovimento'] == 0 else False
        # Tamanho do módulo da estrutura para cálculos
        if estrutura_retratil_direcao_comprimento:
            comprimento_orcamento = comp_real / valores['quantModulos']
        else:
            largura_orcamento = valores['largPoli'] / valores['quantModulos']
    linha_ant = 0
    custo_total = 0
    desc_poli = a11Insumos.objetos.get(codigo=valores['codPoli']).descricao
    if orcamento_com_chapa_compacta:
        if valores['repetPoli'] <= 1:
            if not estrutura_retratil:
                text_desc = f"Cobertura plana fixa de policarbonato compacto com dimensões {valores['largPoli']:.2f} x {(comp_real):.2f}m e com {valores['declPoli']}% de inclinação utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"Cobertura plana retrátil de policarbonato compacto com dimensões {valores['largPoli']:.2f} x {(comp_real):.2f}m e com {valores['declPoli']}% de inclinação utilizando {desc_poli}"
        else:
            if not estrutura_retratil:
                text_desc = f"{valores['repetPoli']} Coberturas planas fixas de policarbonato compacto com dimensões {valores['largPoli']:.2f} x {(comp_real):.2f}m e com {valores['declPoli']}% de inclinação utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"{valores['repetPoli']} Coberturas planas retráteis de policarbonato compacto com dimensões {valores['largPoli']:.2f} x {(comp_real):.2f}m e com {valores['declPoli']}% de inclinação utilizando {desc_poli}"
    else:
        if valores['repetPoli'] <= 1:
            if not estrutura_retratil:
                text_desc = f"Cobertura plana fixa de policarbonato alveolar com dimensões {valores['largPoli']:.2f} x {(comp_real):.2f}m e com {valores['declPoli']}% de inclinação utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"Cobertura plana retrátil de policarbonato alveolar com dimensões {valores['largPoli']:.2f} x {(comp_real):.2f}m e com {valores['declPoli']}% de inclinação utilizando {desc_poli}"
        else:
            if not estrutura_retratil:
                text_desc = f"{valores['repetPoli']} Coberturas planas fixas de policarbonato alveolar com dimensões {valores['largPoli']:.2f} x {(comp_real):.2f}m e com {valores['declPoli']}% de inclinação utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"{valores['repetPoli']} Coberturas planas retráteis de policarbonato alveolar com dimensões {valores['largPoli']:.2f} x {(comp_real):.2f}m e com {valores['declPoli']}% de inclinação utilizando {desc_poli}"
    linha_eap = escrever_linha_eap(
        prefEap, text_desc, 5, f"{float(comp_real * valores['largPoli'] * valores['repetPoli']):.2f}", 'm²', 0, 0, 0)
    eap_result = [linha_eap]
    linha_ant += 1

    ##################### Entrega externa -> Policarbonato #####################
    text_desc = f"Policarbonato e acessórios"
    linha_eap = escrever_linha_eap(
        f'{prefEap}01.', text_desc, 3, 1, 'un', 1, 0, 0)
    linha_ant += 1
    eap_result.append(linha_eap)

    ##################### Chapas #############################
    chapa_policarbonato = ChapaPolicarbonato(valores['codPoli'])
    chapa_policarbonato.calc_poli_alveolar(
        comprimento_orcamento, largura_orcamento, valores['distApoios'], valores['repetPoli'] * valores['quantModulos']
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(chapa_policarbonato)
    )

    ##################### Perfil União ######################
    perfil_uniao = PerfilUniao(valores['codPerfUn'])
    perfil_uniao.calc_perfil_uniao(largura_orcamento, comprimento_orcamento, valores['distApoios'], 
        valores['quantModulos'], valores['repetPoli'], perfil_uniao_igual_ao_arremate
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(perfil_uniao)
    )

    ################# Perfil U ###########################
    perfil_u = PerfilU(valores['codPerfU'])
    perfil_u.calc_perfil_u(largura_orcamento, valores['repetPoli'], valores['quantModulos'])
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(perfil_u)
    )

    ################# Perfil Arremate ####################
    if not orcamento_com_chapa_compacta and not perfil_uniao_igual_ao_arremate:
        perfil_arremate = PerfilArremate(valores['codPerfAr'])
        perfil_arremate.calc_perfil_arremate(
            comprimento_orcamento, 
            valores['repetPoli'], 
            valores['quantModulos']
        )
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(perfil_arremate)
        )

    ################# Perfil Guarnição ###################
    dist_apoios = conf_dist_apoios(
        chapa_policarbonato.espessura, 
        valores['distApoios'],
        1, 
        0, 
        orcamento_com_chapa_compacta
    )
    guarnicao = Guarnicao(valores['codPerfGuar'])
    guarnicao.calc_perfil_guarnicao(
        largura_orcamento, 
        comprimento_orcamento, 
        dist_apoios,
        valores['repetPoli'], 
        valores['quantModulos'], 
        perfil_uniao_igual_ao_arremate
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(guarnicao)
    )

    ################# Perfil Gaxeta ####################
    gaxeta = Gaxeta(valores['codPerfGax'])
    gaxeta.calc_perfil_gaxeta(
        largura_orcamento, 
        comprimento_orcamento, 
        dist_apoios, 
        valores['repetPoli'], 
        valores['quantModulos'], 
        perfil_uniao_igual_ao_arremate
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(gaxeta)
    )

    ################# Fita Alumínio ####################
    if not orcamento_com_chapa_compacta:
        fita_aluminio = FitaAluminio(valores['codFitaAlum'])
        fita_aluminio.calcular_quantidade(valores['largPoli'], valores['repetPoli'])
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(fita_aluminio)
        )
        
        ################# Fita Vent Tape ###################
        fita_vent = FitaVentTape(valores['codFitaVent'])
        fita_vent.calcular_quantidade(valores['largPoli'], valores['repetPoli'])
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(fita_vent)
        )

    ################## Parafusos #######################
    ############# PARAFUSO ARREMATE ###########
    if not orcamento_com_chapa_compacta and not perfil_uniao_igual_ao_arremate:
        # Parafuso arremate -> 10-16x3/4"
        parafuso_arremate = ParafusosPolicarbonato(14132)
        parafuso_arremate.calc_parafuso_arremate(
            comp_real, valores['repetPoli'], valores['quantModulos'], 0.3
        )
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(parafuso_arremate)
        )

    ############# PARAFUSO UNIÃO #############
    if chapa_policarbonato.espessura <= 6:
        # Parafuso união -> trapézio chapa 06 >> 12-14x1.1/2"
        if valores['codPerfUn'] == 10416:
            cod_parafuso = 14130
            dist_parafusos = 0.3
        # Parafuso união -> barra chata chapa 06 >> 12-14x1.1/4"
        else:
            cod_parafuso = 14128
            dist_parafusos = 0.2
    else:
        # Parafuso união -> trapezio chapa 10 >> 12-14x2"
        if valores['codPerfUn'] == 10416:
            cod_parafuso = 14129
            dist_parafusos = 0.3
        # Parafuso união -> barra chata chapa 10 >> 12-14x1.1/2"
        else:
            cod_parafuso = 14130
            dist_parafusos = 0.2
    parafuso_uniao = ParafusosPolicarbonato(cod_parafuso)
    parafuso_uniao.calc_parafuso_uniao(
        valores['largPoli'], 
        valores['distApoios'], 
        comp_real, 
        valores['repetPoli'], 
        dist_parafusos, 
        perfil_uniao_igual_ao_arremate
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(parafuso_uniao)
    )

    ################# Selante ###################
    selante = Selante(valores['cod_selante'])
    selante.calcular_quantidade(valores['largPoli'], comp_real, valores['repetPoli'], estrutura_retratil)
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(selante)
    )

    ##################### Entrega externa -> Outros insumos e MO #####################
    text_desc = f"Outros insumos e mão de obra"
    linha_eap = escrever_linha_eap(
        f'{prefEap}02.', text_desc, 3, 1, 'un', 1, 0, 0)
    linha_ant += 1
    eap_result.append(linha_eap)

    ################# Perfil Estrutural ##################
    distApoios = conf_dist_apoios(
        chapa_policarbonato.espessura, valores['distApoios'], 1, 0, orcamento_com_chapa_compacta)
    if not valores['apEstr']:
        if valores['codPerfEsExterno'] == valores['codPerfEsInterno']:
            perfil_estrutural = PerfisEstruturaisIguais(valores['codPerfEsExterno'])
            perfil_estrutural.calcular_quantidade(
                largura_orcamento, 
                valores['compPoli'],
                comprimento_orcamento,
                altura, 
                distApoios, 
                valores['repetPoli'],
                valores['quantModulos'], 
                valores['distMaosF']
            )
            linha_ant += 1
            eap_result.append(
                escrever_eap_insumos(perfil_estrutural)
            )
            custo_total += perfil_estrutural.preco()
        else:
            perfil_estrutural_interno = PerfisEstruturaisDiferentes(valores['codPerfEsInterno'], "interno")
            perfil_estrutural_interno.calcular_quantidade(
                largura_orcamento,
                valores['compPoli'], 
                comprimento_orcamento, 
                altura, 
                distApoios, 
                valores['repetPoli'],
                valores['quantModulos'], 
                valores['distMaosF'], 
                False
            )
            linha_ant += 1
            eap_result.append(
                escrever_eap_insumos(perfil_estrutural_interno)
            )
            custo_total += perfil_estrutural_interno.preco()
            perfil_estrutural_externo = PerfisEstruturaisDiferentes(valores['codPerfEsExterno'], "externo")
            perfil_estrutural_externo.calcular_quantidade(
                largura_orcamento, 
                valores['compPoli'], 
                comprimento_orcamento, 
                altura, 
                distApoios, 
                valores['repetPoli'],
                valores['quantModulos'], 
                valores['distMaosF'], 
                False
            )
            linha_ant += 1
            eap_result.append(
                escrever_eap_insumos(perfil_estrutural_externo)
            )
            custo_total += perfil_estrutural_externo.preco()

    ########################## Calhas ############################
    calha = Calha(valores['codCalha'])
    calha.calcular_quantidade(
        comp_real, 
        valores['largPoli'], 
        valores['latDir'],
        valores['latEsq'], 
        valores['montante'], 
        valores['jusante'], 
        valores['repetPoli']
    )
    if calha.quantidade != 0:
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(calha)
        )
        custo_total += calha.preco()
    
        ####################### Fechamento de Calha #######################
        obj_fech_calha = a11Insumos.objetos.get(codigo=6164)
        quant_fech_calha = 2
        linha_eap = escrever_linha_eap('', '',
                                       -1, quant_fech_calha, '', 0, 0, 6164)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_fech_calha * float(obj_fech_calha.custo01)
            
    ########################## Rufos ############################
    rufo = Rufo(valores['codRufo'])
    rufo.calcular_quantidade(
        comp_real, 
        valores['largPoli'], 
        valores['latDir'],
        valores['latEsq'], 
        valores['montante'], 
        valores['jusante'], 
        valores['repetPoli']
    )
    if rufo.quantidade != 0:
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(rufo)
        )
        custo_total += rufo.preco()

    ######################### Pintura #############################
    if not valores['apEstr']:
        if valores['quantPintura'] == 0:
            pass
        else:
            objPintura = a11Insumos.objetos.get(
                codigo=valores['codPintura'])
            linha_eap = escrever_linha_eap('', '', -1, valores['quantPintura'], '', 0, 0, valores['codPintura'])
            linha_ant += 1
            eap_result.append(linha_eap)
            custo_total += valores['quantPintura'] * \
                float(objPintura.custo01)

    ######################### Motores ###########################
    # Se a estrutura for retrátil
    if estrutura_retratil:
        linha_eap = escrever_linha_eap('', '', -1, valores['quantMotor'], '', 0, 0, valores['codMotor'])
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += valores['quantMotor'] * float(
            a11Insumos.objetos.get(codigo=valores['codMotor']).custo01)

        ######################### Suporte Motor #####################
        linha_eap = escrever_linha_eap('', '', -1, valores['quantMotor'], '', 0, 0, 14225)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += valores['quantMotor'] * float(
            a11Insumos.objetos.get(codigo=14225).custo01)

        ######################### Cantoneiras #######################
        quantCantoneiras = 0
        larguraModulos = arrend_cima(
            valores['largPoli'] / valores['quantModulos'], 0)
        if valores['quantModulos'] == 1 and estrutura_retratil_direcao_comprimento:
            if valores['quantModulos'] == valores['quantModMoveis']:
                if valores['largPoli'] >= 5:
                    # tem que ser sempre par esta divisão para a estrutura não ficar com um lado fazendo mais esforço
                    if (valores['largPoli']/3) % 2:
                        quantCantoneiras += 1
                    quantCantoneiras = (
                        valores['largPoli'] / 3) * 2 * valores['compPoli'] * 2
                else:
                    quantCantoneiras = 2 * 2 * valores['compPoli']
        elif valores['quantModulos'] == 1 and estrutura_retratil_direcao_largura:
            if valores['quantModulos'] == valores['quantModMoveis']:
                quantCantoneiras = 2 * 2 * valores['largPoli']
        else:
            if valores['quantModulos'] > 1 and estrutura_retratil_direcao_largura:
                if valores['quantModulos'] == valores['quantModMoveis']:
                    for i in arange(1, valores['quantModulos'], 1):
                        if i == valores['quantModulos']-1:
                            quantCantoneiras += larguraModulos*i + larguraModulos
                        else:
                            quantCantoneiras += (larguraModulos *
                                                i + larguraModulos)*2
                elif valores['quantModulos'] > valores['quantModMoveis']:
                    for i in arange(valores['quantModulos'] - valores['quantModMoveis']-1, valores['quantModulos'], 1):
                        if i == (valores['quantModulos']) - 1:
                            quantCantoneiras += larguraModulos*i + larguraModulos
                        else:
                            quantCantoneiras += 2 * \
                                (larguraModulos*i + larguraModulos)
            elif valores['quantModulos'] > 1 and estrutura_retratil_direcao_comprimento:
                quantCantoneiras = (
                    (valores['quantModulos'] * 2) - 1) * valores['compPoli'] / valores['quantModulos'] * 2
        quantCantoneiras = tot_peca_juncao(quantCantoneiras, 6)
        # Se for rolete de tecnil não precisa de cantoneira
        if not valores['codRoldanas'] == 14219 or valores['codRoldanas'] == 14297:
            linha_eap = escrever_linha_eap(
                '', '', -1, quantCantoneiras, '', 0, 0, valores['codCantoneira'])
            linha_ant += 1
            eap_result.append(linha_eap)
            custo_total += quantCantoneiras * float(
                a11Insumos.objetos.get(codigo=valores['codCantoneira']).custo01)

        ####################### Perfis Cantoneiras ####################
        linha_eap = escrever_linha_eap(
            '', '', -1, quantCantoneiras, '', 0, 0, valores['codPerfCant'])
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quantCantoneiras * float(
            a11Insumos.objetos.get(codigo=valores['codPerfCant']).custo01)

        ####################### Roldanas ##############################
        roldana = Roldana(valores['codRoldanas'])
        roldana.calcular_quantidade(
            comprimento_orcamento, 
            largura_orcamento,
            valores['direcMovimento'], 
            valores['repetPoli'], 
            valores['quantModMoveis']
        )
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(roldana)
        )
        custo_total += roldana.preco()

        ###################### Fios 2,5mm² #############################
        obj_fios = a11Insumos.objetos.get(codigo=6325)
        linha_eap = escrever_linha_eap(
            '', '', -1, 10, '', 0, 0, 6325)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += 10 * float(
            a11Insumos.objetos.get(codigo=6325).custo01)

        ##################### Fita Isolante ###########################
        # Adicionar 1 fita isolante por padrão quando a estrutura for retrátil
        linha_eap = escrever_linha_eap(
            '', '', -1, 1, '', 0, 0, 6326)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += 1 * float(
            a11Insumos.objetos.get(codigo=6326).custo01)
        
        #################### Parafuso Para Suporte do Motor ##########
        # Adicionar 4 parafusos por suporte do motor quando a estrutura for retrátil
        quant_parafuso_suporte = valores['quantMotor'] * 4
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_parafuso_suporte, '', 0, 0, 6327)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_parafuso_suporte * float(
            a11Insumos.objetos.get(codigo=6327).custo01)
        
        #################### Porca Para Suporte do Motor ##########
        # Adicionar 4 porcas por suporte do motor quando a estrutura for retrátil
        linha_eap = escrever_linha_eap('', '', -1, quant_parafuso_suporte, '', 0, 0, 6328)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_parafuso_suporte * float(
            a11Insumos.objetos.get(codigo=6328).custo01)

        ################## Arruelas Para Suporte do Motor #########
        # Adicionar 4 arruelas por suporte do motor quando a estrutura for retrátil
        linha_eap = escrever_linha_eap('', '', -1, quant_parafuso_suporte, '', 0, 0, 6329)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_parafuso_suporte * float(
            a11Insumos.objetos.get(codigo=6329).custo01)

    else:
        pass

    if not valores['apEstr']:
        ####################### Discos de Corte ##############################
        disco_de_corte = DiscoCorte(6300)
        disco_de_corte.calcular_quantidade(
            comprimento_orcamento, 
            largura_orcamento,
            distApoios, 
            valores['repetPoli']
        )
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(disco_de_corte)
        )
        custo_total += disco_de_corte.preco()
        ####################### Eletrodos #######################
        eletrodo = Eletrodo(6302)
        eletrodo.calcular_quantidade(
            comprimento_orcamento,
            largura_orcamento, 
            distApoios, 
            valores['repetPoli']
        )
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(eletrodo)
        )
        custo_total += eletrodo.preco()
        ####################### Orelinhas #######################
        quant_orelinhas = calc_orelinhas(
            comprimento_orcamento,
            largura_orcamento, 
            valores['repetPoli']
        )
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_orelinhas, '', 0, 0, 14217)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_orelinhas * float(
            a11Insumos.objetos.get(codigo=14217).custo01)

        ####################### Parafusos 10 #######################
        quant_paraf_est = quant_orelinhas
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_paraf_est, '', 0, 0, 6307)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_paraf_est * float(
            a11Insumos.objetos.get(codigo=6307).custo01)

        ####################### Bucha 10 #######################
        quant_bucha_est = quant_paraf_est
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_bucha_est, '', 0, 0, 6306)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_bucha_est * float(
            a11Insumos.objetos.get(codigo=6306).custo01)

        ####################### Broca de Concreto #######################
        quant_broca_conc = 1
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_broca_conc, '', 0, 0, 6308)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_broca_conc * float(
            a11Insumos.objetos.get(codigo=6308).custo01)

        ####################### Broca de Aço #######################
        quant_broca_aco = 1
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_broca_aco, '', 0, 0, 6309)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_broca_aco * float(
            a11Insumos.objetos.get(codigo=6309).custo01)
    else:
        pass

    # Serralheiro
    if not int(valores['diasSerralheiro']) == 0 or not int(valores['quantSerralheiros']) == 0:
        serralheiros = 8 * valores['quantSerralheiros'] * valores['diasSerralheiro']
        linha_eap = escrever_linha_eap(
            '', '', -1, serralheiros, 'h', 0, 0, 1163)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += float(serralheiros) * float(
            a11Insumos.objetos.get(codigo=1163).custo01)
    # Auxiliar
    if not int(valores['diasAuxiliar']) == 0 or not int(valores['quantAuxiliares']) == 0:
        auxiliares = 8 * valores['quantAuxiliares'] * valores['diasAuxiliar']
        linha_eap = escrever_linha_eap(
            '', '', -1, auxiliares, 'h', 0, 0, 1152)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += float(auxiliares) * float(
            a11Insumos.objetos.get(codigo=1152).custo01)


    ################### Entrega interna -> Riscos Incidentes e Bonificações #############################
    linha_eap = escrever_linha_eap(f'{prefEap}03.', "Riscos Incidentes", 2, 1, 'un', 4, 0, 0)
    linha_ant += 1
    eap_result.append(linha_eap)

    ################### Insumo -> Riscos Incidentes e Bonificações #############################
    bonificacoes = calc_riscos_bonificacoes(custo_total, valores['dificuldade'])
    linha_eap = escrever_linha_eap(
        '', '', -1, bonificacoes, '', 0, 0, 1)
    linha_ant += 1
    eap_result.append(linha_eap)
    return eap_result


def orc_poli_curvo(prefEap, **valores):
    ################# Cálculos ###########################
    raioCirculo = (pow(valores['cordaPoli'] / 2, 2) + pow(valores['flechaPoli'], 2)) / (2 * valores['flechaPoli'])
    anguloCurva = asin((valores['cordaPoli'] / 2) / raioCirculo)
    arcoCurva = (anguloCurva * 2) * raioCirculo
    if arcoCurva - valores['cordaPoli'] <= 0.02:
        arcoCurva = valores['cordaPoli']
    else:
        pass
    linha_ant = 0
    custo_total = 0
    # definir booleans para ifs futuros
    perfil_uniao_igual_ao_arremate = True if valores['codPerfUn'] == valores['codPerfAr'] else False
    orcamento_com_chapa_compacta = True if a11Insumos.objetos.get(codigo=valores['codPoli']).catins_id == 55 else False
    estrutura_retratil = True if valores['estrutura'] == 1 else False
    largura_orcamento = valores['largPoli']
    comprimento_orcamento = arcoCurva
    estrutura_retratil = True if valores['estrutura'] == 1 else False
    if estrutura_retratil:
        estrutura_retratil_direcao_largura = True if valores['direcMovimento'] == 1 else False
        estrutura_retratil_direcao_comprimento = True if valores['direcMovimento'] == 0 else False
        # Tamanho do módulo da estrutura para cálculos
        if estrutura_retratil_direcao_comprimento:
            comprimento_orcamento = arcoCurva / valores['quantModulos']
        else:
            largura_orcamento = valores['largPoli'] / valores['quantModulos']
    desc_poli = a11Insumos.objetos.get(codigo=valores['codPoli']).descricao
    if orcamento_com_chapa_compacta:
        if valores['repetPoli'] <= 1:
            if not estrutura_retratil:
                text_desc = f"Cobertura curva fixa de policarbonato compacto com dimensões {valores['largPoli']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"Cobertura curva retrátil de policarbonato compacto com dimensões {valores['largPoli']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
        else:
            if not estrutura_retratil:
                text_desc = f"{valores['repetPoli']} Coberturas curvas fixas de policarbonato compacto com dimensões {valores['largPoli']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"{valores['repetPoli']} Coberturas curvas retráteis de policarbonato compacto com dimensões {valores['largPoli']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
    else:
        if valores['repetPoli'] <= 1:
            if not estrutura_retratil:
                text_desc = f"Cobertura curva fixa de policarbonato alveolar com dimensões {valores['largPoli']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"Cobertura curva retrátil de policarbonato alveolar com dimensões {valores['largPoli']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
        else:
            if not estrutura_retratil:
                text_desc = f"{valores['repetPoli']} Coberturas curvas fixas de policarbonato alveolar com dimensões {valores['largPoli']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"{valores['repetPoli']} Coberturas curvas retráteis de policarbonato alveolar com dimensões {valores['largPoli']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
    linha_eap = escrever_linha_eap(
        prefEap, text_desc, 5, f"{float(arcoCurva * valores['largPoli'] * valores['repetPoli']):.2f}", 'm²', 0, 0, 0)
    eap_result = [linha_eap]
    linha_ant += 1

    ##################### Entrega externa -> Policarbonato #####################
    text_desc = f"Policarbonato e acessórios"
    linha_eap = escrever_linha_eap(
        f'{prefEap}01.', text_desc, 3, 1, 'un', 1, 0, 0)
    linha_ant += 1
    eap_result.append(linha_eap)

    ##################### Chapas #############################
    chapa_policarbonato = ChapaPolicarbonato(valores['codPoli'])
    chapa_policarbonato.calc_poli_alveolar(
        comprimento_orcamento, 
        largura_orcamento, 
        valores['distApoios'], 
        valores['repetPoli'] * valores['quantModulos']
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(chapa_policarbonato)
    )

    ##################### Perfil União ######################
    perfil_uniao = PerfilUniao(valores['codPerfUn'])
    perfil_uniao.calc_perfil_uniao(
        largura_orcamento, 
        comprimento_orcamento,
        valores['distApoios'],
        valores['quantModulos'], 
        valores['repetPoli'], 
        perfil_uniao_igual_ao_arremate
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(perfil_uniao)
    )

    ################# Perfil U ###########################
    perfil_u = PerfilU(valores['codPerfU'])
    perfil_u.calc_perfil_u(
        largura_orcamento, 
        valores['repetPoli'], 
        valores['quantModulos']
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(perfil_u)
    )

    ################# Perfil Arremate ####################
    if not orcamento_com_chapa_compacta and not perfil_uniao_igual_ao_arremate:
        perfil_arremate = PerfilArremate(valores['codPerfAr'])
        perfil_arremate.calc_perfil_arremate(
            comprimento_orcamento, 
            valores['repetPoli'], 
            valores['quantModulos']
        )
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(perfil_arremate)
        )
    
    ################# Perfil Guarnição ###################
    dist_apoios = conf_dist_apoios(
        chapa_policarbonato.espessura,
        valores['distApoios'], 
        2, 
        raioCirculo, 
        orcamento_com_chapa_compacta
    )
    guarnicao = Guarnicao(valores['codPerfGuar'])
    guarnicao.calc_perfil_guarnicao(
        largura_orcamento, 
        comprimento_orcamento, 
        dist_apoios,
        valores['repetPoli'], 
        valores['quantModulos'], 
        perfil_uniao_igual_ao_arremate
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(guarnicao)
    )

    ################# Perfil Gaxeta ####################
    gaxeta = Gaxeta(valores['codPerfGax'])
    gaxeta.calc_perfil_gaxeta(
        largura_orcamento, 
        comprimento_orcamento, 
        dist_apoios, 
        valores['repetPoli'], 
        valores['quantModulos'], 
        perfil_uniao_igual_ao_arremate
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(gaxeta)
    )

    ################# Fita Alumínio ####################
    if not orcamento_com_chapa_compacta:
        # Não utilizar fita alumínio em coberturas arqueadas
        ################# Fita Vent Tape ###################
        fita_vent = FitaVentTape(valores['codFitaVent'])
        fita_vent.calcular_quantidade(
            2 * valores['largPoli'], valores['repetPoli'])
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(fita_vent)
        )

    ################# Selante ###################
    selante = Selante(valores['cod_selante'])
    selante.calcular_quantidade(
        largura_orcamento, 
        comprimento_orcamento, 
        valores['repetPoli'] * valores['quantModulos'], 
        estrutura_retratil
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(selante)
    )

    ################## Parafusos #######################
    ############# PARAFUSO ARREMATE ###########
    if not orcamento_com_chapa_compacta and not perfil_uniao_igual_ao_arremate:
        # Parafuso arremate -> 10-16x3/4"
        parafuso_arremate = ParafusosPolicarbonato(14132)
        parafuso_arremate.calc_parafuso_arremate(
            comprimento_orcamento, 
            valores['repetPoli'], 
            valores['quantModulos'], 
            0.3
        )
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(parafuso_arremate)
        )

    ############# PARAFUSO UNIÃO #############
    if chapa_policarbonato.espessura <= 6:
        # Parafuso união -> trapézio chapa 06 >> 12-14x1.1/2"
        if valores['codPerfUn'] == 10416:
            cod_parafuso = 14130
            dist_parafusos = 0.3
        # Parafuso união -> barra chata chapa 06 >> 12-14x1.1/4"
        else:
            cod_parafuso = 14128
            dist_parafusos = 0.2
    else:
        # Parafuso união -> trapezio chapa 10 >> 12-14x2"
        if valores['codPerfUn'] == 10416:
            cod_parafuso = 14129
            dist_parafusos = 0.3
        # Parafuso união -> barra chata chapa 10 >> 12-14x1.1/2"
        else:
            cod_parafuso = 14130
            dist_parafusos = 0.2

    parafuso_uniao = ParafusosPolicarbonato(cod_parafuso)
    parafuso_uniao.calc_parafuso_uniao(
        largura_orcamento, 
        valores['distApoios'],
        comprimento_orcamento, 
        valores['repetPoli'] * valores['quantModulos'], 
        dist_parafusos, 
        perfil_uniao_igual_ao_arremate
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(parafuso_uniao)
    )

    ##################### Entrega externa -> Outros insumos e MO #####################
    text_desc = f"Outros insumos e mão de obra"
    linha_eap = escrever_linha_eap(
        f'{prefEap}02.', text_desc, 3, 1, 'un', 1, 0, 0)
    linha_ant += 1
    eap_result.append(linha_eap)

    ################# Perfil Estrutural ##################
    distApoios = conf_dist_apoios(
        chapa_policarbonato.espessura, valores['distApoios'], 2, raioCirculo, orcamento_com_chapa_compacta)
    if not valores['apEstr']:
        if valores['codPerfEsEx'] == valores['codPerfEsIn']:
            perfil_estrutural = PerfisEstruturaisIguais(valores['codPerfEsEx'])
            perfil_estrutural.calcular_quantidade(
                largura_orcamento, 
                valores['cordaPoli'],
                comprimento_orcamento + 0.2,
                valores['flechaPoli'],
                distApoios, 
                valores['repetPoli'], 
                valores['quantModulos'], 
                valores['distMaosF']
            )
            linha_ant += 1
            eap_result.append(
                escrever_eap_insumos(perfil_estrutural)
            )
            custo_total += perfil_estrutural.preco()
        else:
            perfil_estrutural_interno = PerfisEstruturaisDiferentes(
                valores['codPerfEsIn'], "interno")
            perfil_estrutural_interno.calcular_quantidade(
                largura_orcamento, 
                valores['cordaPoli'],
                comprimento_orcamento + 0.2, 
                valores['flechaPoli'], 
                distApoios, 
                valores['repetPoli'], 
                valores['quantModulos'], 
                valores['distMaosF'], 
                True
            )
            linha_ant += 1
            eap_result.append(
                escrever_eap_insumos(perfil_estrutural_interno)
            )
            custo_total += perfil_estrutural_interno.preco()
            perfil_estrutural_externo = PerfisEstruturaisDiferentes(
                valores['codPerfEsEx'], 
                "externo"
            )
            perfil_estrutural_externo.calcular_quantidade(
                largura_orcamento, 
                valores['cordaPoli'],
                comprimento_orcamento + 0.2, 
                valores['flechaPoli'], 
                distApoios, 
                valores['repetPoli'], 
                valores['quantModulos'], 
                valores['distMaosF'], 
                True
            )
            linha_ant += 1
            eap_result.append(
                escrever_eap_insumos(perfil_estrutural_externo)
            )
            custo_total += perfil_estrutural_externo.preco()
    
    
    ########################## Calhas ############################
    calha = Calha(valores['codCalha'])
    calha.calcular_quantidade(
        valores['cordaPoli'], 
        valores['largPoli'], 
        valores['latDir'],
        valores['latEsq'], 
        valores['montante'], 
        valores['jusante'], 
        valores['repetPoli']
    )
    if calha.quantidade != 0:
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(calha)
        )
        custo_total += calha.preco()

        ####################### Fechamento de Calha #######################
        obj_fech_calha = a11Insumos.objetos.get(codigo=6164)
        quant_fech_calha = 2
        linha_eap = escrever_linha_eap('', '', -1, quant_fech_calha, '', 0, 0, 6164)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_fech_calha * float(obj_fech_calha.custo01)

    ########################## Rufos ############################
    rufo = Rufo(valores['codRufo'])
    rufo.calcular_quantidade(
        valores['cordaPoli'], 
        valores['largPoli'], 
        valores['latDir'],
        valores['latEsq'], 
        valores['montante'], 
        valores['jusante'], 
        valores['repetPoli']
    )
    if rufo.quantidade != 0:
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(rufo)
        )
        custo_total += rufo.preco()

    #################### Calandrar Material ######################
    # arcoCurva + 0.20 -> perde 20cm de metalon na calandra
    if valores['apEstr'] == False:
        quantCalandra = arrend_cima((
            arrend_cima(
                round(
                    largura_orcamento / distApoios, 5), 0) + 1) * (
                        comprimento_orcamento + 0.20) * valores['repetPoli'] * valores['quantModulos'], 0)
        objCalandra = a11Insumos.objetos.get(codigo=valores['codCalandra'])
        linha_eap = escrever_linha_eap(f'{prefEap}01.02.04.', f"{quantCalandra} m de {objCalandra.descricao}",
                                -1, quantCalandra, 'm', 2, 21, valores['codCalandra'])
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quantCalandra * float(objCalandra.custo01)

    ######################### Pintura #############################
    if valores['apEstr'] == False:
        if valores['quantPintura'] == 0:
            pass
        else:
            objPintura = a11Insumos.objetos.get(codigo=valores['codPintura'])
            linha_eap = escrever_linha_eap('', '', -1, valores['quantPintura'], '', 0, 0, valores['codPintura'])
            linha_ant += 1
            eap_result.append(linha_eap)
            custo_total += valores['quantPintura'] * float(objPintura.custo01)

    ######################### Motores ###########################
    if estrutura_retratil:
        linha_eap = escrever_linha_eap(
            '', '', -1, valores['quantMotor'], '', 0, 0, valores['codMotor'])
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += valores['quantMotor'] * float(
            a11Insumos.objetos.get(codigo=valores['codMotor']).custo01)

        ######################### Suporte Motor #####################
        linha_eap = escrever_linha_eap('', '', -1, valores['quantMotor'], '', 0, 0, 14225)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += valores['quantMotor'] * float(
            a11Insumos.objetos.get(codigo=14225).custo01)

        ######################### Cantoneiras #######################
        quantCantoneiras = 0
        larguraModulos = arrend_cima(valores['largPoli']/valores['quantModulos'], 0)
        if valores['quantModulos'] == 1 and estrutura_retratil_direcao_comprimento:
            if valores['quantModulos'] == valores['quantModMoveis']:
                if valores['largPoli'] >= 5:
                    # tem que ser sempre par esta divisão para a estrutura não ficar com um lado fazendo mais esforço
                    if (valores['largPoli']/3)%2:
                        quantCantoneiras += 1
                    quantCantoneiras = (valores['largPoli']/3)*2*comprimento_orcamento*2
                else:
                    quantCantoneiras = 2*valores['comprimento']
        elif valores['quantModulos'] == 1 and estrutura_retratil_direcao_largura:
            if valores['quantModulos'] == valores['quantModMoveis']:
                quantCantoneiras = valores['largPoli']*2
        else:
            if valores['quantModulos'] > 1 and estrutura_retratil_direcao_largura:
                if valores['quantModulos'] == valores['quantModMoveis']:
                    for i in arange(1, valores['quantModulos'], 1):
                        if i == valores['quantModulos'] - 1:
                            if i == 1:
                                quantCantoneiras += 2 * (larguraModulos * i + larguraModulos)
                            else:
                                quantCantoneiras += larguraModulos * i + larguraModulos
                        else:
                            quantCantoneiras += (larguraModulos*i + larguraModulos) * 2
                elif valores['quantModulos'] > valores['quantModMoveis']:
                    for i in arange(valores['quantModulos'] - valores['quantModMoveis'], valores['quantModulos'], 1):
                        if i == (valores['quantModulos']) - 1:
                            if i == 1:
                                quantCantoneiras += 2 * (larguraModulos * i + larguraModulos)
                            else:
                                quantCantoneiras += larguraModulos * i + larguraModulos
                        else:
                            quantCantoneiras += 2 * (larguraModulos * i + larguraModulos)
            elif valores['quantModulos'] > 1 and estrutura_retratil_direcao_comprimento:
                quantCantoneiras = ((valores['quantModulos']*2)-1)*comprimento_orcamento*2
        quantCantoneiras = tot_peca_juncao(quantCantoneiras, 6)
        # Se for roldana para 75mm não precisa de cantoneira
        if not valores['codRoldanas'] == 14219 and not valores['codRoldanas'] == 14297:
            linha_eap = escrever_linha_eap(
                '', '', -1, quantCantoneiras, '', 0, 0, valores['codCantoneira'])
            linha_ant += 1
            eap_result.append(linha_eap)
            custo_total += quantCantoneiras * float(
                a11Insumos.objetos.get(codigo=valores['codCantoneira']).custo01)

        ####################### Perfis Cantoneiras ####################
        linha_eap = escrever_linha_eap(
            '', '', -1, quantCantoneiras, '', 0, 0, valores['codPerfCant'])
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quantCantoneiras * float(
            a11Insumos.objetos.get(codigo=valores['codPerfCant']).custo01)

        ####################### Roldanas ##############################
        roldana = Roldana(valores['codRoldanas'])
        roldana.calcular_quantidade(
            comprimento_orcamento, 
            largura_orcamento, 
            valores['direcMovimento'], 
            valores['repetPoli'], 
            valores['quantModMoveis']
        )
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(roldana)
        )
        custo_total += roldana.preco()

        ###################### Fios 2,5mm #############################
        # Adicionar por padrão 10 metros de fio 2,5 quando a estrutura for retrátil
        linha_eap = escrever_linha_eap('', '', -1, 10, '', 0, 0, 6325)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += 10 * float(
            a11Insumos.objetos.get(codigo=6325).custo01)

        ##################### Fita Isolante ###########################
        # Adicionar 1 fita isolante por padrão quando a estrutura for retrátil
        linha_eap = escrever_linha_eap('', '', -1, 1, '', 0, 0, 6326)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += 1 * float(
            a11Insumos.objetos.get(codigo=6326).custo01)

        #################### Parafuso Para Suporte do Motor ##########
        # Adicionar 4 parafusos por suporte do motor quando a estrutura for retrátil
        quant_parafuso_suporte = valores['quantMotor'] * 4
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_parafuso_suporte, '', 0, 0, 6327)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_parafuso_suporte * float(
            a11Insumos.objetos.get(codigo=6327).custo01)

        #################### Porca Para Suporte do Motor ##########
        # Adicionar 4 porcas por suporte do motor quando a estrutura for retrátil
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_parafuso_suporte, '', 0, 0, 6328)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_parafuso_suporte * float(
            a11Insumos.objetos.get(codigo=6328).custo01)

        ################## Arruelas Para Suporte do Motor #########
        # Adicionar 4 arruelas por suporte do motor quando a estrutura for retrátil
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_parafuso_suporte, '', 0, 0, 6329)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_parafuso_suporte * float(
            a11Insumos.objetos.get(codigo=6329).custo01)
    else:
        pass

    if valores['apEstr'] == False:
        ####################### Discos de Corte ##############################
        disco_de_corte = DiscoCorte(6300)
        disco_de_corte.calcular_quantidade(
            comprimento_orcamento, 
            largura_orcamento, 
            distApoios, 
            valores['repetPoli']
        )
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(disco_de_corte)
        )
        custo_total += disco_de_corte.preco()
        ####################### Eletrodos #######################
        eletrodo = Eletrodo(6302)
        eletrodo.calcular_quantidade(
            comprimento_orcamento, 
            largura_orcamento, 
            distApoios, 
            valores['repetPoli']
        )
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(eletrodo)
        )
        custo_total += eletrodo.preco()

        ####################### Orelinhas #######################
        quant_orelinhas = calc_orelinhas(
            comprimento_orcamento, 
            largura_orcamento,
            valores['repetPoli']
        )
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_orelinhas, '', 0, 0, 14217)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_orelinhas * float(
            a11Insumos.objetos.get(codigo=14217).custo01)

        ####################### Parafusos 10 #######################
        quant_paraf_est = quant_orelinhas
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_paraf_est, '', 0, 0, 6307)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_paraf_est * float(
            a11Insumos.objetos.get(codigo=6307).custo01)

        ####################### Bucha 10 #######################
        quant_bucha_est = quant_paraf_est
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_bucha_est, '', 0, 0, 6306)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_bucha_est * float(
            a11Insumos.objetos.get(codigo=6306).custo01)

        ####################### Broca de Concreto #######################
        quant_broca_conc = 1
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_broca_conc, '', 0, 0, 6308)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_broca_conc * float(
            a11Insumos.objetos.get(codigo=6308).custo01)

        ####################### Broca de Aço #######################
        quant_broca_aco = 1
        linha_eap = escrever_linha_eap(
            '', '',  -1, quant_broca_aco, '', 0, 0, 6309)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_broca_aco * float(
            a11Insumos.objetos.get(codigo=6309).custo01)
    else:
        pass

    # Serralheiro
    if not int(valores['diasSerralheiro']) == 0 or not int(valores['quantSerralheiros']) == 0:
        serralheiros = 8 * \
            valores['quantSerralheiros'] * valores['diasSerralheiro']
        linha_eap = escrever_linha_eap(
            '', '', -1, serralheiros, '', 0, 0, 1163)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += float(serralheiros) * float(
            a11Insumos.objetos.get(codigo=1163).custo01)
    # Auxiliar
    if not int(valores['diasAuxiliar']) == 0 or not int(valores['quantAuxiliares']) == 0:
        auxiliares = 8 * valores['quantAuxiliares'] * valores['diasAuxiliar']
        linha_eap = escrever_linha_eap(
            '', '', -1, auxiliares, '', 0, 0, 1152)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += float(auxiliares) * float(
            a11Insumos.objetos.get(codigo=1152).custo01)


    ################### Entrega interna -> Riscos Incidentes e Bonificações #############################
    linha_eap=escrever_linha_eap(
        f'{prefEap}03.', "Riscos Incidentes", 2, 1, 'un', 4, 0, 0)
    linha_ant += 1
    eap_result.append(linha_eap)

    ################### Insumo -> Riscos Incidentes e Bonificações #############################
    bonificacoes=calc_riscos_bonificacoes(custo_total, valores['dificuldade'])
    linha_eap=escrever_linha_eap(
        '', '', -1, bonificacoes, '', 0, 0, 1)
    linha_ant += 1
    eap_result.append(linha_eap)

    return eap_result
