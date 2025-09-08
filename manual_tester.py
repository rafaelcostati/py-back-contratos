# manual_tester.py
import requests
import os
import json
from pprint import pprint

# --- Configuração ---
BASE_URL = 'http://127.0.0.1:5000'
CURRENT_USER = None

# --- Funções Auxiliares ---

def clear_screen():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_for_enter():
    """Pausa a execução até o usuário pressionar Enter."""
    input("\nPressione Enter para continuar...")

def handle_response(response):
    """Verifica a resposta da API e imprime o resultado formatado."""
    print("-" * 50)
    if 200 <= response.status_code < 300:
        print("✅ SUCESSO!")
        try:
            pprint(response.json())
        except json.JSONDecodeError:
            print("(Nenhum conteúdo JSON na resposta)")
        return response.json()
    else:
        print(f"❌ ERRO! (Status Code: {response.status_code})")
        try:
            pprint(response.json())
        except json.JSONDecodeError:
            print("Nenhuma mensagem de erro JSON retornada.")
            print(response.text)
        return None

def get_entities(endpoint):
    """Busca e imprime uma lista de entidades da API."""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        if response.status_code == 200:
            entities = response.json()
            if not entities:
                print(f"Nenhum item encontrado em {endpoint}")
                return None
            
            print(f"\n--- Itens disponíveis em {endpoint} ---")
            for item in entities:
                # Tenta imprimir id e nome, senão imprime o objeto todo
                if isinstance(item, dict) and 'id' in item and 'nome' in item:
                     print(f"  ID: {item['id']} | Nome: {item['nome']}")
                else:
                    pprint(item)
            return entities
        else:
            handle_response(response)
            return None
    except requests.exceptions.ConnectionError:
        print("ERRO: Não foi possível conectar à API. O servidor Flask está rodando?")
        return None

# --- Menus Principais ---

def admin_menu():
    """Menu de ações para o perfil Administrador."""
    while True:
        clear_screen()
        print(f"Você está atuando como: {CURRENT_USER['nome']} (Administrador)")
        print("-" * 50)
        print("1. Gerenciar Contratos")
        print("2. Gerenciar Usuários")
        print("3. Gerenciar Contratados")
        print("4. Voltar para seleção de perfil")
        
        choice = input("> ")
        if choice == '1':
            admin_contracts_menu()
        elif choice == '2':
            print("Funcionalidade de gerenciar usuários a ser implementada.")
            wait_for_enter()
        elif choice == '3':
            print("Funcionalidade de gerenciar contratados a ser implementada.")
            wait_for_enter()
        elif choice == '4':
            return
        else:
            print("Opção inválida.")
            wait_for_enter()

def fiscal_menu():
    """Menu de ações para o perfil Fiscal."""
    while True:
        clear_screen()
        print(f"Você está atuando como: {CURRENT_USER['nome']} (Fiscal)")
        print("-" * 50)
        print("1. Ver Meus Contratos e Pendências")
        print("2. Submeter / Reenviar Relatório")
        print("3. Voltar para seleção de perfil")

        choice = input("> ")
        if choice == '1':
            contratos = get_entities(f"/contratos?fiscal_id={CURRENT_USER['id']}")
            if contratos:
                for contrato in contratos:
                    print(f"\n--- Pendências/Relatórios do Contrato ID {contrato['id']} ---")
                    # Busca e exibe pendências
                    pendencias = requests.get(f"{BASE_URL}/contratos/{contrato['id']}/pendencias").json()
                    if pendencias:
                        print("Pendências:")
                        pprint(pendencias)
                    else:
                        print("Nenhuma pendência encontrada.")
            wait_for_enter()
        elif choice == '2':
            submit_report_flow()
        elif choice == '3':
            return
        else:
            print("Opção inválida.")
            wait_for_enter()

def gestor_menu():
    """Menu de ações para o perfil Gestor."""
    while True:
        clear_screen()
        print(f"Você está atuando como: {CURRENT_USER['nome']} (Gestor)")
        print("-" * 50)
        print("1. Ver Meus Contratos")
        print("2. Voltar para seleção de perfil")

        choice = input("> ")
        if choice == '1':
            get_entities(f"/contratos?gestor_id={CURRENT_USER['id']}")
            wait_for_enter()
        elif choice == '2':
            return
        else:
            print("Opção inválida.")
            wait_for_enter()

# --- Submenus e Fluxos ---

def admin_contracts_menu():
    """Submenu do Admin para gerenciar contratos."""
    while True:
        clear_screen()
        print(f"Você está atuando como: {CURRENT_USER['nome']} (Admin)")
        print("--- Gerenciamento de Contratos ---")
        print("1. Listar TODOS os Contratos")
        print("2. Criar Novo Contrato")
        print("3. Criar Pendência para um Contrato")
        print("4. Analisar um Relatório")
        print("5. Voltar ao menu principal")

        choice = input("> ")
        if choice == '1':
            get_entities("/contratos")
            wait_for_enter()
        elif choice == '2':
            create_contract_flow()
        elif choice == '3':
            create_pendencia_flow()
        elif choice == '4':
            analise_relatorio_flow()
        elif choice == '5':
            return

def create_contract_flow():
    """Fluxo guiado para criar um novo contrato."""
    clear_screen()
    print("--- CRIAR NOVO CONTRATO ---")
    payload = {}
    
    # Coleta de dados com ajuda para o usuário
    payload['nr_contrato'] = input("Número do Contrato: ")
    payload['objeto'] = input("Objeto do Contrato: ")
    payload['data_inicio'] = input("Data de Início (AAAA-MM-DD): ")
    payload['data_fim'] = input("Data de Fim (AAAA-MM-DD): ")

    if get_entities("/contratados"):
        payload['contratado_id'] = int(input("ID do Contratado: "))
    if get_entities("/modalidades"):
        payload['modalidade_id'] = int(input("ID da Modalidade: "))
    if get_entities("/status"):
        payload['status_id'] = int(input("ID do Status do Contrato: "))
    if get_entities("/usuarios"): # Idealmente filtrar por perfil
        payload['gestor_id'] = int(input("ID do Gestor: "))
        payload['fiscal_id'] = int(input("ID do Fiscal: "))
    
    print("\nEnviando dados para a API...")
    response = requests.post(f"{BASE_URL}/contratos", json=payload)
    handle_response(response)
    wait_for_enter()

