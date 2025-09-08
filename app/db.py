# app/db.py
import os
import psycopg2
from psycopg2 import pool
from flask import g
from dotenv import load_dotenv, find_dotenv 

# Carregar variáveis de ambiente do arquivo .env
load_dotenv(find_dotenv())


conn_pool = None

def init_pool():
    global conn_pool
    conn_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20, # min e max de conexões
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME')
    )

def get_db_connection():
    # Pega uma conexão do pool
    if 'db_conn' not in g:
        g.db_conn = conn_pool.getconn()
    return g.db_conn

def close_db_connection(e=None):
    # Devolve a conexão para o pool
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        conn_pool.putconn(db_conn)

def init_app(app):
    # Registra a função close_db_connection para ser chamada ao final de cada request
    app.teardown_appcontext(close_db_connection)
    init_pool()