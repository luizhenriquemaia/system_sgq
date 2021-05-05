# Orçamentos de perfil multi-click (multi telha)
from math import sqrt
from decimal import *

from main.models import a11Insumos
from numpy import arange

from .utils.funcoes_calculos import (arrend_cima, escrever_linha_eap,
                                     tot_peca_juncao)
from .utils.materiais_orcamento import (
    TelhaTrapezoidal, ParafusosTelha, ParafusoCosturaTelhas, FitaTackyTape,
    Calha, DiscoCorte, Eletrodo, PerfisEstruturaisDiferentes, PerfisEstruturaisIguais,
    Roldana, Rufo, Selante)


############ Conferencia Distancia Apoios Multi-Click ########################
def conf_dist_apoios(dist_apoios, tipo):
    # estrutura plana
    # para aplicação plana a distância máxima entre terças é de 1.50m
    if tipo == 1:     
        dist_apoios = dist_apoios / 2 if dist_apoios > 1.50 else dist_apoios
    return Decimal(dist_apoios)

# escrever "eap" para os insumos de orçamentos de policarbonato
def escrever_eap_insumos(self):
    linha_eap = escrever_linha_eap(
            '', '', -1, arrend_cima(self.quantidade, 2), '', 0, 0, self.codigo
        )
    return linha_eap

############ Calculo de  Orelinhas, Parafusos e Buchas ########################
# quantidade de parafusos é igual a quantidade de orelinhas e a de buchas
def calc_orelinhas(comprimento, largura, repeticoes):
    quant_orelinhas = arrend_cima(Decimal(2.5) * (comprimento + largura) * repeticoes / 1 , 0)
    quant_orelinhas = quant_orelinhas + 10 - quant_orelinhas % 10 if quant_orelinhas % 10 != 0 else quant_orelinhas
    return Decimal(quant_orelinhas)


############ Calculo de  Riscos e Bonificações ########################
def calc_riscos_bonificacoes(custo_total, dificuldade):
    riscos = custo_total * Decimal(dificuldade) * Decimal(0.1)
    bonificacoes = (custo_total * Decimal(0.3)) + riscos
    return bonificacoes


