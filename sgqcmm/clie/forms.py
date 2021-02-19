from django import forms
from main.models import e01Cadastros, b01Empresas, a03Estados, a04Municipios, a05Bairros, a06Lograds


class formSelecionarEmpresa(forms.Form):
    empresa = forms.ModelChoiceField(queryset=b01Empresas.objetos.filter(juridica=True), required=False)


class formDadosCliente(forms.Form):
    tratamento = forms.CharField(
        label='tratamento', max_length=200, required=True)
    nome = forms.CharField(label='nome', max_length=200, required=True)
    cnpj = forms.CharField(label='cnpj', max_length=14, required=False)
    descricao = forms.CharField(
        label='descricao', max_length=200, required=True)
    juridica = forms.ChoiceField(
        choices=[('0', 'Pessoa Física'), ('1', 'Jurídica')])
    genero = forms.ChoiceField(
        choices=[('0', 'Feminino'), ('1', 'Masculino')])
    empresa = forms.ModelChoiceField(queryset=e01Cadastros.objetos.filter(
        juridica=True).order_by('descrcad'), required=False)
    telefone = forms.CharField(label='telefone', max_length=15, required=False)
    email = forms.EmailField(label='email', required=False)
    endereco = forms.CharField(label='endereco', max_length=20, required=False,
                               widget=forms.TextInput(attrs={'placeholder': 'Logradouro e Complemento'}))


class formDadosEmpresa(forms.Form):
    nome = forms.CharField(label='nome', max_length=200, required=True)
    cnpj = forms.CharField(label='cnpj', max_length=14, required=False)
    genero = forms.ChoiceField(
        choices=[('0', 'Feminino'), ('1', 'Masculino')])
    telefone = forms.CharField(label='telefone', max_length=15, required=False)
    email = forms.EmailField(label='email', required=False)
    endereco = forms.CharField(label='endereco', max_length=20, required=False,
                               widget=forms.TextInput(attrs={'placeholder': 'Logradouro e Complemento'}))


class formPesqCliente(forms.Form):
    nome = forms.CharField(max_length=200, required=True)
    fone = forms.CharField(max_length=20, required=False,
                           widget=forms.TextInput(attrs={'placeholder': '(dd) nnnnn-nnnn'}))
    email = forms.EmailField(required=False)


class formEscCliente(forms.Form):
    def __init__(self, *args, **kwargs):
        escolhas_cliente = kwargs.pop('escolhas_clientes')
        super().__init__(*args, **kwargs)
        self.fields['clientes'].choices = escolhas_cliente
    clientes = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'with-gap'}),
                                 choices=())

class formNovoEndereco(forms.Form):
    regiao_choices = [(0, ''), ('Norte', 'Norte'), ('Nordeste', 'Nordeste'), (
        'Centro Oeste', 'Centro Oeste'), ('Sul', 'Sul'), ('Sudeste', 'Sudeste')]
    regiao = forms.ChoiceField(choices=regiao_choices, 
        widget=forms.Select(attrs={'onchange': "carregarDados(this);"}))
    estado = forms.ModelChoiceField(queryset=a03Estados.objetos.none(),
        widget=forms.Select(attrs={'onchange': "carregarDados(this);"}))
    cidade = forms.ModelChoiceField(queryset=a04Municipios.objetos.none(),
        widget=forms.Select(attrs={'onchange': "carregarDados(this);"}))
    bairro = forms.ModelChoiceField(queryset=a05Bairros.objetos.none(), required=False,
        widget=forms.Select(attrs={'onchange': "carregarDados(this);"}))
    novo_bairro = forms.CharField(max_length=200, required=False)
    logradouro = forms.ModelChoiceField(queryset=a06Lograds.objetos.none(), required=False)
    novo_logradouro = forms.CharField(max_length=200, required=False)
    complemento = forms.CharField(max_length=200, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            if 'regiao' in self.data:
                regiao = self.data.get('regiao')
                self.fields['estado'].queryset = a03Estados.objetos.filter(
                    regiao=regiao).order_by('estado')
                self.fields['estado'].to_field_name = 'uf'
            if 'estado' in self.data:
                estado = self.data.get('estado')
                self.fields['cidade'].queryset = a04Municipios.objetos.filter(
                    estado_id=estado).order_by('municipio')
            if 'cidade' in self.data:
                cidade = self.data.get('cidade')
                self.fields['bairro'].queryset = a05Bairros.objetos.filter(
                    municipio_id=cidade).order_by('bairro')
            if 'bairro' in self.data:
                bairro = self.data.get('bairro')
                self.fields['logradouro'].queryset = a06Lograds.objetos.filter(
                    bairro_id=bairro).order_by('logradouro')
        except(ValueError, TypeError):
            pass