""" Implementa as funcoes personalizadas """


# Retira parenteses, tracos e espacos de um numeo de telefone
def numpurotelefone(textodigitado):
    numpuro = textodigitado.replace('+', '')
    numpuro = numpuro.replace('(', '')
    numpuro = numpuro.replace(')', '')
    numpuro = numpuro.replace('-', '')
    numpuro = numpuro.replace(' ', '')
    return numpuro


# Formata um numero de telefone colocando parenteses, espacos e traco
def format_telefone(str_numero_puro):
    numero_formatado = str_numero_puro
    n = len(str_numero_puro)
    if len(str_numero_puro) >= 11:
        # telefone celular
        numero_formatado = f'({str_numero_puro[0:2]}) {str_numero_puro[2:7]}-{str_numero_puro[7:n]}'
    elif len(str_numero_puro) >= 10:
        # telefone fixo
        numero_formatado = f'({str_numero_puro[0:2]}) {str_numero_puro[2:7]}-{str_numero_puro[7:n]}'
    elif len(str_numero_puro) >= 7:
        numero_formatado = f'({str_numero_puro[0:2]}) {str_numero_puro[2:n]}'
    return numero_formatado


# Formata uma lista de telefones fornecidos
def format_list_telefone(str_lista_pura):
    lista_telefones = [format_telefone(numero_puro) for numero_puro in str_lista_pura]
    # for numero_puro in str_lista_pura:
    #     lista_telefones.append(format_telefone(numero_puro))
    return lista_telefones


# Retorna o nome da sequencia de novo orcamento requerida
def nomesequencia(strseq):
    if strseq == 1:
        result = 'Novo Pré-Orçamento'
    elif strseq == 2:
        result = 'Nova Visita'
    elif strseq == 3:
        result = 'Novo Orçamento'
    elif strseq == 4:
        result = 'Nova Proposta'
    else:
        result = 'Novo Contrato'
    return result


# Retorna texto para filtro conforme opcoes fornecidas
def textofiltro(nomecampo, filtro):
    tipofiltro, valor = filtro.split(".")
    if tipofiltro == '':
        txtfiltro = ''
    elif tipofiltro == 'A-B-C':
        vlrpar = int(valor)
        txtfiltro = ' ((Left(' + nomecampo + ', 1) = ' + chr(39) + chr(65+3*(vlrpar-1)) + chr(39) + ')'
        txtfiltro = txtfiltro + ' OR (Left(' + nomecampo + ', 1) = ' + chr(39) + chr(66+3*(vlrpar-1)) + chr(39) + ')'
        if vlrpar < 9:
            txtfiltro = txtfiltro + ' OR (Left(' + nomecampo + ', 1) = ' + chr(39) + chr(67+3*(vlrpar-1)) + chr(39) + \
                        ')'
        txtfiltro = txtfiltro + ')'
    else:
        txtfiltro = ' (' + nomecampo + ' like %s )'
    return txtfiltro


# Retorna lista com codigos superiores ao fornecido
def listacodigossup(codatual):
    nivatual = codatual.count('.')
    result = []
    if nivatual > 1:
        numeros = codatual.split('.')
        for cont in range(nivatual-1):
            if cont > 0:
                result.append(result[cont - 1] + numeros[cont] + '.')
            else:
                result.append(numeros[cont] + '.')
    return result
