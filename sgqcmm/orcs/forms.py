from django import forms
from django.db.models import Q
from main.models import (a10CatsInsumos, a11Insumos, a15AtvsPad, a19PlsPgtos,
                         a20StsOrcs, c01Usuarios, e06ContCad)




class formAdicionarDesconto(forms.Form):
    valor_desconto = forms.CharField(
        label='valor_desconto', max_length=5, required=True)
        

class formInserirInsumoNaAtividade(forms.Form):
    insumo = forms.ModelChoiceField(queryset=a11Insumos.objetos.all().only("id", "descricao", "codigo").order_by('descricao'),
        to_field_name="id", widget=forms.Select(attrs={'class':'select-add-button'}))
    quant_insumo = forms.CharField(max_length=10)
    valor_insumo = forms.CharField(max_length=10, required=False)


class formInserirServico(forms.Form):
    descricao = forms.CharField(max_length=255)
    codigo_eap = forms.CharField(max_length=30)
    tipo = forms.ChoiceField(choices=[
        ('3', 'Entrega Externa'), ('5', 'Totalizador de Entrega Externa')])
    quantidade = forms.CharField(max_length=20, required=False)
    unidade = forms.CharField(max_length=20, required=False)
    valor_unitario = forms.CharField(max_length=20, required=False)


class formEditarEap(forms.Form):
    codigo_eap = forms.CharField(max_length=10, required=False)
    descricao = forms.CharField(max_length=400, required=False)
    quantidade = forms.CharField(max_length=20, required=False)
    unidade = forms.CharField(max_length=20, required=False)
    valor_unitario = forms.CharField(max_length=20, required=False)
    

class formCadInsumo(forms.Form):
    categoria_insumo = forms.ModelChoiceField(queryset=a10CatsInsumos.objetos.all().only('id', 'ordenador', 'descricao').order_by('ordenador'), to_field_name="id")
    descricao = forms.CharField(max_length=100, required=True)
    unidade = forms.CharField(max_length=5, required=True)
    custo = forms.DecimalField(max_digits=12, decimal_places=4)
    espessura = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0, required=False)
    comprimento = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0, required=False)
    largura = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0, required=False)


class formAtualizarDadosInsumo(forms.Form):
    descricao = forms.CharField(max_length=100, required=False)
    valor_unitario = forms.DecimalField(max_digits=12, decimal_places=4, required=False)
    unidade = forms.CharField(max_length=5, required=False)
    espessura = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0, required=False)
    comprimento = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0, required=False)
    largura = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0, required=False)
    categoria = forms.ModelChoiceField(queryset=a10CatsInsumos.objetos.all().only('id', 'ordenador', 'descricao').order_by('ordenador'), to_field_name="id", required=False)


class formInserirDeslocamento(forms.Form):
    distancia = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0, required=False)
    tipo_veiculo = forms.ChoiceField(choices=[('0', ''),('1', 'Carro'), ('2', 'Caminhonete'), ('3', 'Caminhão Munck'), ('4', 'Caminhão Toco')], required=False)
    dias = forms.DecimalField(max_digits=12, decimal_places=1, min_value=0, required=False)
    hospedagem = forms.DecimalField(max_digits=12, decimal_places=1, min_value=0, required=False)
    passagem = forms.DecimalField(max_digits=12, decimal_places=1, min_value=0, required=False)


class formAlterarInsumoOrc(forms.Form):
    insumo = forms.ModelChoiceField(queryset=a11Insumos.objetos.all().only("id", "descricao", "codigo").order_by('descricao'),
        to_field_name="id", required=False)
    quantidade = forms.DecimalField(max_digits=12, decimal_places=4, required=False)
    valor_unitario = forms.DecimalField(max_digits=12, decimal_places=4, required=False)


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
    condPgto = forms.ModelChoiceField(
        queryset=a19PlsPgtos.objetos.all(), to_field_name="id", required=False)
    prazoObra = forms.CharField(
        label='prazoObra', max_length=10, required=True)
    prazoValidade = forms.CharField(
        label='prazoValidade', max_length=5, required=True)
    vendedor = forms.ModelChoiceField(
        queryset=c01Usuarios.objetos.all(), to_field_name="id", required=False)
    tipo_proposta = forms.ChoiceField(choices=[('1', 'Execução de serviços'), 
        ('2', 'Só o material')], required=True)


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
    selante = forms.ModelChoiceField(
        queryset=a11Insumos.objetos.filter(catins_id=38).order_by("descricao"),
        to_field_name="codigo")
    base = forms.DecimalField(max_digits=12, decimal_places=4, required=False)
    altura = forms.DecimalField(max_digits=12, decimal_places=4, required=False)
    repeticoes = forms.DecimalField(max_digits=12, decimal_places=4, required=False)
    rebite = forms.DecimalField(max_digits=12, decimal_places=4, required=False)


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
    quantidade_pintura = forms.DecimalField(max_digits=12, decimal_places=4, required=False)
    comprimento = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    largura = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    declividade = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    repeticoes = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    distancia_entre_apoios = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    distancia_entre_maos_f = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    montante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    jusante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    lateral_esquerda = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    lateral_direita = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    dias_serralheiro = forms.DecimalField(max_digits=12, decimal_places=4, required=False)
    quantidade_serralheiro = forms.DecimalField(max_digits=12, decimal_places=4, required=False)
    dias_auxiliar = forms.DecimalField(max_digits=12, decimal_places=4, required=False)
    quantidade_auxiliar = forms.DecimalField(max_digits=12, decimal_places=4, required=False)
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
    quantidade_pintura = forms.DecimalField(max_digits=12, decimal_places=4, required=False)
    comprimento = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    largura = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    declividade = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    repeticoes = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    distancia_entre_apoios = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    distancia_entre_maos_f = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    montante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    jusante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    lateral_esquerda = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    lateral_direita = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    dias_serralheiro = forms.DecimalField(max_digits=12, decimal_places=4, required=False)
    quantidade_serralheiro = forms.DecimalField(max_digits=12, decimal_places=4, required=False)
    dias_auxiliar = forms.DecimalField(max_digits=12, decimal_places=4, required=False)
    quantidade_auxiliar = forms.DecimalField(max_digits=12, decimal_places=4, required=False)
    dificuldade = forms.ChoiceField(choices=[(1, 'fácil'), (2, 'médio'), (3, 'difícil')], required=False)
    aproveitar_estrutura = forms.BooleanField(required=False)


