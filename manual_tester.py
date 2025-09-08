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
    print("-" * 50)
    if 200 <= response.status_code < 300:
        print("✅ SUCESSO!")
        try:
            content = response.json()
            if content: pprint(content)
            else: print("(Operação bem-sucedida sem conteúdo de retorno)")
            return content
        except json.JSONDecodeError:
            print("(Operação bem-sucedida sem conteúdo JSON na resposta)")
        return True
    else:
        print(f"❌ ERRO! (Status Code: {response.status_code})")
        try: pprint(response.json())
        except json.JSONDecodeError: print(f"Nenhuma mensagem de erro JSON retornada.\n{response.text}")
        return None

def get_entities(endpoint):
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        if response.status_code == 200:
            entities = response.json()
            if not entities:
                print(f"\nNenhum item encontrado em {endpoint}")
                return None
            print(f"\n--- Itens disponíveis em {endpoint} ---")
            for item in entities:
                line = f"  ID: {item.get('id', ''):<4} |"
                if 'nome' in item: line += f" Nome: {item.get('nome', '')}"
                if 'nr_contrato' in item: line += f" Número: {item.get('nr_contrato', '')}"
                print(line)
            return entities
        else:
            handle_response(response)
            return None
    except requests.exceptions.ConnectionError:
        print("ERRO: Não foi possível conectar à API. O servidor Flask está rodando?")
        return None

# --- Menus de Atores (Admin, Fiscal, Gestor) ---

def admin_menu():
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
            manage_users_admin() # <<< FUNCIONALIDADE IMPLEMENTADA
        elif choice == '3':
            manage_contractors_admin() # <<< FUNCIONALIDADE IMPLEMENTADA
        elif choice == '4':
            return

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
            print("\nBuscando contratos onde você é fiscal...")
            contratos = get_entities(f"/contratos?fiscal_id={CURRENT_USER['id']}")
            if contratos:
                for contrato in contratos:
                    print(f"\n--- Detalhes do Contrato ID {contrato['id']} ({contrato.get('nr_contrato', '')}) ---")
                    
                    pendencias_url = f"/contratos/{contrato['id']}/pendencias"
                    get_entities(pendencias_url)

                    # A API precisa de uma rota para listar relatórios de um contrato
                    # get_entities(f"/contratos/{contrato['id']}/relatorios")
                    
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

# --- Submenus de Gerenciamento ---

def admin_contracts_menu():
    """Submenu do Admin para gerenciar contratos."""
    while True:
        clear_screen()
        print(f"Você está atuando como: {CURRENT_USER['nome']} (Admin)")
        print("--- Gerenciamento de Contratos ---")
        print("1. Listar TODOS os Contratos")
        print("2. Ver Detalhes de um Contrato")
        print("3. Criar Novo Contrato")
        print("4. Atualizar um Contrato")
        print("5. Deletar (Desativar) um Contrato")
        print("6. Criar Pendência para um Contrato")
        print("7. Analisar um Relatório")
        print("8. Voltar ao menu principal")

        choice = input("> ")
        if choice == '1':
            get_entities("/contratos")
            wait_for_enter()
        elif choice == '2':
            get_contract_details_flow()
        elif choice == '3':
            create_contract_flow()
        elif choice == '4':
            update_contract_flow()
        elif choice == '5':
            delete_contract_flow()
        elif choice == '6':
            create_pendencia_flow()
        elif choice == '7':
            analise_relatorio_flow()
        elif choice == '8':
            return

def get_contract_details_flow():
    clear_screen()
    print("--- DETALHES DO CONTRATO ---")
    if not get_entities("/contratos"):
        wait_for_enter()
        return
    try:
        contrato_id = int(input("\nDigite o ID do contrato para ver os detalhes: "))
        response = requests.get(f"{BASE_URL}/contratos/{contrato_id}")
        handle_response(response)
    except ValueError:
        print("ID inválido.")
    wait_for_enter()

