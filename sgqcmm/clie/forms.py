from django import forms
from main.models import e01Cadastros, a03Estados, a04Municipios, a05Bairros, a06Lograds


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


class frmPesqCliente(forms.Form):
    # Possibilita pesquisar um cliente na base pelo nome, telefone ou e-mail
    nome = forms.CharField(label='Nome', max_length=200, required=True,
                           widget=forms.TextInput(attrs={'placeholder': 'Nome do Cliente'}))
    fone = forms.CharField(label='Telefone', max_length=20, required=False,
                           widget=forms.TextInput(attrs={'placeholder': '(dd) nnnnn-nnnn'}))
    email = forms.EmailField(label='E-mail', required=False)


class frmEscCliente(forms.Form):
    def __init__(self, *args, **kwargs):
        escolhas_cliente = kwargs.pop('escolhas_clientes')
        super().__init__(*args, **kwargs)
        self.fields['clientes'].choices = escolhas_cliente
    clientes = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'with-gap'}),
                                 choices=())


class frmLocalizacao(forms.Form):
    # Define um local vinculado a um cliente
    complemento = forms.CharField(label='Complemento', max_length=200, required=True,
                                  widget=forms.TextInput(attrs={'placeholder': 'Complemento'}))


class frmPesqMunicip(forms.Form):
    pesqmunicip = forms.CharField(label='Pesquisar Municipio', max_length=200, required=True,
                                  widget=forms.TextInput(attrs={'placeholder': 'Pesquisar Municipio'}))
    novomunicip = forms.CharField(label='Novo Municipio', max_length=200, required=False,
                                  widget=forms.TextInput(attrs={'placeholder': 'Incluir Municipio'}))


class frmPesqBairro(forms.Form):
    pesqbairro = forms.CharField(label='Pesquisar Bairro', max_length=200, required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'Pesquisar Bairro'}))
    novobairro = forms.CharField(label='Novo Bairro', max_length=200, required=False,
                                 widget=forms.TextInput(attrs={'placeholder': 'Incluir Bairro'}))


class frmPesqLogradouro(forms.Form):
    codlograd = forms.CharField(
        label='Codigo do Logradouro', max_length=20, required=True)
    novolograd = forms.CharField(
        label='Novo Logradouro', max_length=200, required=False)
    complemento = forms.CharField(label='Complemento', max_length=200, required=True,
                                  widget=forms.TextInput(attrs={'placeholder': 'Complemento'}))


class formNovoEndereco(forms.Form):
    regiao_choices = [(0, ''), ('Norte', 'Norte'), ('Nordeste', 'Nordeste'), (
        'Centro Oeste', 'Centro Oeste'), ('Sul', 'Sul'), ('Sudeste', 'Sudeste')]
    regiao = forms.ChoiceField(choices=regiao_choices, 
        widget=forms.Select(attrs={'onchange': "carregarDados(this);"}))
    estado = forms.ModelChoiceField(queryset=a03Estados.objetos.none(),
        widget=forms.Select(attrs={'onchange': "carregarDados(this);"}))
    cidade = forms.ModelChoiceField(queryset=a04Municipios.objetos.none(),
        widget=forms.Select(attrs={'onchange': "carregarDados(this);"}))
    bairro = forms.ModelChoiceField(queryset=a05Bairros.objetos.none(),
        widget=forms.Select(attrs={'onchange': "carregarDados(this);"}))
    logradouro = forms.ModelChoiceField(queryset=a06Lograds.objetos.none())
    complemento = forms.CharField(label='Complemento', max_length=200, required=True)
