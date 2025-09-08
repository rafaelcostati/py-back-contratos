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
  
