def arrend_cima(valor, casas):
    valor = valor * pow(10, casas)
    valor_int = int(valor)
    if valor > valor_int:
        valor_int += 1
    valor_int /= pow(10, casas)
    return valor_int


def tot_pecas(quant, comp_peca, comp_barra):
    comp_peca = arrend_cima(comp_peca, 1)
    peca_por_barra = int(float(comp_barra) / comp_peca)
    total = arrend_cima(quant / peca_por_barra, 0)
    return total


def escrever_linha_eap(ordenador, descricao, tipo, quantidade, unidade, cod_atv_eap, cod_atv_pad, cod_insumo):
    # tipo 1 -> atividade, tipo 2 -> entrega interna, tipo 3 -> entrega externa
    # tipo 4 -> totalizadores de entrega interna, tipo 5 -> totalizadores de entrega externa
    linha_eap = {
        'Ordenador': ordenador,
        'Descricao': descricao,
        'Tipo': tipo,
        'Quant': quantidade,
        'Unid': unidade,
        'CodAtvEAP': cod_atv_eap,
        'CodAtvPad': cod_atv_pad,
        'CodInsumo': cod_insumo
    }
    return linha_eap


##### Função que considera a junção de peças com solda #####
def tot_peca_juncao(comp_total, comp_barra):
    quantidade = arrend_cima(comp_total / comp_barra, 0)
    return quantidade


##### Função que não considera junção de peças mas considera sobras #####
def tot_peca_sobras(quant_vaos, comp_vao, comp_peca):
    if comp_vao <= comp_peca:
        if comp_peca % comp_vao == 0:
            quantidade = arrend_cima(quant_vaos / (comp_peca / comp_vao), 0)
        else:
            total_vaos_por_peca = int(comp_peca / comp_vao)
            quantidade = arrend_cima(quant_vaos / total_vaos_por_peca, 0)
    else:
        total_vaos_por_peca = int(comp_vao / comp_peca)
        if total_vaos_por_peca <= 1.25:
            total_vaos_por_peca = 1.25
        elif total_vaos_por_peca <= 1.5:
            total_vaos_por_peca = 1.5
        else:
            total_vaos_por_peca = 1
        quantidade = arrend_cima(quant_vaos / total_vaos_por_peca, 0)
    return quantidade
