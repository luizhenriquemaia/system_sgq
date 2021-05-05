# Orçamentos de chapa de policarbonato
from math import asin, pi, sqrt
from decimal import *

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
    quant_orelinhas = arrend_cima(Decimal(2.5) * (comprimento + largura) * repeticoes / 1 , 0)
    quant_orelinhas = quant_orelinhas + 10 - quant_orelinhas % 10 if quant_orelinhas % 10 != 0 else quant_orelinhas
    return Decimal(quant_orelinhas)


############ Calculo de  Riscos e Bonificações ########################
def calc_riscos_bonificacoes(custo_total, dificuldade):
    riscos = custo_total * int(dificuldade) * Decimal(0.1)
    bonificacoes = (custo_total * Decimal(0.3)) + riscos
    return bonificacoes


################# Policarbonato Plano com Inclinação ################
#####################################################################
#####################################################################
def orc_poli_plano(prefEap, **valores):
    ################# Cálculos ###########################
    altura = valores['dados_dimensoes']['comprimento_cobertura'] * (valores['dados_dimensoes']['declividade_cobertura'] / 100)
    comp_real =  round(Decimal(sqrt(pow(valores['dados_dimensoes']['comprimento_cobertura'], 2) + pow(altura, 2))), 4)
    ##### Limite para não haver erro na hora de quantificar chapa #####
    ##### Até 2cm pode-se completar a chapa com fita #####
    if comp_real - valores['dados_dimensoes']['comprimento_cobertura'] <= 0.02:
            comp_real = valores['dados_dimensoes']['comprimento_cobertura']
    # definir booleans para ifs futuros
    perfil_uniao_igual_ao_arremate = True if valores['dados_policarbonato']['cod_perfil_uniao'] == valores['dados_policarbonato']['cod_perfil_arremate'] else False
    orcamento_com_chapa_compacta = True if a11Insumos.objetos.get(codigo=valores['dados_policarbonato']['cod_policarbonato']).catins_id == 55 else False
    comprimento_orcamento = comp_real
    largura_orcamento = valores['dados_dimensoes']['largura_cobertura']
    try: 
        if valores['dados_retratil']:
            estrutura_retratil = True
            quantidade_de_modulos = valores['dados_retratil']['quantidade_modulos']
    except KeyError:
        estrutura_retratil = False
        quantidade_de_modulos = 1
    if estrutura_retratil:
        estrutura_retratil_direcao_largura = True if valores['dados_retratil']['direcao_movimento'] == 1 else False
        estrutura_retratil_direcao_comprimento = True if valores['dados_retratil']['direcao_movimento'] == 0 else False
        # Tamanho do módulo da estrutura para cálculos
        if estrutura_retratil_direcao_comprimento:
            comprimento_orcamento = comp_real / quantidade_de_modulos
        else:
            largura_orcamento = valores['dados_dimensoes']['largura_cobertura'] / quantidade_de_modulos
    linha_ant = 0
    custo_total = 0
    desc_poli = a11Insumos.objetos.get(codigo=valores['dados_policarbonato']['cod_policarbonato']).descricao
    if orcamento_com_chapa_compacta:
        if valores['dados_dimensoes']['repeticoes_cobertura'] <= 1:
            if not estrutura_retratil:
                text_desc = f"Cobertura plana fixa de policarbonato compacto com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(comp_real):.2f}m e com {valores['dados_dimensoes']['declividade_cobertura']}% de inclinação utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"Cobertura plana retrátil de policarbonato compacto com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(comp_real):.2f}m e com {valores['dados_dimensoes']['declividade_cobertura']}% de inclinação utilizando {desc_poli}"
        else:
            if not estrutura_retratil:
                text_desc = f"{valores['dados_dimensoes']['repeticoes_cobertura']} Coberturas planas fixas de policarbonato compacto com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(comp_real):.2f}m e com {valores['dados_dimensoes']['declividade_cobertura']}% de inclinação utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"{valores['dados_dimensoes']['repeticoes_cobertura']} Coberturas planas retráteis de policarbonato compacto com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(comp_real):.2f}m e com {valores['dados_dimensoes']['declividade_cobertura']}% de inclinação utilizando {desc_poli}"
    else:
        if valores['dados_dimensoes']['repeticoes_cobertura'] <= 1:
            if not estrutura_retratil:
                text_desc = f"Cobertura plana fixa de policarbonato alveolar com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(comp_real):.2f}m e com {valores['dados_dimensoes']['declividade_cobertura']}% de inclinação utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"Cobertura plana retrátil de policarbonato alveolar com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(comp_real):.2f}m e com {valores['dados_dimensoes']['declividade_cobertura']}% de inclinação utilizando {desc_poli}"
        else:
            if not estrutura_retratil:
                text_desc = f"{valores['dados_dimensoes']['repeticoes_cobertura']} Coberturas planas fixas de policarbonato alveolar com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(comp_real):.2f}m e com {valores['dados_dimensoes']['declividade_cobertura']}% de inclinação utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"{valores['dados_dimensoes']['repeticoes_cobertura']} Coberturas planas retráteis de policarbonato alveolar com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(comp_real):.2f}m e com {valores['dados_dimensoes']['declividade_cobertura']}% de inclinação utilizando {desc_poli}"
    linha_eap = escrever_linha_eap(
        prefEap, text_desc, 5, f"{float(comp_real * valores['dados_dimensoes']['largura_cobertura'] * valores['dados_dimensoes']['repeticoes_cobertura']):.2f}", 'm²', 0, 0, 0)
    eap_result = [linha_eap]
    linha_ant += 1

    ##################### Entrega externa -> Policarbonato #####################
    text_desc = f"Policarbonato e acessórios"
    linha_eap = escrever_linha_eap(
        f'{prefEap}01.', text_desc, 3, 1, 'un', 1, 0, 0)
    linha_ant += 1
    eap_result.append(linha_eap)

    ##################### Chapas #############################
    chapa_policarbonato = ChapaPolicarbonato(valores['dados_policarbonato']['cod_policarbonato'])
    chapa_policarbonato.calc_poli_alveolar(
        comprimento_orcamento, largura_orcamento, valores['dados_dimensoes']['distancia_apoios_cobertura'], valores['dados_dimensoes']['repeticoes_cobertura'] * quantidade_de_modulos
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(chapa_policarbonato)
    )

    ##################### Perfil União ######################
    perfil_uniao = PerfilUniao(valores['dados_policarbonato']['cod_perfil_uniao'])
    perfil_uniao.calc_perfil_uniao(largura_orcamento, comprimento_orcamento, valores['dados_dimensoes']['distancia_apoios_cobertura'], 
        quantidade_de_modulos, valores['dados_dimensoes']['repeticoes_cobertura'], perfil_uniao_igual_ao_arremate
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(perfil_uniao)
    )

    ################# Perfil U ###########################
    perfil_u = PerfilU(valores['dados_policarbonato']['cod_perfil_u'])
    perfil_u.calc_perfil_u(largura_orcamento, valores['dados_dimensoes']['repeticoes_cobertura'], quantidade_de_modulos)
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(perfil_u)
    )

    ################# Perfil Arremate ####################
    if not orcamento_com_chapa_compacta and not perfil_uniao_igual_ao_arremate:
        perfil_arremate = PerfilArremate(valores['dados_policarbonato']['cod_perfil_arremate'])
        perfil_arremate.calc_perfil_arremate(
            comprimento_orcamento, 
            valores['dados_dimensoes']['repeticoes_cobertura'], 
            quantidade_de_modulos
        )
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(perfil_arremate)
        )

    ################# Perfil Guarnição ###################
    dist_apoios = conf_dist_apoios(
        chapa_policarbonato.espessura, 
        valores['dados_dimensoes']['distancia_apoios_cobertura'],
        1, 
        0, 
        orcamento_com_chapa_compacta
    )
    guarnicao = Guarnicao(valores['dados_policarbonato']['cod_guarnicao'])
    guarnicao.calc_perfil_guarnicao(
        largura_orcamento, 
        comprimento_orcamento, 
        dist_apoios,
        valores['dados_dimensoes']['repeticoes_cobertura'], 
        quantidade_de_modulos, 
        perfil_uniao_igual_ao_arremate
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(guarnicao)
    )

    ################# Perfil Gaxeta ####################
    gaxeta = Gaxeta(valores['dados_policarbonato']['cod_gaxeta'])
    gaxeta.calc_perfil_gaxeta(
        largura_orcamento, 
        comprimento_orcamento, 
        dist_apoios, 
        valores['dados_dimensoes']['repeticoes_cobertura'], 
        quantidade_de_modulos, 
        perfil_uniao_igual_ao_arremate
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(gaxeta)
    )

    ################# Fita Alumínio ####################
    if not orcamento_com_chapa_compacta:
        fita_aluminio = FitaAluminio(valores['dados_policarbonato']['cod_fita_aluminio'])
        fita_aluminio.calcular_quantidade(valores['dados_dimensoes']['largura_cobertura'], valores['dados_dimensoes']['repeticoes_cobertura'])
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(fita_aluminio)
        )
        
        ################# Fita Vent Tape ###################
        fita_vent = FitaVentTape(valores['dados_policarbonato']['cod_fita_vent'])
        fita_vent.calcular_quantidade(valores['dados_dimensoes']['largura_cobertura'], valores['dados_dimensoes']['repeticoes_cobertura'])
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
            comp_real, valores['dados_dimensoes']['repeticoes_cobertura'], quantidade_de_modulos, Decimal(round(0.3, 2))
        )
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(parafuso_arremate)
        )

    ############# PARAFUSO UNIÃO #############
    if chapa_policarbonato.espessura <= 6:
        # Parafuso união -> trapézio chapa 06 >> 12-14x1.1/2"
        if valores['dados_policarbonato']['cod_perfil_uniao'] == 10416:
            cod_parafuso = 14130
            dist_parafusos = round(Decimal(0.3), 3)
        # Parafuso união -> barra chata chapa 06 >> 12-14x1.1/4"
        else:
            cod_parafuso = 14128
            dist_parafusos = round(Decimal(0.2), 3)
    else:
        # Parafuso união -> trapezio chapa 10 >> 12-14x2"
        if valores['dados_policarbonato']['cod_perfil_uniao'] == 10416:
            cod_parafuso = 14129
            dist_parafusos = round(Decimal(0.3), 3)
        # Parafuso união -> barra chata chapa 10 >> 12-14x1.1/2"
        else:
            cod_parafuso = 14130
            dist_parafusos = round(Decimal(0.2), 3)
    parafuso_uniao = ParafusosPolicarbonato(cod_parafuso)
    parafuso_uniao.calc_parafuso_uniao(
        valores['dados_dimensoes']['largura_cobertura'], 
        valores['dados_dimensoes']['distancia_apoios_cobertura'], 
        comp_real, 
        valores['dados_dimensoes']['repeticoes_cobertura'], 
        dist_parafusos, 
        perfil_uniao_igual_ao_arremate
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(parafuso_uniao)
    )

    ################# Selante ###################
    selante = Selante(valores['dados_policarbonato']['cod_selante'])
    selante.calcular_quantidade(valores['dados_dimensoes']['largura_cobertura'], comp_real, valores['dados_dimensoes']['repeticoes_cobertura'], estrutura_retratil)
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
        chapa_policarbonato.espessura, valores['dados_dimensoes']['distancia_apoios_cobertura'], 1, 0, orcamento_com_chapa_compacta)
    if not valores['dados_estrutura']['aproveitar_estrutura']:
        if valores['dados_estrutura']['cod_perfil_estrutural_externo'] == valores['dados_estrutura']['cod_perfil_estrutural_interno']:
            perfil_estrutural = PerfisEstruturaisIguais(valores['dados_estrutura']['cod_perfil_estrutural_externo'])
            perfil_estrutural.calcular_quantidade(
                largura_orcamento, 
                valores['dados_dimensoes']['comprimento_cobertura'],
                comprimento_orcamento,
                altura, 
                distApoios, 
                valores['dados_dimensoes']['repeticoes_cobertura'],
                quantidade_de_modulos, 
                valores['dados_dimensoes']['quantidade_maos_francesas']
            )
            linha_ant += 1
            eap_result.append(
                escrever_eap_insumos(perfil_estrutural)
            )
            custo_total += perfil_estrutural.preco()
        else:
            perfil_estrutural_interno = PerfisEstruturaisDiferentes(valores['dados_estrutura']['cod_perfil_estrutural_interno'], "interno")
            perfil_estrutural_interno.calcular_quantidade(
                largura_orcamento,
                valores['dados_dimensoes']['comprimento_cobertura'], 
                comprimento_orcamento, 
                altura, 
                distApoios, 
                valores['dados_dimensoes']['repeticoes_cobertura'],
                quantidade_de_modulos, 
                valores['dados_dimensoes']['quantidade_maos_francesas'], 
                False
            )
            linha_ant += 1
            eap_result.append(
                escrever_eap_insumos(perfil_estrutural_interno)
            )
            custo_total += perfil_estrutural_interno.preco()
            perfil_estrutural_externo = PerfisEstruturaisDiferentes(valores['dados_estrutura']['cod_perfil_estrutural_externo'], "externo")
            perfil_estrutural_externo.calcular_quantidade(
                largura_orcamento, 
                valores['dados_dimensoes']['comprimento_cobertura'], 
                comprimento_orcamento, 
                altura, 
                distApoios, 
                valores['dados_dimensoes']['repeticoes_cobertura'],
                quantidade_de_modulos, 
                valores['dados_dimensoes']['quantidade_maos_francesas'], 
                False
            )
            linha_ant += 1
            eap_result.append(
                escrever_eap_insumos(perfil_estrutural_externo)
            )
            custo_total += perfil_estrutural_externo.preco()

    ########################## Calhas ############################
    calha = Calha(valores['dados_estrutura']['cod_chapa_calha'])
    calha.calcular_quantidade(
        comp_real, 
        valores['dados_dimensoes']['largura_cobertura'], 
        valores['dados_estrutura']['lateral_direita'],
        valores['dados_estrutura']['lateral_esquerda'], 
        valores['dados_estrutura']['montante'], 
        valores['dados_estrutura']['jusante'], 
        valores['dados_dimensoes']['repeticoes_cobertura']
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
        custo_total += quant_fech_calha * obj_fech_calha.custo01
            
    ########################## Rufos ############################
    rufo = Rufo(valores['dados_estrutura']['cod_chapa_rufo'])
    rufo.calcular_quantidade(
        comp_real, 
        valores['dados_dimensoes']['largura_cobertura'], 
        valores['dados_estrutura']['lateral_direita'],
        valores['dados_estrutura']['lateral_esquerda'], 
        valores['dados_estrutura']['montante'], 
        valores['dados_estrutura']['jusante'], 
        valores['dados_dimensoes']['repeticoes_cobertura']
    )
    if rufo.quantidade != 0:
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(rufo)
        )
        custo_total += rufo.preco()

    ######################### Pintura #############################
    if not valores['dados_estrutura']['aproveitar_estrutura']:
        if valores['dados_estrutura']['quantidade_pintura'] == 0:
            pass
        else:
            objPintura = a11Insumos.objetos.get(
                codigo=valores['dados_estrutura']['cod_pintura'])
            linha_eap = escrever_linha_eap('', '', -1, valores['dados_estrutura']['quantidade_pintura'], '', 0, 0, valores['dados_estrutura']['cod_pintura'])
            linha_ant += 1
            eap_result.append(linha_eap)
            custo_total += valores['dados_estrutura']['quantidade_pintura'] * objPintura.custo01

    ######################### Motores ###########################
    # Se a estrutura for retrátil
    if estrutura_retratil:
        linha_eap = escrever_linha_eap('', '', -1, valores['dados_retratil']['quantidade_motor'], '', 0, 0, valores['dados_retratil']['cod_motor'])
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += valores['dados_retratil']['quantidade_motor'] * a11Insumos.objetos.get(codigo=valores['dados_retratil']['cod_motor']).custo01

        ######################### Suporte Motor #####################
        linha_eap = escrever_linha_eap('', '', -1, valores['dados_retratil']['quantidade_motor'], '', 0, 0, 14225)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += valores['dados_retratil']['quantidade_motor'] * a11Insumos.objetos.get(codigo=14225).custo01

        ######################### Cantoneiras #######################
        quantCantoneiras = 0
        larguraModulos = arrend_cima(
            valores['dados_dimensoes']['largura_cobertura'] / quantidade_de_modulos, 0)
        if quantidade_de_modulos == 1 and estrutura_retratil_direcao_comprimento:
            if quantidade_de_modulos == valores['dados_retratil']['quantidade_modulos_moveis']:
                if valores['dados_dimensoes']['largura_cobertura'] >= 5:
                    # tem que ser sempre par esta divisão para a estrutura não ficar com um lado fazendo mais esforço
                    if (valores['dados_dimensoes']['largura_cobertura']/3) % 2:
                        quantCantoneiras += 1
                    quantCantoneiras = (
                        valores['dados_dimensoes']['largura_cobertura'] / 3) * 2 * valores['dados_dimensoes']['comprimento_cobertura'] * 2
                else:
                    quantCantoneiras = 2 * 2 * valores['dados_dimensoes']['comprimento_cobertura']
        elif quantidade_de_modulos == 1 and estrutura_retratil_direcao_largura:
            if quantidade_de_modulos == valores['dados_retratil']['quantidade_modulos_moveis']:
                quantCantoneiras = 2 * 2 * valores['dados_dimensoes']['largura_cobertura']
        else:
            if quantidade_de_modulos > 1 and estrutura_retratil_direcao_largura:
                if quantidade_de_modulos == valores['dados_retratil']['quantidade_modulos_moveis']:
                    for i in arange(1, quantidade_de_modulos, 1):
                        if i == quantidade_de_modulos-1:
                            quantCantoneiras += larguraModulos*i + larguraModulos
                        else:
                            quantCantoneiras += (larguraModulos *
                                                i + larguraModulos)*2
                elif quantidade_de_modulos > valores['dados_retratil']['quantidade_modulos_moveis']:
                    for i in arange(quantidade_de_modulos - valores['dados_retratil']['quantidade_modulos_moveis']-1, quantidade_de_modulos, 1):
                        if i == (quantidade_de_modulos) - 1:
                            quantCantoneiras += larguraModulos*i + larguraModulos
                        else:
                            quantCantoneiras += 2 * \
                                (larguraModulos*i + larguraModulos)
            elif quantidade_de_modulos > 1 and estrutura_retratil_direcao_comprimento:
                quantCantoneiras = (
                    (quantidade_de_modulos * 2) - 1) * valores['dados_dimensoes']['comprimento_cobertura'] / quantidade_de_modulos * 2
        quantCantoneiras = Decimal(tot_peca_juncao(quantCantoneiras, 6))
        # Se for rolete de tecnil não precisa de cantoneira
        if not valores['dados_retratil']['cod_roldana'] == 14219 or valores['dados_retratil']['cod_roldana'] == 14297:
            linha_eap = escrever_linha_eap(
                '', '', -1, quantCantoneiras, '', 0, 0, valores['dados_retratil']['cod_cantoneira'])
            linha_ant += 1
            eap_result.append(linha_eap)
            custo_total += quantCantoneiras * a11Insumos.objetos.get(codigo=valores['dados_retratil']['cod_cantoneira']).custo01

        ####################### Perfis Cantoneiras ####################
        linha_eap = escrever_linha_eap(
            '', '', -1, quantCantoneiras, '', 0, 0, valores['dados_retratil']['cod_perfil_cantoneira'])
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quantCantoneiras * a11Insumos.objetos.get(codigo=valores['dados_retratil']['cod_perfil_cantoneira']).custo01

        ####################### Roldanas ##############################
        roldana = Roldana(valores['dados_retratil']['cod_roldana'])
        roldana.calcular_quantidade(
            comprimento_orcamento, 
            largura_orcamento,
            valores['dados_retratil']['direcao_movimento'], 
            valores['dados_dimensoes']['repeticoes_cobertura'], 
            valores['dados_retratil']['quantidade_modulos_moveis']
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
        quant_parafuso_suporte = valores['dados_retratil']['quantidade_motor'] * 4
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

    if not valores['dados_estrutura']['aproveitar_estrutura']:
        ####################### Discos de Corte ##############################
        disco_de_corte = DiscoCorte(6300)
        disco_de_corte.calcular_quantidade(
            comprimento_orcamento, 
            largura_orcamento,
            distApoios, 
            valores['dados_dimensoes']['repeticoes_cobertura']
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
            valores['dados_dimensoes']['repeticoes_cobertura']
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
            valores['dados_dimensoes']['repeticoes_cobertura']
        )
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
    if not int(valores['dados_estrutura']['dias_serralheiro']) == 0 or not int(valores['dados_estrutura']['quantidade_serralheiro']) == 0:
        serralheiros = 8 * valores['dados_estrutura']['quantidade_serralheiro'] * valores['dados_estrutura']['dias_serralheiro']
        linha_eap = escrever_linha_eap(
            '', '', -1, serralheiros, 'h', 0, 0, 1163)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += serralheiros * a11Insumos.objetos.get(codigo=1163).custo01
    # Auxiliar
    if not int(valores['dados_estrutura']['dias_auxiliar']) == 0 or not int(valores['dados_estrutura']['quantidade_auxiliar']) == 0:
        auxiliares = 8 * valores['dados_estrutura']['quantidade_auxiliar'] * valores['dados_estrutura']['dias_auxiliar']
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
    bonificacoes = calc_riscos_bonificacoes(custo_total, valores['dados_estrutura']['dificuldade'])
    linha_eap = escrever_linha_eap(
        '', '', -1, bonificacoes, '', 0, 0, 1)
    linha_ant += 1
    eap_result.append(linha_eap)
    return eap_result


def orc_poli_curvo(prefEap, **valores):
    ################# Cálculos ###########################
    raioCirculo = (pow(valores['dados_dimensoes']['corda_cobertura'] / 2, 2) + pow(valores['dados_dimensoes']['flecha_cobertura'], 2)) / (2 * valores['dados_dimensoes']['flecha_cobertura'])
    anguloCurva = Decimal(asin((valores['dados_dimensoes']['corda_cobertura'] / 2) / raioCirculo))
    arcoCurva = (anguloCurva * 2) * raioCirculo
    if arcoCurva - valores['dados_dimensoes']['corda_cobertura'] <= 0.02:
        arcoCurva = valores['dados_dimensoes']['corda_cobertura']
    else:
        pass
    linha_ant = 0
    custo_total = 0
    # definir booleans para ifs futuros
    perfil_uniao_igual_ao_arremate = True if valores['dados_policarbonato']['cod_perfil_uniao'] == valores['dados_policarbonato']['cod_perfil_arremate'] else False
    orcamento_com_chapa_compacta = True if a11Insumos.objetos.get(codigo=valores['dados_policarbonato']['cod_policarbonato']).catins_id == 55 else False
    try: 
        if valores['dados_retratil']:
            estrutura_retratil = True
            quantidade_de_modulos = valores['dados_retratil']['quantidade_modulos']
    except KeyError:
        estrutura_retratil = False
        quantidade_de_modulos = 1
    largura_orcamento = valores['dados_dimensoes']['largura_cobertura']
    comprimento_orcamento = arcoCurva
    if estrutura_retratil:
        estrutura_retratil_direcao_largura = True if valores['dados_retratil']['direcao_movimento'] == 1 else False
        estrutura_retratil_direcao_comprimento = True if valores['dados_retratil']['direcao_movimento'] == 0 else False
        # Tamanho do módulo da estrutura para cálculos
        if estrutura_retratil_direcao_comprimento:
            comprimento_orcamento = arcoCurva / quantidade_de_modulos
        else:
            largura_orcamento = valores['dados_dimensoes']['largura_cobertura'] / quantidade_de_modulos
    desc_poli = a11Insumos.objetos.get(codigo=valores['dados_policarbonato']['cod_policarbonato']).descricao
    if orcamento_com_chapa_compacta:
        if valores['dados_dimensoes']['repeticoes_cobertura'] <= 1:
            if not estrutura_retratil:
                text_desc = f"Cobertura curva fixa de policarbonato compacto com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"Cobertura curva retrátil de policarbonato compacto com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
        else:
            if not estrutura_retratil:
                text_desc = f"{valores['dados_dimensoes']['repeticoes_cobertura']} Coberturas curvas fixas de policarbonato compacto com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"{valores['dados_dimensoes']['repeticoes_cobertura']} Coberturas curvas retráteis de policarbonato compacto com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
    else:
        if valores['dados_dimensoes']['repeticoes_cobertura'] <= 1:
            if not estrutura_retratil:
                text_desc = f"Cobertura curva fixa de policarbonato alveolar com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"Cobertura curva retrátil de policarbonato alveolar com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
        else:
            if not estrutura_retratil:
                text_desc = f"{valores['dados_dimensoes']['repeticoes_cobertura']} Coberturas curvas fixas de policarbonato alveolar com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
            elif estrutura_retratil:
                text_desc = f"{valores['dados_dimensoes']['repeticoes_cobertura']} Coberturas curvas retráteis de policarbonato alveolar com dimensões {valores['dados_dimensoes']['largura_cobertura']:.2f} x {(arcoCurva):.2f}m utilizando {desc_poli}"
    linha_eap = escrever_linha_eap(
        prefEap, text_desc, 5, f"{float(arcoCurva * valores['dados_dimensoes']['largura_cobertura'] * valores['dados_dimensoes']['repeticoes_cobertura']):.2f}", 'm²', 0, 0, 0)
    eap_result = [linha_eap]
    linha_ant += 1

    ##################### Entrega externa -> Policarbonato #####################
    text_desc = f"Policarbonato e acessórios"
    linha_eap = escrever_linha_eap(
        f'{prefEap}01.', text_desc, 3, 1, 'un', 1, 0, 0)
    linha_ant += 1
    eap_result.append(linha_eap)

    ##################### Chapas #############################
    chapa_policarbonato = ChapaPolicarbonato(valores['dados_policarbonato']['cod_policarbonato'])
    chapa_policarbonato.calc_poli_alveolar(
        comprimento_orcamento, 
        largura_orcamento, 
        valores['dados_dimensoes']['distancia_apoios_cobertura'], 
        valores['dados_dimensoes']['repeticoes_cobertura'] * quantidade_de_modulos
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(chapa_policarbonato)
    )

    ##################### Perfil União ######################
    perfil_uniao = PerfilUniao(valores['dados_policarbonato']['cod_perfil_uniao'])
    perfil_uniao.calc_perfil_uniao(
        largura_orcamento, 
        comprimento_orcamento,
        valores['dados_dimensoes']['distancia_apoios_cobertura'],
        quantidade_de_modulos, 
        valores['dados_dimensoes']['repeticoes_cobertura'], 
        perfil_uniao_igual_ao_arremate
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(perfil_uniao)
    )

    ################# Perfil U ###########################
    perfil_u = PerfilU(valores['dados_policarbonato']['cod_perfil_u'])
    perfil_u.calc_perfil_u(
        largura_orcamento, 
        valores['dados_dimensoes']['repeticoes_cobertura'], 
        quantidade_de_modulos
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(perfil_u)
    )

    ################# Perfil Arremate ####################
    if not orcamento_com_chapa_compacta and not perfil_uniao_igual_ao_arremate:
        perfil_arremate = PerfilArremate(valores['dados_policarbonato']['cod_perfil_arremate'])
        perfil_arremate.calc_perfil_arremate(
            comprimento_orcamento, 
            valores['dados_dimensoes']['repeticoes_cobertura'], 
            quantidade_de_modulos
        )
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(perfil_arremate)
        )
    
    ################# Perfil Guarnição ###################
    dist_apoios = conf_dist_apoios(
        chapa_policarbonato.espessura,
        valores['dados_dimensoes']['distancia_apoios_cobertura'], 
        2, 
        raioCirculo, 
        orcamento_com_chapa_compacta
    )
    guarnicao = Guarnicao(valores['dados_policarbonato']['cod_guarnicao'])
    guarnicao.calc_perfil_guarnicao(
        largura_orcamento, 
        comprimento_orcamento, 
        dist_apoios,
        valores['dados_dimensoes']['repeticoes_cobertura'], 
        quantidade_de_modulos, 
        perfil_uniao_igual_ao_arremate
    )
    linha_ant += 1
    eap_result.append(
        escrever_eap_insumos(guarnicao)
    )

    ################# Perfil Gaxeta ####################
    gaxeta = Gaxeta(valores['dados_policarbonato']['cod_gaxeta'])
    gaxeta.calc_perfil_gaxeta(
        largura_orcamento, 
        comprimento_orcamento, 
        dist_apoios, 
        valores['dados_dimensoes']['repeticoes_cobertura'], 
        quantidade_de_modulos, 
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
        fita_vent = FitaVentTape(valores['dados_policarbonato']['cod_fita_vent'])
        fita_vent.calcular_quantidade(
            2 * valores['dados_dimensoes']['largura_cobertura'], valores['dados_dimensoes']['repeticoes_cobertura'])
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(fita_vent)
        )

    ################# Selante ###################
    selante = Selante(valores['dados_policarbonato']['cod_selante'])
    selante.calcular_quantidade(
        largura_orcamento, 
        comprimento_orcamento, 
        valores['dados_dimensoes']['repeticoes_cobertura'] * quantidade_de_modulos, 
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
            valores['dados_dimensoes']['repeticoes_cobertura'], 
            quantidade_de_modulos, 
            Decimal(round(0.3, 2))
        )
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(parafuso_arremate)
        )

    ############# PARAFUSO UNIÃO #############
    if chapa_policarbonato.espessura <= 6:
        # Parafuso união -> trapézio chapa 06 >> 12-14x1.1/2"
        if valores['dados_policarbonato']['cod_perfil_uniao'] == 10416:
            cod_parafuso = 14130
            dist_parafusos = Decimal(round(0.3, 2))
        # Parafuso união -> barra chata chapa 06 >> 12-14x1.1/4"
        else:
            cod_parafuso = 14128
            dist_parafusos = Decimal(round(0.2, 2))
    else:
        # Parafuso união -> trapezio chapa 10 >> 12-14x2"
        if valores['dados_policarbonato']['cod_perfil_uniao'] == 10416:
            cod_parafuso = 14129
            dist_parafusos = Decimal(round(0.3, 2))
        # Parafuso união -> barra chata chapa 10 >> 12-14x1.1/2"
        else:
            cod_parafuso = 14130
            dist_parafusos = Decimal(round(0.2, 2))

    parafuso_uniao = ParafusosPolicarbonato(cod_parafuso)
    parafuso_uniao.calc_parafuso_uniao(
        largura_orcamento, 
        valores['dados_dimensoes']['distancia_apoios_cobertura'],
        comprimento_orcamento, 
        valores['dados_dimensoes']['repeticoes_cobertura'] * quantidade_de_modulos, 
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
        chapa_policarbonato.espessura, valores['dados_dimensoes']['distancia_apoios_cobertura'], 2, raioCirculo, orcamento_com_chapa_compacta)
    if not valores['dados_estrutura']['aproveitar_estrutura']:
        if valores['dados_estrutura']['cod_perfil_estrutural_externo'] == valores['dados_estrutura']['cod_perfil_estrutural_interno']:
            perfil_estrutural = PerfisEstruturaisIguais(valores['dados_estrutura']['cod_perfil_estrutural_externo'])
            perfil_estrutural.calcular_quantidade(
                largura_orcamento, 
                valores['dados_dimensoes']['corda_cobertura'],
                comprimento_orcamento + Decimal(0.2),
                valores['dados_dimensoes']['flecha_cobertura'],
                distApoios, 
                valores['dados_dimensoes']['repeticoes_cobertura'], 
                quantidade_de_modulos, 
                valores['dados_dimensoes']['quantidade_maos_francesas']
            )
            linha_ant += 1
            eap_result.append(
                escrever_eap_insumos(perfil_estrutural)
            )
            custo_total += perfil_estrutural.preco()
        else:
            perfil_estrutural_interno = PerfisEstruturaisDiferentes(
                valores['dados_estrutura']['cod_perfil_estrutural_interno'], "interno")
            perfil_estrutural_interno.calcular_quantidade(
                largura_orcamento, 
                valores['dados_dimensoes']['corda_cobertura'],
                comprimento_orcamento + Decimal(0.2),
                valores['dados_dimensoes']['flecha_cobertura'], 
                distApoios, 
                valores['dados_dimensoes']['repeticoes_cobertura'], 
                quantidade_de_modulos, 
                valores['dados_dimensoes']['quantidade_maos_francesas'], 
                True
            )
            linha_ant += 1
            eap_result.append(
                escrever_eap_insumos(perfil_estrutural_interno)
            )
            custo_total += perfil_estrutural_interno.preco()
            perfil_estrutural_externo = PerfisEstruturaisDiferentes(
                valores['dados_estrutura']['cod_perfil_estrutural_externo'], 
                "externo"
            )
            perfil_estrutural_externo.calcular_quantidade(
                largura_orcamento, 
                valores['dados_dimensoes']['corda_cobertura'],
                comprimento_orcamento + Decimal(0.2), 
                valores['dados_dimensoes']['flecha_cobertura'], 
                distApoios, 
                valores['dados_dimensoes']['repeticoes_cobertura'], 
                quantidade_de_modulos, 
                valores['dados_dimensoes']['quantidade_maos_francesas'], 
                True
            )
            linha_ant += 1
            eap_result.append(
                escrever_eap_insumos(perfil_estrutural_externo)
            )
            custo_total += perfil_estrutural_externo.preco()
    
    
    ########################## Calhas ############################
    calha = Calha(valores['dados_estrutura']['cod_chapa_calha'])
    calha.calcular_quantidade(
        valores['dados_dimensoes']['corda_cobertura'], 
        valores['dados_dimensoes']['largura_cobertura'], 
        valores['dados_estrutura']['lateral_direita'],
        valores['dados_estrutura']['lateral_esquerda'], 
        valores['dados_estrutura']['montante'], 
        valores['dados_estrutura']['jusante'], 
        valores['dados_dimensoes']['repeticoes_cobertura']
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
        custo_total += quant_fech_calha * obj_fech_calha.custo01

    ########################## Rufos ############################
    rufo = Rufo(valores['dados_estrutura']['cod_chapa_rufo'])
    rufo.calcular_quantidade(
        valores['dados_dimensoes']['corda_cobertura'], 
        valores['dados_dimensoes']['largura_cobertura'], 
        valores['dados_estrutura']['lateral_direita'],
        valores['dados_estrutura']['lateral_esquerda'], 
        valores['dados_estrutura']['montante'], 
        valores['dados_estrutura']['jusante'], 
        valores['dados_dimensoes']['repeticoes_cobertura']
    )
    if rufo.quantidade != 0:
        linha_ant += 1
        eap_result.append(
            escrever_eap_insumos(rufo)
        )
        custo_total += rufo.preco()

    #################### Calandrar Material ######################
    # arcoCurva + 0.20 -> perde 20cm de metalon na calandra
    if valores['dados_estrutura']['aproveitar_estrutura'] == False:
        quantidade_de_apoios_calandra = Decimal(arrend_cima(round(largura_orcamento / distApoios, 5), 0) + 1)
        quantCalandra = Decimal(arrend_cima(quantidade_de_apoios_calandra * (
                        comprimento_orcamento + Decimal(0.20)) * valores['dados_dimensoes']['repeticoes_cobertura'] * quantidade_de_modulos, 0))
        objCalandra = a11Insumos.objetos.get(codigo=valores['dados_estrutura_curva']['cod_calandra'])
        linha_eap = escrever_linha_eap(f'{prefEap}01.02.04.', f"{quantCalandra} m de {objCalandra.descricao}",
                                -1, quantCalandra, 'm', 2, 21, valores['dados_estrutura_curva']['cod_calandra'])
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quantCalandra * objCalandra.custo01

    ######################### Pintura #############################
    if valores['dados_estrutura']['aproveitar_estrutura'] == False:
        if valores['dados_estrutura']['quantidade_pintura'] == 0:
            pass
        else:
            objPintura = a11Insumos.objetos.get(codigo=valores['dados_estrutura']['cod_pintura'])
            linha_eap = escrever_linha_eap('', '', -1, valores['dados_estrutura']['quantidade_pintura'], '', 0, 0, valores['dados_estrutura']['cod_pintura'])
            linha_ant += 1
            eap_result.append(linha_eap)
            custo_total += valores['dados_estrutura']['quantidade_pintura'] * objPintura.custo01

    ######################### Motores ###########################
    if estrutura_retratil:
        linha_eap = escrever_linha_eap(
            '', '', -1, valores['dados_retratil']['quantidade_motor'], '', 0, 0, valores['dados_retratil']['cod_motor'])
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += valores['dados_retratil']['quantidade_motor'] * a11Insumos.objetos.get(codigo=valores['dados_retratil']['cod_motor']).custo01

        ######################### Suporte Motor #####################
        linha_eap = escrever_linha_eap('', '', -1, valores['dados_retratil']['quantidade_motor'], '', 0, 0, 14225)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += valores['dados_retratil']['quantidade_motor'] * a11Insumos.objetos.get(codigo=14225).custo01

        ######################### Cantoneiras #######################
        quantCantoneiras = 0
        larguraModulos = arrend_cima(valores['dados_dimensoes']['largura_cobertura']/quantidade_de_modulos, 0)
        if quantidade_de_modulos == 1 and estrutura_retratil_direcao_comprimento:
            if quantidade_de_modulos == valores['dados_retratil']['quantidade_modulos_moveis']:
                if valores['dados_dimensoes']['largura_cobertura'] >= 5:
                    # tem que ser sempre par esta divisão para a estrutura não ficar com um lado fazendo mais esforço
                    if (valores['dados_dimensoes']['largura_cobertura']/3)%2:
                        quantCantoneiras += 1
                    quantCantoneiras = (valores['dados_dimensoes']['largura_cobertura']/3)*2*comprimento_orcamento*2
                else:
                    quantCantoneiras = 2*valores['comprimento']
        elif quantidade_de_modulos == 1 and estrutura_retratil_direcao_largura:
            if quantidade_de_modulos == valores['dados_retratil']['quantidade_modulos_moveis']:
                quantCantoneiras = valores['dados_dimensoes']['largura_cobertura']*2
        else:
            if quantidade_de_modulos > 1 and estrutura_retratil_direcao_largura:
                if quantidade_de_modulos == valores['dados_retratil']['quantidade_modulos_moveis']:
                    for i in arange(1, quantidade_de_modulos, 1):
                        if i == quantidade_de_modulos - 1:
                            if i == 1:
                                quantCantoneiras += 2 * (larguraModulos * i + larguraModulos)
                            else:
                                quantCantoneiras += larguraModulos * i + larguraModulos
                        else:
                            quantCantoneiras += (larguraModulos*i + larguraModulos) * 2
                elif quantidade_de_modulos > valores['dados_retratil']['quantidade_modulos_moveis']:
                    for i in arange(quantidade_de_modulos - valores['dados_retratil']['quantidade_modulos_moveis'], quantidade_de_modulos, 1):
                        if i == (quantidade_de_modulos) - 1:
                            if i == 1:
                                quantCantoneiras += 2 * (larguraModulos * i + larguraModulos)
                            else:
                                quantCantoneiras += larguraModulos * i + larguraModulos
                        else:
                            quantCantoneiras += 2 * (larguraModulos * i + larguraModulos)
            elif quantidade_de_modulos > 1 and estrutura_retratil_direcao_comprimento:
                quantCantoneiras = ((quantidade_de_modulos*2)-1)*comprimento_orcamento*2
        quantCantoneiras = Decimal(tot_peca_juncao(quantCantoneiras, 6))
        # Se for roldana para 75mm não precisa de cantoneira
        if not valores['dados_retratil']['cod_roldana'] == 14219 and not valores['dados_retratil']['cod_roldana'] == 14297:
            linha_eap = escrever_linha_eap(
                '', '', -1, quantCantoneiras, '', 0, 0, valores['dados_retratil']['cod_cantoneira'])
            linha_ant += 1
            eap_result.append(linha_eap)
            custo_total += quantCantoneiras * a11Insumos.objetos.get(codigo=valores['dados_retratil']['cod_cantoneira']).custo01

        ####################### Perfis Cantoneiras ####################
        linha_eap = escrever_linha_eap(
            '', '', -1, quantCantoneiras, '', 0, 0, valores['dados_retratil']['cod_perfil_cantoneira'])
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quantCantoneiras * a11Insumos.objetos.get(codigo=valores['dados_retratil']['cod_perfil_cantoneira']).custo01

        ####################### Roldanas ##############################
        roldana = Roldana(valores['dados_retratil']['cod_roldana'])
        roldana.calcular_quantidade(
            comprimento_orcamento, 
            largura_orcamento, 
            valores['dados_retratil']['direcao_movimento'], 
            valores['dados_dimensoes']['repeticoes_cobertura'], 
            valores['dados_retratil']['quantidade_modulos_moveis']
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
        custo_total += 10 * a11Insumos.objetos.get(codigo=6325).custo01

        ##################### Fita Isolante ###########################
        # Adicionar 1 fita isolante por padrão quando a estrutura for retrátil
        linha_eap = escrever_linha_eap('', '', -1, 1, '', 0, 0, 6326)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += 1 * a11Insumos.objetos.get(codigo=6326).custo01

        #################### Parafuso Para Suporte do Motor ##########
        # Adicionar 4 parafusos por suporte do motor quando a estrutura for retrátil
        quant_parafuso_suporte = valores['dados_retratil']['quantidade_motor'] * 4
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_parafuso_suporte, '', 0, 0, 6327)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_parafuso_suporte * a11Insumos.objetos.get(codigo=6327).custo01

        #################### Porca Para Suporte do Motor ##########
        # Adicionar 4 porcas por suporte do motor quando a estrutura for retrátil
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_parafuso_suporte, '', 0, 0, 6328)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_parafuso_suporte * a11Insumos.objetos.get(codigo=6328).custo01

        ################## Arruelas Para Suporte do Motor #########
        # Adicionar 4 arruelas por suporte do motor quando a estrutura for retrátil
        linha_eap = escrever_linha_eap(
            '', '', -1, quant_parafuso_suporte, '', 0, 0, 6329)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_parafuso_suporte * a11Insumos.objetos.get(codigo=6329).custo01
    else:
        pass

    if valores['dados_estrutura']['aproveitar_estrutura'] == False:
        ####################### Discos de Corte ##############################
        disco_de_corte = DiscoCorte(6300)
        disco_de_corte.calcular_quantidade(
            comprimento_orcamento, 
            largura_orcamento, 
            distApoios, 
            valores['dados_dimensoes']['repeticoes_cobertura']
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
            valores['dados_dimensoes']['repeticoes_cobertura']
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
            valores['dados_dimensoes']['repeticoes_cobertura']
        )
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
            '', '',  -1, quant_broca_aco, '', 0, 0, 6309)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += quant_broca_aco * a11Insumos.objetos.get(codigo=6309).custo01
    else:
        pass

    # Serralheiro
    if not valores['dados_estrutura']['dias_serralheiro'] == 0 or not valores['dados_estrutura']['quantidade_serralheiro'] == 0:
        serralheiros = 8 * \
            valores['dados_estrutura']['quantidade_serralheiro'] * valores['dados_estrutura']['dias_serralheiro']
        linha_eap = escrever_linha_eap(
            '', '', -1, serralheiros, '', 0, 0, 1163)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += serralheiros * a11Insumos.objetos.get(codigo=1163).custo01
    # Auxiliar
    if not valores['dados_estrutura']['dias_auxiliar'] == 0 or not valores['dados_estrutura']['quantidade_auxiliar'] == 0:
        auxiliares = 8 * valores['dados_estrutura']['quantidade_auxiliar'] * valores['dados_estrutura']['dias_auxiliar']
        linha_eap = escrever_linha_eap(
            '', '', -1, auxiliares, '', 0, 0, 1152)
        linha_ant += 1
        eap_result.append(linha_eap)
        custo_total += auxiliares * a11Insumos.objetos.get(codigo=1152).custo01


    ################### Entrega interna -> Riscos Incidentes e Bonificações #############################
    linha_eap=escrever_linha_eap(
        f'{prefEap}03.', "Riscos Incidentes", 2, 1, 'un', 4, 0, 0)
    linha_ant += 1
    eap_result.append(linha_eap)

    ################### Insumo -> Riscos Incidentes e Bonificações #############################
    bonificacoes=calc_riscos_bonificacoes(custo_total, valores['dados_estrutura']['dificuldade'])
    linha_eap=escrever_linha_eap(
        '', '', -1, bonificacoes, '', 0, 0, 1)
    linha_ant += 1
    eap_result.append(linha_eap)

    return eap_result
