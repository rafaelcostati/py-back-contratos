# app/repository/arquivo_repo.py
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