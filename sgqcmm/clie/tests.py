from django.test import TestCase, Client
from django.contrib.auth.models import User


# Setup functions
def add_test_user():
    user_to_test = User.objects.create_user(
        username="user_test",
        password="teste",
        is_staff=True
    )
    return user_to_test

# Tests
class TestAddClient(TestCase):
    def setUp(self):
        user_to_test = add_test_user()
        login = self.client.login(username=user_to_test.username, password="teste")
        self.client.get('/config/add-seeds/ajax/estados/')
        self.client.get('/config/add-seeds/ajax/municipios/')
        self.client.get('/config/add-seeds/ajax/tipos-telefone/')

    def test_search_new_client(self):
        data_to_post = {
            "nome": "Cliente teste - Teste",
            "fone": "62900000000",
            "email": "teste@gmail.com"
        }
        response = self.client.post(
            '/clientes/', data_to_post)
        self.assertEqual(response.status_code, 302)

    def test_add_new_client(self):
        self.client.post('/clientes/', 
        {
            "nome": "Cliente teste - Teste",
            "fone": "62900000000",
            "email": "teste@gmail.com"
        })
        data_to_post = {
            "nome": "Cliente teste",
            "telefone": "62900000000",
            "email": "teste@gmail.com",
            "tratamento": "Sr.",
            "descricao": "Cliente teste - Teste",
            "cnpj": "00000000000000",
            "juridica": "0",
            "genero": "1",
            "empresa": "",
            "endereco": "0"
        }
        response = self.client.post(
            '/clientes/dados-cliente/', data_to_post)
        self.assertEqual(response.status_code, 302)

    def test_add_new_address(self):
        self.client.post('/clientes/', 
        {
            "nome": "Cliente teste - Teste",
            "fone": "62900000000",
            "email": "teste@gmail.com"
        })
        self.client.post(
            '/clientes/dados-cliente/', {
            "nome": "Cliente teste",
            "telefone": "62900000000",
            "email": "teste@gmail.com",
            "tratamento": "Sr.",
            "descricao": "Cliente teste - Teste",
            "cnpj": "00000000000000",
            "juridica": "0",
            "genero": "1",
            "empresa": "",
            "endereco": "0"
        })
        data_to_post = {
            "regiao": "Centro Oeste",
            "estado": "GO",
            "cidade": "94",
            "novo_bairro": "Bairro teste",
            "novo_logradouro": "Logradouro Teste",
            "complemento": "00000000000000"
        }
        response = self.client.post(
            '/clientes/cadastrar-novo-endereco/', data_to_post)
        self.assertEqual(response.status_code, 302)