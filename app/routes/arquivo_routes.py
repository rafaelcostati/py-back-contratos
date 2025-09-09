# app/routes/arquivo_routes.py
import os
from flask import Blueprint, send_from_directory, current_app, abort
from app.repository import arquivo_repo
from flask_jwt_extended import jwt_required
from app.auth_decorators import admin_required

bp = Blueprint('arquivos', __name__, url_prefix='/arquivos')

@bp.route('/<int:arquivo_id>/download')
@jwt_required()
def download_file(arquivo_id):
    """Serve um arquivo para visualização/download."""
    try:
        arquivo = arquivo_repo.find_arquivo_by_id(arquivo_id)
        if not arquivo or not arquivo.get('path_armazenamento'):
            abort(404, description="Arquivo não encontrado.")

        directory = os.path.dirname(arquivo['path_armazenamento'])
        filename = os.path.basename(arquivo['path_armazenamento'])

        if not os.path.exists(os.path.join(directory, filename)):
            abort(404, description="Arquivo físico não encontrado no servidor.")

        # 'as_attachment=True' força o download. 'False' para tentar abrir no navegador.
        return send_from_directory(directory, filename, as_attachment=True)

    except Exception as e:
        current_app.logger.error(f"Erro ao servir arquivo ID {arquivo_id}: {e}")
        abort(500, description="Erro interno ao acessar o arquivo.")