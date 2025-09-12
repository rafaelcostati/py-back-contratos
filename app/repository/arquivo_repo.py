# app/repository/arquivo_repo.py
import os 
from psycopg2.extras import RealDictCursor
from app.db import get_db_connection

def create_arquivo(nome_arquivo, path_armazenamento, tipo_arquivo, tamanho_bytes, contrato_id):
    """Insere um novo registro de arquivo no banco e retorna o objeto criado."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = """
        INSERT INTO arquivo (nome_arquivo, path_armazenamento, tipo_arquivo, tamanho_bytes, contrato_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
    """
    try:
        cursor.execute(sql, (nome_arquivo, path_armazenamento, tipo_arquivo, tamanho_bytes, contrato_id))
        new_arquivo = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return new_arquivo

def find_arquivo_by_id(arquivo_id):
    """Busca um arquivo pelo seu ID."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM arquivo WHERE id = %s", (arquivo_id,))
    arquivo = cursor.fetchone()
    cursor.close()
    return arquivo

def find_arquivos_by_contrato_id(contrato_id):
    """Busca todos os arquivos associados a um contrato pelo ID do contrato."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = "SELECT id, nome_arquivo, tipo_arquivo, tamanho_bytes, created_at FROM arquivo WHERE contrato_id = %s ORDER BY created_at DESC"
    cursor.execute(sql, (contrato_id,))
    arquivos = cursor.fetchall()
    cursor.close()
    return arquivos

def delete_arquivo(arquivo_id):
    """
    Deleta um arquivo do banco de dados e do sistema de arquivos.
    Se o arquivo estiver em uso, ele será desvinculado antes da exclusão.
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # 1. Busca o arquivo para obter o caminho físico
        cursor.execute("SELECT path_armazenamento FROM arquivo WHERE id = %s", (arquivo_id,))
        arquivo = cursor.fetchone()
        if not arquivo:
            # Se o arquivo não existe no banco, não há o que fazer.
            return

        # 2. Desvincula o arquivo de qualquer relatório fiscal que o utilize
        cursor.execute("UPDATE relatoriofiscal SET arquivo_id = NULL WHERE arquivo_id = %s", (arquivo_id,))

        # 3. Desvincula o arquivo de qualquer contrato que o utilize como documento principal
        cursor.execute("UPDATE contrato SET documento = NULL WHERE documento = %s", (arquivo_id,))
       
        # 4. Deleta o registro do arquivo da tabela 'arquivo'
        cursor.execute("DELETE FROM arquivo WHERE id = %s", (arquivo_id,))

        # 5. Deleta o arquivo físico do disco
        filepath = arquivo['path_armazenamento']
        if os.path.exists(filepath):
            os.remove(filepath)

        conn.commit()
    except Exception as e:
        conn.rollback()
        
        raise Exception(f"Erro inesperado no repositório ao deletar arquivo: {e}")
    finally:
        cursor.close()