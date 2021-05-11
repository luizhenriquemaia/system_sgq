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


class TestAddNewBudget(TestCase):
    def setUp(self):
        user_to_test = add_test_user()
        login = self.client.login(username=user_to_test.username, password="teste")
        self.client.get('/config/add-seeds/ajax/estados/')
        self.client.get('/config/add-seeds/ajax/municipios/')
        self.client.get('/config/add-seeds/ajax/tipos-telefone/')
        self.client.get('/config/add-seeds/ajax/fases-do-orcamento/')
        self.client.get('/config/add-seeds/ajax/status-do-orcamento/')
        self.client.get('/config/add-seeds/ajax/planos-de-pagamentos/')
        self.client.get('/config/add-seeds/ajax/tipos-frete/')
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
        self.client.post(
            '/clientes/cadastrar-novo-endereco/', {
                "regiao": "Centro Oeste",
                "estado": "GO",
                "cidade": "94",
                "novo_bairro": "Bairro teste",
                "novo_logradouro": "Logradouro Teste",
                "complemento": "00000000000000"
        })
        data_to_post = {
            "regiao": "Centro Oeste",
            "estado": "GO",
            "cidade": "94",
            "novo_bairro": "Jardim Teste",
            "novo_logradouro": "Av. C-Teste",
            "complemento": "Número 2003",
            "razao": "Empresa Teste",
            "juridica": "True",
            "fantasia": "Empresa Teste",
            "codigo_empresa": "2",
            "cnpj": "00000000000100",
            "inscricao_estadual": "0000000000",
            "observacao": "Criada para testes",
        }
        response = self.client.post(
            '/config/empresas/', data_to_post)
        data_to_post = {
            "descricao": "Empresa Teste",
            "funcionamento": "4",
            "sequencia_holerite": "2",
            "ativo": "True"
        }
        response = self.client.post(
            '/config/empresas/0/centro-de-custos/', data_to_post)
    
    def test_add_new_budget(self):
        response = self.client.get('/orcs/preorcamento/')
        self.assertEqual(response.status_code, 302)    