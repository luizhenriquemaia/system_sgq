# Materiais utilizados nos orçamentos de policarbonato
from main.models import a11Insumos
from .funcoes_calculos import (arrend_cima, tot_peca_juncao, tot_pecas, tot_peca_sobras)


class ChapaPolicarbonato():
    def __init__(self, codigo):
        self.codigo = codigo
        chapa_bd = a11Insumos.objetos.get(codigo=codigo)
        self.tipo = chapa_bd.catins_id
        self.descricao = chapa_bd.descricao
        self.espessura = int(chapa_bd.espessura)
        self.largura = float(round(chapa_bd.largura / 1000, 2))
        self.comprimento = float(round(chapa_bd.comprimento / 1000, 2))

    def calc_poli_alveolar(self, desenvolvimento, largura, dist_apoios, repeticoes):
        pedacos_comp_chapa = int((self.comprimento) / desenvolvimento)
        # - 0.01 -> é devido a 1cm de distância entre as chapas -> 0.71
        pedacos_larg_chapa = int(self.largura / (dist_apoios - 0.01))
        quant_total_pedacos = arrend_cima(
            round(largura / dist_apoios, 5) * repeticoes, 0
        )
        self.quantidade = arrend_cima(
            quant_total_pedacos / (pedacos_comp_chapa * pedacos_larg_chapa), 0
        )


class VenezianaPolicarbonato():
    def __init__(self, codigo):
        self.codigo = codigo
        veneziana_bd = a11Insumos.objetos.get(codigo=codigo)
        self.descricao = veneziana_bd.descricao
        self.espessura = int(veneziana_bd.espessura)
        self.comprimento = float(round(veneziana_bd.comprimento / 1000, 2))

    def quantificar(self, base, altura, repeticoes):
        self.comprimento_peca = base / arrend_cima(base, 0)
        if self.espessura == 3:
            self.linhas_de_aleta = arrend_cima(altura / 0.227, 0)
            # No catálogo para 2 aletas a altura do vão é 0.504
            if altura <= 0.504:
                self.linhas_de_aleta = 2
            # Distância máxima entre aletas = 24cm, sendo que o no catálogo está 22.7cm
            if altura / (self.linhas_de_aleta - 1) <= 0.24:
                self.linhas_de_aleta -= 1
        elif self.espessura == 5:
            self.linhas_de_aleta = arrend_cima(altura / 0.316, 0)
            # No catálogo para 2 aletas a altura do vão é 0.504
            if altura <= 0.504:
                self.linhas_de_aleta = 2
            # Distância máxima entre aletas = 33.6cm, sendo que o no catálogo está 31.6cm
            if altura / (self.linhas_de_aleta - 1) <= 0.336:
                self.linhas_de_aleta -= 1
        self.quantidade_aletas = repeticoes * arrend_cima(base, 0) * self.linhas_de_aleta
        self.total_chapas_aleta = tot_pecas(self.quantidade_aletas, self.comprimento_peca, self.comprimento)


class ChapaMultiClick():
    def __init__(self, codigo):
        self.codigo = codigo
        chapa_bd = a11Insumos.objetos.get(codigo=codigo)
        self.tipo = chapa_bd.catins_id
        self.descricao = chapa_bd.descricao

    def calc_multi_click(self, desenvolvimento, largura, dist_apoios, repeticoes):
        pedacos_comp_chapa = int(6 / desenvolvimento)
        quant_total_pedacos = arrend_cima(
            round(largura / 0.25, 5) * repeticoes, 0)
        self.quantidade = arrend_cima(
            quant_total_pedacos / pedacos_comp_chapa, 0)


class TelhaTrapezoidal():
    def __init__(self, codigo):
        self.codigo = codigo
        telha_bd = a11Insumos.objetos.get(codigo=codigo)
        self.tipo = telha_bd.catins_id
        self.descricao = telha_bd.descricao
        self.largura = float(round(telha_bd.largura / 1000, 2))

    def calcular_quantidade(self, desenvolvimento, largura_cobertura, dist_apoios, repeticoes):
        comprimento_telha = arrend_cima(desenvolvimento, 0)
        quant_telhas = arrend_cima(
            round(largura_cobertura / self.largura, 5) * repeticoes, 0)
        self.quantidade = arrend_cima(
            comprimento_telha * quant_telhas, 0)


