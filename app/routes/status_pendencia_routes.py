# app/routes/status_pendencia_routes.py
from flask import Blueprint, request, jsonify
from app.repository import status_pendencia_repo

bp = Blueprint('statuspendencia', __name__, url_prefix='/statuspendencia')

@bp.route('', methods=['POST'])
def create():
    data = request.get_json()
    if not data or 'nome' not in data:
        return jsonify({'error': 'O campo "nome" é obrigatório'}), 400
    try:
        new_item = status_pendencia_repo.create_statuspendencia(data['nome'])
        return jsonify(new_item), 201
    except Exception as e:
        return jsonify({'error': f'Erro ao criar status de pendência: {e}'}), 409
    
@bp.route('', methods=['GET'])
def list_all():
    items = status_pendencia_repo.get_all_statuspendencia()
    return jsonify(items), 200