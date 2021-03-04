from csv import reader
from io import StringIO
from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist

from main.models import (a03Estados, a04Municipios, a05Bairros, a08TiposFrete, a09TiposFone,
                         a19PlsPgtos, a20StsOrcs, a31FaseOrc)


def add_estados():
    try:
        a03Estados.objetos.get(id=1)
    except:
        csv_file = Path.cwd().joinpath("seeds_db", 'main_a03estados.csv')
        data_set = csv_file.read_text(encoding='UTF-8')
        io_string = StringIO(data_set)
        for column in reader(io_string, delimiter=',', quotechar="|"):
            country = a03Estados(
                uf=column[0].strip(' "'),
                estado=column[1].strip(' "'),
                regiao=column[2].strip(' "'),
                distfab=Decimal(column[3].strip(' "')),
                cepfin=column[4].strip(' "'),
                cepini=column[5].strip(' "'),
            )
            country.save()

def add_municipios():
    try:
        a04Municipios.objetos.get(id=1)
    except:
        csv_file = Path.cwd().joinpath("seeds_db", 'main_a04municipios.csv')
        data_set = csv_file.read_text(encoding='UTF-8')
        io_string = StringIO(data_set)
        for count, column in enumerate(reader(io_string, delimiter=',', quotechar="|")):
            city = a04Municipios(
                id=count,
                municipio=column[1].strip(' "'),
                cepini=column[2].strip(' "'),
                cepfin=column[3].strip(' "'),
                distfab=Decimal(column[4].strip(' "')),
                estado_id=column[5].strip(' "')
            )
            city.save()

def add_tipos_de_telefone():
    try:
        a09TiposFone.objetos.get(id=1)
    except:
        csv_file = Path.cwd().joinpath("seeds_db", 'main_a09tiposfone.csv')
        data_set = csv_file.read_text(encoding='UTF-8')
        io_string = StringIO(data_set)
        for count, column in enumerate(reader(io_string, delimiter=',', quotechar="|")):
            phone = a09TiposFone(
                id=count + 1,
                tfone=column[1].strip(' "'),
            )
            phone.save()

def add_tipos_de_frete():
    try:
        a08TiposFrete.objetos.get(id=1)
    except ObjectDoesNotExist:
        csv_file = Path.cwd().joinpath("seeds_db", 'main_a08tiposfrete.csv')
        data_set = csv_file.read_text(encoding='UTF-8')
        io_string = StringIO(data_set)
        for column in reader(io_string, delimiter=';', quotechar='|'):
            novo_tipo_frete = a08TiposFrete(
                id=column[0].strip(' "'),
                descsing=column[1].strip(' "'),
                descplur=column[2].strip(' "'),
                desccomp=column[3].strip(' "'),
                pesomax=column[4].strip(' "'),
                volmax=column[5].strip(' "'),
                vlrkm=column[6].strip(' "'),
            )
            novo_tipo_frete.save()

def add_planos_de_pagamento():    
    try:
        a19PlsPgtos.objetos.get(id=1)
    except ObjectDoesNotExist:        
        csv_file = Path.cwd().joinpath("seeds_db", 'main_a19plspgtos.csv')
        data_set = csv_file.read_text(encoding='UTF-8')
        io_string = StringIO(data_set)
        for column in reader(io_string, delimiter=';', quotechar='|'):
            novo_plano = a19PlsPgtos(
                id=column[0].strip(' "'),
                tipo=column[1].strip(' "'),
                formapgto=column[2].strip(' "'),
                descricao=column[3].strip(' "'),
                
            )
            novo_plano.save()

def add_status_do_orcamento():
    try:
        a20StsOrcs.objetos.get(id=1)
    except ObjectDoesNotExist:        
        csv_file = Path.cwd().joinpath("seeds_db", 'main_a20stsorcs.csv')
        data_set = csv_file.read_text(encoding='UTF-8')
        io_string = StringIO(data_set)
        for column in reader(io_string, delimiter=',', quotechar='|'):
            novo_status = a20StsOrcs(
                id=column[0].strip(' "'),
                descricao=column[1].strip(' "'),
                alerta=column[2].strip(' "'), 
                ativo=column[3].strip(' "'),
                transfoe=column[4].strip(' "'),
            )
            novo_status.save()

def add_fases_orcamento():
    try:
        a31FaseOrc.objetos.get(id=1)
    except ObjectDoesNotExist:
        csv_file = Path.cwd().joinpath("seeds_db", 'main_a31faseorc.csv')
        data_set = csv_file.read_text(encoding='UTF-8')
        io_string = StringIO(data_set)
        for column in reader(io_string, delimiter=',', quotechar='|'):
            new_fase = a31FaseOrc(
                id=column[0].strip(' "'),
                descricao=column[1].strip(' "')
            )
            new_fase.save()
