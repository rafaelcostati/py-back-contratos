# app/repository/relatorio_repo.py
from psycopg2.extras import RealDictCursor
from app.db import get_db_connection

def create_relatorio(data):
    """Cria um novo registro de relatório fiscal."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = """
        INSERT INTO relatoriofiscal (contrato_id, fiscal_usuario_id, arquivo_id, status_id, mes_competencia, observacoes_fiscal, pendencia_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    try:
        cursor.execute(sql, (
            data['contrato_id'],
            data['fiscal_usuario_id'],
            data['arquivo_id'],
            data['status_id'],
            data['mes_competencia'],
            data.get('observacoes_fiscal'),
            data.get('pendencia_id')
        ))
        new_relatorio = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return new_relatorio
  
def analise_relatorio(relatorio_id, aprovador_id, status_id, observacoes):
    """Atualiza um relatório com a análise de um aprovador."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = """
        UPDATE relatoriofiscal
        SET status_id = %s, aprovador_usuario_id = %s, observacoes_aprovador = %s, data_analise = now()
        WHERE id = %s
        RETURNING *
    """
    try:
        cursor.execute(sql, (status_id, aprovador_id, observacoes, relatorio_id))
        updated_relatorio = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return updated_relatorio

def update_relatorio_reenvio(relatorio_id, novo_arquivo_id, observacoes_fiscal):
    """Atualiza um relatório que foi reenviado pelo fiscal."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    # Status volta para "Pendente de Análise" (vamos assumir que o ID é 1)
    status_pendente_analise_id = 1 
    sql = """
        UPDATE relatoriofiscal
        SET arquivo_id = %s, observacoes_fiscal = %s, status_id = %s, 
            aprovador_usuario_id = NULL, observacoes_aprovador = NULL, data_analise = NULL,
            updated_at = now()
        WHERE id = %s
        RETURNING *
    """
    try:
        cursor.execute(sql, (novo_arquivo_id, observacoes_fiscal, status_pendente_analise_id, relatorio_id))
        updated_relatorio = cursor.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
    return updated_relatorio

def find_relatorio_by_id(relatorio_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM relatoriofiscal WHERE id = %s", (relatorio_id,))
    relatorio = cursor.fetchone()
    cursor.close()
    return relatorio

def find_relatorios_by_contrato_id(contrato_id):
    """Busca todos os relatórios de um contrato, com informações do arquivo."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    sql = """
        SELECT
            rf.id,
            rf.mes_competencia,
            rf.observacoes_fiscal,
            rf.created_at as data_envio,
            u.nome as enviado_por,
            s.nome as status_relatorio,
            a.id as arquivo_id,
            a.nome_arquivo
        FROM relatoriofiscal rf
        LEFT JOIN usuario u ON rf.fiscal_usuario_id = u.id
        LEFT JOIN statusrelatorio s ON rf.status_id = s.id
        LEFT JOIN arquivo a ON rf.arquivo_id = a.id
        WHERE rf.contrato_id = %s
        ORDER BY rf.created_at DESC
    """
    cursor.execute(sql, (contrato_id,))
    relatorios = cursor.fetchall()
    cursor.close()
    return relatorios