def update_contract_flow():
    clear_screen()
    print("--- ATUALIZAR CONTRATO ---")
    if not get_entities("/contratos"):
        wait_for_enter()
        return
    try:
        contrato_id = int(input("\nDigite o ID do contrato a ser atualizado: "))
        print("Deixe o campo em branco para não alterar.")
        payload = {}
        
        objeto = input("Novo objeto do contrato: ")
        if objeto: payload['objeto'] = objeto

        nr_contrato = input(f"Novo número do contrato: ")
        if nr_contrato: payload['nr_contrato'] = nr_contrato

        if not payload:
            print("Nenhum dado para atualizar.")
            wait_for_enter()
            return
        
        response = requests.patch(f"{BASE_URL}/contratos/{contrato_id}", json=payload)
        handle_response(response)
    except ValueError:
        print("ID inválido.")
    wait_for_enter()

def delete_contract_flow():
    clear_screen()
    print("--- DELETAR (DESATIVAR) CONTRATO ---")
    if not get_entities("/contratos"):
        wait_for_enter()
        return
    try:
        contrato_id = int(input("\nDigite o ID do contrato a ser desativado: "))
        confirm = input(f"Tem certeza que deseja desativar o contrato ID {contrato_id}? [s/N]: ")
        if confirm.lower() == 's':
            response = requests.delete(f"{BASE_URL}/contratos/{contrato_id}")
            handle_response(response)
        else:
            print("Operação cancelada.")
    except ValueError:
        print("ID inválido.")
    wait_for_enter()
    
def manage_users_admin():
    """Submenu do Admin para gerenciar usuários."""
    while True:
        clear_screen()
        print(f"Você está atuando como: {CURRENT_USER['nome']} (Admin)")
        print("--- Gerenciamento de Usuários ---")
        print("1. Listar todos os Usuários")
        print("2. Criar Novo Usuário")
        print("3. Atualizar Usuário")
        print("4. Deletar Usuário (Desativar)")
        print("5. Resetar Senha de um Usuário")
        print("6. Voltar ao menu principal")

        choice = input("> ")
        if choice == '1':
            get_entities("/usuarios")
            wait_for_enter()
        elif choice == '2':
            create_user_flow()
        elif choice == '3':
            update_user_flow()
        elif choice == '4':
            delete_user_flow()
        elif choice == '5':
            reset_password_flow()
        elif choice == '6':
            return

def manage_contractors_admin():
    """Submenu do Admin para gerenciar contratados."""
    while True:
        clear_screen()
        print(f"Você está atuando como: {CURRENT_USER['nome']} (Admin)")
        print("--- Gerenciamento de Contratados ---")
        print("1. Listar todos os Contratados")
        print("2. Criar Novo Contratado")
        print("3. Atualizar Contratado")
        print("4. Deletar Contratado (Desativar)")
        print("5. Voltar ao menu principal")

        choice = input("> ")
        if choice == '1':
            get_entities("/contratados")
            wait_for_enter()
        elif choice == '2':
            create_contractor_flow()
        elif choice == '3':
            update_contractor_flow()
        elif choice == '4':
            delete_contractor_flow()
        elif choice == '5':
            return

# --- Fluxos de Ações ---

def create_user_flow():
    clear_screen()
    print("--- CRIAR NOVO USUÁRIO ---")
    payload = {
        'nome': input("Nome: "),
        'email': input("Email: "),
        'cpf': input("CPF (apenas números): "),
        'matricula': input("Matrícula (opcional): "),
        'senha': input("Senha: ")
    }
    if get_entities("/perfis"):
        payload['perfil_id'] = int(input("ID do Perfil: "))
    
    print("\nEnviando dados...")
    response = requests.post(f"{BASE_URL}/usuarios", json=payload)
    handle_response(response)
    wait_for_enter()

def update_user_flow():
    clear_screen()
    print("--- ATUALIZAR USUÁRIO ---")
    users = get_entities("/usuarios")
    if not users:
        wait_for_enter()
        return
    
    user_id = int(input("\nDigite o ID do usuário que deseja atualizar: "))
    print("Deixe o campo em branco para não alterar.")
    
    payload = {}
    nome = input("Novo nome: ")
    if nome: payload['nome'] = nome
    
    email = input("Novo email: ")
    if email: payload['email'] = email

    if not payload:
        print("Nenhum dado para atualizar.")
        wait_for_enter()
        return
        
    print("\nEnviando dados...")
    response = requests.patch(f"{BASE_URL}/usuarios/{user_id}", json=payload)
    handle_response(response)
    wait_for_enter()