class PerfilUniao():
    def __init__(self, codigo):
        self.codigo = codigo
        self.descricao = a11Insumos.objetos.get(
            codigo=codigo
        ).descricao

    def calc_perfil_uniao(self, largura, comprimento, dist_apoios, quant_modulos, repeticoes, perfil_uniao_igual_ao_arremate):
        if perfil_uniao_igual_ao_arremate:
            # para ver o motivo da utilização de round faça 8,40/0,7 no python
            self.quantidade = tot_peca_sobras(
                (
                    arrend_cima(round(largura / dist_apoios, 5), 0) + 1) * quant_modulos * repeticoes, 
                    comprimento, 6
                )
        else:
            # para ver o motivo da utilização de round faça 8,40/0,7 no python
            self.quantidade = tot_peca_sobras(
                (
                    arrend_cima(
                        round(largura / dist_apoios, 5), 0
                    ) - 1
                ) * quant_modulos * repeticoes, comprimento, 6
            )


class PerfilU():
    def __init__(self, codigo):
        self.codigo = codigo
        self.descricao = a11Insumos.objetos.get(
            codigo=codigo
        ).descricao

    def calc_perfil_u(self, largura, repeticoes, quant_modulos):
        self.quantidade = arrend_cima(
            2 * largura * repeticoes * quant_modulos / 6, 0
        ) if largura > 6 else tot_peca_sobras(
            2 * repeticoes * quant_modulos, largura, 6
        )


class PerfilArremate():
    def __init__(self, codigo):
        self.codigo = codigo
        self.descricao = a11Insumos.objetos.get(
            codigo=codigo
        ).descricao

    def calc_perfil_arremate(self, comprimento, repeticoes, quant_modulos):
        self.quantidade = arrend_cima(
            2 * comprimento * repeticoes * quant_modulos / 6, 0
        ) if comprimento > 6 else tot_peca_sobras(
            2 * repeticoes * quant_modulos, comprimento, 6
        )



class PerfilVenezianaAluminio():
    def __init__(self, codigo):
        self.codigo = codigo
        perfil_bd = a11Insumos.objetos.get(codigo=codigo)
        self.descricao = perfil_bd.descricao
        self.comprimento = float(round(perfil_bd.comprimento / 1000, 2))

    def quantificar(self, base, altura, repeticoes):
        self.total_perfis_horizontais = arrend_cima(2 * repeticoes * base / self.comprimento, 0)
        quantidade_perfis_verticais = 2 * repeticoes * (arrend_cima(base, 0) + 1)
        self.total_perfis_verticais = arrend_cima(quantidade_perfis_verticais * altura / self.comprimento, 0)
        self.total_perfis = self.total_perfis_horizontais + self.total_perfis_verticais


class Rebite():
    def __init__(self, codigo):
        self.codigo = codigo
        self.descricao = a11Insumos.objetos.get(codigo=codigo).descricao

    def quantificar(self, quantidade_aletas, quantidade_rebites_por_aleta, repeticoes):
        self.total_fixacao_aletas = arrend_cima(quantidade_aletas * quantidade_rebites_por_aleta / 10, 0) / 10
        self.total_fixacao_modulos = arrend_cima(repeticoes * 8 / 10, 0) / 10
        self.total_rebites = self.total_fixacao_aletas + self.total_fixacao_modulos



class Tampa():
    def __init__(self, codigo):
        self.codigo = codigo
        self.descricao = a11Insumos.objetos.get(
            codigo=codigo
        ).descricao

    def calc_tampa(self, largura, repeticoes, quant_modulos):
        self.quantidade = 2 * arrend_cima(
            (arrend_cima((largura / 0.25), 0) + 1) * repeticoes * quant_modulos, 0)


