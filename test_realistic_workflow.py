# test_realistic_workflow.py
import unittest
import requests
import os
import random
import string
from dotenv import load_dotenv, find_dotenv
from pprint import pprint

# Carrega as variáveis de ambiente do .env
load_dotenv(find_dotenv())

BASE_URL = 'http://127.0.0.1:5000'
# Caminhos para os arquivos de teste
PDF_CONTRATO_PATH = '/home/rafael/py-back-contratos/teste.pdf'
TXT_RELATORIO_PATH = '/home/rafael/py-back-contratos/relatorio_teste.txt'


def generate_random_string(length=8):
    """Gera uma string aleatória para criar dados únicos."""
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

class TestFullWorkflow(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """
        Prepara o ambiente antes de todos os testes.
        Cria usuários, obtém IDs e tokens de autenticação.
        """
        print("\n--- INICIANDO PREPARAÇÃO DO AMBIENTE DE TESTE COMPLETO ---")
        
        cls.created_ids = {}
        cls.seed_ids = {}
        cls.auth_tokens = {}

        # --- 1. Login como Admin e Obtenção do Token de Admin ---
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')
        assert admin_email and admin_password, "ADMIN_EMAIL e ADMIN_PASSWORD devem estar no .env"
        
        r_login_admin = requests.post(f'{BASE_URL}/auth/login', json={'email': admin_email, 'senha': admin_password})
        assert r_login_admin.status_code == 200, "Falha ao fazer login como Admin. Verifique as credenciais no .env e se o seeder foi executado."
        cls.auth_tokens['admin'] = r_login_admin.json()['token']
        cls.created_ids['admin'] = r_login_admin.json()['usuario']['id']
        print("-> Login como Admin bem-sucedido.")

        # Headers de autenticação para o admin
        cls.admin_headers = {'Authorization': f'Bearer {cls.auth_tokens["admin"]}'}

        # --- 2. Função auxiliar para buscar IDs de dados do Seeder ---
        def get_id_by_name(endpoint, name):
            r = requests.get(f"{BASE_URL}{endpoint}", headers=cls.admin_headers)
            assert r.status_code == 200, f"Falha ao buscar dados de {endpoint}. Resposta: {r.text}"
            for item in r.json():
                if item['nome'] == name: return item['id']
            raise Exception(f"'{name}' não encontrado em {endpoint}. O banco foi populado com 'flask seed-db'?")

        print("-> Buscando IDs dos dados do seed...")
        cls.seed_ids['perfil_gestor'] = get_id_by_name('/perfis', 'Gestor')
        cls.seed_ids['perfil_fiscal'] = get_id_by_name('/perfis', 'Fiscal')
        cls.seed_ids['modalidade'] = get_id_by_name('/modalidades', 'Pregão')
        cls.seed_ids['status_vigente'] = get_id_by_name('/status', 'Vigente')
        cls.seed_ids['status_suspenso'] = get_id_by_name('/status', 'Suspenso')
        cls.seed_ids['status_pendencia_pendente'] = get_id_by_name('/statuspendencia', 'Pendente')
        cls.seed_ids['status_relatorio_pendente'] = get_id_by_name('/statusrelatorio', 'Pendente de Análise')
        cls.seed_ids['status_relatorio_aprovado'] = get_id_by_name('/statusrelatorio', 'Aprovado')
        cls.seed_ids['status_relatorio_rejeitado'] = get_id_by_name('/statusrelatorio', 'Rejeitado com Pendência')
        print("-> IDs do seed carregados com sucesso.")

        # --- 3. Criando Atores (Contratado, Gestor, Fiscal) ---
        print("-> Criando atores para o teste (Contratado, Gestor, Fiscal)...")
        random_str = generate_random_string()
        
        # Contratado
        r_contratado = requests.post(f'{BASE_URL}/contratados', json={"nome": "Empresa Workflow LTDA", "email": f"contratado_wf_{random_str}@teste.com", "cnpj": f"{random.randint(10**13, 10**14-1)}"}, headers=cls.admin_headers)
        cls.created_ids['contratado'] = r_contratado.json()['id']
        
        # Gestor
        cls.gestor_email = f"gestor_wf_{random_str}@teste.com"
        gestor_pass = "senha_gestor"
        r_gestor = requests.post(f'{BASE_URL}/usuarios', json={"nome": "Gestor de Workflow", "email": cls.gestor_email, "cpf": f"{random.randint(10**10, 10**11-1)}", "senha": gestor_pass, "perfil_id": cls.seed_ids['perfil_gestor']}, headers=cls.admin_headers)
        cls.created_ids['gestor'] = r_gestor.json()['id']

        # Fiscal
        fiscal_email = f"fiscal_wf_{random_str}@teste.com"
        fiscal_pass = "senha_fiscal"
        r_fiscal = requests.post(f'{BASE_URL}/usuarios', json={"nome": "Fiscal de Workflow", "email": fiscal_email, "cpf": f"{random.randint(10**10, 10**11-1)}", "senha": fiscal_pass, "perfil_id": cls.seed_ids['perfil_fiscal']}, headers=cls.admin_headers)
        cls.created_ids['fiscal'] = r_fiscal.json()['id']
        
        print(f"-> Atores criados: Contratado({cls.created_ids['contratado']}), Gestor({cls.created_ids['gestor']}), Fiscal({cls.created_ids['fiscal']})")
        
        # --- 4. Login como Gestor e Fiscal para obter seus tokens ---
        r_login_gestor = requests.post(f'{BASE_URL}/auth/login', json={'email': cls.gestor_email, 'senha': gestor_pass})
        cls.auth_tokens['gestor'] = r_login_gestor.json()['token']
        
        r_login_fiscal = requests.post(f'{BASE_URL}/auth/login', json={'email': fiscal_email, 'senha': fiscal_pass})
        cls.auth_tokens['fiscal'] = r_login_fiscal.json()['token']
        print("-> Tokens de autenticação para Gestor e Fiscal foram obtidos.")

    def test_01_admin_can_manage_users(self):
        """ Testa o ciclo de vida completo (CRUD) de um Usuário pelo Admin. """
        print("\nPASSO 1: Testando Gerenciamento de Usuários (Admin)")
        random_str = generate_random_string()
        
        # CREATE
        email = f"user_crud_{random_str}@teste.com"
        payload = {"nome": f"User CRUD {random_str}", "email": email, "cpf": f"{random.randint(10**10, 10**11-1)}", "senha": "123", "perfil_id": self.seed_ids['perfil_fiscal']}
        r_create = requests.post(f'{BASE_URL}/usuarios', json=payload, headers=self.admin_headers)
        self.assertEqual(r_create.status_code, 201)
        user_id = r_create.json()['id']
        print(f"-> Usuário {user_id} criado.")

        # READ (By ID)
        r_read = requests.get(f'{BASE_URL}/usuarios/{user_id}', headers=self.admin_headers)
        self.assertEqual(r_read.status_code, 200)
        self.assertEqual(r_read.json()['email'], email)
        print(f"-> Usuário {user_id} lido com sucesso.")

        # UPDATE
        update_payload = {"nome": f"User CRUD Alterado {random_str}"}
        r_update = requests.patch(f'{BASE_URL}/usuarios/{user_id}', json=update_payload, headers=self.admin_headers)
        self.assertEqual(r_update.status_code, 200)
        self.assertEqual(r_update.json()['nome'], update_payload['nome'])
        print(f"-> Usuário {user_id} atualizado.")

        # DELETE
        r_delete = requests.delete(f'{BASE_URL}/usuarios/{user_id}', headers=self.admin_headers)
        self.assertEqual(r_delete.status_code, 204)
        r_verify_delete = requests.get(f'{BASE_URL}/usuarios/{user_id}', headers=self.admin_headers)
        self.assertEqual(r_verify_delete.status_code, 404)
        print(f"-> Usuário {user_id} deletado.")
        
    def test_02_admin_can_manage_contratados(self):
        """ Testa o ciclo de vida completo (CRUD) de um Contratado pelo Admin. """
        print("\nPASSO 2: Testando Gerenciamento de Contratados (Admin)")
        random_str = generate_random_string()
        
        # CREATE
        payload = {"nome": f"Contratado Teste CRUD {random_str}", "email": f"crud_{random_str}@teste.com", "cnpj": f"{random.randint(10**13, 10**14-1)}"}
        r_create = requests.post(f'{BASE_URL}/contratados', json=payload, headers=self.admin_headers)
        self.assertEqual(r_create.status_code, 201)
        contratado_id = r_create.json()['id']
        print(f"-> Contratado {contratado_id} criado.")

        # READ (By ID)
        r_read = requests.get(f'{BASE_URL}/contratados/{contratado_id}', headers=self.admin_headers)
        self.assertEqual(r_read.status_code, 200)
        self.assertEqual(r_read.json()['nome'], payload['nome'])
        print(f"-> Contratado {contratado_id} lido com sucesso.")

        # UPDATE
        update_payload = {"nome": f"Contratado Teste CRUD Alterado {random_str}"}
        r_update = requests.patch(f'{BASE_URL}/contratados/{contratado_id}', json=update_payload, headers=self.admin_headers)
        self.assertEqual(r_update.status_code, 200)
        self.assertEqual(r_update.json()['nome'], update_payload['nome'])
        print(f"-> Contratado {contratado_id} atualizado.")

        # DELETE
        r_delete = requests.delete(f'{BASE_URL}/contratados/{contratado_id}', headers=self.admin_headers)
        self.assertEqual(r_delete.status_code, 204)
        r_verify_delete = requests.get(f'{BASE_URL}/contratados/{contratado_id}', headers=self.admin_headers)
        self.assertEqual(r_verify_delete.status_code, 404)
        print(f"-> Contratado {contratado_id} deletado.")

    def test_03_permission_denied_for_non_admins(self):
        """ Testa se usuários não-admin (Fiscal, Gestor) são bloqueados de rotas de admin. """
        print("\nPASSO 3: Testando restrições de permissão")
        
        # Fiscal tentando criar um usuário (deve falhar)
        fiscal_headers = {'Authorization': f'Bearer {self.auth_tokens["fiscal"]}'}
        payload = {"nome": "Tentativa Fiscal", "email": "tentativa@fiscal.com", "senha": "123", "perfil_id": self.seed_ids['perfil_fiscal']}
        r_fiscal = requests.post(f'{BASE_URL}/usuarios', json=payload, headers=fiscal_headers)
        self.assertEqual(r_fiscal.status_code, 403)
        print("-> Fiscal foi corretamente bloqueado de criar usuários.")
        
        # Gestor tentando listar todos os contratados (deve funcionar, pois é rota JWT)
        gestor_headers = {'Authorization': f'Bearer {self.auth_tokens["gestor"]}'}
        r_gestor_get = requests.get(f'{BASE_URL}/contratados', headers=gestor_headers)
        self.assertEqual(r_gestor_get.status_code, 200)
        print("-> Gestor conseguiu listar contratados (rota @jwt_required).")

        # Gestor tentando deletar um contratado (deve falhar)
        r_gestor_del = requests.delete(f"{BASE_URL}/contratados/{self.created_ids['contratado']}", headers=gestor_headers)
        self.assertEqual(r_gestor_del.status_code, 403)
        print("-> Gestor foi corretamente bloqueado de deletar contratados.")
        
    def test_04_validation_and_error_handling(self):
        """ Testa se a API lida corretamente com entradas inválidas. """
        print("\nPASSO 4: Testando validação e tratamento de erros")

        # Tentar criar usuário com email que já existe (do gestor criado no setup)
        payload = {"nome": "Duplicado", "email": self.gestor_email, "cpf": f"{random.randint(10**10, 10**11-1)}", "senha": "123", "perfil_id": self.seed_ids['perfil_fiscal']}
        r_duplicate = requests.post(f'{BASE_URL}/usuarios', json=payload, headers=self.admin_headers)
        self.assertIn(r_duplicate.status_code, [409, 500]) # 409 (Conflict) é o ideal
        print("-> API retornou erro ao tentar criar usuário com email duplicado.")

        # Tentar criar contrato com um gestor_id inválido
        invalid_id = 999999
        form_data = {
            "nr_contrato": f"WF-INVALID-{generate_random_string()}", "objeto": "Contrato com ID inválido",
            "data_inicio": "2025-01-01", "data_fim": "2025-12-31",
            "contratado_id": self.created_ids['contratado'], "modalidade_id": self.seed_ids['modalidade'],
            "status_id": self.seed_ids['status_vigente'], "gestor_id": invalid_id, 
            "fiscal_id": self.created_ids['fiscal']
        }
        r_invalid_id = requests.post(f'{BASE_URL}/contratos', json=form_data, headers=self.admin_headers)
        self.assertEqual(r_invalid_id.status_code, 404)
        print("-> API retornou erro 404 ao criar contrato com gestor_id inválido.")

    def test_05_full_contract_and_report_workflow(self):
        """ Simula o fluxo de ponta a ponta: criação, pendência, envio, download e aprovação. """
        print("\nPASSO 5: Iniciando fluxo completo de Contrato e Relatório")
        
        # --- ETAPA 1 (Admin): Cria o Contrato com anexo ---
        print(" -> ETAPA 1 (Admin): Criando o contrato com anexo...")
        self.assertTrue(os.path.exists(PDF_CONTRATO_PATH), f"Arquivo de contrato não encontrado em {PDF_CONTRATO_PATH}")

        form_data = {
            "nr_contrato": f"WF-FULL-{generate_random_string()}", "objeto": "Contrato do Workflow Completo",
            "data_inicio": "2025-01-01", "data_fim": "2025-12-31",
            "contratado_id": self.created_ids['contratado'], "modalidade_id": self.seed_ids['modalidade'],
            "status_id": self.seed_ids['status_vigente'], "gestor_id": self.created_ids['gestor'], 
            "fiscal_id": self.created_ids['fiscal']
        }
        with open(PDF_CONTRATO_PATH, 'rb') as f:
            files = {'documento_contrato': (os.path.basename(PDF_CONTRATO_PATH), f, 'application/pdf')}
            r_contrato = requests.post(f'{BASE_URL}/contratos', data=form_data, files=files, headers=self.admin_headers)
        
        self.assertEqual(r_contrato.status_code, 201)
        contrato_id = r_contrato.json()['id']
        self.__class__.created_ids['contrato'] = contrato_id
        print(f" -> Contrato ID {contrato_id} criado.")

        # --- ETAPA 2 (Admin): Cria a Pendência ---
        print(" -> ETAPA 2 (Admin): Criando pendência para o fiscal...")
        pendencia_payload = {
            "descricao": "Relatório inicial de atividades.", "data_prazo": "2025-02-28",
            "status_pendencia_id": self.seed_ids['status_pendencia_pendente'], 
            "criado_por_usuario_id": self.created_ids['admin']
        }
        r_pendencia = requests.post(f'{BASE_URL}/contratos/{contrato_id}/pendencias', json=pendencia_payload, headers=self.admin_headers)
        self.assertEqual(r_pendencia.status_code, 201)
        pendencia_id = r_pendencia.json()['id']
        print(f" -> Pendência ID {pendencia_id} criada.")
        
        # --- ETAPA 3 (Fiscal): Envia o Relatório ---
        print(" -> ETAPA 3 (Fiscal): Enviando o primeiro relatório...")
        self.assertTrue(os.path.exists(TXT_RELATORIO_PATH), f"Arquivo de relatório não encontrado em {TXT_RELATORIO_PATH}")
        fiscal_headers = {'Authorization': f'Bearer {self.auth_tokens["fiscal"]}'}
        
        with open(TXT_RELATORIO_PATH, "rb") as f:
            files = {'arquivo': (os.path.basename(TXT_RELATORIO_PATH), f, 'text/plain')}
            form_data = {
                'mes_competencia': '2025-01-01', 'fiscal_usuario_id': self.created_ids['fiscal'],
                'pendencia_id': pendencia_id
            }
            r_relatorio = requests.post(f'{BASE_URL}/contratos/{contrato_id}/relatorios', data=form_data, files=files, headers=fiscal_headers)
        
        self.assertEqual(r_relatorio.status_code, 201, f"Falha ao enviar relatório: {r_relatorio.text}")
        relatorio_id = r_relatorio.json()['id']
        arquivo_id = r_relatorio.json()['arquivo_id']
        self.__class__.created_ids['relatorio'] = relatorio_id
        print(f" -> Relatório ID {relatorio_id} (Arquivo ID {arquivo_id}) enviado pelo fiscal.")

        # --- ETAPA 4 (Fiscal): Tenta baixar o próprio relatório ---
        print(" -> ETAPA 4 (Fiscal): Verificando o download do relatório...")
        r_download = requests.get(f'{BASE_URL}/arquivos/{arquivo_id}/download', headers=fiscal_headers)
        self.assertEqual(r_download.status_code, 200)
        self.assertIn('Este é um relatório de teste', r_download.text)
        print(" -> Fiscal conseguiu baixar o relatório com sucesso.")
        
        # --- ETAPA 5 (Admin): Rejeita o Relatório ---
        print(" -> ETAPA 5 (Admin): Rejeitando o relatório com observações...")
        analise_payload = {
            "aprovador_usuario_id": self.created_ids['admin'],
            "status_id": self.seed_ids['status_relatorio_rejeitado'],
            "observacoes_aprovador": "Faltou incluir o anexo B. Corrija e reenvie."
        }
        r_rejeita = requests.patch(f'{BASE_URL}/contratos/{contrato_id}/relatorios/{relatorio_id}/analise', json=analise_payload, headers=self.admin_headers)
        self.assertEqual(r_rejeita.status_code, 200)
        self.assertEqual(r_rejeita.json()['status_id'], self.seed_ids['status_relatorio_rejeitado'])
        print(" -> Relatório rejeitado com sucesso.")
        
        # --- ETAPA 6 (Fiscal): Reenvia o Relatório Corrigido ---
        print(" -> ETAPA 6 (Fiscal): Reenviando o relatório corrigido...")
        with open(TXT_RELATORIO_PATH, "rb") as f:
            files = {'arquivo': ('relatorio_v2.txt', f, 'text/plain')}
            form_data = {'observacoes_fiscal': 'Correções aplicadas conforme solicitado.'}
            r_reenvio = requests.put(f'{BASE_URL}/contratos/{contrato_id}/relatorios/{relatorio_id}', data=form_data, files=files, headers=fiscal_headers)
        
        self.assertEqual(r_reenvio.status_code, 200, f"Falha ao reenviar relatório: {r_reenvio.text}")
        self.assertEqual(r_reenvio.json()['status_id'], self.seed_ids['status_relatorio_pendente'])
        print(f" -> Relatório ID {relatorio_id} reenviado e status 'Pendente de Análise'.")
        
        # --- ETAPA 7 (Admin): Aprova o Relatório Final ---
        print(" -> ETAPA 7 (Admin): Aprovando o relatório final...")
        analise_aprovacao_payload = { "aprovador_usuario_id": self.created_ids['admin'], "status_id": self.seed_ids['status_relatorio_aprovado'] }
        r_aprova = requests.patch(f'{BASE_URL}/contratos/{contrato_id}/relatorios/{relatorio_id}/analise', json=analise_aprovacao_payload, headers=self.admin_headers)
        self.assertEqual(r_aprova.status_code, 200)
        self.assertEqual(r_aprova.json()['status_id'], self.seed_ids['status_relatorio_aprovado'])
        print(" -> Relatório final aprovado.")
        
        # --- ETAPA 8 (Gestor): Consulta seus contratos ---
        print(" -> ETAPA 8 (Gestor): Verificando se consegue ver o contrato...")
        gestor_headers = {'Authorization': f'Bearer {self.auth_tokens["gestor"]}'}
        r_gestor_lista = requests.get(f"{BASE_URL}/contratos?gestor_id={self.created_ids['gestor']}", headers=gestor_headers)
        self.assertEqual(r_gestor_lista.status_code, 200)
        contratos_gestor = r_gestor_lista.json()
        self.assertEqual(len(contratos_gestor), 1)
        self.assertEqual(contratos_gestor[0]['id'], contrato_id)
        print(" -> Consulta de contratos por gestor funciona corretamente.")
        
        # --- ETAPA 9 (Admin): Altera o status do contrato ---
        print(" -> ETAPA 9 (Admin): Alterando o status do ciclo de vida do contrato...")
        r_patch_contrato = requests.patch(f'{BASE_URL}/contratos/{contrato_id}', json={"status_id": self.seed_ids['status_suspenso']}, headers=self.admin_headers)
        self.assertEqual(r_patch_contrato.status_code, 200)
        r_verify = requests.get(f'{BASE_URL}/contratos/{contrato_id}', headers=self.admin_headers)
        self.assertEqual(r_verify.json()['status_nome'], 'Suspenso')
        print(" -> Status do contrato alterado com sucesso para 'Suspenso'.")
        
    def test_06_contract_filtering(self):
        """ Testa a lógica de filtragem da lista de contratos para cada perfil. """
        print("\nPASSO 6: Testando a filtragem de contratos por perfil.")
        
        # Garante que um contrato exista para o teste.
        self.assertIn('contrato', self.created_ids, "O contrato do teste de workflow não foi criado.")
        contrato_id = self.created_ids['contrato']

        # Admin: sem filtros, deve ver pelo menos um contrato.
        r_admin = requests.get(f'{BASE_URL}/contratos', headers=self.admin_headers)
        self.assertEqual(r_admin.status_code, 200)
        self.assertGreater(len(r_admin.json()), 0)
        print(" -> Admin vê todos os contratos.")

        # Fiscal: deve ver apenas o seu contrato.
        fiscal_headers = {'Authorization': f'Bearer {self.auth_tokens["fiscal"]}'}
        r_fiscal = requests.get(f"{BASE_URL}/contratos?fiscal_id={self.created_ids['fiscal']}", headers=fiscal_headers)
        self.assertEqual(r_fiscal.status_code, 200)
        self.assertEqual(len(r_fiscal.json()), 1)
        self.assertEqual(r_fiscal.json()[0]['id'], contrato_id)
        print(" -> Fiscal vê apenas seus contratos.")
        
        # Gestor: não deve ver o contrato do fiscal ao filtrar por outro ID.
        gestor_headers = {'Authorization': f'Bearer {self.auth_tokens["gestor"]}'}
        r_gestor_vazio = requests.get(f"{BASE_URL}/contratos?fiscal_id={self.created_ids['gestor']}", headers=gestor_headers)
        self.assertEqual(r_gestor_vazio.status_code, 200)
        self.assertEqual(len(r_gestor_vazio.json()), 0)
        print(" -> Filtro por ID de fiscal diferente retorna lista vazia, como esperado.")
        
    @classmethod
    def tearDownClass(cls):
        """ Limpa todos os recursos criados durante os testes. """
        print("\n--- INICIANDO LIMPEZA DO AMBIENTE DE TESTE ---")
        
        # A ordem de deleção é importante para evitar erros de chave estrangeira
        if 'contrato' in cls.created_ids:
            r = requests.delete(f"{BASE_URL}/contratos/{cls.created_ids['contrato']}", headers=cls.admin_headers)
            print(f"Contrato ID {cls.created_ids['contrato']} deletado (Status: {r.status_code}).")

        if 'gestor' in cls.created_ids:
            r = requests.delete(f"{BASE_URL}/usuarios/{cls.created_ids['gestor']}", headers=cls.admin_headers)
            print(f"Usuário Gestor ID {cls.created_ids['gestor']} deletado (Status: {r.status_code}).")

        if 'fiscal' in cls.created_ids:
            r = requests.delete(f"{BASE_URL}/usuarios/{cls.created_ids['fiscal']}", headers=cls.admin_headers)
            print(f"Usuário Fiscal ID {cls.created_ids['fiscal']} deletado (Status: {r.status_code}).")

        if 'contratado' in cls.created_ids:
            r = requests.delete(f"{BASE_URL}/contratados/{cls.created_ids['contratado']}", headers=cls.admin_headers)
            print(f"Contratado ID {cls.created_ids['contratado']} deletado (Status: {r.status_code}).")
            
        print("Limpeza concluída.")


if __name__ == '__main__':
    unittest.main()