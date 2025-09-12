# app/repository/contrato_repo.py
from psycopg2.extras import RealDictCursor
from app.db import get_db_connection

def create_contrato(data):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    fields = [
        'nr_contrato', 'objeto', 'valor_anual', 'valor_global', 'base_legal',
        'data_inicio', 'data_fim', 'termos_contratuais', 'contratado_id',
        'modalidade_id', 'status_id', 'gestor_id', 'fiscal_id',
        'fiscal_substituto_id', 'pae', 'doe', 'data_doe', 'documento'
    ]
    
    query_fields = []
    query_values_placeholder = []
    query_values = []

    for field in fields:
        if field in data:
            query_fields.append(field)
            query_values_placeholder.append('%s')
            query_values.append(data[field])

    sql = f"""
        INSERT INTO contrato ({", ".join(query_fields)})
        VALUES ({", ".join(query_values_placeholder)})
        RETURNING *
    """
    
    try:
        cursor.execute(sql, tuple(query_values))
        new_contrato = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return new_contrato

def get_all_contratos(filters=None, order_by='c.data_fim DESC', limit=10, offset=0):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    base_query = """
        FROM contrato c
        LEFT JOIN contratado ct ON c.contratado_id = ct.id
        LEFT JOIN modalidade m ON c.modalidade_id = m.id
        LEFT JOIN status s ON c.status_id = s.id
    """
    
    where_clauses = ["c.ativo = TRUE"]
    params = []

    if filters:
        
        if filters.get('gestor_id'):
            where_clauses.append("c.gestor_id = %s")
            params.append(filters['gestor_id'])
        if filters.get('fiscal_id'):
            where_clauses.append("c.fiscal_id = %s")
            params.append(filters['fiscal_id'])
        if filters.get('contratado_id'):
            where_clauses.append("c.contratado_id = %s")
            params.append(filters['contratado_id'])
        if filters.get('modalidade_id'):
            where_clauses.append("c.modalidade_id = %s")
            params.append(filters['modalidade_id'])
        if filters.get('objeto'):
            where_clauses.append("c.objeto ILIKE %s")
            params.append(f"%{filters['objeto']}%")
        if filters.get('nr_contrato'):
            where_clauses.append("c.nr_contrato ILIKE %s")
            params.append(f"%{filters['nr_contrato']}%")
        if filters.get('status_id'):
            where_clauses.append("c.status_id = %s")
            params.append(filters['status_id'])
        if filters.get('pae'):
            where_clauses.append("c.pae ILIKE %s")
            params.append(f"%{filters['pae']}%")
        
        if filters.get('ano'):
            where_clauses.append("EXTRACT(YEAR FROM c.data_inicio) = %s")
            params.append(filters['ano'])

    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    count_sql = f"SELECT COUNT(c.id) AS total {base_query}"
    cursor.execute(count_sql, tuple(params))
    total_items = cursor.fetchone()['total']

    data_sql = f"""
        SELECT
            c.id, c.nr_contrato, c.objeto, c.data_inicio, c.data_fim, c.pae,
            ct.nome as contratado_nome, m.nome as modalidade_nome, s.nome as status_nome
        {base_query}
        ORDER BY {order_by}
        LIMIT %s OFFSET %s
    """
    paginated_params = tuple(params) + (limit, offset)
    cursor.execute(data_sql, paginated_params)
    contratos = cursor.fetchall()
    
    cursor.close()

    return contratos, total_items

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

def update_contrato(contrato_id, data):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    update_fields = [f"{key} = %s" for key in data.keys()]
    sql = f"UPDATE contrato SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
    values = list(data.values()) + [contrato_id]
    try:
        cursor.execute(sql, values)
        updated_contrato = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return updated_contrato

def delete_contrato(contrato_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "UPDATE contrato SET ativo = FALSE WHERE id = %s"
    try:
        cursor.execute(sql, (contrato_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()