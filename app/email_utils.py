# app/email_utils.py
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, subject, body):
    """
    Função para enviar um e-mail usando as configurações do .env.
    """
    # Carrega as configurações do ambiente
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')

    if not all([smtp_server, sender_email, sender_password]):
        print("ERRO DE CONFIGURAÇÃO: As variáveis de ambiente SMTP não foram definidas.")
        return

    try:
        # Cria a mensagem
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Conecta ao servidor e envia
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Habilita segurança
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        print(f"Email enviado com sucesso para {to_email}")
    except Exception as e:
        print(f"Falha ao enviar email para {to_email}: {e}")