def delete_user_flow():
    clear_screen()
    print("--- DELETAR (DESATIVAR) USUÁRIO ---")
    users = get_entities("/usuarios")
    if not users:
        wait_for_enter()
        return
    
    user_id = int(input("\nDigite o ID do usuário que deseja deletar (desativar): "))
    confirm = input(f"Tem certeza que deseja desativar o usuário ID {user_id}? [s/N]: ")

    if confirm.lower() == 's':
        print("\nEnviando requisição...")
        response = requests.delete(f"{BASE_URL}/usuarios/{user_id}")
        handle_response(response)
    else:
        print("Operação cancelada.")
    wait_for_enter()

def reset_password_flow():
    clear_screen()
    print("--- RESETAR SENHA DE USUÁRIO ---")
    users = get_entities("/usuarios")
    if not users:
        wait_for_enter()
        return
    
    user_id = int(input("\nDigite o ID do usuário para resetar a senha: "))
    nova_senha = input("Digite a NOVA senha: ")

    print("\nEnviando dados...")
    response = requests.patch(f"{BASE_URL}/usuarios/{user_id}/resetar-senha", json={'nova_senha': nova_senha})
    handle_response(response)
    wait_for_enter()

def create_contractor_flow():
    clear_screen()
    print("--- CRIAR NOVO CONTRATADO ---")
    payload = {
        'nome': input("Nome/Razão Social: "),
        'email': input("Email de contato: "),
        'cnpj': input("CNPJ (opcional, apenas números): "),
        'cpf': input("CPF (opcional, apenas números): "),
        'telefone': input("Telefone (opcional): ")
    }
    print("\nEnviando dados...")
    response = requests.post(f"{BASE_URL}/contratados", json=payload)
    handle_response(response)
    wait_for_enter()

def update_contractor_flow():
    clear_screen()
    print("--- ATUALIZAR CONTRATADO ---")
    contractors = get_entities("/contratados")
    if not contractors:
        wait_for_enter()
        return
    
    contractor_id = int(input("\nDigite o ID do contratado que deseja atualizar: "))
    print("Deixe o campo em branco para não alterar.")
    
    payload = {}
    nome = input("Novo nome/razão social: ")
    if nome: payload['nome'] = nome
    
    email = input("Novo email: ")
    if email: payload['email'] = email
    
    telefone = input("Novo telefone: ")
    if telefone: payload['telefone'] = telefone

    if not payload:
        print("Nenhum dado para atualizar.")
        wait_for_enter()
        return
        
    print("\nEnviando dados...")
    response = requests.patch(f"{BASE_URL}/contratados/{contractor_id}", json=payload)
    handle_response(response)
    wait_for_enter()

def delete_contractor_flow():
    clear_screen()
    print("--- DELETAR (DESATIVAR) CONTRATADO ---")
    contractors = get_entities("/contratados")
    if not contractors:
        wait_for_enter()
        return
    
    contractor_id = int(input("\nDigite o ID do contratado que deseja deletar (desativar): "))
    confirm = input(f"Tem certeza que deseja desativar o contratado ID {contractor_id}? [s/N]: ")

    if confirm.lower() == 's':
        print("\nEnviando requisição...")
        response = requests.delete(f"{BASE_URL}/contratados/{contractor_id}")
        handle_response(response)
    else:
        print("Operação cancelada.")
    wait_for_enter()

