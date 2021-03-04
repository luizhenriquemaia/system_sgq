from django import forms
from django.db.models import Q
from main.models import (a10CatsInsumos, a11Insumos, a15AtvsPad, a19PlsPgtos,
                         a20StsOrcs, c01Usuarios, e06ContCad)




class formAdicionarDesconto(forms.Form):
    valor_desconto = forms.CharField(
        label='valor_desconto', max_length=5, required=True)

class formInserirInsumo(forms.Form):
    combInsumo = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(
        Q(catins_id=8) | Q(catins_id=15) | Q(catins_id=16) | Q(catins_id=17) | Q(catins_id=36) | Q(catins_id=37) | Q(catins_id=38) | Q(catins_id=39) | Q(catins_id=41) | Q(catins_id=42) | Q(catins_id=43) | Q(catins_id=44) | Q(catins_id=45) | Q(catins_id=46) | Q(catins_id=47) | Q(catins_id=48) | Q(catins_id=49) | Q(catins_id=51) | Q(catins_id=52) | Q(catins_id=53) | Q(catins_id=54)|Q(catins_id=55)|Q(catins_id=57)|Q(catins_id=58)|Q(catins_id=59)|Q(catins_id=60)|Q(catins_id=61)|Q(catins_id=62)).order_by('descricao'),
        to_field_name="codigo", widget=forms.Select(attrs={'class':'select-add-button'}))
    quantInsumo = forms.CharField(label='Quantidade', max_length=5, required=True)
    combAtvPad = forms.ModelChoiceField(queryset=a15AtvsPad.objetos.filter(Q(id=21)|Q(id=35)|Q(id=36)|Q(id=55)|Q(id=56)).order_by('descricao'),
                                   to_field_name="id")

class formInserirInsumoNaAtividade(forms.Form):
    insumo = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(
        Q(catins_id=8)|Q(catins_id=15)|Q(catins_id=16)|Q(catins_id=17)|Q(catins_id=36)|Q(catins_id=37)|Q(catins_id=38)|Q(catins_id=39)|Q(catins_id=41)|Q(catins_id=42)|Q(catins_id=43)|Q(catins_id=44)|Q(catins_id=45)|Q(catins_id=46)|Q(catins_id=47)|Q(catins_id=48)|Q(catins_id=49)| Q(catins_id=51)|Q(catins_id=52)|Q(catins_id=53)|Q(catins_id=54)|Q(catins_id=55)|Q(catins_id=57)|Q(catins_id=58)|Q(catins_id=59)|Q(catins_id=60)|Q(catins_id=61)|Q(catins_id=62)).order_by('descricao'),
        to_field_name="id", widget=forms.Select(attrs={'class':'select-add-button'}))
    quant_insumo = forms.CharField(max_length=10)
    valor_insumo = forms.CharField(max_length=10, required=False)

class formInserirServico(forms.Form):
    descricao = forms.CharField(max_length=255)
    codigo_eap = forms.CharField(max_length=30)
    tipo = forms.ChoiceField(choices=[
        ('1', 'Atividade'), ('2', 'Entrega Interna'), ('3', 'Entrega Externa')])
    

class formCadInsumo(forms.Form):
    combcatInsumo = forms.ModelChoiceField(queryset=a10CatsInsumos.objetos.filter(
        Q(id=15)|Q(id=16)|Q(id=17)|Q(id=36)|Q(id=37)|Q(id=38)|Q(id=39)|Q(id=42)|Q(id=43)|Q(id=44)|Q(id=45)|Q(id=46)|Q(id=47)|Q(id=48)|Q(id=49)|Q(id=50)|Q(id=51)|Q(id=52)|Q(id=53)|Q(id=54)|Q(id=55)|Q(id=56)|Q(id=57)|Q(id=58)|Q(id=59)|Q(id=60)|Q(id=61)|Q(id=62)).order_by('descricao'),
        to_field_name="id")
    descInsumo = forms.CharField(label='descricao', max_length=100, required=True)
    unidInsumo = forms.CharField(label='unidade', max_length=5, required=True)
    custoInsumo = forms.CharField(label='custo', max_length=10, required=True)
    espessura = forms.CharField(max_length=10, required=False)
    comprimento = forms.CharField(max_length=10, required=False)
    largura = forms.CharField(max_length=10, required=False)


