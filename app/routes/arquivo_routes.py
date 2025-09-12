# app/routes/arquivo_routes.py
import os
from flask import Blueprint, send_from_directory, current_app, abort, jsonify
from app.repository import arquivo_repo
from flask_jwt_extended import jwt_required
from app.auth_decorators import admin_required

bp = Blueprint('arquivos', __name__, url_prefix='/arquivos')

@bp.route('/<int:arquivo_id>/download')
@jwt_required()
def download_file(arquivo_id):
    """Serve um arquivo para visualização/download com seu nome original."""
    try:
        arquivo = arquivo_repo.find_arquivo_by_id(arquivo_id)
        if not arquivo or not arquivo.get('path_armazenamento'):
            abort(404, description="Arquivo não encontrado no banco de dados.")

        path_completo = arquivo['path_armazenamento']
        nome_original = arquivo['nome_arquivo']
        
        directory = os.path.dirname(path_completo)
        filename_com_hash = os.path.basename(path_completo)

        if not os.path.exists(path_completo):
            abort(404, description="Arquivo físico não encontrado no servidor.")

        return send_from_directory(
            directory, 
            filename_com_hash, 
            as_attachment=True, 
            download_name=nome_original 
        )

    except Exception as e:
        current_app.logger.error(f"Erro ao servir arquivo ID {arquivo_id}: {e}")
        abort(500, description="Erro interno ao acessar o arquivo.")

@bp.route('/<int:arquivo_id>', methods=['DELETE'])
@admin_required()
def delete_file(arquivo_id):
    """Deleta um arquivo específico do sistema."""
    try:
        arquivo_repo.delete_arquivo(arquivo_id)
        return '', 204
    except FileNotFoundError:
        return jsonify({'error': 'Arquivo não encontrado.'}), 404
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 409
    except Exception as e:
        current_app.logger.error(f"Erro ao deletar arquivo ID {arquivo_id}: {e}")
        return jsonify({'error': 'Erro interno ao tentar deletar o arquivo.'}), 500