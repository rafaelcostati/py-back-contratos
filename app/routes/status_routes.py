# app/routes/status_routes.py
from flask import Blueprint, request, jsonify
from app.repository import status_repo
from flask_jwt_extended import jwt_required
from app.auth_decorators import admin_required

bp = Blueprint('status', __name__, url_prefix='/status')

@bp.route('', methods=['POST'])
@admin_required()
def create():
    data = request.get_json()
    if not data or 'nome' not in data:
        return jsonify({'error': 'O campo "nome" é obrigatório'}), 400
    try:
        new_item = status_repo.create_status(data['nome'])
        return jsonify(new_item), 201
    except Exception as e:
        return jsonify({'error': f'Erro ao criar status: {e}'}), 409

@bp.route('', methods=['GET'])
@jwt_required()
def list_all():
    items = status_repo.get_all_status()
    return jsonify(items), 200