class formEditarTextoEAP(forms.Form):
    texto_novo = forms.CharField(max_length=400, required=False)
    codigo_eap_novo = forms.CharField(max_length=10, required=False)
    valor_unitario_novo = forms.CharField(max_length=20, required=False)
    quantidade_nova = forms.CharField(max_length=100, required=False)


class formAtualizarDadosInsumo(forms.Form):
    nova_descricao = forms.CharField(max_length=100, required=False)
    novo_preco = forms.CharField(max_length=10, required=False)
    nova_unidade = forms.CharField(max_length=5, required=False)
    nova_espessura = forms.CharField(max_length=10, required=False)
    novo_comprimento = forms.CharField(max_length=10, required=False)
    nova_largura = forms.CharField(max_length=10, required=False)
    nova_cat_insumo = forms.ModelChoiceField(queryset=a10CatsInsumos.objetos.filter(
        Q(id=15)|Q(id=16)|Q(id=17)|Q(id=36)|Q(id=37)|Q(id=38)|Q(id=39)|Q(id=42)|Q(id=43)|Q(id=44)|Q(id=45)|Q(id=46)|Q(id=47)|Q(id=48)|Q(id=49)|Q(id=50)|Q(id=51)|Q(id=52)|Q(id=53)|Q(id=54)|Q(id=55)|Q(id=56)|Q(id=57)|Q(id=58)|Q(id=59)|Q(id=60)|Q(id=61)|Q(id=62)).order_by('descricao'),
        to_field_name="id", required=False)


class formInserirDeslocamento(forms.Form):
    quantKm = forms.CharField(max_length=5, required=False)
    combVeiculo = forms.ChoiceField(choices=[('0', ''),('1', 'Carro'), ('2', 'Caminhonete'), ('3', 'Caminhão Munck'), ('4', 'Caminhão Toco')], required=False)
    quantDias = forms.CharField(max_length=10, required=False)
    quantHosp = forms.CharField(max_length=10, required=False)
    quantPassagens = forms.CharField(max_length=10, required=False)


class formAlterarInsumoOrc(forms.Form):
    quantidadeInsumo = forms.CharField(max_length=10, required=False)
    valorUnitarioInsumo = forms.CharField(max_length=10, required=False)
    novoInsumoOrc = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(Q(catins_id=15)|Q(catins_id=16)|Q(catins_id=36)|Q(catins_id=37)|Q(catins_id=38)|Q(catins_id=39)|Q(catins_id=41)|Q(catins_id=42)|Q(catins_id=43)|Q(catins_id=44)|Q(catins_id=45)|Q(catins_id=46)|Q(catins_id=47)|Q(catins_id=48)|Q(catins_id=49)|Q(catins_id=51)|Q(catins_id=52)|Q(catins_id=53)|Q(catins_id=54)|Q(catins_id=61)|Q(catins_id=62)).order_by('descricao'),
                                   to_field_name="id", widget=forms.Select(attrs={'class':'select-add-button'}), required=False)


