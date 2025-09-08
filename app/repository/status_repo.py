# app/repository/status_repo.py
from psycopg2.extras import RealDictCursor
from app.db import get_db_connection

def create_status(nome):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("INSERT INTO status (nome) VALUES (%s) RETURNING *", (nome,))
        new_item = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return new_item

def get_all_status():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM status ORDER BY nome")
    items = cursor.fetchall()
    cursor.close()
    return items
  
def find_status_by_id(status_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM status WHERE id = %s", (status_id,))
    item = cursor.fetchone()
    cursor.close()
    return item
