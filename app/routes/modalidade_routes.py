# app/routes/modalidade_routes.py
from flask import Blueprint, request, jsonify
from app.repository import modalidade_repo

bp = Blueprint('modalidades', __name__, url_prefix='/modalidades')

@bp.route('/', methods=['POST'])
def create():
    data = request.get_json()
    if not data or 'nome' not in data:
        return jsonify({'error': 'O campo "nome" é obrigatório'}), 400
    try:
        new_item = modalidade_repo.create_modalidade(data['nome'])
        return jsonify(new_item), 201
    except Exception as e:
        return jsonify({'error': f'Erro ao criar modalidade: {e}'}), 409

@bp.route('/', methods=['GET'])
def list_all():
    items = modalidade_repo.get_all_modalidades()
    return jsonify(items), 200