class formEditarProposta(forms.Form):
    def __init__(self, *args, **kwargs):
        escolhas_empresas = kwargs.pop('escolhas_empresas')
        super().__init__(*args, **kwargs)
        self.fields['empresa'].choices = escolhas_empresas
    tratamento = forms.CharField(
        label='tratamento', max_length=20, required=True)
    nomeCliente = forms.CharField(
        label='nomeCliente', max_length=300, required=True)
    empresa = forms.ChoiceField()
    enderecoObra = forms.CharField(
        label='enderecoObra', max_length=500, required=False)
    condPgto = forms.ModelChoiceField(
        queryset=a19PlsPgtos.objetos.all(), to_field_name="id", required=False)
    prazoObra = forms.CharField(
        label='prazoObra', max_length=10, required=True)
    prazoValidade = forms.CharField(
        label='prazoValidade', max_length=5, required=True)
    vendedor = forms.ModelChoiceField(
        queryset=c01Usuarios.objetos.all(), to_field_name="id", required=False)
    tipo_proposta = forms.ChoiceField(choices=[('1', 'Fabricação e instalação da cobertura'), 
        ('2', 'Só o material'), ('3', 'Outros serviços')], required=True)


class formEditarContrato(forms.Form):
    def __init__(self, *args, **kwargs):
        escolhas_empresas = kwargs.pop('escolhas_empresas')
        super().__init__(*args, **kwargs)
        self.fields['empresa'].choices = escolhas_empresas
    nomeCliente = forms.CharField(
        label='nomeCliente', max_length=300, required=True)
    cnpj = forms.CharField(label='cnpj', max_length=14, required=True)
    telefone = forms.CharField(label='telefone', max_length=20, required=True)
    empresa = forms.ChoiceField()
    enderecoObra = forms.CharField(
        label='enderecoObra', max_length=500, required=False)
    condPgto = forms.ModelChoiceField(
        queryset=a19PlsPgtos.objetos.all(), to_field_name="id")
    prazoObra = forms.CharField(
        label='prazoObra', max_length=10, required=True)
    vendedor = forms.ModelChoiceField(
        queryset=c01Usuarios.objetos.all(), to_field_name="id")


class formAlterarStatus(forms.Form):
    combStatus = forms.ModelChoiceField(queryset=a20StsOrcs.objetos.all().order_by('descricao'))


class formMarcarVisita(forms.Form):
    dataVisita = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}), required=True)
    horaVisita = forms.TimeField(widget=forms.TextInput(attrs={'class': 'timepicker'}), required=True)
    combTiposVisita = forms.ChoiceField(choices=[('0', ''),('1', 'Cobertura de Policarbonato'), ('2', 'Venezianas')], required=True)


class formMedidasVenezianas(forms.Form):
    base1 = forms.CharField(label='Base1', max_length=20)
    altura1 = forms.CharField(label='Altura1', max_length=20)
    repet1 = forms.CharField(label='Repet1', max_length=20)
    rebite1 = forms.CharField(label='Rebite1', max_length=20)
    base2 = forms.CharField(label='Base2', max_length=20, required=False)
    altura2 = forms.CharField(label='Altura2', max_length=20, required=False)
    repet2 = forms.CharField(label='Repet2', max_length=20, required=False)
    rebite2 = forms.CharField(label='Rebite2', max_length=20, required=False)
    base3 = forms.CharField(label='Base3', max_length=20, required=False)
    altura3 = forms.CharField(label='Altura3', max_length=20, required=False)
    repet3 = forms.CharField(label='Repet3', max_length=20, required=False)
    rebite3 = forms.CharField(label='Rebite3', max_length=20, required=False)
    base4 = forms.CharField(label='Base4', max_length=20, required=False)
    altura4 = forms.CharField(label='Altura4', max_length=20, required=False)
    repet4 = forms.CharField(label='Repet4', max_length=20, required=False)
    rebite4 = forms.CharField(label='Rebite4', max_length=20, required=False)
    base5 = forms.CharField(label='Base5', max_length=20, required=False)
    altura5 = forms.CharField(label='Altura5', max_length=20, required=False)
    repet5 = forms.CharField(label='Repet5', max_length=20, required=False)
    rebite5 = forms.CharField(label='Rebite5', max_length=20, required=False)


