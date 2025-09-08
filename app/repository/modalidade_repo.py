# app/repository/modalidade_repo.py
from psycopg2.extras import RealDictCursor
from app.db import get_db_connection

def create_modalidade(nome):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("INSERT INTO modalidade (nome) VALUES (%s) RETURNING *", (nome,))
        new_item = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return new_item

def get_all_modalidades():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM modalidade ORDER BY nome")
    items = cursor.fetchall()
    cursor.close()
    return items
  
def find_modalidade_by_id(modalidade_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM modalidade WHERE id = %s", (modalidade_id,))
    item = cursor.fetchone()
    cursor.close()
    return item