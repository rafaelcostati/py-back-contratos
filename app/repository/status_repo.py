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
    cursor.execute("SELECT * FROM status WHERE ativo = TRUE ORDER BY nome")
    items = cursor.fetchall()
    cursor.close()
    return items
  
def find_status_by_id(status_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM status WHERE id = %s AND ativo = TRUE", (status_id,))
    item = cursor.fetchone()
    cursor.close()
    return item

def update_status(status_id, nome):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("UPDATE status SET nome = %s WHERE id = %s RETURNING *", (nome, status_id))
        updated_item = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return updated_item

def delete_status(status_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "UPDATE status SET ativo = FALSE WHERE id = %s"
    try:
        cursor.execute(sql, (status_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()