class formOrcamentoMultiClickPlanoFixo(forms.Form):
    chapa = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=57).order_by("descricao"),
        to_field_name="codigo")
    perfil_arremate = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(Q(catins_id=43)|Q(catins_id=42)).order_by("descricao"),
        to_field_name="codigo")
    tampa = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=58).order_by("descricao"),
        to_field_name="codigo")
    garra = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=59).order_by("descricao"),
        to_field_name="codigo")
    fita = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=46).order_by("descricao"),
        to_field_name="codigo")
    selante = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=38).order_by("descricao"),
        to_field_name="codigo")
    parafuso_arremate = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=60).order_by("descricao"),
        to_field_name="codigo")
    parafuso_terca = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=60).order_by("descricao"),
        to_field_name="codigo")
    perfil_estrutural_externo = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
        to_field_name="codigo")
    perfil_estrutural_interno = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
        to_field_name="codigo")
    rufo = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=16).order_by("descricao"),
        to_field_name="codigo")
    calha = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=16).order_by("descricao"),
        to_field_name="codigo")
    tipo_pintura = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=52).order_by("descricao"),
        to_field_name="codigo")
    quantidade_pintura = forms.CharField(max_length=5, required=False)
    comprimento = forms.CharField(max_length=20, required=True)
    largura = forms.CharField(max_length=20, required=True)
    declividade = forms.CharField(max_length=20, required=True)
    repeticoes = forms.CharField(max_length=20, required=True)
    distancia_entre_apoios = forms.CharField(max_length=20, required=True)
    distancia_entre_maos_f = forms.CharField(max_length=20, required=False)
    montante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    jusante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    lateral_esquerda = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    lateral_direita = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    dias_serralheiro = forms.CharField(max_length=20, required=False)
    quantidade_serralheiro = forms.CharField(max_length=20, required=False)
    dias_auxiliar = forms.CharField(max_length=20, required=False)
    quantidade_auxiliar = forms.CharField(max_length=20, required=False)
    dificuldade = forms.ChoiceField(choices=[('1', 'fácil'), ('2', 'médio'), ('3', 'difícil')], required=False)
    aproveitar_estrutura = forms.BooleanField(required=False)


class formOrcamentoTelhaTrapezoidalFixo(forms.Form):
    telha = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(
            Q(catins_id=61)|Q(catins_id=62)).order_by("descricao"),
        to_field_name="codigo")
    parafuso_costura = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(
            Q(catins_id=37)|Q(catins_id=60)).order_by("descricao"),
        to_field_name="codigo")
    parafuso_fixacao = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(
            Q(catins_id=37) | Q(catins_id=60)).order_by("descricao"),
        to_field_name="codigo")
    selante = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=38).order_by("descricao"),
        to_field_name="codigo")
    perfil_estrutural_externo = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
        to_field_name="codigo")
    perfil_estrutural_interno = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
        to_field_name="codigo")
    rufo = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=16).order_by("descricao"),
        to_field_name="codigo")
    calha = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=16).order_by("descricao"),
        to_field_name="codigo")
    tipo_pintura = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=52).order_by("descricao"),
        to_field_name="codigo")
    quantidade_pintura = forms.CharField(max_length=5, required=False)
    comprimento = forms.CharField(max_length=20, required=True)
    largura = forms.CharField(max_length=20, required=True)
    declividade = forms.CharField(max_length=20, required=True)
    repeticoes = forms.CharField(max_length=20, required=True)
    distancia_entre_apoios = forms.CharField(max_length=20, required=True)
    distancia_entre_maos_f = forms.CharField(max_length=20, required=False)
    montante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    jusante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    lateral_esquerda = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    lateral_direita = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    dias_serralheiro = forms.CharField(max_length=20, required=False)
    quantidade_serralheiro = forms.CharField(max_length=20, required=False)
    dias_auxiliar = forms.CharField(max_length=20, required=False)
    quantidade_auxiliar = forms.CharField(max_length=20, required=False)
    dificuldade = forms.ChoiceField(choices=[('1', 'fácil'), ('2', 'médio'), ('3', 'difícil')], required=False)
    aproveitar_estrutura = forms.BooleanField(required=False)