def orc_telha_trapezoidal(prefEap, **valores):
    ################# Cálculos ###########################
    altura = valores['comprimento'] * (valores['declividade'] / 100)
    comp_real = Decimal(sqrt(pow(valores['comprimento'], 2) + pow(altura, 2)))
    if comp_real - valores['comprimento'] <= 0.02:
            comp_real = valores['comprimento']
    categoria_telha = a11Insumos.objetos.get(codigo=valores['codigo_telha']).catins_id
    # definir booleans para ifs futuros
    estrutura_retratil = True if valores['estrutura'] == 1 else False
    if estrutura_retratil:
        estrutura_retratil_direcao_largura = True if valores['direcMovimento'] == 1 else False
        estrutura_retratil_direcao_comprimento = True if valores['direcMovimento'] == 0 else False
        # Tamanho do módulo da estrutura para cálculos
        if estrutura_retratil_direcao_comprimento:
            tam_modulos = arrend_cima(
                comp_real / valores['quantidade_modulos'], 0)
        else:
            tam_modulos = arrend_cima(
                valores['largura'] / valores['quantidade_modulos'], 0)
    linha_ant = 0
    custo_total = 0
    tam_modulos = 0
    desc_telha = a11Insumos.objetos.get(
        codigo=valores['codigo_telha']).descricao
    if valores['repeticoes'] <= 1:
        if not estrutura_retratil:
            text_desc = f"Cobertura plana fixa de {desc_telha}  com dimensões {valores['largura']:.2f} x {(comp_real):.2f}m e com {valores['declividade']}% de inclinação"
        elif estrutura_retratil:
            text_desc = f"Cobertura plana retrátil de {desc_telha} com dimensões {valores['largura']:.2f} x {(comp_real):.2f}m e com {valores['declividade']}% de inclinação"
    else:
        if not estrutura_retratil:
            text_desc = f"{valores['repeticoes']}Coberturas planas fixas de {desc_telha} com dimensões {valores['largura']:.2f} x {(comp_real):.2f}m e com {valores['declividade']}% de inclinação"
        elif estrutura_retratil:
            text_desc = f"{valores['repeticoes']}Coberturas planas retráteis de {desc_telha} com dimensões {valores['largura']:.2f} x {(comp_real):.2f}m e com {valores['declividade']}% de inclinação"
    linha_eap = escrever_linha_eap(
        prefEap, text_desc, 5, f"{float(comp_real * valores['largura'] * valores['repeticoes']):.2f}", 'm²', 0, 0, 0)
    eap_result = [linha_eap]
    linha_ant += 1

    ##################### Entrega Externa -> Telha e Acessórios #####################
    text_desc = f"Telha e acessórios"
    linha_eap = escrever_linha_eap(
        f'{prefEap}01.', text_desc, 3, 1, 'un', 1, 0, 0)
    linha_ant += 1
    eap_result.append(linha_eap)

    ##################### Telhas #############################
    telha = TelhaTrapezoidal(valores['codigo_telha'])
    telha.calcular_quantidade(
        comp_real, valores['largura'], valores['distancia_entre_apoios'], valores['repeticoes']
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(telha))

    ################## Parafusos #######################
    # Parafuso fixação
    parafuso_fixacao = ParafusosTelha(
        valores['codigo_parafuso_fixacao'])
    # telha trapezoidal zincada 
    if telha.tipo == 62:
        parafuso_fixacao.calc_parafusos_telha_zincada(
            valores['largura'], comp_real, valores['repeticoes'], valores['quantidade_modulos'], telha.largura)
    # telha termoacústica id = 61
    else:
        parafuso_fixacao.calc_parafusos_telha_termoacustica(
            valores['largura'], comp_real, valores['repeticoes'], valores['quantidade_modulos'], telha.largura)
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(parafuso_fixacao))

    # Parafuso terças
    parafuso_costura = ParafusoCosturaTelhas(
        valores['codigo_parafuso_costura'])
    parafuso_costura.calcular_quantidade(
        valores['largura'], 
        telha.largura,
        comp_real,
        valores['distancia_entre_apoios'], 
        valores['repeticoes'], 
        valores['quantidade_modulos'])
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(parafuso_costura))

    ################# Selante ###################
    selante = Selante(valores['codigo_selante'])
    selante.calcular_quantidade(valores['largura'], comp_real, valores['repeticoes'], estrutura_retratil)
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(selante))
    
    ################# Fita Tacky Tape ###################
    # utiliza na telha isotérmica
    if telha.tipo == 61:
        fita_tacky_tape = FitaTackyTape(14307)
        fita_tacky_tape.calcular_quantidade(
            valores['largura'], telha.largura, comp_real, valores['repeticoes'], valores['quantidade_modulos'])
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(fita_tacky_tape))

    ##################### Entrega externa -> Outros insumos e MO #####################
    text_desc = f"Outros insumos e mão de obra"
    linha_eap = escrever_linha_eap(
        f'{prefEap}02.', text_desc, 3, 1, 'un', 1, 0, 0)
    linha_ant += 1
    eap_result.append(linha_eap)

    ################# Perfil Estrutural ##################
    distancia_entre_apoios = conf_dist_apoios(
        valores['distancia_entre_apoios'], 1)
    if not valores['aproveitar_estrutura']:
        if estrutura_retratil:
            if estrutura_retratil_direcao_largura:
                largura_real_perf_estrutural = valores['largura'] / valores['quantidade_modulos']
                comprimento_real_perf_estrutural = comp_real
            else:
                largura_real_perf_estrutural = valores['largura']
                comprimento_real_perf_estrutural = comp_real / valores['quantidade_modulos']
        else:
            largura_real_perf_estrutural = valores['largura']
            comprimento_real_perf_estrutural = comp_real
        # Para aproveitar o mesmo material inventer comprimento e largura pois o material foi baseado em policarbonato
        if valores['codigo_perfil_estrutural_externo'] == valores['codigo_perfil_estrutural_interno']:
            perfil_estrutural = PerfisEstruturaisIguais(valores['codigo_perfil_estrutural_externo'])
            perfil_estrutural.calcular_quantidade(comprimento_real_perf_estrutural, valores['comprimento'],
                largura_real_perf_estrutural, altura, distancia_entre_apoios, valores['repeticoes'],
                valores['quantidade_modulos'], valores['distancia_entre_maos_f'])
            linha_ant += 1
            eap_result.append(
                escrever_eap_insumos(perfil_estrutural)
            )
            custo_total += perfil_estrutural.preco()
        else:
            perfil_estrutural_interno = PerfisEstruturaisDiferentes(valores['codigo_perfil_estrutural_interno'], "interno")
            perfil_estrutural_interno.calcular_quantidade(
                comprimento_real_perf_estrutural, valores['comprimento'], 
                valores['largura'], altura, distancia_entre_apoios, valores['repeticoes'],
                valores['quantidade_modulos'], valores['distancia_entre_maos_f'], False
            )
            linha_ant += 1
            eap_result.append(
                escrever_eap_insumos(perfil_estrutural_interno)
            )
            custo_total += perfil_estrutural_interno.preco()
            perfil_estrutural_externo = PerfisEstruturaisDiferentes(valores['codigo_perfil_estrutural_externo'], "externo")
            perfil_estrutural_externo.calcular_quantidade(
                comprimento_real_perf_estrutural, valores['comprimento'], 
                valores['largura'], altura, distancia_entre_apoios, valores['repeticoes'],
                valores['quantidade_modulos'], valores['distancia_entre_maos_f'], False
            )
            linha_ant += 1
            eap_result.append(
                escrever_eap_insumos(perfil_estrutural_externo)
            )
            custo_total += perfil_estrutural_externo.preco()

    ########################## Calhas ############################
    calha = Calha(valores['codigo_calha'])
    calha.calcular_quantidade(comp_real, valores['largura'], valores['lateral_direita'],
        valores['lateral_esquerda'], valores['montante'], valores['jusante'], valores['repeticoes'])
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
        custo_total += quant_fech_calha * obj_fech_calha.custo01
            
    ########################## Rufos ############################
    rufo = Rufo(valores['codigo_rufo'])
    rufo.calcular_quantidade(comp_real, valores['largura'], valores['lateral_direita'],
        valores['lateral_esquerda'], valores['montante'], valores['jusante'], valores['repeticoes'])
    if rufo.quantidade != 0:
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(rufo)
        )
        custo_total += rufo.preco()

    ######################### Pintura #############################
    if not valores['aproveitar_estrutura']:
        if valores['quantidade_pintura'] == 0:
            pass
        else:
            objPintura = a11Insumos.objetos.get(
                codigo=valores['codigo_pintura'])
            linha_eap = escrever_linha_eap('', '', -1, valores['quantidade_pintura'], '', 0, 0, valores['codigo_pintura'])
            linha_ant += 1
            eap_result.append(linha_eap)
            custo_total += valores['quantidade_pintura'] * objPintura.custo01

    ######################### Motores ###########################
    # Se a estrutura for retrátil
    if estrutura_retratil:
        linha_eap = escrever_linha_eap('', '', -1, valores['quantMotor'], '', 0, 0, valores['codMotor'])
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += valores['quantMotor'] * a11Insumos.objetos.get(codigo=valores['codMotor']).custo01

        ######################### Suporte Motor #####################
        linha_eap = escrever_linha_eap('', '', -1, valores['quantMotor'], '', 0, 0, 14225)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += valores['quantMotor'] * a11Insumos.objetos.get(codigo=14225).custo01

        ######################### Cantoneiras #######################
        quantCantoneiras = 0
        larguraModulos = arrend_cima(
            valores['largura'] / valores['quantidade_modulos'], 0)
        if valores['quantidade_modulos'] == 1 and estrutura_retratil_direcao_comprimento:
            if valores['quantidade_modulos'] == valores['quantModMoveis']:
                if valores['largura'] >= 5:
                    # tem que ser sempre par esta divisão para a estrutura não ficar com um lado fazendo mais esforço
                    if (valores['largura']/3) % 2:
                        quantCantoneiras += 1
                    quantCantoneiras = (
                        valores['largura'] / 3) * 2 * valores['comprimento'] * 2
                else:
                    quantCantoneiras = 2 * 2 * valores['comprimento']
        elif valores['quantidade_modulos'] == 1 and estrutura_retratil_direcao_largura:
            if valores['quantidade_modulos'] == valores['quantModMoveis']:
                quantCantoneiras = 2 * 2 * valores['largura']
        else:
            if valores['quantidade_modulos'] > 1 and estrutura_retratil_direcao_largura:
                if valores['quantidade_modulos'] == valores['quantModMoveis']:
                    for i in arange(1, valores['quantidade_modulos'], 1):
                        if i == valores['quantidade_modulos']-1:
                            quantCantoneiras += larguraModulos*i + larguraModulos
                        else:
                            quantCantoneiras += (larguraModulos *
                                                i + larguraModulos)*2
                elif valores['quantidade_modulos'] > valores['quantModMoveis']:
                    for i in arange(valores['quantidade_modulos'] - valores['quantModMoveis']-1, valores['quantidade_modulos'], 1):
                        if i == (valores['quantidade_modulos']) - 1:
                            quantCantoneiras += larguraModulos*i + larguraModulos
                        else:
                            quantCantoneiras += 2 * \
                                (larguraModulos*i + larguraModulos)
            elif valores['quantidade_modulos'] > 1 and estrutura_retratil_direcao_comprimento:
                quantCantoneiras = (
                    (valores['quantidade_modulos'] * 2) - 1) * valores['comprimento'] / valores['quantidade_modulos'] * 2
        quantCantoneiras = tot_peca_juncao(quantCantoneiras, 6)
        # Se for roldana para 75mm não precisa de cantoneira
        if not valores['codRoldanas'] == 14219 or valores['codRoldanas'] == 14297:
            linha_eap = escrever_linha_eap(
                '', '', -1, quantCantoneiras, '', 0, 0, valores['codCantoneira'])
            linha_ant += 1
            eap_result.append(linha_eap)
            custo_total += quantCantoneiras * a11Insumos.objetos.get(codigo=valores['codCantoneira']).custo01

        ####################### Perfis Cantoneiras ####################
        linha_eap = escrever_linha_eap(
            '', '', -1, quantCantoneiras, '', 0, 0, valores['codPerfCant'])
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quantCantoneiras * a11Insumos.objetos.get(codigo=valores['codPerfCant']).custo01

        ####################### Roldanas ##############################
        roldana = Roldana(valores['codRoldanas'])
        roldana.calcular_quantidade(comp_real, valores['largura'], valores['direcMovimento'], valores['repeticoes'], valores['quantModMoveis'])
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
        custo_total += 10 * a11Insumos.objetos.get(codigo=6325).custo01

        ##################### Fita Isolante ###########################
        # Adicionar 1 fita isolante por padrão quando a estrutura for retrátil
        linha_eap = escrever_linha_eap(
            '', '', -1, 1, '', 0, 0, 6326)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += 1 * a11Insumos.objetos.get(codigo=6326).custo01
        
        #################### Parafuso Para Suporte do Motor ##########
        # Adicionar 4 parafusos por suporte do motor quando a estrutura for retrátil
        quant_parafuso_suporte = valores['quantMotor'] * 4
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_parafuso_suporte, '', 0, 0, 6327)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_parafuso_suporte * a11Insumos.objetos.get(codigo=6327).custo01
        
        #################### Porca Para Suporte do Motor ##########
        # Adicionar 4 porcas por suporte do motor quando a estrutura for retrátil
        linha_eap = escrever_linha_eap('', '', -1, quant_parafuso_suporte, '', 0, 0, 6328)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_parafuso_suporte * a11Insumos.objetos.get(codigo=6328).custo01

        ################## Arruelas Para Suporte do Motor #########
        # Adicionar 4 arruelas por suporte do motor quando a estrutura for retrátil
        linha_eap = escrever_linha_eap('', '', -1, quant_parafuso_suporte, '', 0, 0, 6329)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_parafuso_suporte * a11Insumos.objetos.get(codigo=6329).custo01

    else:
        pass

    if not valores['aproveitar_estrutura']:
        ####################### Discos de Corte ##############################
        disco_de_corte = DiscoCorte(6300)
        disco_de_corte.calcular_quantidade(comp_real, valores['largura'], distancia_entre_apoios, valores['repeticoes'])
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(disco_de_corte)
        )
        custo_total += disco_de_corte.preco()
        ####################### Eletrodos #######################
        eletrodo = Eletrodo(6302)
        eletrodo.calcular_quantidade(comp_real, valores['largura'], distancia_entre_apoios, valores['repeticoes'])
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(eletrodo)
        )
        custo_total += eletrodo.preco()
        ####################### Orelinhas #######################
        quant_orelinhas = calc_orelinhas(
            comp_real, valores['largura'], valores['repeticoes'])
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_orelinhas, '', 0, 0, 14217)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_orelinhas * a11Insumos.objetos.get(codigo=14217).custo01

        ####################### Parafusos 10 #######################
        quant_paraf_est = quant_orelinhas
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_paraf_est, '', 0, 0, 6307)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_paraf_est * a11Insumos.objetos.get(codigo=6307).custo01

        ####################### Bucha 10 #######################
        quant_bucha_est = quant_paraf_est
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_bucha_est, '', 0, 0, 6306)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_bucha_est * a11Insumos.objetos.get(codigo=6306).custo01

        ####################### Broca de Concreto #######################
        quant_broca_conc = 1
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_broca_conc, '', 0, 0, 6308)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_broca_conc * a11Insumos.objetos.get(codigo=6308).custo01

        ####################### Broca de Aço #######################
        quant_broca_aco = 1
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_broca_aco, '', 0, 0, 6309)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_broca_aco * a11Insumos.objetos.get(codigo=6309).custo01
    else:
        pass

    # Serralheiro
    if not valores['dias_serralheiro'] == 0 or not valores['quantidade_serralheiro'] == 0:
        serralheiros = 8 * valores['quantidade_serralheiro'] * valores['dias_serralheiro']
        linha_eap = escrever_linha_eap(
            '', '', -1, serralheiros, 'h', 0, 0, 1163)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += serralheiros * a11Insumos.objetos.get(codigo=1163).custo01
    # Auxiliar
    if not valores['dias_auxiliar'] == 0 or not valores['quantidade_auxiliar'] == 0:
        auxiliares = 8 * valores['quantidade_auxiliar'] * valores['dias_auxiliar']
        linha_eap = escrever_linha_eap(
            '', '', -1, auxiliares, 'h', 0, 0, 1152)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += auxiliares * a11Insumos.objetos.get(codigo=1152).custo01


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