class Garra():
    def __init__(self, codigo):
        self.codigo = codigo
        self.descricao = a11Insumos.objetos.get(
            codigo=codigo
        ).descricao

    def calcular_quantidade(self, largura, comprimento, dist_apoios, repeticoes, quant_modulos):
        self.quantidade = arrend_cima(
            (arrend_cima(largura / 0.25, 0) *
                (arrend_cima(comprimento / dist_apoios, 0) + 1) *
                    repeticoes * quant_modulos), 0)


class ParafusoTercasMultiTelha():
    def __init__(self, codigo):
        self.codigo = codigo
        self.descricao = a11Insumos.objetos.get(
            codigo=codigo
        ).descricao

    def calcular_quantidade(self, largura, comprimento, dist_apoios, repeticoes, quant_modulos):
        quantidade = arrend_cima(
            (arrend_cima(largura / 0.25, 0) *
                (arrend_cima(comprimento / dist_apoios, 0) - 1) *
             repeticoes * quant_modulos), 0)
        quantidade = quantidade * 1.1
        quant_parafusos_conf = quantidade
        if not quant_parafusos_conf % 5 == 0:
            quantidade += 5 - (quant_parafusos_conf % 5)
        self.quantidade = quantidade / 100


class Guarnicao():
    def __init__(self, codigo_guarnicao):
        self.codigo = codigo_guarnicao
        self.descricao = a11Insumos.objetos.get(
            codigo=codigo_guarnicao
        ).descricao

    def calc_perfil_guarnicao(self, largura, comprimento, dist_apoios, repeticoes, quant_modulos, perf_uniao_no_lugar_do_arremate):
        if perf_uniao_no_lugar_do_arremate:
            quant_guarnicao = arrend_cima(
                (
                    (arrend_cima(largura / dist_apoios, 0) + 1) * comprimento * repeticoes * quant_modulos
                ), 0
            )
        else:
            quant_guarnicao = arrend_cima(
                (
                    (arrend_cima(largura / dist_apoios, 0) - 1) * comprimento * repeticoes * quant_modulos
                ), 0
            )
        self.quantidade = quant_guarnicao + 10 - \
            quant_guarnicao % 10 if quant_guarnicao % 10 != 0 else quant_guarnicao


class Gaxeta():
    def __init__(self, codigo_gaxeta):
        self.codigo = codigo_gaxeta
        self.descricao = a11Insumos.objetos.get(
            codigo=codigo_gaxeta
        ).descricao
    
    def calc_perfil_gaxeta(self, largura, comprimento, dist_apoios, repeticoes, quant_modulos, perf_uniao_no_lugar_do_arremate):
        quantidade_tiras_gaxeta = arrend_cima(largura / dist_apoios, 0) + 1 if perf_uniao_no_lugar_do_arremate else arrend_cima(largura / dist_apoios, 0) - 1
        quant_gaxeta = arrend_cima(
            (
                quantidade_tiras_gaxeta * comprimento * repeticoes * quant_modulos * 2
            ), 0
        )
        self.quantidade = quant_gaxeta + 10 - \
            quant_gaxeta % 10 if quant_gaxeta % 10 != 0 else quant_gaxeta


class ParafusosPolicarbonato():
    def __init__(self, codigo_parafuso):
        self.codigo = codigo_parafuso
        self.descricao = a11Insumos.objetos.get(
            codigo=codigo_parafuso
        ).descricao
        
    def calc_parafuso_arremate(self, comprimento, repeticoes, quant_modulos, dist_entre_furos):
        quant_parafusos = arrend_cima(
            2 * comprimento * repeticoes * quant_modulos / dist_entre_furos, 2
        )
        # 10% a mais
        quantidade = quant_parafusos * 1.1
        quant_parafusos_conf = quantidade
        if not quant_parafusos_conf % 5 == 0:
            quantidade += 5 - (quant_parafusos_conf % 5)
        self.quantidade = quantidade / 100
    
    def calc_parafuso_uniao(self, largura, dist_apoios, comprimento, repeticoes, dist_parafusos, perfil_uniao_igual_ao_arremate):
        if perfil_uniao_igual_ao_arremate:
            quant_parafusos = arrend_cima((
            arrend_cima(largura / dist_apoios, 2) + 1
            ) * comprimento * repeticoes / dist_parafusos, 2)
        else:
            quant_parafusos = arrend_cima((
                arrend_cima(largura / dist_apoios, 2) - 1
                ) * comprimento * repeticoes / dist_parafusos, 2)
        # 10% a mais
        quantidade = quant_parafusos * 1.1
        quant_parafusos_conf = quantidade 
        if not quant_parafusos_conf % 5 == 0:
            quantidade += 5 - (quant_parafusos_conf % 5)
        self.quantidade = quantidade / 100