class formPoliPlanFix(forms.Form):
    combPolicarbonato = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(Q(catins_id=41) | Q(catins_id=49) | Q(catins_id=55)).order_by("descricao"),
                                               to_field_name="codigo")
    combPerfUn = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=42).order_by("descricao"),
                                        to_field_name="codigo")
    combPerfAr = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(Q(catins_id=43) | Q(catins_id=42)).order_by("descricao"),
                                        to_field_name="codigo")
    combPerfU = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=44).order_by("descricao"),
                                       to_field_name="codigo")
    comb_selante = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=38).order_by("descricao"),
                                          to_field_name="codigo")
    combPerfEsExterno = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
                                               to_field_name="codigo")
    combPerfEsInterno = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
                                               to_field_name="codigo")
    combRufo = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=16).order_by("descricao"),
                                      to_field_name="codigo")
    combCalha = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=16).order_by("descricao"),
                                       to_field_name="codigo")
    combPerfGuar = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=47).order_by("descricao"),
                                          to_field_name="codigo")
    combPerfGax = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=47).order_by("descricao"),
                                         to_field_name="codigo")
    combFitaVent = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=46).order_by("descricao"),
                                          to_field_name="codigo")
    combFitaAlum = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=46).order_by("descricao"),
                                          to_field_name="codigo")
    combPintura = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=52).order_by("descricao"),
                                         to_field_name="codigo")
    quantPintura = forms.CharField(
        label='Quantidade Pintura', max_length=5, required=False)
    compPoli = forms.CharField(
        label='Comprimento', max_length=20, required=True)
    largPoli = forms.CharField(label='Largura', max_length=20, required=True)
    declPoli = forms.CharField(
        label='Declividade', max_length=20, required=True)
    repetPoli = forms.CharField(
        label='Repetições', max_length=20, required=True)
    distApoios = forms.CharField(
        label='Distância Entre Apoios', max_length=20, required=True)
    distMaosF = forms.CharField(
        label='Distância Entre Mãos Francesas', max_length=20, required=False)
    montante = forms.ChoiceField(choices=[(
        '0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    jusante = forms.ChoiceField(choices=[(
        '0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    latEsq = forms.ChoiceField(choices=[(
        '0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    latDir = forms.ChoiceField(choices=[(
        '0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    diasSerralheiro = forms.CharField(max_length=20, required=False)
    quantSerralheiros = forms.CharField(max_length=20, required=False)
    diasAuxiliar = forms.CharField(max_length=20, required=False)
    quantAuxiliares = forms.CharField(max_length=20, required=False)
    dificuldade = forms.ChoiceField(
        choices=[('1', 'fácil'), ('2', 'médio'), ('3', 'difícil')], required=False)
    apEstr = forms.BooleanField(required=False)


class formPoliPlanRet(forms.Form):
    combPolicarbonato = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(Q(catins_id=41)|Q(catins_id=49)| Q(catins_id=55)).order_by("descricao"),
                                               to_field_name="codigo")
    combPerfUn = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=42).order_by("descricao"),
                                        to_field_name="codigo")
    combPerfAr = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(Q(catins_id=43)|Q(catins_id=42)).order_by("descricao"),
                                              to_field_name="codigo")
    combPerfU = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=44).order_by("descricao"),
                                        to_field_name="codigo")
    comb_selante = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=38).order_by("descricao"),
                                          to_field_name="codigo")
    combPerfEsExterno = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
                                               to_field_name="codigo")
    combPerfEsInterno = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
                                               to_field_name="codigo")
    combRufo = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=16).order_by("descricao"),
                                        to_field_name="codigo")
    combCalha = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=16).order_by("descricao"),
                                        to_field_name="codigo")
    combPerfGuar = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=47).order_by("descricao"),
                                            to_field_name="codigo")
    combPerfGax = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=47).order_by("descricao"),
                                            to_field_name="codigo")
    combFitaVent = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=46).order_by("descricao"),
                                            to_field_name="codigo")
    combFitaAlum = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=46).order_by("descricao"),
                                            to_field_name="codigo")
    combMotores = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=53).order_by("descricao"),
                                              to_field_name="codigo")
    quantMotores = forms.CharField(label='Quantidade de Motores', max_length=3, required=True)
    quantModulos = forms.CharField(label='Quantidade de Total Módulos', max_length=3, required=True)
    quantModMoveis = forms.CharField(label='Quantidade de Módulos Móveis', max_length=3, required=True)
    direcMovimento = forms.ChoiceField(choices=[('0', 'comprimento'), ('1', 'largura')], required=True)
    combCantoneira = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
                                            to_field_name="codigo")
    combPerfCant = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
                                            to_field_name="codigo")
    combRoldanas = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=54).order_by("descricao"),
                                            to_field_name="codigo")
    combPintura = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=52).order_by("descricao"),
                                              to_field_name="codigo")
    quantPintura = forms.CharField(label='Quantidade Pintura', max_length=5, required=False)
    compPoli = forms.CharField(label='Comprimento', max_length=20, required=True)
    largPoli = forms.CharField(label='Largura', max_length=20, required=True)
    declPoli = forms.CharField(label='Declividade', max_length=20, required=True)
    repetPoli = forms.CharField(label='Repetições', max_length=20, required=True)
    distApoios = forms.CharField(
        label='Distância Entre Apoios', max_length=20, required=False)
    montante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    jusante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    latEsq = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    latDir = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    diasSerralheiro = forms.CharField(max_length=20, required=False)
    quantSerralheiros = forms.CharField(max_length=20, required=False)
    diasAuxiliar = forms.CharField(max_length=20, required=False)
    quantAuxiliares = forms.CharField(max_length=20, required=False)
    dificuldade = forms.ChoiceField(choices=[('1', 'facil'), ('2', 'medio'), ('3', 'dificil')], required=False)
    apEstr = forms.BooleanField(required=False)


