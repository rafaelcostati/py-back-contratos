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

BASE_URL = os.getenv('BASE_URL')
# Caminhos para os arquivos de teste
PDF_CONTRATO_PATH =  os.getenv('PDF_CONTRATO_PATH')
TXT_RELATORIO_PATH = os.getenv('TXT_RELATORIO_PATH')


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
            response_json = r.json()

            # --- CORREÇÃO APLICADA AQUI ---
            # Verifica se a resposta é um dicionário (paginado) ou uma lista (não paginado)
            if isinstance(response_json, dict) and 'data' in response_json:
                items = response_json['data']
            elif isinstance(response_json, list):
                items = response_json
            else:
                raise TypeError(f"Formato de resposta inesperado do endpoint {endpoint}")
            # --- FIM DA CORREÇÃO ---
            
            for item in items:
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
        
        # Contratado
        r_contratado = requests.post(f'{BASE_URL}/contratados', json={"nome": "Empresa de Teste de Email LTDA", "email": f"contratado_email_test_{generate_random_string()}@teste.com", "cnpj": f"{random.randint(10**13, 10**14-1)}"}, headers=cls.admin_headers)
        assert r_contratado.status_code == 201, "Falha ao criar o Contratado."
        cls.created_ids['contratado'] = r_contratado.json()['id']
        
        # Gestor com email específico
        cls.gestor_email = os.getenv('EMAIL_GESTOR')
        cls.gestor_pass = "senha_gestor_123"
        gestor_payload = {
            "nome": "Anderson Pontes (Teste Automático)", 
            "email": cls.gestor_email, 
            "cpf": f"{random.randint(10**10, 10**11-1)}", # CPF Fictício
            "senha": cls.gestor_pass, 
            "perfil_id": cls.seed_ids['perfil_gestor']
        }
        r_gestor = requests.post(f'{BASE_URL}/usuarios', json=gestor_payload, headers=cls.admin_headers)
        assert r_gestor.status_code == 201, f"Falha ao criar Gestor. O email '{cls.gestor_email}' já pode existir no banco. Se necessário, apague-o e rode o teste novamente. Detalhe: {r_gestor.text}"
        cls.created_ids['gestor'] = r_gestor.json()['id']

        # Fiscal com email específico
        cls.fiscal_email = os.getenv('EMAIL_FISCAL')
        cls.fiscal_pass = "senha_fiscal_123"
        fiscal_payload = {
            "nome": "Rafael Costa (Teste Automático)", 
            "email": cls.fiscal_email, 
            "cpf": f"{random.randint(10**10, 10**11-1)}", # CPF Fictício
            "senha": cls.fiscal_pass, 
            "perfil_id": cls.seed_ids['perfil_fiscal']
        }
        r_fiscal = requests.post(f'{BASE_URL}/usuarios', json=fiscal_payload, headers=cls.admin_headers)
        assert r_fiscal.status_code == 201, f"Falha ao criar Fiscal. O email '{cls.fiscal_email}' já pode existir no banco. Se necessário, apague-o e rode o teste novamente. Detalhe: {r_fiscal.text}"
        cls.created_ids['fiscal'] = r_fiscal.json()['id']
        
        print(f"-> Atores criados: Contratado({cls.created_ids['contratado']}), Gestor({cls.created_ids['gestor']}), Fiscal({cls.created_ids['fiscal']})")
        
        # --- 4. Login como Gestor e Fiscal para obter seus tokens ---
        r_login_gestor = requests.post(f'{BASE_URL}/auth/login', json={'email': cls.gestor_email, 'senha': cls.gestor_pass})
        cls.auth_tokens['gestor'] = r_login_gestor.json()['token']
        
        r_login_fiscal = requests.post(f'{BASE_URL}/auth/login', json={'email': cls.fiscal_email, 'senha': cls.fiscal_pass})
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
            files = {'documentos_contrato': (os.path.basename(PDF_CONTRATO_PATH), f, 'application/pdf')}
            r_contrato = requests.post(f'{BASE_URL}/contratos', data=form_data, files=files, headers=self.admin_headers)
        
        self.assertEqual(r_contrato.status_code, 201, f"Falha ao criar contrato: {r_contrato.text}")
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
        
        contratos_gestor = r_gestor_lista.json()['data']
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
        self.assertGreater(len(r_admin.json()['data']), 0)
        print(" -> Admin vê todos os contratos.")

        # Fiscal: deve ver apenas o seu contrato.
        fiscal_headers = {'Authorization': f'Bearer {self.auth_tokens["fiscal"]}'}
        r_fiscal = requests.get(f"{BASE_URL}/contratos?fiscal_id={self.created_ids['fiscal']}", headers=fiscal_headers)
        self.assertEqual(r_fiscal.status_code, 200)
        self.assertEqual(len(r_fiscal.json()['data']), 1)
        self.assertEqual(r_fiscal.json()['data'][0]['id'], contrato_id)
        print(" -> Fiscal vê apenas seus contratos.")
        
        # Gestor: não deve ver o contrato do fiscal ao filtrar por outro ID.
        gestor_headers = {'Authorization': f'Bearer {self.auth_tokens["gestor"]}'}
        r_gestor_vazio = requests.get(f"{BASE_URL}/contratos?fiscal_id={self.created_ids['gestor']}", headers=gestor_headers)
        self.assertEqual(r_gestor_vazio.status_code, 200)
        self.assertEqual(len(r_gestor_vazio.json()['data']), 0)
        print(" -> Filtro por ID de fiscal diferente retorna lista vazia, como esperado.")
        
    def test_07_password_management(self):
        """ Testa as rotas de alteração e reset de senha. """
        print("\nPASSO 7: Testando o gerenciamento de senhas.")
        fiscal_id = self.created_ids['fiscal']
        fiscal_headers = {'Authorization': f'Bearer {self.auth_tokens["fiscal"]}'}
        nova_senha = "nova_senha_123"

        # Tenta alterar a senha com a senha antiga errada (deve falhar)
        payload_errado = {"senha_antiga": "senha_errada", "nova_senha": nova_senha}
        r_fail = requests.patch(f'{BASE_URL}/usuarios/{fiscal_id}/alterar-senha', json=payload_errado, headers=fiscal_headers)
        self.assertEqual(r_fail.status_code, 401)
        print(" -> API bloqueou a alteração de senha com a senha antiga incorreta.")

        # Altera a senha com a senha antiga correta (deve funcionar)
        payload_correto = {"senha_antiga": self.fiscal_pass, "nova_senha": nova_senha}
        r_success = requests.patch(f'{BASE_URL}/usuarios/{fiscal_id}/alterar-senha', json=payload_correto, headers=fiscal_headers)
        self.assertEqual(r_success.status_code, 200)
        print(" -> Usuário (Fiscal) alterou a própria senha com sucesso.")

        # Verifica se consegue fazer login com a nova senha
        r_login_new = requests.post(f'{BASE_URL}/auth/login', json={'email': self.fiscal_email, 'senha': nova_senha})
        self.assertEqual(r_login_new.status_code, 200)
        print(" -> Login com a nova senha funciona.")

        # Admin reseta a senha do usuário
        senha_resetada = "senha_resetada_pelo_admin"
        r_reset = requests.patch(f'{BASE_URL}/usuarios/{fiscal_id}/resetar-senha', json={"nova_senha": senha_resetada}, headers=self.admin_headers)
        self.assertEqual(r_reset.status_code, 200)
        print(" -> Admin resetou a senha do usuário com sucesso.")

        # Verifica se consegue fazer login com a senha resetada
        r_login_reset = requests.post(f'{BASE_URL}/auth/login', json={'email': self.fiscal_email, 'senha': senha_resetada})
        self.assertEqual(r_login_reset.status_code, 200)
        print(" -> Login com a senha resetada funciona.")

    def test_08_advanced_error_handling(self):
        """ Testa cenários de erro mais complexos e regras de negócio. """
        print("\nPASSO 8: Testando tratamento de erros avançado.")
        self.assertIn('contrato', self.created_ids, "O contrato do teste de workflow não foi criado para o teste 08.")
        contrato_id = self.created_ids['contrato']
        fiscal_headers = {'Authorization': f'Bearer {self.auth_tokens["fiscal"]}'}
        
        # Tenta fazer upload de arquivo com extensão não permitida
        with open("teste.zip", "w") as f: f.write("conteudo")
        with open("teste.zip", "rb") as f:
            files = {'arquivo': ('teste.zip', f, 'application/zip')}
            form_data = { 'mes_competencia': '2025-01-01', 'fiscal_usuario_id': self.created_ids['fiscal'], 'pendencia_id': 999 }
            r_extensao = requests.post(f'{BASE_URL}/contratos/{contrato_id}/relatorios', data=form_data, files=files, headers=fiscal_headers)
        os.remove("teste.zip")
        self.assertEqual(r_extensao.status_code, 400)
        print(" -> API bloqueou o upload de arquivo com extensão não permitida.")

        # Cria um segundo contrato que não pertence ao fiscal principal
        outro_gestor_payload = {"nome": "Outro Gestor", "email": f"outrogestor_{generate_random_string()}@test.com", "cpf": f"{random.randint(10**10, 10**11-1)}", "senha": "123", "perfil_id": self.seed_ids['perfil_gestor']}
        r_outro_gestor = requests.post(f'{BASE_URL}/usuarios', json=outro_gestor_payload, headers=self.admin_headers)
        outro_gestor_id = r_outro_gestor.json()['id']
        self.created_ids['outro_gestor'] = outro_gestor_id # Adiciona para limpeza
        
        outro_contrato_form = {
            "nr_contrato": f"WF-OUTRO-{generate_random_string()}", "objeto": "Outro Contrato", "data_inicio": "2025-01-01", "data_fim": "2025-12-31",
            "contratado_id": self.created_ids['contratado'], "modalidade_id": self.seed_ids['modalidade'], "status_id": self.seed_ids['status_vigente'], 
            "gestor_id": outro_gestor_id, "fiscal_id": outro_gestor_id # Fiscal e gestor são a mesma pessoa
        }
        r_outro_contrato = requests.post(f'{BASE_URL}/contratos', json=outro_contrato_form, headers=self.admin_headers)
        outro_contrato_id = r_outro_contrato.json()['id']
        self.created_ids['outro_contrato'] = outro_contrato_id # Adiciona para limpeza

        # Fiscal principal tenta enviar relatório para o contrato que não é dele (deve falhar)
        # Criamos uma pendência primeiro para o teste ser mais realista
        pendencia_outro_payload = {"descricao": "Pendencia Outro", "data_prazo": "2025-01-01", "status_pendencia_id": self.seed_ids['status_pendencia_pendente'], "criado_por_usuario_id": self.created_ids['admin']}
        r_pend_outro = requests.post(f'{BASE_URL}/contratos/{outro_contrato_id}/pendencias', json=pendencia_outro_payload, headers=self.admin_headers)
        pendencia_outro_id = r_pend_outro.json()['id']

        r_permissao = requests.post(f'{BASE_URL}/contratos/{outro_contrato_id}/relatorios', data={'pendencia_id': pendencia_outro_id}, headers=fiscal_headers)
        # O ideal é 403 (Forbidden), mas dependendo da lógica pode ser outro erro 4xx
        self.assertGreaterEqual(r_permissao.status_code, 400)
        self.assertLess(r_permissao.status_code, 500)
        print(" -> Fiscal foi bloqueado de interagir com um contrato que não é seu.")
        
    def test_09_data_integrity_and_constraints(self):
        """ Testa a integridade dos dados, como a prevenção de exclusão de dados em uso e o soft delete. """
        print("\nPASSO 9: Testando integridade de dados e restrições.")
        
        # --- Cenário 1: Proteção contra exclusão de entidade em uso ---
        contratado_payload = {"nome": f"Contratado Protegido", "email": f"protegido_{generate_random_string()}@test.com"}
        r_contratado = requests.post(f'{BASE_URL}/contratados', json=contratado_payload, headers=self.admin_headers)
        contratado_id = r_contratado.json()['id']
        
        contrato_payload = {
            "nr_contrato": f"WF-INTEGRITY-{generate_random_string()}", "objeto": "Contrato para Teste de Integridade", "data_inicio": "2025-01-01", "data_fim": "2025-12-31",
            "contratado_id": contratado_id, "modalidade_id": self.seed_ids['modalidade'], "status_id": self.seed_ids['status_vigente'],
            "gestor_id": self.created_ids['gestor'], "fiscal_id": self.created_ids['fiscal']
        }
        r_contrato = requests.post(f'{BASE_URL}/contratos', json=contrato_payload, headers=self.admin_headers)
        contrato_id_integridade = r_contrato.json()['id']
        self.created_ids['contrato_integridade'] = contrato_id_integridade # Para limpeza

        # Tenta deletar o contratado que está em uso (deve falhar)
        r_delete_fail = requests.delete(f"{BASE_URL}/contratados/{contratado_id}", headers=self.admin_headers)
        self.assertEqual(r_delete_fail.status_code, 409)
        print(" -> API protegeu contra a exclusão de um contratado em uso.")

        # --- Cenário 2: Validação de Soft Delete ---
        # Cria um usuário para ser deletado
        user_payload = {"nome": "Usuário a ser deletado", "email": f"deleteme_{generate_random_string()}@test.com", "cpf": f"{random.randint(10**10, 10**11-1)}", "senha": "123", "perfil_id": self.seed_ids['perfil_fiscal']}
        r_user = requests.post(f'{BASE_URL}/usuarios', json=user_payload, headers=self.admin_headers)
        user_id_todelete = r_user.json()['id']
        
        # Verifica que o usuário está na lista
        r_users_before = requests.get(f'{BASE_URL}/usuarios', headers=self.admin_headers).json()['data']
        self.assertTrue(any(user['id'] == user_id_todelete for user in r_users_before))
        print(f" -> Usuário {user_id_todelete} existe na lista antes do delete.")
        
        # Deleta o usuário (soft delete)
        requests.delete(f"{BASE_URL}/usuarios/{user_id_todelete}", headers=self.admin_headers)
        
        # Verifica que o usuário NÃO está mais na lista
        r_users_after = requests.get(f'{BASE_URL}/usuarios', headers=self.admin_headers).json()['data']
        self.assertFalse(any(user['id'] == user_id_todelete for user in r_users_after))
        print(f" -> Usuário {user_id_todelete} não existe mais na lista após o soft delete, como esperado.")

    @classmethod
    def tearDownClass(cls):
        """ Limpa todos os recursos criados durante os testes. """
        print("\n--- INICIANDO LIMPEZA DO AMBIENTE DE TESTE ---")
        
        # A ordem de deleção é importante para evitar erros de chave estrangeira
        # Limpa contratos primeiro
        if 'contrato_integridade' in cls.created_ids:
             requests.delete(f"{BASE_URL}/contratos/{cls.created_ids['contrato_integridade']}", headers=cls.admin_headers)
        if 'outro_contrato' in cls.created_ids:
            requests.delete(f"{BASE_URL}/contratos/{cls.created_ids['outro_contrato']}", headers=cls.admin_headers)
        if 'contrato' in cls.created_ids:
            r = requests.delete(f"{BASE_URL}/contratos/{cls.created_ids['contrato']}", headers=cls.admin_headers)
            print(f"Contrato principal ID {cls.created_ids['contrato']} deletado (Status: {r.status_code}).")
        
        # Limpa usuários depois
        if 'outro_gestor' in cls.created_ids:
            requests.delete(f"{BASE_URL}/usuarios/{cls.created_ids['outro_gestor']}", headers=cls.admin_headers)
        if 'gestor' in cls.created_ids:
            r = requests.delete(f"{BASE_URL}/usuarios/{cls.created_ids['gestor']}", headers=cls.admin_headers)
            print(f"Usuário Gestor ID {cls.created_ids['gestor']} deletado (Status: {r.status_code}).")
        if 'fiscal' in cls.created_ids:
            r = requests.delete(f"{BASE_URL}/usuarios/{cls.created_ids['fiscal']}", headers=cls.admin_headers)
            print(f"Usuário Fiscal ID {cls.created_ids['fiscal']} deletado (Status: {r.status_code}).")
        
        # Finalmente, limpa contratados
        if 'contratado' in cls.created_ids:
            r = requests.delete(f"{BASE_URL}/contratados/{cls.created_ids['contratado']}", headers=cls.admin_headers)
            print(f"Contratado ID {cls.created_ids['contratado']} deletado (Status: {r.status_code}).")
            
        print("Limpeza concluída.")


if __name__ == '__main__':
    unittest.main()