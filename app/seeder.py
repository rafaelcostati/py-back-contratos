# app/seeder.py
import os
from werkzeug.security import generate_password_hash
from app.db import get_db_connection


# --- DADOS ESSENCIAIS A SEREM INSERIDOS ---

PERFIS = ['Administrador', 'Gestor', 'Fiscal']
MODALIDADES = [
    'Pregão', 'Concorrência', 'Concurso', 'Leilão', 'Diálogo Competitivo',
    'Dispensa de Licitação', 'Inexigibilidade de Licitação', 'Credenciamento'
]
STATUS_CONTRATO = ['Vigente', 'Encerrado', 'Rescindido', 'Suspenso', 'Aguardando Publicação']
STATUS_RELATORIO = ['Pendente de Análise', 'Aprovado', 'Rejeitado com Pendência']
STATUS_PENDENCIA = ['Pendente', 'Concluída', 'Cancelada']

# --- LÓGICA DO SEEDER ---

def seed_data():
    """Verifica e insere os dados essenciais no banco de dados se eles não existirem."""
    conn = get_db_connection()
    try:
        print("Iniciando o processo de seed do banco de dados...")
        
        # Helper para inserir dados se a tabela estiver vazia
        def seed_table(table_name, data_list):
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                if cursor.fetchone()[0] == 0:
                    print(f"Populando tabela '{table_name}'...")
                    for item_nome in data_list:
                        cursor.execute(f"INSERT INTO {table_name} (nome) VALUES (%s)", (item_nome,))
                else:
                    print(f"Tabela '{table_name}' já populada. Pulando.")

        # Popula as tabelas de lookup
        seed_table('perfil', PERFIS)
        seed_table('modalidade', MODALIDADES)
        seed_table('status', STATUS_CONTRATO)
        seed_table('statusrelatorio', STATUS_RELATORIO)
        seed_table('statuspendencia', STATUS_PENDENCIA)

        # Cria o usuário Administrador se ele não existir
        with conn.cursor() as cursor:
            admin_email = os.getenv('ADMIN_EMAIL')
            cursor.execute("SELECT id FROM usuario WHERE email = %s", (admin_email,))
            if cursor.fetchone() is None:
                print(f"Criando usuário Administrador ({admin_email})...")
                admin_pass = os.getenv('ADMIN_PASSWORD')
                senha_hash = generate_password_hash(admin_pass)
                
                # Pega o ID do perfil 'Administrador'
                cursor.execute("SELECT id FROM perfil WHERE nome = 'Administrador'")
                perfil_admin_id = cursor.fetchone()[0]

                cursor.execute(
                    """
                    INSERT INTO usuario (nome, email, cpf, senha, perfil_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    ('Administrador do Sistema', admin_email, '00000000000', senha_hash, perfil_admin_id)
                )
            else:
                print(f"Usuário Administrador ({admin_email}) já existe. Pulando.")
        
        conn.commit()
        print("Seed do banco de dados concluído com sucesso!")

    except Exception as e:
        conn.rollback()
        print(f"ERRO durante o seed do banco de dados: {e}")
    finally:
        conn.close()