class formPoliCurvoFix(forms.Form):
    combPolicarbonato = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(Q(catins_id=41)|Q(catins_id=49)| Q(catins_id=55)).order_by("descricao"),
                                               to_field_name="codigo")
    combPerfUn = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=42).order_by("descricao"),
                                               to_field_name="codigo")
    combPerfAr = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(Q(catins_id=43)|Q(catins_id=42)).order_by("descricao"),
                                              to_field_name="codigo")
    combPerfU = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=44).order_by("descricao"),
                                               to_field_name="codigo")
    comb_selante = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=38).order_by("descricao"),
                                            to_field_name="codigo")
    combPerfEsExterno = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
                                               to_field_name="codigo")
    combPerfEsInterno = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
                                               to_field_name="codigo")
    combCalandra = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=51).order_by("descricao"),
                                              to_field_name="codigo")
    combRufo = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=16).order_by("descricao"),
                                              to_field_name="codigo")
    combCalha = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=16).order_by("descricao"),
                                               to_field_name="codigo")
    combPerfGuar = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=47).order_by("descricao"),
                                              to_field_name="codigo")
    combPerfGax = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=47).order_by("descricao"),
                                               to_field_name="codigo")
    combFitaVent = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=46).order_by("descricao"),
                                              to_field_name="codigo")
    combPintura = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=52).order_by("descricao"),
                                              to_field_name="codigo")
    quantPintura = forms.CharField(
        label='Quantidade Pintura', max_length=5, required=False)
    cordaPoli = forms.CharField(label='Corda', max_length=20, required=True)
    flechaPoli = forms.CharField(label='Flecha', max_length=20, required=True)
    largPoli = forms.CharField(label='Largura', max_length=20, required=True)
    repetPoli = forms.CharField(label='Repetições', max_length=20, required=True)
    distApoios = forms.CharField(label='Distância Entre Apoios', max_length=20, required=True)
    distMaosF = forms.CharField(
        label='Distância Entre Mãos Francesas', max_length=20, required=False)
    montante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    jusante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    latEsq = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    latDir = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    diasSerralheiro = forms.CharField(max_length=20, required=False)
    quantSerralheiros = forms.CharField(max_length=20, required=False)
    diasAuxiliar = forms.CharField(max_length=20, required=False)
    quantAuxiliares = forms.CharField(max_length=20, required=False)
    dificuldade = forms.ChoiceField(choices=[('0', 'facil'), ('1', 'medio'), ('2', 'dificil')], required=False)
    apEstr = forms.BooleanField(required=False)


