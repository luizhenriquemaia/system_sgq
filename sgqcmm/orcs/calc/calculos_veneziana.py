from main.models import a11Insumos
from .utils.funcoes_calculos import arrend_cima, tot_pecas, escrever_linha_eap


def orc_venezianas(espessura, prefEAP, codAleta, **venezianas):
    numVao = 0
    linha_ant = 0
    areaTot = 0
    for veneziana, valores in venezianas.items():
        numVao += 1
        # Calcular quantitativos
        repeticoes = int(valores['repeticoes'])
        areaVao = repeticoes * float(valores['base']) * float(valores['altura'])
        areaTot += areaVao
        quantQuadrosVao = arrend_cima(float(valores['base'])/1, 0)
        compPeca = float(valores['base'])/quantQuadrosVao
        if espessura == 3:
            linhasAleta = arrend_cima(float(valores['altura'])/0.227, 0)
            # No catálogo para 2 aletas a altura do vão é 0.504
            if linhasAleta <= 3:
                if float(valores['altura']) <= 0.504:
                    linhasAleta = 2
            # Distância máxima entre aletas = 24cm, sendo que o no catálogo está 22.7cm
            if float(valores['altura']) / (linhasAleta - 1) <= 0.24:
                linhasAleta -= 1
            else:
                pass
            codrebite = 12734
            quantFita = 0
        elif espessura == 5:
            linhasAleta = arrend_cima(float(valores['altura'])/0.316, 0)
            # No catálogo para 2 aletas a altura do vão é 0.504
            if linhasAleta <= 3:
                if float(valores['altura']) <= 0.682:
                    linhasAleta = 2
            # Distância máxima entre aletas = 33.6cm, sendo que o no catálogo está 31.6cm
            if float(valores['altura']) / (linhasAleta - 1) <= 0.336:
                linhasAleta -= 1
            else:
                pass
            codrebite = 13330
            # 0.384 x 2 + margem de erro
            quantFita = arrend_cima(0.800 * quantQuadrosVao * linhasAleta * repeticoes / 30, 0)
        compAleta = 3.3
        compBarra = 6
        quantAletas = repeticoes * quantQuadrosVao * linhasAleta
        totAletas = tot_pecas(quantAletas, compPeca, compAleta)
        ##### a formula dos perfis horizontais so funciona com vaos menores que 6m  #####
        totPerfilHoriz = tot_pecas(repeticoes * 2, float(valores['base']), compBarra)
        # totPerfilVert = tot_pecas(2 * repeticoes * quantQuadrosVao, arrend_cima(float(valores['altura']), 0), compBarra)
        totPerfilVert = tot_pecas(repeticoes * 2 * quantQuadrosVao, arrend_cima(float(valores['altura']), 1), compBarra)
        totFixAletas = arrend_cima(quantAletas * int(valores['rebitesAleta']) / 10, 0) / 10
        totFixMod = arrend_cima(float(valores['repeticoes']) * 8 / 10, 0) / 10
        if repeticoes == 1:
            txtDesc = "Vão de "
        else:
            txtDesc = f"{repeticoes} vãos de "
        txtDesc = txtDesc + f"{float(valores['base']):.2f} x {float(valores['altura']):.2f}m utilizando aletas de {espessura}mm"
        linha_eap = escrever_linha_eap(f'{prefEAP}', txtDesc,
                                3, areaVao, 'm²', 0, 0, 0)
        linha_ant += 1
        eap_result = [linha_eap]
        # Colocar quantidade de modulos na EAP
        txtDesc = f"Fabricação de {quantQuadrosVao * repeticoes:.0f} módulos de {compPeca:.2f}x{float(valores['altura']):.2f}m"
        linha_eap = escrever_linha_eap(f'{prefEAP}01.', txtDesc,
                                1, repeticoes*quantQuadrosVao, 'mód.', 1, 55, 0)
        linha_ant += 1
        eap_result.append(linha_eap)
        # Colocar quantidade de linhas de aletas
        linha_eap = escrever_linha_eap(f'{prefEAP}01.01.', f"{int(linhasAleta)} linhas de aletas em cada módulo",
                                2, linhasAleta, 'linhas', 0, 0, 0)
        linha_ant += 1
        eap_result.append(linha_eap)
        # Colocar quantidade de pecas de aletas
        linha_eap = escrever_linha_eap(f'{prefEAP}01.02.', f"{quantAletas} peças de aletas de {compPeca:.2f}m cada",
                                2, quantAletas, 'pç', 0, 0, 0)
        linha_ant += 1
        eap_result.append(linha_eap)
        # Colocar quantidade de barras de aletas
        linha_eap = escrever_linha_eap(f'{prefEAP}01.03.', f"{totAletas} barras totais de aletas",
                                -1, totAletas, 'br', 1, 55, int(codAleta))
        linha_ant += 1
        eap_result.append(linha_eap)
        # Colocar quantidade de perfis horizontais
        linha_eap = escrever_linha_eap(f'{prefEAP}01.04.', f"{totPerfilHoriz} barras de perfis horizontais",
                                2, totPerfilHoriz, 'br', 0, 0, 14114)
        linha_ant += 1
        eap_result.append(linha_eap)
        # Colocar quantidade de perfis verticais
        linha_eap = escrever_linha_eap(f'{prefEAP}01.05.', f"{totPerfilVert} barras de perfis verticais",
                                2, totPerfilVert, 'br', 0, 0, 14114)
        linha_ant += 1
        eap_result.append(linha_eap)
        # Colocar quantidade totais de perfis
        linha_eap = escrever_linha_eap(f'{prefEAP}01.06.', f"{float(totPerfilHoriz+totPerfilVert):.2f} barras totais de perfis",
                                -1, totPerfilHoriz+totPerfilVert, 'br', 1, 55, 14114)
        linha_ant += 1
        eap_result.append(linha_eap)
        # Colocar quantidade de rebites para a fixacao das aletas
        linha_eap = escrever_linha_eap(f'{prefEAP}01.07.', f"{totFixAletas:.2f} centos de rebites para fixação das aletas",
                                2, totFixAletas, 'cto', 0, 0, codrebite)
        linha_ant += 1
        eap_result.append(linha_eap)
        # Colocar quantidade de rebites para a fixacao dos modulos
        linha_eap = escrever_linha_eap(f'{prefEAP}01.08.', f"{totFixMod:.2f} centos de rebites para fixação dos módulos",
                                2, totFixMod, 'cto', 0, 0, codrebite)
        linha_ant += 1
        eap_result.append(linha_eap)
        # Colocar quantidade total de rebites
        linha_eap = escrever_linha_eap(f'{prefEAP}01.09.', f"{float(totFixAletas+totFixMod):.2f} centos totais de rebites",
                                -1, totFixAletas+totFixMod, 'cto', 1, 55, codrebite)
        linha_ant += 1
        eap_result.append(linha_eap)
        # Colocar quantidade total de fita de alumínio
        if quantFita != 0:
            objFitaAlum = a11Insumos.objetos.get(codigo=13770)
            linha_eap = escrever_linha_eap(f'{prefEAP}01.10.', f"{float(quantFita):.2f} rolos de {objFitaAlum.descricao}",
                                    -1, quantFita, 'rl', 1, 55, 13770)
            linha_ant += 1
            eap_result.append(linha_eap)

            # Estimar mao de obra de fabricacao
            mObra = (quantAletas/2 + totPerfilHoriz/2 + totPerfilVert/4 + (totFixAletas+totFixMod)/20) * 1.3
            mObra = arrend_cima(mObra, 2)
            linha_eap = escrever_linha_eap(f'{prefEAP}01.11.', 'Mão de obra para fabricação',
                                    -1, mObra, 'h', 1, 55, 1163)
            linha_ant += 1
            eap_result.append(linha_eap)
        else:
            # Estimar mao de obra de fabricacao
            mObra = (quantAletas/2 + totPerfilHoriz/2 + totPerfilVert/4 + (totFixAletas+totFixMod)/20) * 1.3
            mObra = arrend_cima(mObra, 2)
            linha_eap = escrever_linha_eap(f'{prefEAP}01.10.', 'Mão de obra para fabricação',
                                    -1, mObra, 'h', 1, 55, 1163)
            linha_ant += 1
            eap_result.append(linha_eap)
        # Estimar mao de obra de instalacao
        mObra = areaVao * 8 / 6
        mObra = arrend_cima(mObra, 2)
        linha_eap = escrever_linha_eap(f'{prefEAP}02.', 'Mão de obra para instalação no local da obra',
                                1, mObra, 'h', 2, 56, 1163)
        linha_ant += 1
        eap_result.append(linha_eap)
        linha_eap = escrever_linha_eap(f'{prefEAP}02.01.', 'Mão de obra para instalação no local da obra',
                                -1, mObra, 'h', 1, 55, 1163)
        linha_ant += 1
        eap_result.append(linha_eap)
    eap_result[0]['Quant'] = areaTot
    return eap_result