class ParafusosTelha():
    def __init__(self, codigo_parafuso):
        self.codigo = codigo_parafuso
        self.descricao = a11Insumos.objetos.get(
            codigo=codigo_parafuso
        ).descricao

    def calc_parafusos_telha_zincada(self, largura, comprimento, repeticoes, quant_modulos, largura_telha):
        quantidade_vaos = arrend_cima(largura / largura_telha, 0)
        # vão máximo entre terças de 1,50m
        quantidade_tercas = arrend_cima(comprimento / 1.5, 0) + 1
        quant_parafusos = arrend_cima(quantidade_vaos * 4 * quantidade_tercas * repeticoes * quant_modulos, 0)
        # 10% a mais
        quantidade = quant_parafusos * 1.1
        quant_parafusos_conf = quantidade
        if not quant_parafusos_conf % 5 == 0:
            quantidade += 5 - (quant_parafusos_conf % 5)
        self.quantidade = quantidade / 100

    def calc_parafusos_telha_termoacustica(self, largura, comprimento, repeticoes, quant_modulos, largura_telha):
        quantidade_vaos = arrend_cima(largura / largura_telha, 0)
        # vão máximo entre terças de 1,00m
        quantidade_tercas = arrend_cima(comprimento / 1, 0) + 1
        quant_parafusos = arrend_cima(
            ((quantidade_vaos * 2) + 2) * quantidade_tercas * repeticoes * quant_modulos, 0)
        # 10% a mais
        quantidade = quant_parafusos * 1.1
        quant_parafusos_conf = quantidade
        if not quant_parafusos_conf % 5 == 0:
            quantidade += 5 - (quant_parafusos_conf % 5)
        self.quantidade = quantidade / 100


class ParafusoCosturaTelhas():
    def __init__(self, codigo):
        self.codigo = codigo
        self.descricao = a11Insumos.objetos.get(
            codigo=codigo
        ).descricao

    def calcular_quantidade(self, largura, largura_telha, comprimento, dist_apoios, repeticoes, quant_modulos):
        quantidade_vaos = arrend_cima(largura / largura_telha, 0)
        # Parafusos a cada 50cm
        quantidade = arrend_cima(((quantidade_vaos - 1) * comprimento / 0.5) * repeticoes * quant_modulos, 0)
        quantidade = quantidade * 1.1
        quant_parafusos_conf = quantidade
        if not quant_parafusos_conf % 5 == 0:
            quantidade += 5 - (quant_parafusos_conf % 5)
        self.quantidade = quantidade / 100


class FitaTackyTape():
    def __init__(self, codigo_fita):
        self.codigo = codigo_fita
        fita_bd = a11Insumos.objetos.get(codigo=codigo_fita)
        self.descricao = fita_bd.descricao
        self.comprimento = float(round(fita_bd.comprimento / 1000, 2))

    def calcular_quantidade(self, largura, largura_telha, comprimento, repeticoes, quant_modulos):
        quantidade_vaos = arrend_cima(largura / largura_telha, 0)
        self.quantidade = arrend_cima((quantidade_vaos - 1) * comprimento * repeticoes * quant_modulos / self.comprimento, 0)


