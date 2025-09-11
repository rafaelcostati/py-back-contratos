# app/__init__.py
from datetime import timedelta
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from . import db
from .routes import (
    usuario_routes, contratado_routes, modalidade_routes, 
    status_routes, perfil_routes, contrato_routes,
    pendencia_routes, status_pendencia_routes, status_relatorio_routes, 
    relatorio_routes, arquivo_routes, auth_routes
)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY') 
    jwt = JWTManager(app)
    
    
    CORS(app, resources={r"/*": {"origins": "*"}})
    upload_folder = os.path.join(app.instance_path, '..', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)

    db.init_app(app)

    # Registra todos os Blueprints
    app.register_blueprint(usuario_routes.bp)
    app.register_blueprint(contratado_routes.bp)
    app.register_blueprint(modalidade_routes.bp)
    app.register_blueprint(status_routes.bp)
    app.register_blueprint(perfil_routes.bp)
    app.register_blueprint(contrato_routes.bp)
    app.register_blueprint(pendencia_routes.bp)
    app.register_blueprint(status_pendencia_routes.bp)
    app.register_blueprint(status_relatorio_routes.bp) 
    app.register_blueprint(relatorio_routes.bp)
    app.register_blueprint(arquivo_routes.bp)
    app.register_blueprint(auth_routes.bp)

    @app.cli.command("seed-db")
    def seed_db_command():
        """Popula o banco de dados com dados iniciais."""
        from . import seeder
        seeder.seed_data()
        print("Comando 'seed-db' executado.")
    return app