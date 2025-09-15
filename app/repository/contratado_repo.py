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

def get_all_contratados(filters=None, limit=10, offset=0):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    base_query = "FROM contratado WHERE ativo = TRUE"
    params = []

    if filters and 'nome' in filters:
        base_query += " AND nome ILIKE %s"
        params.append(f"%{filters['nome']}%")
    
    count_sql = f"SELECT COUNT(id) AS total {base_query}"
    cursor.execute(count_sql, tuple(params))
    total_items = cursor.fetchone()['total']

    data_sql = f"SELECT * {base_query} ORDER BY nome LIMIT %s OFFSET %s"
    
    paginated_params = tuple(params) + (limit, offset)
    cursor.execute(data_sql, paginated_params)
    contratados = cursor.fetchall()
    cursor.close()
    return contratados, total_items

def find_contratado_by_id(contratado_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
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
    sql = "UPDATE contratado SET ativo = FALSE WHERE id = %s"
    try:
        cursor.execute(sql, (contratado_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        
def find_contrato_by_id(contrato_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    sql = """
        SELECT
            c.*,
            ct.nome AS contratado_nome, ct.cnpj AS contratado_cnpj,
            m.nome AS modalidade_nome,
            s.nome AS status_nome,
            gestor.nome AS gestor_nome,
            fiscal.nome AS fiscal_nome,
            fiscal_sub.nome AS fiscal_substituto_nome,
            doc.nome_arquivo AS documento_nome_arquivo
        FROM contrato c
        LEFT JOIN contratado ct ON c.contratado_id = ct.id
        LEFT JOIN modalidade m ON c.modalidade_id = m.id
        LEFT JOIN status s ON c.status_id = s.id
        LEFT JOIN usuario gestor ON c.gestor_id = gestor.id
        LEFT JOIN usuario fiscal ON c.fiscal_id = fiscal.id
        LEFT JOIN usuario fiscal_sub ON c.fiscal_substituto_id = fiscal_sub.id
        LEFT JOIN arquivo doc ON c.documento::int = doc.id
        WHERE c.id = %s AND c.ativo = TRUE
    """
    cursor.execute(sql, (contrato_id,))
    contrato = cursor.fetchone()
    cursor.close()
    return contrato