# app/repository/status_pendencia_repo.py
from psycopg2.extras import RealDictCursor
from app.db import get_db_connection

def create_statuspendencia(nome):
    """Cria um novo status de pendência."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("INSERT INTO statuspendencia (nome) VALUES (%s) RETURNING *", (nome,))
        new_item = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return new_item

def find_statuspendencia_by_id(status_id):
    """Busca um status de pendência específico pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM statuspendencia WHERE id = %s", (status_id,))
    item = cursor.fetchone()
    cursor.close()
    return item
  
def get_all_statuspendencia():
    """Busca todos os status de pendência."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM statuspendencia ORDER BY nome")
    items = cursor.fetchall()
    cursor.close()
    return items

def find_statuspendencia_by_name(nome):
    """Busca um status de pendência pelo nome."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM statuspendencia WHERE nome = %s", (nome,))
    item = cursor.fetchone()
    cursor.close()
    return item

def update_pendencia_status(pendencia_id, status_id):
    """Atualiza o status de uma pendência específica."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = "UPDATE pendenciarelatorio SET status_pendencia_id = %s, updated_at = now() WHERE id = %s RETURNING *"
    try:
        cursor.execute(sql, (status_id, pendencia_id))
        updated_pendencia = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return updated_pendencia