class FormChapasPolicarbonato(forms.Form):
    tipo_policarbonato = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(Q(catins_id=41) | Q(catins_id=49) | Q(catins_id=55)).order_by("descricao"),
                                               to_field_name="codigo")
    tipo_perfil_uniao = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=42).order_by("descricao"),
                                        to_field_name="codigo")
    tipo_perfil_arremate = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(Q(catins_id=43) | Q(catins_id=42)).order_by("descricao"),
                                        to_field_name="codigo")
    tipo_perfil_u = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=44).order_by("descricao"),
                                       to_field_name="codigo")
    tipo_guarnicao = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=47).order_by("descricao"),
                                          to_field_name="codigo")
    tipo_gaxeta = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=47).order_by("descricao"),
                                         to_field_name="codigo")
    tipo_fita_vent = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=46).order_by("descricao"),
                                          to_field_name="codigo")
    tipo_fita_aluminio = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=46).order_by("descricao"),
                                          to_field_name="codigo")
    tipo_selante = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=38).order_by("descricao"),
                                          to_field_name="codigo")


class FormEstruturaCobertura(forms.Form):
    tipo_perfil_externo = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
                                               to_field_name="codigo")
    tipo_perfil_interno = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
                                               to_field_name="codigo")
    tipo_pintura = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=52).order_by("descricao").order_by("descricao"),
                                              to_field_name="codigo")
    quantidade_pintura = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0, required=False)
    chapa_rufo = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(Q(catins_id=16)|Q(catins_id=63)).order_by("descricao"),
                                              to_field_name="codigo")
    chapa_calha = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(Q(catins_id=16)|Q(catins_id=63)).order_by("descricao"),
                                               to_field_name="codigo")
    montante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    jusante = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    lateral_esquerda = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    lateral_direita = forms.ChoiceField(choices=[('0', 'livre'), ('1', 'rufo'), ('2', 'calha'), ('3', 'tampar')], required=False)
    dias_serralheiro = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0, required=False)
    quantidade_serralheiro = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0, required=False)
    dias_auxiliar = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0, required=False)
    quantidade_auxiliar = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0, required=False)
    dificuldade = forms.ChoiceField(
        choices=[(1, 'fácil'), (2, 'médio'), (3, 'difícil')], required=False)
    aproveitar_estrutura = forms.BooleanField(required=False)


class FormEstruturaCoberturaCurva(forms.Form):
    tipo_calandra = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=51).order_by("descricao"),
                                              to_field_name="codigo")


class FormMedidasCoberturaPlana(forms.Form):
    comprimento_cobertura = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    largura_cobertura = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    declividade_cobertura = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    repeticoes_cobertura = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    distancia_apoios_cobertura = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    quantidade_maos_francesas = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0, required=False)


class FormMedidasCoberturaCurva(forms.Form):
    corda_cobertura = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    flecha_cobertura = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    largura_cobertura = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    repeticoes_cobertura = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    distancia_apoios_cobertura = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0)
    quantidade_maos_francesas = forms.DecimalField(max_digits=12, decimal_places=4, min_value=0, required=False)


class FormCoberturaRetratil(forms.Form):
    tipo_motor = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=53).order_by("descricao"),
                                              to_field_name="codigo")
    quantidade_motor = forms.DecimalField(max_digits=12, decimal_places=0, min_value=0)
    quantidade_modulos = forms.DecimalField(max_digits=12, decimal_places=0, min_value=0)
    quantidade_modulos_moveis = forms.DecimalField(max_digits=12, decimal_places=0, min_value=0)
    direcao_movimento = forms.ChoiceField(choices=[('0', 'comprimento'), ('1', 'largura')], required=True)
    tipo_cantoneira = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
                                            to_field_name="codigo")
    tipo_perfil_cantoneira = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=15).order_by("descricao"),
                                            to_field_name="codigo")
    tipo_roldana = forms.ModelChoiceField(queryset=a11Insumos.objetos.filter(catins_id=54).order_by("descricao"),
                                            to_field_name="codigo")