from django import forms

from main.models import a03Estados, a04Municipios, a05Bairros, a06Lograds, b01Empresas


class formCadastrarEmpresa(forms.Form):
    juridica = forms.BooleanField(required=False)
    razao = forms.CharField(max_length=255)
    fantasia = forms.CharField(max_length=255)
    codigo_empresa = forms.CharField(max_length=2)
    cnpj = forms.CharField(max_length=14)
    inscricao_estadual = forms.CharField(max_length=20)
    observacao = forms.CharField(max_length=400, required=False)
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