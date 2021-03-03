from csv import reader
from io import StringIO
from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist

from main.models import a08TiposFrete, a19PlsPgtos, a20StsOrcs, a31FaseOrc


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