def create_pendencia_flow():
    """Fluxo guiado para criar uma pendência."""
    clear_screen()
    print("--- CRIAR PENDÊNCIA ---")
    if not get_entities("/contratos"):
        wait_for_enter()
        return
    
    contrato_id = int(input("Para qual Contrato (ID) deseja criar a pendência? "))
    
    payload = {
        'descricao': input("Descrição da pendência: "),
        'data_prazo': input("Data Prazo (AAAA-MM-DD): "),
        'criado_por_usuario_id': CURRENT_USER['id']
    }

    if get_entities("/statuspendencia"):
        payload['status_pendencia_id'] = int(input("ID do Status da Pendência: "))
        
    print("\nEnviando dados para a API...")
    response = requests.post(f"{BASE_URL}/contratos/{contrato_id}/pendencias", json=payload)
    handle_response(response)
    wait_for_enter()

def submit_report_flow():
    """Fluxo guiado para o Fiscal submeter um relatório."""
    clear_screen()
    print("--- SUBMETER RELATÓRIO ---")
    
    contratos = get_entities(f"/contratos?fiscal_id={CURRENT_USER['id']}")
    if not contratos:
        wait_for_enter()
        return

    contrato_id = int(input("Para qual Contrato (ID) é este relatório? "))
    
    filepath = input("Digite o caminho completo para o arquivo (ex: /home/user/relatorio.pdf): ")
    if not os.path.exists(filepath):
        print("ERRO: Arquivo não encontrado.")
        wait_for_enter()
        return

    form_data = {
        'mes_competencia': input("Mês de Competência (AAAA-MM-DD): "),
        'fiscal_usuario_id': CURRENT_USER['id'],
        'observacoes_fiscal': input("Observações (opcional): ")
    }
    
    # Assumindo que o status inicial é "Pendente de Análise"
    # O ideal seria buscar o ID pelo nome
    form_data['status_id'] = 1 

    print("\nEnviando arquivo e dados para a API...")
    try:
        with open(filepath, "rb") as f:
            filename = os.path.basename(filepath)
            files = {'arquivo': (filename, f)}
            response = requests.post(f'{BASE_URL}/contratos/{contrato_id}/relatorios', data=form_data, files=files)
        handle_response(response)
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        
    wait_for_enter()

def analise_relatorio_flow():
    """Fluxo para o Admin analisar um relatório."""
    clear_screen()
    print("--- ANALISAR RELATÓRIO ---")
    if not get_entities("/contratos"):
        wait_for_enter()
        return
    contrato_id = int(input("De qual Contrato (ID) você quer ver os relatórios? "))
    
    # Aqui seria ideal ter uma rota para listar relatórios
    print(f"Funcionalidade de listar relatórios do contrato {contrato_id} a ser implementada.")
    relatorio_id = int(input("Qual Relatório (ID) você quer analisar? "))

    print("Opções de Status de Relatório:")
    status_relatorios = get_entities("/statusrelatorio")
    if not status_relatorios:
        wait_for_enter()
        return
    
    status_id = int(input("Qual o novo Status (ID) para este relatório? "))
    observacoes = input("Observações da análise (obrigatório se for rejeitado): ")

    payload = {
        "aprovador_usuario_id": CURRENT_USER['id'],
        "status_id": status_id,
        "observacoes_aprovador": observacoes
    }
    
    response = requests.patch(f"{BASE_URL}/contratos/{contrato_id}/relatorios/{relatorio_id}/analise", json=payload)
    handle_response(response)
    wait_for_enter()


# --- Ponto de Entrada ---
def main():
    """Função principal que inicia o seletor de perfil."""
    global CURRENT_USER
    
    while True:
        clear_screen()
        print("Bem-vindo ao Testador Manual da API SIGESCON!")
        print("=" * 50)
        
        users = get_entities("/usuarios")
        if not users:
            print("\nNão foi possível buscar usuários. Saindo.")
            break
            
        choice = input("\nDigite o ID do usuário para assumir o papel (ou 'sair'): ")
        
        if choice.lower() == 'sair':
            break
        
        try:
            user_id = int(choice)
            user_found = False
            for user in users:
                if user['id'] == user_id:
                    CURRENT_USER = user
                    user_found = True
                    # Busca o nome do perfil
                    perfil_id = user['perfil_id']
                    # A API de perfis precisaria de um GET by ID
                    # Por simplicidade, vamos mapear aqui
                    perfil_map = {1: 'Administrador', 2: 'Gestor', 3: 'Fiscal'}
                    perfil_nome = perfil_map.get(perfil_id, "Desconhecido")
                    
                    if perfil_nome == 'Administrador':
                        admin_menu()
                    elif perfil_nome == 'Fiscal':
                        fiscal_menu()
                    elif perfil_nome == 'Gestor':
                        gestor_menu()
                    else:
                        print(f"Perfil '{perfil_nome}' não tem um menu definido.")
                        wait_for_enter()
                    break
            if not user_found:
                print("ID de usuário inválido.")
                wait_for_enter()
        except ValueError:
            print("Entrada inválida. Por favor, digite um número de ID.")
            wait_for_enter()

if __name__ == "__main__":
    main()