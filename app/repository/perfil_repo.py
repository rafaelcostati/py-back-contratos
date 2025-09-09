# app/repository/perfil_repo.py
from psycopg2.extras import RealDictCursor
from app.db import get_db_connection

def create_perfil(nome):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("INSERT INTO perfil (nome) VALUES (%s) RETURNING *", (nome,))
        new_item = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return new_item

def get_all_perfis():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM perfil ORDER BY nome")
    items = cursor.fetchall()
    cursor.close()
    return items

def find_perfil_by_id(perfil_id):
    """Busca um perfil pelo seu ID."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM perfil WHERE id = %s", (perfil_id,))
    perfil = cursor.fetchone()
    cursor.close()
    return perfil