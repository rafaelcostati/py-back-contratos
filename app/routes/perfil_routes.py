# app/routes/perfil_routes.py
from flask import Blueprint, request, jsonify
from app.repository import perfil_repo

bp = Blueprint('perfis', __name__, url_prefix='/perfis')

@bp.route('/', methods=['POST'])
def create():
    data = request.get_json()
    if not data or 'nome' not in data:
        return jsonify({'error': 'O campo "nome" é obrigatório'}), 400
    try:
        new_item = perfil_repo.create_perfil(data['nome'])
        return jsonify(new_item), 201
    except Exception as e:
        return jsonify({'error': f'Erro ao criar perfil: {e}'}), 409

@bp.route('/', methods=['GET'])
def list_all():
    items = perfil_repo.get_all_perfis()
    return jsonify(items), 200