# scheduler.py
import os
from datetime import date, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from app.db import init_pool, get_db_connection, close_db_connection
from app.email_utils import send_email
from psycopg2.extras import RealDictCursor
from flask import g # Precisamos do 'g' para simular o contexto da aplicação

def check_deadlines():
    """
    Função que o scheduler irá executar para verificar os prazos das pendências.
    """
    print("Executando verificação de prazos de pendências...")
    
    # Simula o contexto de aplicação para a conexão com o banco
    g.db_conn = None 
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Busca todas as pendências que ainda estão com status "Pendente"
        # JOIN com contrato para pegar o fiscal_id e o nr_contrato
        # JOIN com usuario para pegar o email e nome do fiscal
        sql = """
            SELECT 
                pr.id, pr.descricao, pr.data_prazo,
                c.nr_contrato,
                u.nome as fiscal_nome, u.email as fiscal_email
            FROM pendenciarelatorio pr
            JOIN statuspendencia sp ON pr.status_pendencia_id = sp.id
            JOIN contrato c ON pr.contrato_id = c.id
            JOIN usuario u ON c.fiscal_id = u.id
            WHERE sp.nome = 'Pendente'
        """
        cursor.execute(sql)
        pendencias = cursor.fetchall()
        
        today = date.today()
        
        for p in pendencias:
            prazo = p['data_prazo']
            dias_restantes = (prazo - today).days
            
            # Lista de dias para enviar o lembrete
            dias_lembrete = [15, 5, 3, 0]
            
            if dias_restantes in dias_lembrete:
                subject = f"Lembrete de Prazo: Pendência do Contrato {p['nr_contrato']}"
                
                if dias_restantes > 0:
                    prazo_str = f"expira em {dias_restantes} dia(s) ({prazo.strftime('%d/%m/%Y')})."
                elif dias_restantes == 0:
                    prazo_str = f"expira HOJE ({prazo.strftime('%d/%m/%Y')})."
                else:
                    # Não envia email para prazos já vencidos, mas você pode adicionar essa lógica se quiser
                    continue

                body = f"""
                Olá, {p['fiscal_nome']},

                Este é um lembrete automático sobre uma pendência de relatório para o contrato '{p['nr_contrato']}'.

                - Descrição: {p['descricao']}
                - O prazo para envio {prazo_str}

                Por favor, não se esqueça de submeter o relatório a tempo.
                """
                send_email(p['fiscal_email'], subject, body)
                
    except Exception as e:
        print(f"ERRO ao executar a verificação de prazos: {e}")
    finally:
        cursor.close()
        # Simula o teardown da conexão
        close_db_connection()

if __name__ == '__main__':
    # Inicializa o pool de conexões com o banco antes de iniciar o scheduler
    init_pool()
    
    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")
    
    # Agenda a tarefa para rodar todos os dias às 08:00 da manhã
    scheduler.add_job(check_deadlines, 'cron', hour=8, minute=0)
    
    print("Agendador de lembretes iniciado. Pressione Ctrl+C para sair.")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass