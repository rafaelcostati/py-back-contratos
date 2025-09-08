# app/routes/status_relatorio_routes.py
from flask import Blueprint, request, jsonify
from app.repository import status_relatorio_repo

bp = Blueprint('statusrelatorio', __name__, url_prefix='/statusrelatorio')

@bp.route('', methods=['POST'])
def create():
    data = request.get_json()
    if not data or 'nome' not in data:
        return jsonify({'error': 'O campo "nome" é obrigatório'}), 400
    try:
        new_item = status_relatorio_repo.create_statusrelatorio(data['nome'])
        return jsonify(new_item), 201
    except Exception as e:
        return jsonify({'error': f'Erro ao criar status de relatório: {e}'}), 409