class formPoliCurvoRet(forms.Form):
    combPolicarbonato = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(Q(catins_id=41) | Q(catins_id=49) | Q(catins_id=55)).order_by("descricao"),
                                               to_field_name="codigo")
    combPerfUn = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=42).order_by("descricao"),
                                               to_field_name="codigo")
    combPerfAr = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(Q(catins_id=43)|Q(catins_id=42)).order_by("descricao"),
                                              to_field_name="codigo")
    combPerfU = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=44).order_by("descricao"),
                                               to_field_name="codigo")
    comb_selante = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=38).order_by("descricao"),
                                            to_field_name="codigo")
    combPerfEsExterno = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
                                               to_field_name="codigo")
    combPerfEsInterno = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
                                               to_field_name="codigo")
    combCalandra = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=51).order_by("descricao"),
                                              to_field_name="codigo")
    combRufo = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=16).order_by("descricao"),
                                              to_field_name="codigo")
    combCalha = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=16).order_by("descricao"),
                                               to_field_name="codigo")
    combPerfGuar = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=47).order_by("descricao"),
                                              to_field_name="codigo")
    combPerfGax = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=47).order_by("descricao"),
                                               to_field_name="codigo")
    combFitaVent = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=46).order_by("descricao"),
                                              to_field_name="codigo")
    combMotores = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=53).order_by("descricao"),
                                              to_field_name="codigo")
    quantMotores = forms.CharField(label='Quantidade de Motores', max_length=3, required=True)
    quantModulos = forms.CharField(label='Quantidade de Total Módulos', max_length=3, required=True)
    quantModMoveis = forms.CharField(label='Quantidade de Módulos Móveis', max_length=3, required=True)
    direcMovimento = forms.ChoiceField(choices=[('0', 'comprimento'), ('1', 'largura')], required=True)
    combCantoneira = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao").order_by("descricao"),
                                            to_field_name="codigo")
    combPerfCant = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao").order_by("descricao"),
                                            to_field_name="codigo")
    combRoldanas = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=54).order_by("descricao").order_by("descricao"),
                                            to_field_name="codigo")
    combPintura = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=52).order_by("descricao").order_by("descricao"),
                                              to_field_name="codigo")
    quantPintura = forms.CharField(label='Quantidade Pintura', max_length=5, required=False)
    cordaPoli = forms.CharField(label='Corda', max_length=20, required=True)
    flechaPoli = forms.CharField(label='Flecha', max_length=20, required=True)
    largPoli = forms.CharField(label='Largura', max_length=20, required=True)
    repetPoli = forms.CharField(label='Repetições', max_length=20, required=True)
    distApoios = forms.CharField(label='Distância Entre Apoios', max_length=20, required=True)
    montante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    jusante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    latEsq = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    latDir = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    diasSerralheiro = forms.CharField(max_length=20, required=False)
    quantSerralheiros = forms.CharField(max_length=20, required=False)
    diasAuxiliar = forms.CharField(max_length=20, required=False)
    quantAuxiliares = forms.CharField(max_length=20, required=False)
    dificuldade = forms.ChoiceField(choices=[('1', 'facil'), ('2', 'medio'), ('3', 'dificil')], required=False)
    apEstr = forms.BooleanField(required=False)
