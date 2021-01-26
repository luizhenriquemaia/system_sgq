from django.db import models
from django.contrib.auth.models import User
from main.funcoes import numpurotelefone, textofiltro


# Tabelas de dados gerais

class a01Comandos(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    tipo = models.PositiveSmallIntegerField(default=1)
    comando = models.CharField(max_length=255)
    exibgrid = models.BooleanField(default=False)
    filtro = models.PositiveSmallIntegerField(default=0)
    checagem = models.PositiveSmallIntegerField(default=0)
    infcompl = models.BooleanField(default=False)
    totalizacao = models.PositiveSmallIntegerField(default=0)
    acaobot = models.PositiveSmallIntegerField(default=0)
    objetos = models.Manager()

    def __str__(self):
        return self.comando

    def permitidos(self, codusr, programa, numarea):
        comando = "SELECT main_a01comandos.*, Concat('/sgqcmm/" + programa + "/', main_a01comandos.id) AS urlcomando  " \
                  "FROM main_a01comandos " \
                  "INNER JOIN main_c02cmdsperms ON main_a01comandos.id = main_c02cmdsperms.comando_id " \
                  "WHERE (main_c02cmdsperms.usuario_id=" + str(codusr) + ") AND " \
                  "(truncate(main_a01comandos.id/1000,0)=" + str(numarea) + ");"
        try:
            pesquisa = self.objetos.raw(comando)
            return pesquisa
        except self.DoesNotExist:
            return None


class a02Pesquisas(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    descricao = models.CharField(max_length=255)
    strcomando = models.CharField(max_length=255)
    listlargs = models.CharField(max_length=255) # Lista com as larguras das colunas
    tipo = models.PositiveSmallIntegerField(default=1)
    objetos = models.Manager()


class a03Estados(models.Model):
    uf = models.CharField(max_length=2, primary_key=True)
    estado = models.CharField(max_length=20)
    regiao = models.CharField(max_length=20, blank=True)
    cepini = models.CharField(max_length=8, blank=True, null=True)
    cepfin = models.CharField(max_length=8, blank=True, null=True)
    distfab = models.DecimalField(max_digits=6, decimal_places=2)
    objetos = models.Manager()

    def __str__(self):
        return self.estado

    def nomeestado(self, sigla):
        try:
            estadoesc = self.objetos.get(uf=sigla)
            nomeuf = estadoesc.estado
            return nomeuf
        except self.DoesNotExist:
            return None


class a04Municipios(models.Model):
    id = models.IntegerField(primary_key=True)
    estado = models.ForeignKey(a03Estados, on_delete=models.CASCADE)
    municipio = models.CharField(max_length=40)
    cepini = models.CharField(max_length=8, blank=True, null=True)
    cepfin = models.CharField(max_length=8, blank=True, null=True)
    distfab = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    objetos = models.Manager()

    def __str__(self):
        return self.municipio + "-" + self.estado.uf

    def proxnumcad(self):
        ultcad = self.objetos.all().values_list('id', flat=True)
        if bool(ultcad):
            maiorvalor = max(ultcad)
            return maiorvalor + 1
        else:
            return 1

    def nomemuncipio(self, codmunic):
        try:
            municipioesc = self.objetos.get(id=codmunic)
            nomemun = municipioesc.municipio
            return nomemun
        except self.DoesNotExist:
            return None

    def municipiosestado(self, siglauf, filtro):
        tipofiltro, valorfiltro = filtro.split(".")
        txtfiltro = textofiltro('municipio', filtro)
        if txtfiltro:
            txtfiltro = " AND " + txtfiltro
        comando = "SELECT municipio, id FROM main_a04municipios WHERE estado_id = " + chr(39) + str(siglauf) + chr(39) \
                  + txtfiltro + ";"
        try:
            if tipofiltro == 'like':
                coringa = chr(37) + valorfiltro + chr(37)
                possiveis = self.objetos.raw(comando, [coringa])
            else:
                possiveis = self.objetos.raw(comando)
            return possiveis
        except self.DoesNotExist:
            return None


class a05Bairros(models.Model):
    id = models.IntegerField(primary_key=True)
    municipio = models.ForeignKey(a04Municipios, on_delete=models.CASCADE)
    bairro = models.CharField(max_length=50)
    cepini = models.CharField(max_length=8, blank=True, null=True)
    cepfin = models.CharField(max_length=8, blank=True, null=True)
    distfab = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    objetos = models.Manager()

    def __str__(self):
        return self.bairro

    def proxnumcad(self):
        ultcad = self.objetos.all().values_list('id', flat=True)
        if bool(ultcad):
            maiorvalor = max(ultcad)
            return maiorvalor + 1
        else:
            return 1

    def nomebairro(self, codbair):
        try:
            bairroesc = self.objetos.get(id=codbair)
            nomebair = bairroesc.bairro
            return nomebair
        except self.DoesNotExist:
            return None

    def bairrosmunicipio(self, codmun, filtro):
        tipofiltro, valorfiltro = filtro.split(".")
        txtfiltro = textofiltro('bairro', filtro)
        if txtfiltro:
            txtfiltro = " AND " + txtfiltro
        comando = "SELECT bairro, id FROM main_a05bairros WHERE municipio_id = " + str(codmun) + txtfiltro + ";"
        try:
            if tipofiltro == 'like':
                coringa = chr(37) + valorfiltro + chr(37)
                possiveis = self.objetos.raw(comando, [coringa])
            else:
                possiveis = self.objetos.raw(comando)
            return possiveis
        except self.DoesNotExist:
            return None


class a06Lograds(models.Model):
    id = models.IntegerField(primary_key=True)
    bairro = models.ForeignKey(a05Bairros, on_delete=models.CASCADE)
    logradouro = models.CharField(max_length=100)
    ceplogr = models.CharField(max_length=8, blank=True, null=True)
    distfab = models.DecimalField(max_digits=6, decimal_places=2, blank=True)
    objetos = models.Manager()

    def __str__(self):
        return self.logradouro

    def proxnumcad(self):
        ultcad = self.objetos.all().values_list('id', flat=True)
        if bool(ultcad):
            maiorvalor = max(ultcad)
            return maiorvalor + 1
        else:
            return 1

    def nomelogradouro(self, codlogr):
        try:
            logresc = self.objetos.get(id=codlogr)
            nomelogr = logresc.logradouro
            return nomelogr
        except self.DoesNotExist:
            return None

    def logrsbairro(self, codbairro):
        try:
            return self.objetos.filter(id=codbairro)
        except self.DoesNotExist:
            return None


class a07TiposEnd(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    tend = models.CharField(max_length=30)
    objetos = models.Manager()

    def __str__(self):
        return self.tend


class a08TiposFrete(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    descsing = models.CharField(max_length=15)
    descplur = models.CharField(max_length=15)
    desccomp = models.CharField(max_length=255)
    pesomax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    volmax = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    vlrkm = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    objetos = models.Manager()

    def __str__(self):
        return self.desccomp


class a09TiposFone(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    tfone = models.CharField(max_length=30)
    objetos = models.Manager()

    def __str__(self):
        return self.tfone


class a10CatsInsumos(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    hierarquia = models.PositiveSmallIntegerField()
    ordenador = models.IntegerField()
    descricao = models.CharField(max_length=100)
    tipo = models.PositiveSmallIntegerField()
    objetos = models.Manager()

    def __str__(self):
        return self.descricao

    def ordtxt(self):
        return str(self.ordenador)

    def ordenadas(self):
        comando = "SELECT * FROM main_a10catsinsumos ORDER BY CONCAT('A' + main_a10catsinsumos.ordenador);"
        try:
            pesquisa = self.objetos.raw(comando)
            return pesquisa
        except self.DoesNotExist:
            return None


class a11Insumos(models.Model):
    id = models.IntegerField(primary_key=True)
    catins = models.ForeignKey(a10CatsInsumos, on_delete=models.CASCADE)
    codigo = models.IntegerField()
    descricao = models.CharField(max_length=200)
    undbas = models.CharField(max_length=10)
    undcompr = models.CharField(max_length=10)
    fatundcomp = models.FloatField()
    custo01 = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    custo02 = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    prvda = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    pesunbas = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    qtppal = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    comprimento = models.DecimalField(
        max_digits=8, decimal_places=1, default=0, null=True)
    largura = models.DecimalField(
        max_digits=8, decimal_places=1, default=0, null=True)
    espessura = models.DecimalField(
        max_digits=8, decimal_places=1, default=0, null=True)
    dataatualizacao = models.DateField(auto_now=False, auto_now_add=True)
    objetos = models.Manager()

    def __str__(self):
        if self.largura != 0 and self.comprimento != 0:
            return f"{self.descricao} {self.comprimento}x{self.largura}x{self.espessura}mm"
        else:
            return self.descricao



class a12FtesComps(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    descricao = models.CharField(max_length=255)
    diretorio = models.CharField(max_length=255, blank=True)
    objetos = models.Manager()

    def __str__(self):
        return self.descricao


class a13CompsCads(models.Model):
    id = models.IntegerField(primary_key=True)
    ftecomp = models.ForeignKey(a12FtesComps, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=20)
    descricao = models.CharField(max_length=255)
    producao = models.DecimalField(max_digits=12, decimal_places=4, default=1)
    unidade = models.CharField(max_length=10)
    anomesref = models.PositiveSmallIntegerField(default=0)
    txadferram = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    cstequip = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    cstmobra = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    cstmater = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    cstespec = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    csttrans = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    cstunita = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    txbdi = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    especificacoes = models.CharField(max_length=255, blank=True)
    objetos = models.Manager()

    def __str__(self):
        return self.descricao


class a14InsComps(models.Model):
    composicao = models.ForeignKey(a13CompsCads, on_delete=models.CASCADE)
    insumo = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    quant = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    utprod = models.DecimalField(max_digits=10, decimal_places=4, default=1)
    utimprod = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    fprod = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    objetos = models.Manager()


class a15AtvsPad(models.Model):
    id = models.IntegerField(primary_key=True)
    ordenador = models.CharField(max_length=30)
    descricao = models.CharField(max_length=255)
    unidade = models.CharField(max_length=10)
    tipo = models.PositiveSmallIntegerField(default=0)
    selecionada = models.BooleanField()
    objetos = models.Manager()

    def __str__(self):
        return self.descricao


class a16CompsAtvsPad(models.Model):
    atvpad = models.ForeignKey(a15AtvsPad, on_delete=models.CASCADE)
    compos = models.ForeignKey(a13CompsCads, on_delete=models.CASCADE)
    qtdcomp = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    objetos = models.Manager()


class a17RiscosCad(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    positivo = models.BooleanField(default=False)
    causaraiz = models.CharField(max_length=255)
    efeito = models.CharField(max_length=255)
    objetos = models.Manager()

    def __str__(self):
        return self.causaraiz


class a18CstInd(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    descricao = models.CharField(max_length=255)
    pertot = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    tipo = models.PositiveSmallIntegerField(default=0)
    objetos = models.Manager()

    def __str__(self):
        return self.descricao


class a19PlsPgtos(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    tipo = models.PositiveSmallIntegerField()
    formapgto = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255)
    objetos = models.Manager()

    def __str__(self):
        return self.descricao


class a20StsOrcs(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    descricao = models.CharField(max_length=100)
    alerta = models.PositiveSmallIntegerField()
    ativo = models.BooleanField()
    transfoe = models.BooleanField()
    objetos = models.Manager()

    def __str__(self):
        return self.descricao


class a21RhFuncoes(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    insumo = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    funcao = models.CharField(max_length=255)
    tipo = models.PositiveSmallIntegerField(default=1)  # 1 - Administrativo e 2 - Operacional
    obrcnh = models.BooleanField(default=False)


class a22RhSindicatos(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    nome = models.CharField(max_length=255)
    abrev = models.CharField(max_length=30)


class a23RhRegTrab(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    descricao = models.CharField(max_length=255)
    hndom = models.DurationField(default=0)
    hnseg = models.DurationField(default=0)
    hnter = models.DurationField(default=0)
    hnqua = models.DurationField(default=0)
    hnqui = models.DurationField(default=0)
    hnsex = models.DurationField(default=0)
    hnsab = models.DurationField(default=0)
    thedom = models.PositiveSmallIntegerField(default=1)
    theseg = models.PositiveSmallIntegerField(default=1)
    theter = models.PositiveSmallIntegerField(default=1)
    thequa = models.PositiveSmallIntegerField(default=1)
    thequi = models.PositiveSmallIntegerField(default=1)
    thesex = models.PositiveSmallIntegerField(default=1)
    thesab = models.PositiveSmallIntegerField(default=1)
    horini = models.TimeField()
    horint = models.TimeField()
    durint = models.DurationField(default=72)
    objetos = models.Manager()

    def __str__(self):
        return self.descricao


class a24RhPlSaude(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    descricao = models.CharField(max_length=255)


class a25RhHabilid(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    descricao = models.CharField(max_length=255)


class a26RhTreinam(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    descricao = models.CharField(max_length=255)


class a27Bancos(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    banco = models.CharField(max_length=255)
    objetos = models.Manager()

    def __str__(self):
        return self.banco


class a28Historicos(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    historico = models.CharField(max_length=40)
    tipo = models.PositiveSmallIntegerField(default=0)
    histexp = models.PositiveSmallIntegerField(default=0)


class a29TipsMovFin(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    descricao = models.CharField(max_length=255)
    tipo = models.PositiveSmallIntegerField(default=1)
    podeprev = models.BooleanField(default=False)
    vincad = models.PositiveSmallIntegerField(default=0)
    tipocad = models.PositiveSmallIntegerField(default=0)
    detcad = models.BooleanField(default=False)
    vinpatr = models.PositiveSmallIntegerField(default=0)
    tipopatr = models.PositiveSmallIntegerField(default=0)
    vincontr = models.PositiveSmallIntegerField(default=0)
    vinativ = models.PositiveSmallIntegerField(default=0)
    detativs = models.BooleanField(default=False)
    detinsumos = models.BooleanField(default=False)
    detprodutos = models.BooleanField(default=False)
    ordcatinsesp = models.IntegerField(null=True)
    hist = models.ForeignKey(a28Historicos, on_delete=models.CASCADE)
    complpad = models.CharField(max_length=255)
    descpad = models.CharField(max_length=255)
    tipoctasdo = models.PositiveSmallIntegerField(default=0)
    tipoctares = models.PositiveSmallIntegerField(default=0)


class a30ItHoler(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    seq = models.PositiveSmallIntegerField(default=1)
    descricao = models.CharField(max_length=255)
    historico = models.ForeignKey(a28Historicos, on_delete=models.CASCADE)
    complhist = models.CharField(max_length=100, null=True)
    formula = models.CharField(max_length=255)
    operacoes = models.CharField(max_length=20)
    condicao = models.CharField(max_length=100, default='1')
    exibobrig = models.BooleanField(default=False)
    campoexib = models.SmallIntegerField(default=1)

class a31FaseOrc(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    descricao = models.CharField(max_length=255)
    objetos = models.Manager()


# Dados das Empresas

class b01Empresas(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    juridica = models.BooleanField(default=True)
    razao = models.CharField(max_length=255)
    fantasia = models.CharField(max_length=255)
    codemp = models.CharField(max_length=2)
    lograd = models.ForeignKey(a06Lograds, on_delete=models.CASCADE)
    complend = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=14)
    inscest = models.CharField(max_length=20)
    observs = models.TextField(blank=True, null=True)
    objetos = models.Manager()

    def __str__(self):
        return self.razao

    def permitidas(self, codusr):
        comando = "SELECT main_b01empresas.* " \
                  "FROM main_b01empresas " \
                  "INNER JOIN main_c03empsperms ON main_b01empresas.id = main_c03empsperms.empresa_id " \
                  "WHERE (main_c03empsperms.usuario_id=" + str(codusr) + ");"
        try:
            pesquisa = self.objetos.raw(comando)
            return pesquisa
        except self.DoesNotExist:
            return None


class b02PlContas(models.Model):
    id = models.IntegerField(primary_key=True)
    empresa = models.ForeignKey(b01Empresas, on_delete=models.CASCADE)
    ordenador = models.IntegerField()
    descricao = models.CharField(max_length=255)
    tipo = models.PositiveSmallIntegerField(default=0)
    hierarquia = models.PositiveSmallIntegerField(default=10)
    sdoant = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    entras = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    saidas = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    dtcons = models.DateField(null=True)
    ctacor = models.PositiveSmallIntegerField(null=True)


class b03CtasCaixa(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    descricao = models.CharField(max_length=255)
    empresa = models.ForeignKey(b01Empresas, on_delete=models.CASCADE)
    tipo = models.PositiveSmallIntegerField(default=1)
    banco = models.ForeignKey(a27Bancos, on_delete=models.CASCADE)
    agencia = models.CharField(max_length=6)
    tipooper = models.CharField(max_length=10)
    noconta = models.CharField(max_length=20)
    objetos = models.Manager()

    def __str__(self):
        return self.descricao

    def permitidos(self, codusr):
        comando = "SELECT main_b03ctascaixa.* " \
            "FROM main_b03ctascaixa " \
            "INNER JOIN main_c04cxasperm ON main_b03ctascaixa.id = main_c04cxasperm.ctacaix_id " \
            "WHERE (main_c04cxasperm.usuario_id=" + str(codusr) + ");"
        try:
            pesquisa = self.objetos.raw(comando)
            return pesquisa
        except self.DoesNotExist:
            return None


class b04CCustos(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    empresa = models.ForeignKey(b01Empresas, on_delete=models.CASCADE)
    funccc = models.PositiveSmallIntegerField()
    descricao = models.CharField(max_length=255)
    ativo = models.BooleanField(default=True)
    seqmfhol = models.PositiveSmallIntegerField(default=2)
    objetos = models.Manager()

    def __str__(self):
        return self.descricao
 
    def permitidos(self, codusr, ativos):
        comando = "SELECT main_b04ccustos.* " \
            "FROM (main_b01empresas " \
            "INNER JOIN main_c03empsperms ON main_b01empresas.id = main_c03empsperms.empresa_id) " \
                  "INNER JOIN main_b04ccustos ON main_b01empresas.id = main_b04ccustos.empresa_id "\
                  "WHERE (main_c03empsperms.usuario_id=" + str(codusr) + ")"
        if ativos == 1:
            comando += " AND (main_b04ccustos.ativo=True)"
        elif ativos == 0:
            comando += " AND (main_b04ccustos.ativo=False)"
        comando += ";"
        try:
            pesquisa = self.objetos.raw(comando)
            return pesquisa
        except self.DoesNotExist:
            return None


class b05VinCtCxas(models.Model):
    ctcxa = models.ForeignKey(b03CtasCaixa, on_delete=models.CASCADE)
    empresa = models.ForeignKey(b01Empresas, on_delete=models.CASCADE)
    ccentr = models.ForeignKey(b04CCustos, on_delete=models.CASCADE, related_name='ccustoentrada')
    ctaentr = models.ForeignKey(b02PlContas, on_delete=models.CASCADE, related_name='contaentrada')
    ccsaid = models.ForeignKey(b04CCustos, on_delete=models.CASCADE, related_name='ccustosaida')
    ctasaid = models.ForeignKey(b02PlContas, on_delete=models.CASCADE, related_name='contasaida')


class b06CtasTpMovFin(models.Model):
    tpmovfin = models.ForeignKey(a29TipsMovFin, on_delete=models.CASCADE)
    empresa = models.ForeignKey(b01Empresas, on_delete=models.CASCADE)
    ctamov = models.ForeignKey(b02PlContas, on_delete=models.CASCADE, related_name='contamovim')
    ctasdo = models.ForeignKey(b02PlContas, on_delete=models.CASCADE, related_name='contasaldo')


class b07CtasPlPgtos(models.Model):
    plano = models.ForeignKey(a19PlsPgtos, on_delete=models.CASCADE)
    empresa = models.ForeignKey(b01Empresas, on_delete=models.CASCADE)
    ctcxa = models.ForeignKey(b03CtasCaixa, on_delete=models.CASCADE)
    ctasdo = models.ForeignKey(b02PlContas, on_delete=models.CASCADE)


class b08CtasMfHoler(models.Model):
    itholer = models.ForeignKey(a30ItHoler, on_delete=models.CASCADE)
    empresa = models.ForeignKey(b01Empresas, on_delete=models.CASCADE)
    ctalanc = models.ForeignKey(b02PlContas, on_delete=models.CASCADE)


class b09ProdCCusto(models.Model):
    ccusto = models.ForeignKey(b04CCustos, on_delete=models.CASCADE)
    catins = models.ForeignKey(a10CatsInsumos, on_delete=models.CASCADE)
    relac = models.PositiveSmallIntegerField()  # Soma de: Compra (1), Venda (2), Producao (4)
    estmp = models.BooleanField(default=False)
    estvd = models.BooleanField(default=True)
    ctapri = models.ForeignKey(b02PlContas, on_delete=models.CASCADE, related_name='contaprincipal')
    ctafre = models.ForeignKey(b02PlContas, on_delete=models.CASCADE, related_name='contafrete')
    ctades = models.ForeignKey(b02PlContas, on_delete=models.CASCADE, related_name='contadesconto')


class b10LicAprend(models.Model):
    id = models.IntegerField(primary_key=True)
    datlic = models.DateField(null=False)
    explic = models.CharField(max_length=255)


# Dados dos Usuarios

class c01Usuarios(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    nomeusr = models.CharField(max_length=200)
    fone = models.CharField(max_length=30)
    genero = models.PositiveSmallIntegerField(default=1)
    ativo = models.BooleanField(default=True)
    nivel = models.PositiveSmallIntegerField(default=1)
    emppad = models.PositiveSmallIntegerField(default=0)
    ccpad = models.PositiveSmallIntegerField(default=0)
    cxapad = models.PositiveSmallIntegerField(default=0)
    ctapad = models.IntegerField(default=0)
    dadcad = models.IntegerField(default=0)
    nomecomp = models.CharField(max_length=255)
    senha = models.CharField(max_length=20)
    objetos = models.Manager()

    def __str__(self):
        return self.nomeusr

    def codUser(self, nomeUser):
        try:
            userEsc = self.objetos.get(nomeusr=nomeUser)
            codUser = userEsc.id
            return codUser
        except self.DoesNotExist:
            return None


class c02CmdsPerms(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    usuario = models.ForeignKey(c01Usuarios, on_delete=models.CASCADE)
    comando = models.ForeignKey(a01Comandos, on_delete=models.CASCADE)
    objetos = models.Manager()


class c03EmpsPerms(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    usuario = models.ForeignKey(c01Usuarios, on_delete=models.CASCADE)
    empresa = models.ForeignKey(b01Empresas, on_delete=models.CASCADE)
    nivperm = models.PositiveSmallIntegerField(default=1)
    restrcc = models.PositiveIntegerField(default=0, null=True)
    rstctcx = models.PositiveIntegerField(default=0, null=True)


class c04CxasPerm(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    usuario = models.ForeignKey(c01Usuarios, on_delete=models.CASCADE)
    ctacaix = models.ForeignKey(b03CtasCaixa, on_delete=models.CASCADE, related_name='cxaper')


# Dados do Patrimonio das Empresas

class d01Patrim(models.Model):
    id = models.IntegerField(primary_key=True)
    empresa = models.ForeignKey(b01Empresas, on_delete=models.CASCADE)
    ccusto = models.ForeignKey(b04CCustos, on_delete=models.CASCADE)
    insumo = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    tipo = models.PositiveSmallIntegerField(default=1)
    codigo = models.CharField(max_length=20)
    descres = models.CharField(max_length=255)
    desccom = models.TextField(null=False)
    dtcompra = models.DateField(null=True)
    vlrcompra = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    vlrcontab = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    vlrmercad = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    vendido = models.BooleanField(default=False)
    dtvenda = models.DateField(null=True)
    vlrvenda = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    observ = models.CharField(max_length=255, null=True)
    objetos = models.Manager()

    def __str__(self):
        return self.codeap

    def permitidos(self, codusr, ativos):
        comando = "SELECT main_d01patrim.* " \
                  "FROM ((main_b01empresas  " \
                  "INNER JOIN main_c03empsperms ON main_b01empresas.id = main_c03empsperms.empresa_id) " \
                  "INNER JOIN main_b04ccustos ON main_b01empresas.id = main_b04ccustos.empresa_id) " \
                  "INNER JOIN main_d01patrim ON main_b04ccustos.id = main_d01patrim.ccusto_id " \
                  "WHERE (main_c03empsperms.usuario_id=" + str(codusr) + ") "
        if ativos == 1:
            comando += "AND (main_b04ccustos.ativo=True) "
        elif ativos == 0:
            comando += "AND (main_b04ccustos.ativo=False) "
        comando += "ORDER BY main_d01patrim.ccusto_id, main_d01patrim.id;"
        try:
            pesquisa = self.objetos.raw(comando)
            return pesquisa
        except self.DoesNotExist:
            return None


class d02DetImoveis(models.Model):
    patrim = models.OneToOneField(d01Patrim, on_delete=models.CASCADE)
    subtipo = models.PositiveSmallIntegerField(default=1)
    lograd = models.ForeignKey(a06Lograds, on_delete=models.CASCADE)
    complend = models.CharField(max_length=255)
    vlrvenal = models.DecimalField(max_digits=12, decimal_places=2, null=True)


class d03DetVeics(models.Model):
    patrim = models.OneToOneField(d01Patrim, on_delete=models.CASCADE)
    marca = models.CharField(max_length=25)
    modelo = models.CharField(max_length=40)
    cor = models.CharField(max_length=25)
    anofab = models.SmallIntegerField(null=True)
    anomod = models.SmallIntegerField(null=True)
    cappot = models.CharField(max_length=20)
    combust = models.PositiveSmallIntegerField(default=1)  # 1 - Diesel, 2 - Gasolina, 3 - Etanol, 4 - Flex, 5 - GNV
    renavan = models.CharField(max_length=15)
    chassi = models.CharField(max_length=20)
    status = models.PositiveSmallIntegerField(default=1)


class d04DetEqptos(models.Model):
    patrim = models.OneToOneField(d01Patrim, on_delete=models.CASCADE)
    marca = models.CharField(max_length=25)
    modelo = models.CharField(max_length=40)
    cor = models.CharField(max_length=25)
    serie = models.CharField(max_length=25)
    anofab = models.SmallIntegerField(null=True)
    anomod = models.SmallIntegerField(null=True)
    cappot = models.CharField(max_length=20)
    combust = models.PositiveSmallIntegerField(default=1)  # ..., 6 - Eletrico, 7 - Gasolina + Oleo 2T
    renavan = models.CharField(max_length=15)
    status = models.PositiveSmallIntegerField(default=1)  # 1 - disp, 2 - alocado, 3 - em manut, 4 - vendido
    vlrlocdia = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    vlrlocmes = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    vlrcaucao = models.DecimalField(max_digits=10, decimal_places=2, null=True)


class d05DetMoveis(models.Model):
    patrim = models.OneToOneField(d01Patrim, on_delete=models.CASCADE)
    marca = models.CharField(max_length=25)
    modelo = models.CharField(max_length=40)
    serie = models.CharField(max_length=25)
    status = models.PositiveSmallIntegerField(default=1)  # 1 - disp, 2 - alocado, 3 - em manut, 4 - vendido


class d06AvisPatrim(models.Model):
    id = models.IntegerField(primary_key=True)
    patrim = models.ForeignKey(d01Patrim, on_delete=models.CASCADE)
    dtavis = models.DateField()
    odomavis = models.DecimalField(max_digits=8, decimal_places=1, null=True)
    aviso = models.CharField(max_length=255)
    resolvido = models.BooleanField(default=False)
    dtconcl = models.DateField(null=True)
    odomsol = models.DecimalField(max_digits=8, decimal_places=1, null=True)


class d07MovsPatrim(models.Model):
    id = models.IntegerField(primary_key=True)
    ccorig = models.ForeignKey(b04CCustos, on_delete=models.CASCADE, related_name='ccustoorigem')
    ccdest = models.ForeignKey(b04CCustos, on_delete=models.CASCADE, related_name='ccustodestino')
    tipo = models.PositiveSmallIntegerField(default=1)
    dtmov = models.DateField()
    dtprevdev = models.DateField()


class d08ItsMovsPatr(models.Model):
    movpatrim = models.ForeignKey(d07MovsPatrim, on_delete=models.CASCADE)
    patrim = models.ForeignKey(d01Patrim, on_delete=models.CASCADE)


# Dados dos Clientes, Colaboradores e Fornecedores

class e01Cadastros(models.Model):
    id = models.IntegerField(primary_key=True)
    usrcad = models.ForeignKey(User, on_delete=models.CASCADE)
    descrcad = models.CharField(max_length=255)
    juridica = models.BooleanField()
    razao = models.CharField(max_length=255)
    fantasia = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=14, blank=True, null=True)
    inscest = models.CharField(max_length=30, blank=True, null=True)
    orgaorg = models.CharField(max_length=30, null=True)
    dtemisrg = models.DateField(null=True)
    dtnascimento = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    genero = models.PositiveSmallIntegerField(default=0)  # 0 - Nao Informado, 1 - Masculino, 2 - Feminino
    nacionalid = models.CharField(max_length=40, null=True)
    dtchegada = models.DateField(null=True)
    naturalid = models.ForeignKey(a04Municipios, on_delete=models.CASCADE, default=0)
    nomepai = models.CharField(max_length=255, null=True)
    nomemae = models.CharField(max_length=255, null=True)
    estadocivil = models.SmallIntegerField(default=0)
    contemerg = models.CharField(max_length=100, null=True)
    ramoatv = models.CharField(max_length=255, blank=True, null=True)
    observs = models.TextField(blank=True, null=True)
    classificacao = models.PositiveSmallIntegerField(blank=True, null=True)
    selecionado = models.BooleanField(blank=True, null=True)
    indicadopor = models.CharField(max_length=50, blank=True, null=True)
    codref = models.CharField(max_length=20, blank=True, null=True)
    tipo = models.PositiveSmallIntegerField(blank=True, null=True)
    dtincl = models.DateField(auto_now=False, auto_now_add=True, blank=True, null=True)
    ativo = models.BooleanField(default=True, null=True)
    contempresa = models.CharField(max_length=255, blank=True, null=True)
    objetos = models.Manager()

    def __str__(self):
        return self.razao

    def proxnumcad(self):
        ultcad = self.objetos.all().values_list('id', flat=True)
        if bool(ultcad):
            maiorvalor = max(ultcad)
            return maiorvalor + 1
        else:
            return 1

    def possiveisclientes(self, nomepesq):
        try:
            coringa = chr(37) + nomepesq + chr(37)
            comando = "SELECT fantasia, razao, main_e01cadastros.id AS id, main_e01cadastros.descrcad AS descricao, " \
                      "numero, LEFT(numero, 2) AS DDD, " \
                      "MID(numero,3,CHAR_LENGTH(numero)-6) AS PriParte, RIGHT(numero, 4) AS UltPart  " \
                      "FROM main_e01cadastros Left Join main_e02fonescad " \
                      "On main_e02fonescad.cadastro_id = main_e01cadastros.id WHERE (razao like %s);"
            possiveis = self.objetos.raw(comando, [coringa])
            return possiveis
        except self.DoesNotExist:
            return None

    def nometratcliente(self, codclie):
        try:
            clienteesc = self.objetos.get(id=codclie)
            nometrat = clienteesc.fantasia + ' ' + clienteesc.razao
            return nometrat
        except self.DoesNotExist:
            return None

    def colabspermitidos(self, codusr, ativos):
        comando = "SELECT main_e07dadcol.ccusto_id, main_e01cadastros.* " \
                  "FROM main_e01cadastros  " \
                  "INNER JOIN (((main_b01empresas INNER JOIN main_c03empsperms ON main_b01empresas.id = " \
                  "main_c03empsperms.empresa_id) INNER JOIN main_b04ccustos ON main_b01empresas.id = " \
                  "main_b04ccustos.empresa_id) INNER JOIN main_e07dadcol ON main_b04ccustos.id = " \
                  "main_e07dadcol.ccusto_id) ON main_e01cadastros.id = main_e07dadcol.cadastro_id " \
                  "WHERE (main_c03empsperms.usuario_id=" + str(codusr) + ") "
        if ativos == 1:
            comando += "AND (main_b04ccustos.ativo=True) AND (main_e07dadcol.statusat<3) "
        elif ativos == 0:
            comando += "AND (main_b04ccustos.ativo=False) AND (main_e07dadcol.statusat>2) "
        comando += "ORDER BY main_e07dadcol.ccusto_id, main_e01cadastros.descrcad;"
        try:
            pesquisa = self.objetos.raw(comando)
            return pesquisa
        except self.DoesNotExist:
            return None


class e02FonesCad(models.Model):
    id = models.IntegerField(primary_key=True)
    cadastro = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    tipfone = models.ForeignKey(a09TiposFone, on_delete=models.CASCADE)
    numero = models.CharField(max_length=12)
    objetos = models.Manager()

    def __str__(self):
        return self.numero

    def proxnumfone(self):
        ultcad = self.objetos.all().values_list('id', flat=True)
        if bool(ultcad):
            maiorvalor = max(ultcad)
            return maiorvalor + 1
        else:
            return 1

    def numjacadastrado(self, numproc):
        numpuro = numpurotelefone(numproc)
        listanum = self.objetos.filter(numero=numpuro)
        valores = listanum.values_list('cadastro', flat=True)
        if len(listanum) > 0:
            codcad = valores[0]
            return codcad
        else:
            return 0

    def fonescad(self, codclie):
        try:
            return self.objetos.filter(cadastro=codclie).values_list('numero', flat=True)
        except self.DoesNotExist:
            return None

    def novofonecad(self, codclie, numtelefone):
        novcodfone = self.proxnumfone(self)
        novofone = self(
            id=novcodfone,
            cadastro=e01Cadastros.objetos.get(id=codclie),
            tipfone=a09TiposFone.objetos.get(id=1),
            numero=numpurotelefone(numtelefone)
        )
        novofone
        novofone.save()


class e03WebCad(models.Model):
    id = models.IntegerField(primary_key=True)
    cadastro = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    tipo = models.PositiveSmallIntegerField(default=1)  # 1 para e-mail e 2 para site
    endweb = models.CharField(max_length=50)
    objetos = models.Manager()

    def __str__(self):
        return self.endweb

    def proxnumweb(self):
        ultcad = self.objetos.all().values_list('cadastro', flat=True)
        if bool(ultcad):
            maiorvalor = max(ultcad)
            return maiorvalor + 1
        else:
            return 1

    def emailjacadastrado(self, emailproc):
        listaemails = self.objetos.filter(endweb=emailproc)
        if len(listaemails) > 0:
            return self.first.cadastro.id
        else:
            return 0

    def emailscad(self, codclie):
        try:
            return self.objetos.get(cadastro=codclie)
        except self.DoesNotExist:
            return None

    def novoemail(self, codclie, endemail):
        novocodweb = self.proxnumweb(self)
        novoemail = self(
            id=novocodweb,
            cadastro=e01Cadastros.objetos.get(id=codclie),
            tipo=1,
            endweb=endemail
        )
        novoemail.save()


class e04EndCad(models.Model):
    id = models.IntegerField(primary_key=True)
    cadastro = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    tipend = models.ForeignKey(a07TiposEnd, on_delete=models.CASCADE)
    lograd = models.ForeignKey(a06Lograds, on_delete=models.CASCADE)
    complend = models.CharField(max_length=255, blank=True, null=True)
    cxpostal = models.CharField(max_length=20, blank=True, null=True)
    disponib = models.CharField(max_length=255, blank=True, null=True)
    objetos = models.Manager()

    def __str__(self):
        return self.complend

    def proxnumcad(self):
        ultcad = self.objetos.all().values_list('id', flat=True)
        if bool(ultcad):
            maiorvalor = max(ultcad)
            return maiorvalor + 1
        else:
            return 1

    def enderecoscad(self, codclie):
        try:
            comando = "SELECT estado_id, municipio, bairro, logradouro, complend, main_e04endcad.id " \
                      "FROM main_e04endcad " \
                      "INNER JOIN main_a06lograds ON main_e04endcad.lograd_id = main_a06lograds.id " \
                      "INNER JOIN main_a05bairros ON main_a06lograds.bairro_id = main_a05bairros.id " \
                      "INNER JOIN main_a04municipios ON main_a05bairros.municipio_id = main_a04municipios.id " \
                      "WHERE main_e04endcad.cadastro_id = %s;"
            possiveis = self.objetos.raw(comando, [codclie])
            return possiveis
        except self.DoesNotExist:
            return None

    def enderecocompletocad(self, codend):
        endcadastrado = self.objetos.get(pk=codend)
        logradcad = a06Lograds.objetos.get(pk=endcadastrado.lograd_id)
        bairrocad = a05Bairros.objetos.get(pk=logradcad.bairro_id)
        municipcad = a04Municipios.objetos.get(pk=bairrocad.municipio_id)
        completo = logradcad.logradouro + ', ' + endcadastrado.complend
        completo = completo + ', ' + bairrocad.bairro + ', ' + municipcad.municipio + '-' + municipcad.estado_id
        return completo


class e05CtaBcaCad(models.Model):
    id = models.IntegerField(primary_key=True)
    cadastro = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    banco = models.ForeignKey(a27Bancos, on_delete=models.CASCADE)
    agencia = models.CharField(max_length=10)
    tipo = models.CharField(max_length=10)
    nocta = models.CharField(max_length=20)
    ctaprinc = models.BooleanField()
    objetos = models.Manager()

    def __str__(self):
        return self.banco.id + " - Ag. " + self.agencia + " - " + self.tipo + " - No. " + self.nocta


class e06ContCad(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    empresa = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE, related_name='empresacad')
    contato = models.DecimalField(max_digits=10, decimal_places=0)
    titulo = models.CharField(max_length=20, null=True, blank=True)
    cargo = models.CharField(max_length=100, null=True, blank=True)
    objetos = models.Manager()


class e07DadCol(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    cadastro = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    empresa = models.ForeignKey(b01Empresas, on_delete=models.CASCADE)
    ccusto = models.ForeignKey(b04CCustos, on_delete=models.CASCADE)
    codcontrforn = models.PositiveIntegerField(null=True) #  Codigo do Contrato de Fornecimento, qdo for o caso
    turma = models.CharField(max_length=30, null=True)
    noreg = models.IntegerField(null=True)
    funcao = models.ForeignKey(a21RhFuncoes, on_delete=models.CASCADE)
    sindicato = models.ForeignKey(a22RhSindicatos, on_delete=models.CASCADE)
    ordcontr = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    regtrab = models.ForeignKey(a23RhRegTrab, on_delete=models.CASCADE)
    opadint = models.BooleanField(default=False)
    dtadmissao = models.DateField()
    vinculo = models.SmallIntegerField(default=0)  # Desligado (0), CLT (1), Diarista (2), P. Serv. (3), Afast. (4)
    durctexp = models.SmallIntegerField(default=0)
    proctexp = models.SmallIntegerField(default=0)
    statusat = models.PositiveSmallIntegerField(default=0)
    motafast = models.PositiveSmallIntegerField(default=0)
    dtafastam = models.DateField(null=True)
    prevretor = models.DateField(null=True)
    qtvtdia = models.SmallIntegerField(default=0)
    nocartvt = models.CharField(max_length=40, null=True)
    planosaude = models.ForeignKey(a24RhPlSaude, on_delete=models.CASCADE)
    alojado = models.BooleanField(default=False)
    tamcamis = models.CharField(max_length=10, null=True)
    tamcalca = models.CharField(max_length=10, null=True)
    tambutin = models.CharField(max_length=10, null=True)
    grauinstr = models.SmallIntegerField(default=0)
    conselho = models.CharField(max_length=20, null=True)
    nopis = models.CharField(max_length=20, null=True)
    nocnh = models.CharField(max_length=20, null=True)
    catcnh = models.CharField(max_length=5, null=True)
    valcnh = models.DateField(null=True)
    notiteleit = models.CharField(max_length=20, null=True)
    zontiteleit = models.CharField(max_length=10, null=True)
    sectiteleit = models.CharField(max_length=10, null=True)
    noctps = models.CharField(max_length=20, null=True)
    serctps = models.CharField(max_length=20, null=True)
    expctps = models.DateField(null=True)
    noreserv = models.CharField(max_length=30, null=True)
    antcrimin = models.CharField(max_length=40, null=True)
    arqdocs = models.CharField(max_length=30, null=True)
    objetos = models.Manager()


class e08DepCol(models.Model):
    id = models.IntegerField(primary_key=True)
    cadastro = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255, null=True)
    vinculo = models.SmallIntegerField(default=2)
    dtnascim = models.DateField(null=True)
    partplsaude = models.BooleanField(default=False)


class e09RefCol(models.Model):
    id = models.IntegerField(primary_key=True)
    cadastro = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    nomeempresa = models.CharField(max_length=255, null=True)
    foneempresa = models.CharField(max_length=12, null=True)
    dtiniemp = models.DateField(null=True)
    dtafaemp = models.DateField(null=True)
    motivoafa = models.CharField(max_length=255, null=True)
    observs = models.CharField(max_length=255, null=True)


class e10HabCol(models.Model):
    id = models.IntegerField(primary_key=True)
    cadastro = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    habilidade = models.ForeignKey(a25RhHabilid, on_delete=models.CASCADE)


class e11ExamCol(models.Model):
    id = models.IntegerField(primary_key=True)
    vinculo = models.ForeignKey(e07DadCol, on_delete=models.CASCADE)
    motivo = models.SmallIntegerField(default=1)
    descricao = models.CharField(max_length=255)
    dtrealiz = models.DateField()
    dtvencim = models.DateField()
    ativo = models.BooleanField()


class e12EpisCol(models.Model):
    id = models.IntegerField(primary_key=True)
    vinculo = models.ForeignKey(e07DadCol, on_delete=models.CASCADE)
    epientr = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    dtentr = models.DateField()
    qtdentr = models.DecimalField(max_digits=6, decimal_places=2, null=True)


class e13LanAutCol(models.Model):
    id = models.IntegerField(primary_key=True)
    vinculo = models.ForeignKey(e07DadCol, on_delete=models.CASCADE)
    itholeri = models.ForeignKey(a30ItHoler, on_delete=models.CASCADE)


class e14TreinCol(models.Model):
    id = models.IntegerField(primary_key=True)
    cadastro = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    treinamento = models.ForeignKey(a26RhTreinam, on_delete=models.CASCADE)
    aproveit = models.DecimalField(max_digits=6, decimal_places=2, null=True)


class e15PtoCol(models.Model):
    id = models.IntegerField(primary_key=True)
    vinculo = models.ForeignKey(e07DadCol, on_delete=models.CASCADE)
    dia = models.DateField(null=False)
    tphist = models.SmallIntegerField(default=1)  # Normal (1), Fer. Trab (2), Fer. N.T. (3), Folga (4), Atest. (5)
    hrini = models.TimeField(null=True)
    hrint = models.TimeField(null=True)
    hrrec = models.TimeField(null=True)
    hrfin = models.TimeField(null=True)
    tpcalhn = models.SmallIntegerField(default=1)  # Horas Normais (1), Banco de Horas (2)
    tpcalhe = models.SmallIntegerField(default=1)  # H.E. 50% (1), H.E. 60% (2), H.E. 100% (3), Bco. Horas (4)


class e16HolCol(models.Model):
    id = models.IntegerField(primary_key=True)
    vinculo = models.ForeignKey(e07DadCol, on_delete=models.CASCADE)
    refer = models.IntegerField(null=False)
    dtini = models.DateField(null=False)
    dtfin = models.DateField(null=False)
    regtrab = models.ForeignKey(a23RhRegTrab, on_delete=models.CASCADE)


class e17ItHolCol(models.Model):
    id = models.IntegerField(primary_key=True)
    holerite = models.ForeignKey(e16HolCol, on_delete=models.CASCADE)
    itempad = models.ForeignKey(a30ItHoler, on_delete=models.CASCADE)
    paramad = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True)


# Dados dos Contratos de Fornecimento


class f01ContrForn(models.Model):
    id = models.IntegerField(primary_key=True)
    conttant = models.ForeignKey(b01Empresas, on_delete=models.CASCADE)
    conttado = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    desccont = models.CharField(max_length=255, null=True)
    objcontr = models.CharField(max_length=255, null=True)
    tiporemu = models.PositiveSmallIntegerField(default=1)
    prazcont = models.IntegerField(default=0)
    dtaassin = models.DateField(null=False)
    contratv = models.BooleanField(default=True)


class f02ItContForn(models.Model):
    id = models.IntegerField(primary_key=True)
    contrato = models.ForeignKey(f01ContrForn, on_delete=models.CASCADE)
    insuforn = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    unidforn = models.CharField(max_length=10, null=True)
    vlrunite = models.DecimalField(max_digits=12, decimal_places=4, null=True, default=0)


class f03MedContForn(models.Model):
    id = models.IntegerField(primary_key=True)
    respons = models.ForeignKey(c01Usuarios, on_delete=models.CASCADE)
    dtinimd = models.DateField(null=False)
    dtfinmd = models.DateField(null=False)
    faturad = models.BooleanField(default=False)


class f04ItMedContForn(models.Model):
    itcontr = models.ForeignKey(f02ItContForn, on_delete=models.CASCADE)
    qtdemed = models.DecimalField(max_digits=12, decimal_places=4, null=True, default=0)


# Dados dos Orcamentos

class g01Orcamento(models.Model):
    id = models.IntegerField(primary_key=True)
    ccusto = models.ForeignKey(b04CCustos, on_delete=models.CASCADE)
    vended = models.ForeignKey(c01Usuarios, on_delete=models.CASCADE)
    fase = models.ForeignKey(a31FaseOrc, on_delete=models.CASCADE)
    plpgto = models.ForeignKey(a19PlsPgtos, on_delete=models.CASCADE)
    ender = models.ForeignKey(e04EndCad, on_delete=models.CASCADE)
    dtorc = models.DateField(auto_now=False, auto_now_add=True)
    dtval = models.DateField(auto_now=False, auto_now_add=True)
    prazo = models.PositiveSmallIntegerField()
    vlrprod = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    tipofrete = models.ForeignKey(a08TiposFrete, on_delete=models.CASCADE)
    distfrete = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    vlrfret = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    vlrdesc = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    vlrout = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    vlrbdi = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    descout = models.CharField(max_length=255, null=True)
    status = models.ForeignKey(a20StsOrcs, on_delete=models.CASCADE)
    orcsubst = models.IntegerField(null=True)
    gerouprop = models.BooleanField(null=True)
    observ = models.TextField(null=True)
    tipoorc = models.SmallIntegerField(default=2)  # 1 - Venda; 2 - Instalações (sem CC); 3 - Obras (com CC)
    objetos = models.Manager()

    def __str__(self):
        return str(self.id)

    def proxnumorc(self):
        ultorc = self.objetos.all().values_list('id', flat=True)
        if bool(ultorc):
            maiorvalor = max(ultorc)
            return maiorvalor + 1
        else:
            return 1

    def pendentes(self, codusuario, tipopend):
        try:
            comando = "SELECT main_g01orcamento.id, main_g01orcamento.dtorc, main_g01orcamento.dtval, " + \
                    "main_e01cadastros.razao AS razCliente, main_a19plspgtos.descricao AS plPgto, " \
                    "main_a20stsorcs.descricao AS stsOrc, " + \
                    "concat(repeat('0',3-length(main_g01orcamento.id)),main_g01orcamento.id) AS NumOrc " + \
                    "FROM main_g01orcamento " + \
                    "INNER JOIN main_e04endcad ON main_e04endcad.id = main_g01orcamento.ender_id " + \
                    "INNER JOIN main_e01cadastros ON main_e01cadastros.id = main_e04endcad.cadastro_id " + \
                    "INNER JOIN main_a19plspgtos ON main_a19plspgtos.id = main_g01orcamento.plpgto_id " + \
                    "INNER JOIN main_a20stsorcs ON main_a20stsorcs.id = main_g01orcamento.status_id " + \
                    "WHERE (main_g01orcamento.vended_id = %s) AND (main_g01orcamento.tipo = %s) " + \
                    "ORDER BY main_g01orcamento.dtorc, main_g01orcamento.id;"
            possiveis = self.objetos.raw(comando, [codusuario, tipopend])
            return possiveis
        except self.DoesNotExist:
            return None


    def lista_atualizada_insumos(self, codorcam):
        lista_de_atividades_eap = g03EapOrc.objetos.filter(
            orcamento_id=g01Orcamento.objetos.get(id=codorcam), tipo=1)
        lista_de_insumos = [g05InsEAP.objetos.filter(eap_id=eap.id) for eap in lista_de_atividades_eap]
        return lista_de_insumos
    
    # essa versão foi descontinuada em 22-07-2020
    def listaatualizadainsumos(self, codorcam):
        try:
            comando = "SELECT main_g01orcamento.id, main_g05inseap.insumo_id, " + \
                    "sum(main_g05inseap.qtdprod) as totQtProd, sum(main_g05inseap.qtdimpr) as totQtImp, " + \
                    "avg(main_g05inseap.cstunpr) as medCstProd, avg(main_g05inseap.cstunim) as medCstImp " + \
                    "FROM main_g01orcamento " + \
                    "INNER JOIN main_g03eaporc ON main_g03eaporc.orcamento_id = main_g01orcamento.id " + \
                    "INNER JOIN main_g04atveap ON main_g04atveap.eap_id = main_g03eaporc.id " + \
                    "INNER JOIN main_g05inseap ON main_g05inseap.atividade_id = main_g04atveap.id " + \
                    "GROUP BY main_g01orcamento.id, main_g05inseap.insumo_id " + \
                    "HAVING main_g01orcamento.id= %s " + \
                    "ORDER BY main_g01orcamento.id, main_g05inseap.insumo_id;"
            lista = self.objetos.raw(comando, [codorcam])
            return lista
        except self.DoesNotExist:
            return None


class g02ItOrc(models.Model):
    orcamento = models.ForeignKey(g01Orcamento, on_delete=models.CASCADE)
    insumo = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    qtdprod = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    qtdimpr = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    cstunpr = models.DecimalField(max_digits=12, decimal_places=4, default=0, null=True)
    cstunim = models.DecimalField(max_digits=12, decimal_places=4, default=0, null=True)
    objetos = models.Manager()

    def __str__(self):
        return self.insumo.descricao

    def apresentarListaOrc(self, codorcam):
        try:
            comando = "SELECT main_g02itorc.id, main_g02itorc.insumo_id, main_a11insumos.codigo AS codigo, " + \
                      "main_a11insumos.descricao AS descricao, main_a11insumos.undbas AS undBas, main_a10catsinsumos.tipo, " + \
                      "main_g02itorc.qtdprod AS qtdProd, main_g02itorc.cstunpr AS cstUnPr, main_g02itorc.qtdimpr AS qtdImpr, " + \
                      "main_g02itorc.cstunim AS cstUnImpr, (main_g02itorc.qtdprod * main_g02itorc.cstunpr + " + \
                      "main_g02itorc.qtdimpr * main_g02itorc.cstunim) AS vlrTotal " + \
                      "FROM main_g02itorc  " + \
                      "INNER JOIN main_a11insumos ON main_a11insumos.id = main_g02itorc.insumo_id " + \
                      "INNER JOIN main_a10catsinsumos ON main_a10catsinsumos.id = main_a11insumos.catins_id " + \
                      "WHERE orcamento_id = %s " + \
                      "ORDER BY main_a11insumos.codigo;"
            lista = self.objetos.raw(comando, [codorcam])
            return lista
        except self.DoesNotExist:
            return None


class g03EapOrc(models.Model):
    id = models.IntegerField(primary_key=True)
    orcamento = models.ForeignKey(g01Orcamento, on_delete=models.CASCADE)
    codeap = models.CharField(max_length=30)
    coditem = models.CharField(max_length=20)
    descitem = models.CharField(max_length=255)
    tipo = models.PositiveSmallIntegerField()
    qtdorc = models.DecimalField(max_digits=12, decimal_places=4, null=True, default=0)
    unidade = models.CharField(max_length=20, null=True, default="-")
    vlrunit = models.DecimalField(max_digits=12, decimal_places=4, null=True, default=0)
    cstser = models.DecimalField(max_digits=12, decimal_places=4, null=True, default=0)
    cstmat = models.DecimalField(max_digits=12, decimal_places=4, null=True, default=0)
    cstdistindi = models.DecimalField(max_digits=12, decimal_places=4, null=True, default=0)
    cstdistrisc = models.DecimalField(max_digits=12, decimal_places=4, null=True, default=0)
    cstdistbdi = models.DecimalField(max_digits=12, decimal_places=4, null=True, default=0)
    cstpatvpad = models.BooleanField(default=True)
    objetos = models.Manager()

    def __str__(self):
        return self.descitem

    def proxnumeap(self):
        #ult_eap = self.objetos.all().values_list('id', flat=True)
        try:
            ult_eap = self.objetos.latest('id').id
            if ult_eap:
                return ult_eap + 1
            else:
                return 1
        except:
            ult_eap = self.objetos.all().values_list('id', flat=True)
            if bool(ult_eap):
                maior_valor = max(ult_eap)
                return maior_valor + 1
            else:
                return 1

    def exibir(self, codOrc, nivelExib):
        try:
            comando = "SELECT main_g03eaporc.id, main_g03eaporc.codeap, main_g03eaporc.descitem, " + \
                    "CAST(main_g03eaporc.qtdorc AS DECIMAL(12,2)), main_g03eaporc.unidade, CAST(main_g03eaporc.vlrunit AS DECIMAL(12,2)), " + \
                    "main_g03eaporc.qtdorc * main_g03eaporc.vlrunit AS vlrtot, main_g03eaporc.tipo, " + \
                    " if(main_g03eaporc.tipo=2,'D','') as Detalhe FROM main_g03eaporc " + \
                    "WHERE (main_g03eaporc.orcamento_id = %s) AND (main_g03eaporc.tipo >= %s) " + \
                    "ORDER BY main_g03eaporc.codeap;"
            possiveis = self.objetos.raw(comando, [codOrc, nivelExib])
            return possiveis
        except self.DoesNotExist:
            return None

    def custosservatveaporc(self, codorcam):
        try:
            comando = "SELECT main_g03eaporc.id, " + \
                    "Sum(main_g05inseap.qtdprod * main_g05inseap.cstunpr + main_g05inseap.qtdimpr * " + \
                    "main_g05inseap.cstunim) As CustoServAtiv FROM main_g05inseap " + \
                    "INNER JOIN main_g04atveap ON main_g04atveap.id = main_g05inseap.atividade_id " + \
                    "INNER JOIN main_g03eaporc ON main_g03eaporc.id = main_g04atveap.eap_id " + \
                    "INNER JOIN main_a11insumos ON main_a11insumos.id = main_g05inseap.insumo_id " + \
                    "INNER JOIN main_a10catsinsumos on main_a10catsinsumos.id = main_a11insumos.catins_id " + \
                    "GROUP BY main_g03eaporc.orcamento_id, main_g03eaporc.id, main_a10catsinsumos.tipo " + \
                    "HAVING main_g03eaporc.orcamento_id = %s and " + \
                    "(main_a10catsinsumos.tipo <> 3 AND main_a10catsinsumos.tipo <> 10); "
            custos = self.objetos.raw(comando, [codorcam])
            return custos
        except self.DoesNotExist:
            return None

    def custosmateatveaporc(self, codorcam):
        try:
            comando = "SELECT main_g03eaporc.id, " + \
                    "Sum(main_g05inseap.qtdprod * main_g05inseap.cstunpr + main_g05inseap.qtdimpr * " + \
                    "main_g05inseap.cstunim) As CustoMatAtiv FROM main_g05inseap " + \
                    "INNER JOIN main_g04atveap ON main_g04atveap.id = main_g05inseap.atividade_id " + \
                    "INNER JOIN main_g03eaporc ON main_g03eaporc.id = main_g04atveap.eap_id " + \
                    "INNER JOIN main_a11insumos ON main_a11insumos.id = main_g05inseap.insumo_id " + \
                    "INNER JOIN main_a10catsinsumos on main_a10catsinsumos.id = main_a11insumos.catins_id " + \
                    "GROUP BY main_g03eaporc.orcamento_id, main_g03eaporc.id, main_a10catsinsumos.tipo " + \
                    "HAVING main_g03eaporc.orcamento_id = %s and " + \
                    "(main_a10catsinsumos.tipo = 3 OR main_a10catsinsumos.tipo = 10); "
            custos = self.objetos.raw(comando, [codorcam])
            return custos
        except self.DoesNotExist:
            return None


class g04AtvEap(models.Model):
    id = models.IntegerField(primary_key=True)
    eap = models.ForeignKey(g03EapOrc, on_delete=models.CASCADE)
    atvpadr = models.ForeignKey(a15AtvsPad, on_delete=models.CASCADE)
    durativ = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    depativ = models.CharField(max_length=255, null=True)
    dtiniprev = models.DateField(auto_now=False, auto_now_add=True)
    dtfinprev = models.DateField(auto_now=False, auto_now_add=True)
    cstprev = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    cstprevser = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    cstprevmat = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    desconto = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    objetos = models.Manager()

    def proxnumatveap(self):
        ultatveap = self.objetos.all().values_list('id', flat=True)
        if bool(ultatveap):
            maiorvalor = max(ultatveap)
            return maiorvalor + 1
        else:
            return 1


class g05InsEAP(models.Model):
    eap = models.ForeignKey(g03EapOrc, on_delete=models.CASCADE)
    insumo = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    qtdprod = models.DecimalField(max_digits=12, decimal_places=4)
    qtdimpr = models.DecimalField(max_digits=12, decimal_places=4)
    cstunpr = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    cstunim = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    objetos = models.Manager()


class g06DetOrc(models.Model):
    orcamento = models.OneToOneField(g03EapOrc, on_delete=models.CASCADE, primary_key=True)
    modprop = models.CharField(max_length=255)
    incdestin = models.BooleanField()
    txtdestin = models.TextField()
    increfobr = models.BooleanField()
    txtrefobr = models.TextField()
    incprzentr = models.BooleanField()
    txtprzentr = models.TextField()
    incfrmpgt = models.BooleanField()
    txtfrmpgt = models.TextField()
    incassinat = models.BooleanField()
    txtassinat = models.TextField()
    objetivos = models.TextField()
    premissas = models.TextField()
    restricoes = models.TextField()
    escopogeral = models.TextField()
    outrasinfs = models.TextField()
    objetos = models.Manager()


class g07RiscOrc(models.Model):
    orcamento = models.ForeignKey(g03EapOrc, on_delete=models.CASCADE)
    risco = models.ForeignKey(a17RiscosCad, on_delete=models.CASCADE)
    fase = models.CharField(max_length=255)
    probestim = models.FloatField()
    impestim = models.DecimalField(max_digits=12, decimal_places=4)
    prioridade = models.PositiveSmallIntegerField()
    resposta = models.CharField(max_length=255)
    estrategia = models.PositiveSmallIntegerField()
    custoresp = models.DecimalField(max_digits=12, decimal_places=4)
    novaprob = models.FloatField()
    novoimpacto = models.DecimalField(max_digits=12, decimal_places=4)
    novaprior = models.PositiveSmallIntegerField()
    objetos = models.Manager()


class g08CstIndOrc(models.Model):
    orcamento = models.ForeignKey(g01Orcamento, on_delete=models.CASCADE)
    cstindir = models.ForeignKey(a18CstInd, on_delete=models.CASCADE)
    objetos = models.Manager()


class g09VisitasOrc(models.Model):
    id = models.IntegerField(primary_key=True)
    orcamento = models.ForeignKey(g01Orcamento, on_delete=models.CASCADE)
    data = models.DateField(null=False)
    hora = models.TimeField(null=False)
    tipovisita = models.IntegerField(null=False)
    pendente = models.BooleanField(default=True)
    objetos = models.Manager()


# Dados dos Contratos de Prestacao de Servicos das Empresas

class h01ContrPServ(models.Model):
    id = models.IntegerField(primary_key=True)
    ccustvinc = models.ForeignKey(b04CCustos, on_delete=models.CASCADE)
    tipservic = models.PositiveSmallIntegerField(default=1)
    numcontra = models.CharField(max_length=20)
    contratan = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    objtcontr = models.CharField(max_length=255)
    valrcontr = models.DecimalField(max_digits=12, decimal_places=4)
    przocontr = models.IntegerField(null=False, default=0)
    paracontr = models.IntegerField(null=False, default=0)
    orcamorig = models.ForeignKey(g01Orcamento, on_delete=models.CASCADE)
    dtassinat = models.DateField(null=True)
    codprojet = models.CharField(max_length=20, null=True)
    palchaves = models.CharField(max_length=255, null=True)
    procprinc = models.CharField(max_length=25, null=True)
    dtordserv = models.DateField(null=True)
    procmedic = models.CharField(max_length=25, null=True)
    dtultmedi = models.DateField(null=True)
    diretbase = models.CharField(max_length=255, null=True)
    objetos = models.Manager()


class h02DocsContr(models.Model):
    id = models.IntegerField(primary_key=True)
    tipodoc = models.PositiveSmallIntegerField(default=1)
    datadoc = models.DateField(null=True)
    numedoc = models.CharField(max_length=20)
    descdoc = models.CharField(max_length=255)
    valrdoc = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    contrato = models.ForeignKey(h01ContrPServ, on_delete=models.CASCADE)
    apdfdoc = models.CharField(max_length=255, null=True)


class h03EapContr(models.Model):
    id = models.IntegerField(primary_key=True)
    contrato = models.ForeignKey(h01ContrPServ, on_delete=models.CASCADE)
    codeap = models.CharField(max_length=30)
    coditem = models.CharField(max_length=20)
    descitem = models.CharField(max_length=255)
    tipo = models.PositiveSmallIntegerField()
    qtdcont = models.DecimalField(max_digits=12, decimal_places=4, null=True, default=0)
    unidade = models.CharField(max_length=20, null=True, default="-")
    vlrunit = models.DecimalField(max_digits=12, decimal_places=4, null=True, default=0)
    objetos = models.Manager()

    def __str__(self):
        return self.codeap

    def permitidos(self, codusr, ativos):
        comando = "SELECT main_h01contrpserv.ccustvinc_id, main_h03eapcontr.* " \
                  "FROM (((main_b01empresas  " \
                  "INNER JOIN main_c03empsperms ON main_b01empresas.id = main_c03empsperms.empresa_id) " \
                  "INNER JOIN main_b04ccustos ON main_b01empresas.id = main_b04ccustos.empresa_id) " \
                  "INNER JOIN main_h01contrpserv ON main_b04ccustos.id = main_h01contrpserv.ccustvinc_id) " \
                  "INNER JOIN main_h03eapcontr ON main_h01contrpserv.id = main_h03eapcontr.contrato_id " \
                  "WHERE (main_c03empsperms.usuario_id=" + str(codusr) + ") "
        if ativos == 1:
            comando += "AND (main_b04ccustos.ativo=True) "
        elif ativos == 0:
            comando += "AND (main_b04ccustos.ativo=False) "
        comando += "ORDER BY main_h01contrpserv.ccustvinc_id, main_h03eapcontr.codeap;"
        try:
            pesquisa = self.objetos.raw(comando)
            return pesquisa
        except self.DoesNotExist:
            return None


class h04AtvContr(models.Model):
    id = models.IntegerField(primary_key=True)
    eap = models.ForeignKey(h03EapContr, on_delete=models.CASCADE)
    atvpadr = models.ForeignKey(a15AtvsPad, on_delete=models.CASCADE)
    durativ = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    depativ = models.CharField(max_length=255, null=True)
    dtiniprev = models.DateField(auto_now=False, auto_now_add=True)
    dtfinprev = models.DateField(auto_now=False, auto_now_add=True)
    cstprev = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    cstprevser = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    cstprevmat = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    objetos = models.Manager()


class h05ProdDiar(models.Model):
    id = models.IntegerField(primary_key=True)
    datprod = models.DateField(null=False)
    atvcontr = models.ForeignKey(h04AtvContr, on_delete=models.CASCADE)
    resplanc = models.ForeignKey(c01Usuarios, on_delete=models.CASCADE)
    respexec = models.CharField(max_length=30)
    relatdia = models.CharField(max_length=255)
    ativconc = models.BooleanField(default=False)
    climadru = models.PositiveSmallIntegerField(default=1)
    climanha = models.PositiveSmallIntegerField(default=1)
    clitarde = models.PositiveSmallIntegerField(default=1)
    clinoite = models.PositiveSmallIntegerField(default=1)


class h06PtoProd(models.Model):
    id = models.IntegerField(primary_key=True)
    produc = models.ForeignKey(h05ProdDiar, on_delete=models.CASCADE)
    ptocol = models.ForeignKey(e15PtoCol, on_delete=models.CASCADE)
    perpto = models.FloatField(default=1)


class h07PatProd(models.Model):
    id = models.IntegerField(primary_key=True)
    produc = models.ForeignKey(h05ProdDiar, on_delete=models.CASCADE)
    patprd = models.ForeignKey(d01Patrim, on_delete=models.CASCADE)
    qtprod = models.DecimalField(max_digits=10, decimal_places=4, null=True, default=0)
    qtimpr = models.DecimalField(max_digits=10, decimal_places=4, null=True, default=0)


class h08ForProd(models.Model):
    id = models.IntegerField(primary_key=True)
    produc = models.ForeignKey(h05ProdDiar, on_delete=models.CASCADE)
    contra = models.ForeignKey(f02ItContForn, on_delete=models.CASCADE)
    qtprod = models.DecimalField(max_digits=10, decimal_places=4, null=True, default=0)
    qtimpr = models.DecimalField(max_digits=10, decimal_places=4, null=True, default=0)


class h09FotosProd(models.Model):
    id = models.IntegerField(primary_key=True)
    produc = models.ForeignKey(h05ProdDiar, on_delete=models.CASCADE)
    dtfoto = models.DateField(null=False)
    legend = models.CharField(max_length=255, null=True)
    arquiv = models.CharField(max_length=255, null=True)


# Dados da Producao Industrial


class i01OrdProd(models.Model):
    id = models.IntegerField(primary_key=True)
    respons = models.ForeignKey(c01Usuarios, on_delete=models.CASCADE)
    dtprodu = models.DateField(null=False)
    produto = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    qtdereq = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)
    trcouti = models.ForeignKey(a13CompsCads, on_delete=models.CASCADE)


class i02LotesProd(models.Model):
    id = models.IntegerField(primary_key=True)
    ordprod = models.ForeignKey(i01OrdProd, on_delete=models.CASCADE)
    dtprodu = models.DateField(null=False)
    produto = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    qtdprod = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)
    qtdvend = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)


class i03InsLotes(models.Model):
    id = models.IntegerField(primary_key=True)
    lote = models.ForeignKey(i02LotesProd, on_delete=models.CASCADE)
    insumo = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    qtdins = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)


class i04PtoLotes(models.Model):
    id = models.IntegerField(primary_key=True)
    lote = models.ForeignKey(i02LotesProd, on_delete=models.CASCADE)
    ptocol = models.ForeignKey(e15PtoCol, on_delete=models.CASCADE)
    perpto = models.FloatField(default=1)


class i05PatrLotes(models.Model):
    id = models.IntegerField(primary_key=True)
    lote = models.ForeignKey(i02LotesProd, on_delete=models.CASCADE)
    patrim = models.ForeignKey(d01Patrim, on_delete=models.CASCADE)
    utprod = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)
    utimpd = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)


class i06ForProd(models.Model):
    id = models.IntegerField(primary_key=True)
    lote = models.ForeignKey(i02LotesProd, on_delete=models.CASCADE)
    contra = models.ForeignKey(f02ItContForn, on_delete=models.CASCADE)
    qtprod = models.DecimalField(max_digits=10, decimal_places=4, null=True, default=0)
    qtimpr = models.DecimalField(max_digits=10, decimal_places=4, null=True, default=0)


# Dados das Entregas

class j01OrdEntr(models.Model):
    id = models.IntegerField(primary_key=True)
    respons = models.ForeignKey(c01Usuarios, on_delete=models.CASCADE)
    cliente = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    endentr = models.ForeignKey(e04EndCad, on_delete=models.CASCADE)


class j02ItVendOE(models.Model):
    id = models.IntegerField(primary_key=True)
    ordentr = models.ForeignKey(j01OrdEntr, on_delete=models.CASCADE)
    produto = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    qtdvend = models.DecimalField(max_digits=10, decimal_places=4, null=True, default=0)
    prcvend = models.DecimalField(max_digits=10, decimal_places=4, null=True, default=0)


class j03Entregas(models.Model):
    id = models.IntegerField(primary_key=True)
    dtentre = models.DateField(null=False)
    motoris = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    tipofre = models.ForeignKey(a08TiposFrete, on_delete=models.CASCADE)
    kminici = models.DecimalField(max_digits=8, decimal_places=1, null=True, default=0)
    kminici = models.DecimalField(max_digits=8, decimal_places=1, null=True, default=0)


class j04ItEntrOE(models.Model):
    id = models.IntegerField(primary_key=True)
    itorden = models.ForeignKey(j02ItVendOE, on_delete=models.CASCADE)
    entrega = models.ForeignKey(j03Entregas, on_delete=models.CASCADE)
    qtdentr = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)


# Dados do Faturamento

class k01Faturas(models.Model):
    id = models.IntegerField(primary_key=True)
    tipo = models.PositiveSmallIntegerField(default=1)
    empresa = models.ForeignKey(b01Empresas, on_delete=models.CASCADE)
    cliente = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    datafat = models.DateField(null=False)
    histori = models.ForeignKey(a28Historicos, on_delete=models.CASCADE)
    comphst = models.CharField(max_length=255, null=True)
    valrfat = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)


class k02EapFat(models.Model):
    id = models.IntegerField(primary_key=True)
    fatura = models.ForeignKey(k01Faturas, on_delete=models.CASCADE)
    eapcontr = models.ForeignKey(h03EapContr, on_delete=models.CASCADE)
    qtdmedid = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)


class k03EntFat(models.Model):
    id = models.IntegerField(primary_key=True)
    fatura = models.ForeignKey(k01Faturas, on_delete=models.CASCADE)
    entrega = models.ForeignKey(j03Entregas, on_delete=models.CASCADE)


# Dados da Movimentacao Financeira


class l01Lancamentos(models.Model):
    id = models.IntegerField(primary_key=True)
    respons = models.ForeignKey(c01Usuarios, on_delete=models.CASCADE)
    histori = models.ForeignKey(a28Historicos, on_delete=models.CASCADE)
    comphst = models.CharField(max_length=255, null=True)
    documen = models.CharField(max_length=30, null=True)
    dtinclu = models.DateField(null=False)
    orgmlan = models.PositiveSmallIntegerField(null=False, default=1)
    desccom = models.CharField(max_length=255, null=True)


class l02Operacoes(models.Model):
    id = models.IntegerField(primary_key=True)
    lancto = models.ForeignKey(l01Lancamentos, on_delete=models.CASCADE)
    ccusto = models.ForeignKey(b04CCustos, on_delete=models.CASCADE)
    dtoper = models.DateField(null=False)
    realiz = models.BooleanField(default=True)
    acestq = models.BooleanField(default=True)
    consol = models.BooleanField(default=True)


class l03PrevFinan(models.Model):
    id = models.IntegerField(primary_key=True)
    operac = models.ForeignKey(l02Operacoes, on_delete=models.CASCADE)
    pagmto = models.BooleanField(default=True)
    cadast = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    cdcont = models.IntegerField(default=0)  # Cod. Contrato Fornecimento
    cdcban = models.IntegerField(default=0)  # Cod. Conta Bancaria Cadastro
    period = models.PositiveSmallIntegerField(default=0)
    tipvlr = models.PositiveSmallIntegerField(default=0)
    qtdrep = models.SmallIntegerField(default=0)
    ctaref = models.IntegerField(default=0)
    bxauto = models.BooleanField(default=False)
    stspar = models.PositiveSmallIntegerField(default=0)
    dtconf = models.DateField(null=True)
    usrcon = models.IntegerField(default=0)
    codbar = models.CharField(max_length=255, null=True)
    arqdoc = models.CharField(max_length=30, null=True)
    dtauto = models.DateField(null=True)
    usraut = models.IntegerField(default=0)


class l04ContrComprov(models.Model):
    id = models.IntegerField(primary_key=True)
    operac = models.ForeignKey(l02Operacoes, on_delete=models.CASCADE)
    cdcont = models.IntegerField(default=0)  # Cod. Contrato Fornecimento
    ctaori = models.ForeignKey(b02PlContas, on_delete=models.CASCADE, related_name='contaorigem')
    ctades = models.ForeignKey(b02PlContas, on_delete=models.CASCADE, related_name='contadestino')
    respon = models.ForeignKey(c01Usuarios, on_delete=models.CASCADE)
    arqdoc = models.CharField(max_length=30, null=True)
    arqcmp = models.CharField(max_length=30, null=True)
    vlrcmp = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)


class l05MovFinan(models.Model):
    id = models.IntegerField(primary_key=True)
    operac = models.ForeignKey(l02Operacoes, on_delete=models.CASCADE)
    ctamov = models.ForeignKey(b02PlContas, on_delete=models.CASCADE)
    vlrmov = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)


class l06MovEstoq(models.Model):
    id = models.IntegerField(primary_key=True)
    operac = models.ForeignKey(l02Operacoes, on_delete=models.CASCADE)
    produt = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    qtdmov = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)
    vlruni = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)


class l07DspPatr(models.Model):
    id = models.IntegerField(primary_key=True)
    operac = models.ForeignKey(l02Operacoes, on_delete=models.CASCADE)
    patrim = models.ForeignKey(d01Patrim, on_delete=models.CASCADE)
    produt = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    qtdfor = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)
    vlruni = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)
    odomet = models.DecimalField(max_digits=8, decimal_places=1, null=False, default=0)


class l08DspCad(models.Model):
    id = models.IntegerField(primary_key=True)
    operac = models.ForeignKey(l02Operacoes, on_delete=models.CASCADE)
    cadast = models.ForeignKey(e01Cadastros, on_delete=models.CASCADE)
    produt = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    qtdfor = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)
    vlruni = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)


class l09DspCtForn(models.Model):
    id = models.IntegerField(primary_key=True)
    operac = models.ForeignKey(l02Operacoes, on_delete=models.CASCADE)
    contra = models.ForeignKey(f01ContrForn, on_delete=models.CASCADE)
    produt = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    qtdfor = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)
    vlruni = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)
    descon = models.BooleanField(default=False)  # Ja descontado no contrato


class l10DspAtv(models.Model):
    id = models.IntegerField(primary_key=True)
    operac = models.ForeignKey(l02Operacoes, on_delete=models.CASCADE)
    atveap = models.ForeignKey(h04AtvContr, on_delete=models.CASCADE)
    produt = models.ForeignKey(a11Insumos, on_delete=models.CASCADE)
    qtdfor = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)
    vlruni = models.DecimalField(max_digits=10, decimal_places=4, null=False, default=0)