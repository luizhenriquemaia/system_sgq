from main.models import a11Insumos
from .utils.materiais_orcamento import VenezianaPolicarbonato, PerfilVenezianaAluminio, Rebite, FitaAluminio, Selante
from .utils.funcoes_calculos import arrend_cima, tot_pecas, escrever_linha_eap


# escrever "eap" para os insumos de orçamentos de policarbonato
def escrever_eap_insumos(self):
    linha_eap = escrever_linha_eap(
            '', '', -1, arrend_cima(self.quantidade, 2), '', 0, 0, self.codigo
        )
    return linha_eap


def orc_venezianas(codigo_aleta, codigo_selante, prefixo_eap, *valores):
    eap_resultante = []
    for valores_vao in valores:
        repeticoes = float(valores_vao['repeticoes'])
        base_vao = float(valores_vao['base'])
        altura_vao = float(valores_vao['altura'])
        quantidade_rebites_por_aleta = float(valores_vao['rebite'])
        objeto_aleta = a11Insumos.objetos.get(codigo=codigo_aleta)
        area_vao = repeticoes * base_vao * altura_vao

        # Totalizador entrega externa
        if repeticoes == 1:
            texto_descricao = "Vão de "
        else:
            texto_descricao = f"{repeticoes} vãos de "
        texto_descricao += f"{base_vao:.2f} x {altura_vao:.2f}m utilizando {objeto_aleta.descricao}"
        linha_eap = escrever_linha_eap(f'{prefixo_eap}.', texto_descricao, 5, area_vao, 'm²', 0, 0, 0)
        eap_resultante.append(linha_eap)

        # Entregas externas -> policarbonato
        texto_descricao = f"Policarbonato e acessórios"
        linha_atual_entrega = 1
        linha_eap = escrever_linha_eap(
            f'{prefixo_eap}.0{linha_atual_entrega}.', texto_descricao, 3, 1, 'un', 1, 55, 0
        )
        eap_resultante.append(linha_eap)
        # Insumo entrega externa -> Aleta
        linha_atual_atividade = 1
        chapa_aleta = VenezianaPolicarbonato(codigo_aleta)
        chapa_aleta.quantificar(
            base_vao, 
            altura_vao, 
            repeticoes
        )
        eap_resultante.append(
            escrever_eap_insumos(chapa_aleta)
        )
        # Insumo entrega externa -> Perfis Veneziana
        linha_atual_atividade += 1
        perfil_veneziana = PerfilVenezianaAluminio(14114)
        perfil_veneziana.quantificar(
            base_vao, 
            altura_vao, 
            repeticoes
        )
        eap_resultante.append(
            escrever_eap_insumos(perfil_veneziana)
        )
        # Insumo entrega externa -> Rebites
        linha_atual_atividade += 1
        rebites = Rebite(12734) if chapa_aleta.espessura == 3 else Rebite(13330)
        rebites.quantificar(
            chapa_aleta.quantidade_aletas, 
            quantidade_rebites_por_aleta, 
            repeticoes
        )
        eap_resultante.append(
            escrever_eap_insumos(rebites)
        )
        # Insumo entrega externa -> Selante
        linha_atual_atividade += 1
        selante = Selante(codigo_selante)
        selante.calcular_quantidade(
            altura_vao,
            base_vao,
            repeticoes,
            False
        )
        eap_resultante.append(
            escrever_eap_insumos(selante)
        )
        # Insumo entrega externa -> Fita de alumínio
        if chapa_aleta.espessura != 3:
            linha_atual_atividade += 1
            fita_aluminio = FitaAluminio(13770)
            # 0.997 = 0.414 x 2 / 0.83 -> +- 20% de margem de erro
            fita_aluminio.calcular_quantidade(
                1 * arrend_cima(base_vao, 0) * chapa_aleta.linhas_de_aleta,
                repeticoes
            )
            eap_resultante.append(
                escrever_eap_insumos(fita_aluminio)
            )

        # Entrega externa -> Outros insumos e mão de obra
        texto_descricao = f"Outros insumos e mão de obra"
        linha_atual_entrega += 1
        linha_atual_atividade = 0
        linha_eap = escrever_linha_eap(
            f'{prefixo_eap}.0{linha_atual_entrega}.', texto_descricao, 3, 1, 'un', 1, 55, 0
        )
        eap_resultante.append(linha_eap)
        # Atividade entrega externa -> Mão de obra
        linha_atual_atividade += 1
        # Estimar mao de obra de fabricacao
        mao_de_obra = arrend_cima(((chapa_aleta.quantidade / 2) + (perfil_veneziana.total_perfis_verticais / 2) + (perfil_veneziana.total_perfis_verticais / 4) + (rebites.quantidade / 20)) * 1.3, 2)
        # Estimar mao de obra de instalacao
        mao_de_obra += arrend_cima(area_vao * 8 / 6, 2)
        texto_descricao = f"Mão de obra para fabricação e instalação"
        linha_eap = escrever_linha_eap(
            f'{prefixo_eap}.0{linha_atual_entrega}.0{linha_atual_atividade}.', texto_descricao, -1, mao_de_obra, 'h', 0, 0, 1163
        )
        eap_resultante.append(linha_eap)

        # Entregas internas
        linha_atual_entrega += 1
        linha_atual_atividade = 0
        texto_descricao = f"Fabricação de {arrend_cima(base_vao, 0) * repeticoes:.0f} módulos de {chapa_aleta.comprimento_peca:.2f} x {altura_vao:.2f}m"
        linha_eap = escrever_linha_eap(
            f'{prefixo_eap}.0{linha_atual_entrega}.', texto_descricao, 4, repeticoes * arrend_cima(base_vao, 0), 'mód.', 1, 0, 0
        )
        eap_resultante.append(linha_eap)
        # Atividade entrega interna -> Linhas de aleta
        linha_atual_atividade += 1
        texto_descricao = f"{chapa_aleta.linhas_de_aleta} linhas de aletas em cada módulo"
        linha_eap = escrever_linha_eap(
            f'{prefixo_eap}.0{linha_atual_entrega}.0{linha_atual_atividade}.', texto_descricao, 2, chapa_aleta.linhas_de_aleta, 'linhas', 0, 0, 0
        )
        eap_resultante.append(linha_eap)
        # Atividade entrega interna -> Peças de aleta
        linha_atual_atividade += 1
        texto_descricao = f'{chapa_aleta.quantidade_aletas} peças de aletas de {chapa_aleta.comprimento_peca:.2f}m cada'
        linha_eap = escrever_linha_eap(
            f'{prefixo_eap}.0{linha_atual_entrega}.0{linha_atual_atividade}.', texto_descricao, 2, chapa_aleta.quantidade_aletas, 'pç', 0, 0, 0
        )
        eap_resultante.append(linha_eap)
        # Atividade entrega interna -> Perfis horizontais
        linha_atual_atividade += 1
        texto_descricao = f'{perfil_veneziana.total_perfis_horizontais} barras de perfis horizontais'
        linha_eap = escrever_linha_eap(
            f'{prefixo_eap}.0{linha_atual_entrega}.0{linha_atual_atividade}.', texto_descricao, 2, perfil_veneziana.total_perfis_horizontais, 'br', 0, 0, 0
        )
        eap_resultante.append(linha_eap)
        # Atividade entrega interna -> Perfis verticais
        linha_atual_atividade += 1
        texto_descricao = f'{perfil_veneziana.total_perfis_verticais} barras de perfis verticais'
        linha_eap = escrever_linha_eap(
            f'{prefixo_eap}.0{linha_atual_entrega}.0{linha_atual_atividade}.', texto_descricao, 2, perfil_veneziana.total_perfis_verticais, 'br', 0, 0, 0
        )
        eap_resultante.append(linha_eap)
        # Atividade entrega interna -> Rebites aletas
        linha_atual_atividade += 1
        texto_descricao = f'{rebites.total_fixacao_aletas:.2f} centos de rebites para fixação das aletas'
        linha_eap = escrever_linha_eap(
            f'{prefixo_eap}.0{linha_atual_entrega}.0{linha_atual_atividade}.', texto_descricao, 2, rebites.total_fixacao_aletas, 'cto', 0, 0, 0
        )
        eap_resultante.append(linha_eap)
        linha_atual_atividade += 1
        texto_descricao = f'{rebites.total_fixacao_modulos:.2f} centos de rebites para fixação dos módulos'
        linha_eap = escrever_linha_eap(
            f'{prefixo_eap}.0{linha_atual_entrega}.0{linha_atual_atividade}.', texto_descricao, 2, rebites.total_fixacao_modulos, 'cto', 0, 0, 0
        )
        eap_resultante.append(linha_eap)
        prefixo_eap += 1
    return eap_resultante
