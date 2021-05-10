from django.test import TestCase, Client
from django.contrib.auth.models import User

from main.models import a03Estados


# Setup functions
def add_test_user():
    user_to_test = User.objects.create_user(
        username="user_test",
        password="teste",
        is_staff=True
    )
    return user_to_test


# Tests
class TestAddStates(TestCase):
    def setUp(self):
        user_to_test = add_test_user()
        login = self.client.login(username=user_to_test.username, password="teste")
    
    def test_add_states(self):
        response = self.client.get('/config/add-seeds/ajax/estados/')
        self.assertEqual(response.status_code, 201)
    
    def test_add_states_duplicated(self):
        self.client.get('/config/add-seeds/ajax/estados/')
        response = self.client.get('/config/add-seeds/ajax/estados/')
        self.assertEqual(response.status_code, 400)


class TestAddCitiesFromSeeds(TestCase):
    def setUp(self):
        user_to_test = add_test_user()
        login = self.client.login(username=user_to_test.username, password="teste")
        self.client.get('/config/add-seeds/ajax/estados/')
    
    def test_add_cities(self):
        response = self.client.get('/config/add-seeds/ajax/municipios/')
        self.assertEqual(response.status_code, 201)
    
    def test_add_cities_duplicated(self):
        self.client.get('/config/add-seeds/ajax/municipios/')
        response = self.client.get('/config/add-seeds/ajax/municipios/')
        self.assertEqual(response.status_code, 400)


class TestAddAddressTypes(TestCase):
    def setUp(self):
        user_to_test = add_test_user()
        login = self.client.login(username=user_to_test.username, password="teste")

    def test_add_address_types(self):
        response = self.client.get('/config/add-seeds/ajax/tipos-endereco/')
        self.assertEqual(response.status_code, 201)

    def test_add_address_types_duplicated(self):
        self.client.get('/config/add-seeds/ajax/tipos-endereco/')
        response = self.client.get('/config/add-seeds/ajax/tipos-endereco/')
        self.assertEqual(response.status_code, 400)

class TestAddShippingTypes(TestCase):
    def setUp(self):
        user_to_test = add_test_user()
        login = self.client.login(username=user_to_test.username, password="teste")

    def test_add_shipping_types(self):
        response = self.client.get('/config/add-seeds/ajax/tipos-frete/')
        self.assertEqual(response.status_code, 201)

    def test_add_shipping_types_duplicated(self):
        self.client.get('/config/add-seeds/ajax/tipos-frete/')
        response = self.client.get('/config/add-seeds/ajax/tipos-frete/')
        self.assertEqual(response.status_code, 400)

class TestAddPhoneTypes(TestCase):
    def setUp(self):
        user_to_test = add_test_user()
        login = self.client.login(username=user_to_test.username, password="teste")

    def test_add_phone_types(self):
        response = self.client.get('/config/add-seeds/ajax/tipos-telefone/')
        self.assertEqual(response.status_code, 201)

    def test_add_phone_types_duplicated(self):
        self.client.get('/config/add-seeds/ajax/tipos-telefone/')
        response = self.client.get('/config/add-seeds/ajax/tipos-telefone/')
        self.assertEqual(response.status_code, 400)
    
class TestAddPaymentsPlans(TestCase):
    def setUp(self):
        user_to_test = add_test_user()
        login = self.client.login(username=user_to_test.username, password="teste")

    def test_add_payments_plans(self):
        response = self.client.get('/config/add-seeds/ajax/planos-de-pagamentos/')
        self.assertEqual(response.status_code, 201)

    def test_add_payments_plans_duplicated(self):
        self.client.get('/config/add-seeds/ajax/planos-de-pagamentos/')
        response = self.client.get('/config/add-seeds/ajax/planos-de-pagamentos/')
        self.assertEqual(response.status_code, 400)

class TestAddBudgetStatesAndFases(TestCase):
    def setUp(self):
        user_to_test = add_test_user()
        login = self.client.login(username=user_to_test.username, password="teste")

    def test_add_budget_states(self):
        response = self.client.get('/config/add-seeds/ajax/status-do-orcamento/')
        self.assertEqual(response.status_code, 201)

    def test_add_budget_states_duplicated(self):
        self.client.get('/config/add-seeds/ajax/status-do-orcamento/')
        response = self.client.get('/config/add-seeds/ajax/status-do-orcamento/')
        self.assertEqual(response.status_code, 400)
    
    def test_add_budget_fases(self):
        response = self.client.get('/config/add-seeds/ajax/fases-do-orcamento/')
        self.assertEqual(response.status_code, 201)

    def test_add_budget_fases_duplicated(self):
        self.client.get('/config/add-seeds/ajax/fases-do-orcamento/')
        response = self.client.get('/config/add-seeds/ajax/fases-do-orcamento/')
        self.assertEqual(response.status_code, 400)

class TestAddInputTypes(TestCase):
    def setUp(self):
        user_to_test = add_test_user()
        login = self.client.login(username=user_to_test.username, password="teste")
        
    def test_add_inputs_types(self):
        response = self.client.get('/config/add-seeds/ajax/categorias-insumos/')
        self.assertEqual(response.status_code, 201)

    def test_add_inputs_types_duplicated(self):
        self.client.get('/config/add-seeds/ajax/categorias-insumos/')
        response = self.client.get('/config/add-seeds/ajax/categorias-insumos/')
        self.assertEqual(response.status_code, 400)
    

class TestAddInputs(TestCase):
    def setUp(self):
        user_to_test = add_test_user()
        login = self.client.login(username=user_to_test.username, password="teste")
        self.client.get('/config/add-seeds/ajax/categorias-insumos/')
    
    def test_add_inputs(self):
        response = self.client.get('/config/add-seeds/ajax/insumos/')
        self.assertEqual(response.status_code, 201)

    def test_add_inputs_duplicated(self):
        self.client.get('/config/add-seeds/ajax/insumos/')
        response = self.client.get('/config/add-seeds/ajax/insumos/')
        self.assertEqual(response.status_code, 400)


class TestCompanies(TestCase):
    def setUp(self):
        user_to_test = add_test_user()
        login = self.client.login(username=user_to_test.username, password="teste")
        self.client.get('/config/add-seeds/ajax/estados/')
        self.client.get('/config/add-seeds/ajax/municipios/')


    def test_list_companies(self):
        response = self.client.get('/config/empresas/')
        self.assertEqual(response.status_code, 200)

    def test_add_new_company(self):
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
        self.assertEqual(response.status_code, 200)


class TestCostCenter(TestCase):
    def setUp(self):
        user_to_test = add_test_user()
        login = self.client.login(username=user_to_test.username, password="teste")
        self.client.get('/config/add-seeds/ajax/estados/')
        self.client.get('/config/add-seeds/ajax/municipios/')
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
        self.assertEqual(response.status_code, 200)

    def test_add_new_cost_center(self):
        data_to_post = {
            "descricao": "Empresa Teste",
            "funcionamento": "4",
            "sequencia_holerite": "2",
            "ativo": "True"
        }
        response = self.client.post(
            '/config/empresas/0/centro-de-custos/', data_to_post)
        self.assertEqual(response.status_code, 200)