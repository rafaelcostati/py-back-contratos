# app/repository/pendencia_repo.py
from psycopg2.extras import RealDictCursor
from app.db import get_db_connection

def create_pendencia(contrato_id, data):
    """Cria uma nova pendência para um contrato."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = """
        INSERT INTO pendenciarelatorio (contrato_id, descricao, data_prazo, status_pendencia_id, criado_por_usuario_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
    """
    try:
        cursor.execute(sql, (
            contrato_id,
            data['descricao'],
            data['data_prazo'],
            data['status_pendencia_id'],
            data['criado_por_usuario_id']
        ))
        new_pendencia = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return new_pendencia

def get_pendencias_by_contrato_id(contrato_id):
    """Lista todas as pendências de um contrato específico, com dados enriquecidos."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = """
        SELECT
            p.*,
            s.nome as status_nome,
            u.nome as criado_por_nome
        FROM pendenciarelatorio p
        LEFT JOIN statuspendencia s ON p.status_pendencia_id = s.id
        LEFT JOIN usuario u ON p.criado_por_usuario_id = u.id
        WHERE p.contrato_id = %s
        ORDER BY p.data_prazo ASC
    """
    cursor.execute(sql, (contrato_id,))
    pendencias = cursor.fetchall()
    cursor.close()
    return pendencias