class FitaAluminio():
    def __init__(self, codigo_fita):
        self.codigo = codigo_fita
        self.descricao = a11Insumos.objetos.get(
            codigo=codigo_fita
        ).descricao

    def calcular_quantidade(self, largura, repeticoes):
        self.quantidade = arrend_cima((largura * repeticoes) / 30, 0)


class FitaVentTape():
    def __init__(self, codigo):
        self.codigo = codigo
        self.descricao = a11Insumos.objetos.get(
            codigo=self.codigo
        ).descricao

    def calcular_quantidade(self, largura, repeticoes):
        self.quantidade = arrend_cima((largura * repeticoes) / 50, 0)


class Selante():
    def __init__(self, codigo):
        self.codigo = codigo
        self.descricao = a11Insumos.objetos.get(
            codigo=self.codigo
        ).descricao
    
    def calcular_quantidade(self, largura, comprimento, repeticoes, estrutura_retratil):
        dimensoes = 2 * (largura + comprimento) * repeticoes
        if estrutura_retratil:
            self.quantidade = arrend_cima(1.5 * dimensoes / 40, 0) * 2
        else:
            self.quantidade = arrend_cima(1.5 * dimensoes / 40, 0)


class PerfisEstruturaisIguais():
    def __init__(self, codigo):
        self.codigo = codigo
        objeto_bd = a11Insumos.objetos.get(codigo=self.codigo)
        self.descricao = objeto_bd.descricao
        self.custo = objeto_bd.custo01
    
    def calcular_quantidade(self, largura, corda, comprimento, altura, dist_apoios, repeticoes, quant_modulos, dist_maos_franc):
        perimetro = 2 * (comprimento + largura)
        if dist_maos_franc != 0:
            maos_franc = (arrend_cima(round(
                largura / dist_maos_franc, 5), 0) + 1
            ) * (corda + altura)
            quant_metalon = tot_peca_juncao((maos_franc + perimetro + (
                    (arrend_cima(round(largura / dist_apoios, 5), 0) - 1
                    ) * comprimento)
                ) * quant_modulos * repeticoes, 6)
        else:
            perimetro = 2 * (comprimento + largura)
            quant_metalon = tot_peca_juncao(
                (perimetro + (
                    (arrend_cima(round(
                        largura / dist_apoios, 5), 0) - 1
                    ) * comprimento)
                ) * quant_modulos * repeticoes, 6)
        self.quantidade = quant_metalon

    def preco(self):
        return self.quantidade * float(self.custo)
        

class PerfisEstruturaisDiferentes():
    def __init__(self, codigo, tipo):
        self.codigo = codigo
        self.tipo = tipo
        objeto_bd = a11Insumos.objetos.get(codigo=self.codigo)
        self.descricao = objeto_bd.descricao
        self.custo = objeto_bd.custo01

    def calcular_quantidade(self, largura, corda, comprimento, altura, dist_apoios, repeticoes, quant_modulos, dist_maos_franc, estrutura_em_arco):
        perimetro = 2 * (comprimento + largura)
        if self.tipo == "externo":
            if dist_maos_franc != 0:
                maos_franc = round(
                    (arrend_cima(round(largura / dist_maos_franc, 5), 0) + 1) * (corda + altura), 5)
                quant_metalon_ext = tot_peca_juncao(
                    ((largura * 2) + maos_franc) *quant_modulos * repeticoes, 6)
            else:
                perimetro = 2 * (comprimento + largura)
                quant_metalon_ext = tot_peca_juncao(perimetro *  quant_modulos * repeticoes, 6)
            self.quantidade = quant_metalon_ext
        elif self.tipo == "interno":
            if not estrutura_em_arco:
                quant_metalon_int = tot_peca_juncao((arrend_cima(round(
                    largura / dist_apoios, 5), 0) - 1) * quant_modulos * comprimento * repeticoes, 6)
            else:
                # 23-01-20 -> considerar as calandras para os perfis laterais externos
                quant_metalon_int = tot_peca_juncao((arrend_cima(round(
                    largura / dist_apoios, 5), 0) + 1) * quant_modulos * comprimento * repeticoes, 6)
            self.quantidade = quant_metalon_int

    def preco(self):
        return self.quantidade * float(self.custo)


