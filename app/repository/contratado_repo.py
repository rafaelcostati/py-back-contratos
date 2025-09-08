# app/repository/contratado_repo.py
import psycopg2
from psycopg2.extras import RealDictCursor
from app.db import get_db_connection

def create_contratado(nome, email, cnpj, cpf, telefone):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = """
        INSERT INTO contratado (nome, email, cnpj, cpf, telefone)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
    """
    try:
        cursor.execute(sql, (nome, email, cnpj, cpf, telefone))
        new_contratado = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return new_contratado

def get_all_contratados():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    # AJUSTE: Adicionado "WHERE ativo = TRUE"
    sql = "SELECT * FROM contratado WHERE ativo = TRUE ORDER BY nome"
    cursor.execute(sql)
    contratados = cursor.fetchall()
    cursor.close()
    return contratados

def find_contratado_by_id(contratado_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    # AJUSTE: Adicionado "WHERE ativo = TRUE"
    sql = "SELECT * FROM contratado WHERE id = %s AND ativo = TRUE"
    cursor.execute(sql, (contratado_id,))
    contratado = cursor.fetchone()
    cursor.close()
    return contratado

def update_contratado(contratado_id, data):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    update_fields = [f"{key} = %s" for key in data.keys()]
    sql = f"UPDATE contratado SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
    values = list(data.values()) + [contratado_id]
    try:
        cursor.execute(sql, values)
        updated_contratado = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return updated_contratado

def delete_contratado(contratado_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # AJUSTE: Alterado de DELETE para UPDATE (Soft Delete)
    sql = "UPDATE contratado SET ativo = FALSE WHERE id = %s"
    try:
        cursor.execute(sql, (contratado_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()