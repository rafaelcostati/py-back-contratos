import unittest
import requests
import os
import random
import string

BASE_URL = 'http://127.0.0.1:5000'

def generate_random_string(length=8):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

class TestRealisticWorkflow(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Prepara o ambiente para o fluxo de teste completo."""
        print("\n--- INICIANDO PREPARAÇÃO DO FLUXO DE TESTE REALÍSTICO ---")
        
        cls.created_ids = {}
        cls.seed_ids = {}

        def get_id_by_name(endpoint, name):
            r = requests.get(f"{BASE_URL}{endpoint}")
            assert r.status_code == 200, f"Falha ao buscar dados de {endpoint}"
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
        
        # Pega o ID do Admin criado pelo seeder
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@sigescon.com')
        r_users = requests.get(f'{BASE_URL}/usuarios')
        cls.created_ids['admin'] = next(user['id'] for user in r_users.json() if user['email'] == admin_email)
        print("-> IDs do seed carregados com sucesso.")

        print("-> Criando atores para o teste (Contratado, Gestor, Fiscal)...")
        random_str = generate_random_string()
        r_contratado = requests.post(f'{BASE_URL}/contratados/', json={"nome": "Empresa de Teste de Workflow", "email": f"workflow_{random_str}@teste.com", "cnpj": f"{random.randint(10**13, 10**14-1)}"})
        cls.created_ids['contratado'] = r_contratado.json()['id']
        
        r_gestor = requests.post(f'{BASE_URL}/usuarios/', json={"nome": "Gestor de Workflow", "email": f"gestor_wf_{random_str}@teste.com", "cpf": f"{random.randint(10**10, 10**11-1)}", "senha": "123", "perfil_id": cls.seed_ids['perfil_gestor']})
        cls.created_ids['gestor'] = r_gestor.json()['id']

        r_fiscal = requests.post(f'{BASE_URL}/usuarios/', json={"nome": "Fiscal de Workflow", "email": f"fiscal_wf_{random_str}@teste.com", "cpf": f"{random.randint(10**10, 10**11-1)}", "senha": "123", "perfil_id": cls.seed_ids['perfil_fiscal']})
        cls.created_ids['fiscal'] = r_fiscal.json()['id']
        
        print(f"-> Atores criados com sucesso: Contratado({cls.created_ids['contratado']}), Gestor({cls.created_ids['gestor']}), Fiscal({cls.created_ids['fiscal']})")


    def test_workflow_completo(self):
        """Simula o fluxo de ponta a ponta com diferentes perfis."""
        
        # --- PASSO 1 (Admin): Cria o Contrato ---
        print("\nPASSO 1 (Admin): Criando o contrato...")
        contrato_payload = {
            "nr_contrato": f"WF-{generate_random_string()}", "objeto": "Contrato do Workflow de Teste",
            "data_inicio": "2025-01-01", "data_fim": "2025-12-31",
            "contratado_id": self.created_ids['contratado'], "modalidade_id": self.seed_ids['modalidade'],
            "status_id": self.seed_ids['status_vigente'], "gestor_id": self.created_ids['gestor'], 
            "fiscal_id": self.created_ids['fiscal'], "fiscal_substituto_id": self.created_ids['fiscal']
        }
        r = requests.post(f'{BASE_URL}/contratos/', json=contrato_payload); self.assertEqual(r.status_code, 201)
        contrato_id = r.json()['id']
        self.__class__.created_ids['contrato'] = contrato_id
        print(f"-> Contrato ID {contrato_id} criado.")

        # --- PASSO 2 (Admin): Cria a Pendência ---
        print("\nPASSO 2 (Admin): Criando pendência para o fiscal...")
        pendencia_payload = {
            "descricao": "Relatório inicial de atividades.", "data_prazo": "2025-02-28",
            "status_pendencia_id": self.seed_ids['status_pendencia_pendente'], 
            "criado_por_usuario_id": self.created_ids['admin']
        }
        r = requests.post(f'{BASE_URL}/contratos/{contrato_id}/pendencias', json=pendencia_payload); self.assertEqual(r.status_code, 201)
        pendencia_id = r.json()['id']
        print(f"-> Pendência ID {pendencia_id} criada.")
        
        # --- PASSO 3 (Fiscal): Envia o Relatório ---
        print("\nPASSO 3 (Fiscal): Enviando o primeiro relatório...")
        test_filename_1 = "relatorio_v1.txt"
        with open(test_filename_1, "w") as f: f.write("Primeira versão do relatório.")
        with open(test_filename_1, "rb") as f:
            files = {'arquivo': (test_filename_1, f, 'text/plain')}
            form_data = {
                'mes_competencia': '2025-01-01', 'fiscal_usuario_id': self.created_ids['fiscal'],
                'status_id': self.seed_ids['status_relatorio_pendente'], 'pendencia_id': pendencia_id
            }
            r = requests.post(f'{BASE_URL}/contratos/{contrato_id}/relatorios', data=form_data, files=files)
        os.remove(test_filename_1)
        self.assertEqual(r.status_code, 201)
        relatorio_id = r.json()['id']
        self.__class__.created_ids['relatorio'] = relatorio_id
        print(f"-> Relatório ID {relatorio_id} enviado pelo fiscal.")
        
        # --- PASSO 4 (Admin): Rejeita o Relatório ---
        print("\nPASSO 4 (Admin): Rejeitando o relatório com observações...")
        analise_payload = {
            "aprovador_usuario_id": self.created_ids['admin'],
            "status_id": self.seed_ids['status_relatorio_rejeitado'],
            "observacoes_aprovador": "Faltou incluir o anexo B. Corrija e reenvie."
        }
        r = requests.patch(f'{BASE_URL}/contratos/{contrato_id}/relatorios/{relatorio_id}/analise', json=analise_payload)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['status_id'], self.seed_ids['status_relatorio_rejeitado'])
        print("-> Relatório rejeitado com sucesso.")
        
        # --- PASSO 5 (Fiscal): Reenvia o Relatório ---
        print("\nPASSO 5 (Fiscal): Reenviando o relatório corrigido...")
        test_filename_2 = "relatorio_v2.txt"
        with open(test_filename_2, "w") as f: f.write("Segunda versão corrigida do relatório com anexo B.")
        with open(test_filename_2, "rb") as f:
            files = {'arquivo': (test_filename_2, f, 'text/plain')}
            form_data = {'observacoes_fiscal': 'Correções aplicadas conforme solicitado.'}
            r = requests.put(f'{BASE_URL}/contratos/{contrato_id}/relatorios/{relatorio_id}', data=form_data, files=files)
        os.remove(test_filename_2)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['status_id'], self.seed_ids['status_relatorio_pendente'])
        print(f"-> Relatório ID {relatorio_id} reenviado com sucesso e status 'Pendente de Análise'.")
        
        # --- PASSO 6 (Admin): Aprova o Relatório Final ---
        print("\nPASSO 6 (Admin): Aprovando o relatório final...")
        analise_aprovacao_payload = { "aprovador_usuario_id": self.created_ids['admin'], "status_id": self.seed_ids['status_relatorio_aprovado'] }
        r = requests.patch(f'{BASE_URL}/contratos/{contrato_id}/relatorios/{relatorio_id}/analise', json=analise_aprovacao_payload)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['status_id'], self.seed_ids['status_relatorio_aprovado'])
        print("-> Relatório final aprovado.")
        
        # --- PASSO 7 (Gestor): Consulta seus contratos ---
        print("\nPASSO 7 (Gestor): Verificando se consegue ver apenas seu contrato...")
        r = requests.get(f"{BASE_URL}/contratos?gestor_id={self.created_ids['gestor']}")
        self.assertEqual(r.status_code, 200)
        contratos_gestor = r.json()
        self.assertEqual(len(contratos_gestor), 1)
        self.assertEqual(contratos_gestor[0]['id'], contrato_id)
        print("-> Consulta de contratos por gestor funciona corretamente.")
        
        # --- PASSO 8 (Admin): Altera o status do ciclo de vida do contrato ---
        print("\nPASSO 8 (Admin): Alterando o status do ciclo de vida do contrato...")
        r = requests.patch(f'{BASE_URL}/contratos/{contrato_id}', json={"status_id": self.seed_ids['status_suspenso']})
        self.assertEqual(r.status_code, 200)
        r_verify = requests.get(f'{BASE_URL}/contratos/{contrato_id}')
        self.assertEqual(r_verify.json()['status_nome'], 'Suspenso')
        print("-> Status do contrato alterado com sucesso.")

    @classmethod
    def tearDownClass(cls):
        print("\n--- INICIANDO LIMPEZA DO AMBIENTE DE TESTE ---")
        if 'contrato' in cls.created_ids:
            requests.delete(f"{BASE_URL}/contratos/{cls.created_ids['contrato']}")
            print(f"Contrato ID {cls.created_ids['contrato']} deletado.")
        if 'gestor' in cls.created_ids:
            requests.delete(f"{BASE_URL}/usuarios/{cls.created_ids['gestor']}")
            print(f"Usuário Gestor ID {cls.created_ids['gestor']} deletado.")
        if 'fiscal' in cls.created_ids:
            requests.delete(f"{BASE_URL}/usuarios/{cls.created_ids['fiscal']}")
            print(f"Usuário Fiscal ID {cls.created_ids['fiscal']} deletado.")
        if 'contratado' in cls.created_ids:
            requests.delete(f"{BASE_URL}/contratados/{cls.created_ids['contratado']}")
            print(f"Contratado ID {cls.created_ids['contratado']} deletado.")
        print("Limpeza concluída.")


if __name__ == '__main__':
    unittest.main()