class Calha():
    def __init__(self, codigo):
        self.codigo = codigo
        objeto_bd = a11Insumos.objetos.get(codigo=self.codigo)
        self.descricao = objeto_bd.descricao
        self.custo = objeto_bd.custo01

    def calcular_quantidade(self, comprimento, largura, lat_dir, lat_esq, montante, jusante, repeticoes):
        quantidade = 0
        if lat_dir == '2':
            quantidade += comprimento
        if lat_esq == '2':
            quantidade += comprimento
        if montante == '2':
            quantidade += largura
        if jusante == '2':
            quantidade += largura
        self.quantidade = round(quantidade * repeticoes, 2)

    def preco(self):
        return self.quantidade * float(self.custo)


class Rufo():
    def __init__(self, codigo):
        self.codigo = codigo
        objeto_bd = a11Insumos.objetos.get(codigo=self.codigo)
        self.descricao = objeto_bd.descricao
        self.custo = objeto_bd.custo01
    
    def calcular_quantidade(self, comprimento, largura, lat_dir, lat_esq, montante, jusante, repeticoes):
        quantidade = 0
        if lat_dir == '1':
            quantidade += comprimento
        if lat_esq == '1':
            quantidade += comprimento
        if montante == '1':
            quantidade += largura
        if jusante == '1':
            quantidade += largura
        self.quantidade = round(quantidade * repeticoes, 2)
    
    def preco(self):
        return self.quantidade * float(self.custo)


class Roldana():
    def __init__(self, codigo):
        self.codigo = codigo
        objeto_bd = a11Insumos.objetos.get(codigo=self.codigo)
        self.descricao = objeto_bd.descricao
        self.custo = objeto_bd.custo01

    def calcular_quantidade(self, comprimento, largura, direcao_movimento, repeticoes, quant_modulos):
        if direcao_movimento == 0:
            quant_roldanas = 4 * quant_modulos * int(comprimento / 2) * repeticoes if comprimento >= 3 else quant_modulos * 4 * repeticoes
        elif direcao_movimento == 1:
            largura_modulos = largura / quant_modulos
            # 4 roldanas + 1 a cada 2 metros
            # 1 roldana a cada 2 metros de cada lado pela largura de cada módulo
            quant_roldanas = 2 * (int(largura_modulos / 2) + 1) * quant_modulos if largura >= 3 else quant_modulos * 4 * repeticoes
        quant_roldanas = arrend_cima(quant_roldanas, 0)
        self.quantidade = quant_roldanas + 1 if quant_roldanas % 2 != 0 else quant_roldanas
    
    def preco(self):
        return self.quantidade * float(self.custo)


class DiscoCorte():
    def __init__(self, codigo):
        self.codigo = codigo
        objeto_bd = a11Insumos.objetos.get(codigo=self.codigo)
        self.descricao = objeto_bd.descricao
        self.custo = objeto_bd.custo01

    def calcular_quantidade(self, comprimento, largura, dist_apoios, repeticoes):
        quant_discos = arrend_cima(
            arrend_cima(largura / dist_apoios, 0) * repeticoes / 3, 0)
        quant_discos += arrend_cima(comprimento * largura * repeticoes / 45, 0)
        self.quantidade = quant_discos

    def preco(self):
        return self.quantidade * float(self.custo)


class Eletrodo():
    def __init__(self, codigo):
        self.codigo = codigo
        objeto_bd = a11Insumos.objetos.get(codigo=self.codigo)
        self.descricao = objeto_bd.descricao
        self.custo = objeto_bd.custo01

    def calcular_quantidade(self, comprimento, largura, dist_apoios, repeticoes):
        quant_eletrodos = arrend_cima(
            arrend_cima(largura / dist_apoios, 0) * repeticoes / 100, 1)
        quant_eletrodos += arrend_cima(comprimento * largura * repeticoes / 100, 1)
        self.quantidade = quant_eletrodos

    def preco(self):
        return self.quantidade * float(self.custo)