# --- Copie e cole as funções que não mudaram ---
def create_contract_flow():
    """Fluxo guiado para criar um novo contrato, com todos os campos opcionais."""
    clear_screen()
    print("--- CRIAR NOVO CONTRATO ---")
    print("Preencha os campos obrigatórios. Para os opcionais, pressione Enter para pular.")
    
    # Dicionário para os dados do formulário
    form_data = {}
    
    # --- Campos Obrigatórios ---
    form_data['nr_contrato'] = input("(*) Número do Contrato: ")
    form_data['objeto'] = input("(*) Objeto do Contrato: ")
    form_data['data_inicio'] = input("(*) Data de Início (AAAA-MM-DD): ")
    form_data['data_fim'] = input("(*) Data de Fim (AAAA-MM-DD): ")

    if get_entities("/contratados"):
        form_data['contratado_id'] = input("(*) ID do Contratado: ")
    if get_entities("/modalidades"):
        form_data['modalidade_id'] = input("(*) ID da Modalidade: ")
    if get_entities("/status"):
        form_data['status_id'] = input("(*) ID do Status do Contrato: ")
    
    print("\n--- Seleção de Pessoal ---")
    if get_entities("/usuarios"):
        form_data['gestor_id'] = input("(*) ID do Gestor: ")
        form_data['fiscal_id'] = input("(*) ID do Fiscal Principal: ")
        # --- CAMPO OPCIONAL ADICIONADO ---
        fiscal_sub_id = input("(Opcional) ID do Fiscal Substituto: ")
        if fiscal_sub_id:
            form_data['fiscal_substituto_id'] = fiscal_sub_id

    # --- Campos Opcionais de Texto ---
    print("\n--- Outros Dados (Opcional) ---")
    valor_anual = input("(Opcional) Valor Anual: ")
    if valor_anual: form_data['valor_anual'] = valor_anual
    
    valor_global = input("(Opcional) Valor Global: ")
    if valor_global: form_data['valor_global'] = valor_global
    
    termos = input("(Opcional) Termos Contratuais: ")
    if termos: form_data['termos_contratuais'] = termos

    pae = input("(Opcional) Processo Administrativo (PAe): ")
    if pae: form_data['pae'] = pae

    # --- Anexo de Arquivo Opcional ---
    print("\n--- Anexo do Contrato (Opcional) ---")
    filepath = input("(Opcional) Caminho completo para o arquivo do contrato (PDF, etc.): ")

    print("\nEnviando dados para a API...")

    files = {}
    try:
        if filepath and os.path.exists(filepath):
            filename = os.path.basename(filepath)
            files = {'documento_contrato': (filename, open(filepath, 'rb'))}
            print(f"Anexando arquivo: {filename}")
        
        # Requisição é POST, com 'data' para os campos do formulário e 'files' para o anexo
        response = requests.post(f"{BASE_URL}/contratos", data=form_data, files=files)
        handle_response(response)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        # Garante que o arquivo seja fechado
        if 'documento_contrato' in files:
            files['documento_contrato'][1].close()

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
    
    status_relatorios = get_entities("/statusrelatorio")
    if not status_relatorios:
        wait_for_enter()
        return
    form_data['status_id'] = int(input("ID do Status do Relatório: "))

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
    
    print(f"\nBuscando relatórios para o contrato {contrato_id}...")
    # Aqui seria ideal ter uma rota para listar relatórios
    # Por enquanto, pediremos o ID diretamente
    print("Funcionalidade de listar relatórios do contrato a ser implementada.")
    relatorio_id = int(input("Qual Relatório (ID) você quer analisar? "))

    print("\nOpções de Status de Relatório:")
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

def main():
    """Função principal que inicia o seletor de perfil."""
    global CURRENT_USER
    
    while True:
        clear_screen()
        print("Bem-vindo ao Testador Manual da API SIGESCON!")
        print("=" * 50)
        
        users = get_entities("/usuarios")
        if not users:
            print("\nNão foi possível buscar usuários. O servidor está rodando? Saindo.")
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
                    perfil_id = user['perfil_id']
                    
                    perfil_nome = "Desconhecido"
                    perfis = requests.get(f"{BASE_URL}/perfis").json()
                    if perfis:
                        for perfil in perfis:
                            if perfil['id'] == perfil_id:
                                perfil_nome = perfil['nome']
                                break
                    
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
        except (ValueError, TypeError, requests.exceptions.ConnectionError) as e:
            print(f"Ocorreu um erro: {e}. Verifique se a API está no ar.")
            wait_for_enter()


if __name__ == "__main__":
    # Carrega as funções que não mudaram para o escopo global
    fiscal_menu = globals().get('fiscal_menu', fiscal_menu)
    gestor_menu = globals().get('gestor_menu', gestor_menu)
    admin_contracts_menu = globals().get('admin_contracts_menu', admin_contracts_menu)
    main()