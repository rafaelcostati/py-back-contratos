# app/repository/usuario_repo.py
import psycopg2
from psycopg2.extras import RealDictCursor 
from app.db import get_db_connection

# --- FUNÇÕES EXISTENTES ---

def create_user(nome, email, cpf, matricula, senha_hash, perfil_id):
    conn = get_db_connection()
    # Adicionamos o cursor_factory aqui para que o RETURNING venha como dicionário
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    sql = """
        INSERT INTO usuario (nome, email, cpf, matricula, senha, perfil_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, nome, email, cpf, matricula, perfil_id
    """
    try:
        cursor.execute(sql, (nome, email, cpf, matricula, senha_hash, perfil_id))
        # Capturamos o novo usuário retornado pelo banco
        new_user = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    # Retornamos o novo usuário
    return new_user

def find_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor) 
    sql = "SELECT * FROM usuario WHERE email = %s AND ativo = TRUE"
    cursor.execute(sql, (email,))
    user = cursor.fetchone()
    cursor.close()
    return user

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = "SELECT id, nome, email, matricula, perfil_id FROM usuario WHERE ativo = TRUE ORDER BY nome"
    cursor.execute(sql)
    users = cursor.fetchall()
    cursor.close()
    return users

def find_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = "SELECT id, nome, email, cpf, matricula, perfil_id FROM usuario WHERE id = %s AND ativo = TRUE"
    cursor.execute(sql, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return user

def update_user(user_id, data):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    update_fields = [f"{key} = %s" for key in data.keys()]
    sql = f"UPDATE usuario SET {', '.join(update_fields)} WHERE id = %s RETURNING id, nome, email, cpf, matricula, perfil_id"
    values = list(data.values()) + [user_id]
    try:
        cursor.execute(sql, values)
        updated_user = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return updated_user

def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "UPDATE usuario SET ativo = FALSE WHERE id = %s"
    try:
        cursor.execute(sql, (user_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        
# --- NOVAS FUNÇÕES PARA GESTÃO DE SENHA ---

def find_user_for_auth(user_id):
    """
    Busca um usuário pelo ID, mas inclui a senha.
    Usado especificamente para verificação de senha antiga.
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = "SELECT id, senha FROM usuario WHERE id = %s AND ativo = TRUE"
    cursor.execute(sql, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return user

def update_password(user_id, new_password_hash):
    """
    Atualiza apenas a senha de um usuário.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "UPDATE usuario SET senha = %s WHERE id = %s"
    try:
        cursor.execute(sql, (new_password_hash, user_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()