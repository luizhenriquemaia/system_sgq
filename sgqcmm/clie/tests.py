import csv, io
from decimal import Decimal
from pathlib import Path
from django.test import TestCase, Client
from main.models import a03Estados, a04Municipios, a09TiposFone, e01Cadastros
from django.contrib.auth.models import User


# Funções Gerais para Testes
def add_test_user():
    user_to_test = User.objects.create_user(
        username="user_test",
        password="teste",
        is_staff=True
    )
    return user_to_test

def add_country_data():
    print("\n\n\n ---------- ADDING COUNTRYS ---------- \n\n\n")
    csv_file = Path.cwd().joinpath("seeds_db", 'main_a03estados.csv')
    data_set = csv_file.read_text(encoding='UTF-8')
    io_string = io.StringIO(data_set)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        country = a03Estados(
            uf=column[0].strip(' "'),
            estado=column[1].strip(' "'),
            regiao=column[2].strip(' "'),
            distfab=Decimal(column[3].strip(' "')),
            cepfin=column[4].strip(' "'),
            cepini=column[5].strip(' "'),
        )
        country.save()

def add_city_data():
    add_country_data()
    print("\n\n\n ---------- ADDING CITIES ---------- \n\n\n")
    csv_file = Path.cwd().joinpath("seeds_db", 'main_a04municipios.csv')
    data_set = csv_file.read_text(encoding='UTF-8')
    io_string = io.StringIO(data_set)
    for count, column in enumerate(csv.reader(io_string, delimiter=',', quotechar="|")):
        city = a04Municipios(
            id=count,
            municipio=column[1].strip(' "'),
            cepini=column[2].strip(' "'),
            cepfin=column[3].strip(' "'),
            distfab=Decimal(column[4].strip(' "')),
            estado_id=column[5].strip(' "')
        )
        city.save()
    
def add_types_phone():
    print("\n\n\n ---------- ADDING TYPES PHONE ---------- \n\n\n")
    csv_file = Path.cwd().joinpath("seeds_db", 'main_a09tiposfone.csv')
    data_set = csv_file.read_text(encoding='UTF-8')
    io_string = io.StringIO(data_set)
    for count, column in enumerate(csv.reader(io_string, delimiter=',', quotechar="|")):
        phone = a09TiposFone(
            id=count,
            tfone=column[1].strip(' "'),
        )
        phone.save()


# Testes
class ClientTestWithoutData(TestCase):
    def setUp(self):
        user_to_test = add_test_user()
        login = self.client.login(username=user_to_test.username, password="teste")

    def test_add_new_client(self):
        add_city_data()
        add_types_phone()
        print("\n\n\n ---------- Adding New Client ---------- \n\n\n")
        data_to_post = {
            "nome": "Kelmiton - Chateau Provence",
            "fone": "62999783717",
            "email": "kelmiton@gmail.com"
        }
        response = self.client.post(
            '/clientes/1', data_to_post)
        self.assertEqual(response.status_code, 302)

    
