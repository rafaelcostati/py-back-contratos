# app/repository/usuario_repo.py
import psycopg2
from psycopg2.extras import RealDictCursor 
from app.db import get_db_connection

def create_user(nome, email, cpf, matricula, senha_hash, perfil_id):
    conn = get_db_connection()
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    sql = """
        INSERT INTO usuario (nome, email, cpf, matricula, senha, perfil_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, nome, email, cpf, matricula, perfil_id
    """
    try:
        cursor.execute(sql, (nome, email, cpf, matricula, senha_hash, perfil_id))
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

def get_all_users(filters=None, limit=10, offset=0): 
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    base_query = "FROM usuario WHERE ativo = TRUE"
    params = []
    
    if filters and 'nome' in filters:
        base_query += " AND nome ILIKE %s"
        params.append(f"%{filters['nome']}%")

    count_sql = f"SELECT COUNT(id) AS total {base_query}"
    cursor.execute(count_sql, tuple(params))
    total_items = cursor.fetchone()['total']

    data_sql = f"SELECT id, nome, cpf, email, matricula, perfil_id {base_query} ORDER BY nome LIMIT %s OFFSET %s"
    
    paginated_params = tuple(params) + (limit, offset)
    cursor.execute(data_sql, paginated_params)
    users = cursor.fetchall()
    cursor.close()
    return users, total_items

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

def find_user_by_email_for_auth(email):
    """Busca um usuário pelo email, incluindo a senha para autenticação."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = "SELECT id, nome, cpf, email, senha, perfil_id FROM usuario WHERE email = %s"
    cursor.execute(sql, (email,))
    user = cursor.fetchone()
    cursor.close()
    return user