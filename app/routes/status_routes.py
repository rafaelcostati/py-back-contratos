# app/routes/status_routes.py
from flask import Blueprint, request, jsonify
from app.repository import status_repo, contrato_repo
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

@bp.route('/<int:id>', methods=['PATCH'])
@admin_required()
def update(id):
    data = request.get_json()
    if not data or 'nome' not in data:
        return jsonify({'error': 'O campo "nome" é obrigatório'}), 400
    
    if status_repo.find_status_by_id(id) is None:
        return jsonify({'error': 'Status não encontrado'}), 404
        
    try:
        updated_item = status_repo.update_status(id, data['nome'])
        return jsonify(updated_item), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar status: {e}'}), 409

@bp.route('/<int:id>', methods=['DELETE'])
@admin_required()
def delete(id):
    if status_repo.find_status_by_id(id) is None:
        return jsonify({'error': 'Status não encontrado'}), 404

    contratos_associados, _ = contrato_repo.get_all_contratos(filters={'status_id': id})
    if contratos_associados:
        return jsonify({
            'error': 'Este status não pode ser excluído pois está associado a um ou mais contratos.',
        }), 409 
    
    status_repo.delete_status(id)
    return '', 204