# app/routes/arquivo_routes.py
import os
from flask import Blueprint, send_from_directory, current_app, abort
from app.repository import arquivo_repo

bp = Blueprint('arquivos', __name__, url_prefix='/arquivos')

@bp.route('/<int:arquivo_id>')
def download_file(arquivo_id):
    """Serve um arquivo para visualização/download."""
    try:
        # Busca o arquivo no banco para obter seu caminho
        arquivo = arquivo_repo.find_arquivo_by_id(arquivo_id)
        if not arquivo:
            abort(404, description="Arquivo não encontrado no banco de dados.")

        # Pega o diretório e o nome do arquivo
        directory = os.path.dirname(arquivo['path_armazenamento'])
        filename = os.path.basename(arquivo['path_armazenamento'])

        # Usa a função segura do Flask para servir o arquivo
        return send_from_directory(directory, filename, as_attachment=False)

    except Exception as e:
        # Adiciona um log do erro no servidor para depuração
        current_app.logger.error(f"Erro ao tentar servir o arquivo ID {arquivo_id}: {e}")
        abort(500, description="Erro interno ao tentar acessar o arquivo.")