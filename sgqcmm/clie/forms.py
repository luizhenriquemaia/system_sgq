from django import forms
from main.models import (a03Estados, a04Municipios, a05Bairros, a06Lograds,
                         b01Empresas, b04CCustos, e01Cadastros)


class formSelecionarEmpresa(forms.Form):
    empresa_orcamento = forms.ModelChoiceField(queryset=b01Empresas.objetos.filter(juridica=True), required=False,
                                               widget=forms.Select(attrs={'onchange': 'carregarCentrosDeCusto(this.value)'}))
    centros_de_custo = forms.ModelChoiceField(queryset=b04CCustos.objetos.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            if 'cod_empresa' in self.data:
                empresa = self.data.get('cod_empresa')
                self.fields['centros_de_custo'].queryset = b04CCustos.objetos.filter(empresa=empresa, ativo=True).order_by('descricao')
        except(ValueError, TypeError):
            pass


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
