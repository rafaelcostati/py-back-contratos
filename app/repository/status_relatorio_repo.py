# app/repository/status_relatorio_repo.py
from psycopg2.extras import RealDictCursor
from app.db import get_db_connection

def create_statusrelatorio(nome):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("INSERT INTO statusrelatorio (nome) VALUES (%s) RETURNING *", (nome,))
        new_item = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return new_item

# --- ADICIONE ESTAS NOVAS FUNÇÕES ABAIXO ---

def get_all_statusrelatorio():
    """Busca todos os status de relatório."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM statusrelatorio ORDER BY nome")
    items = cursor.fetchall()
    cursor.close()
    return items

def find_statusrelatorio_by_id(status_id):
    """Busca um status de relatório específico pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM statusrelatorio WHERE id = %s", (status_id,))
    item = cursor.fetchone()
    cursor.close()
    return item