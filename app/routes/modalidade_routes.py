# app/routes/modalidade_routes.py
from flask import Blueprint, request, jsonify
from app.repository import modalidade_repo, contrato_repo
from flask_jwt_extended import jwt_required
from app.auth_decorators import admin_required

bp = Blueprint('modalidades', __name__, url_prefix='/modalidades')

@bp.route('', methods=['POST'])
@admin_required()
def create():
    data = request.get_json()
    if not data or 'nome' not in data:
        return jsonify({'error': 'O campo "nome" é obrigatório'}), 400
    try:
        new_item = modalidade_repo.create_modalidade(data['nome'])
        return jsonify(new_item), 201
    except Exception as e:
        return jsonify({'error': f'Erro ao criar modalidade: {e}'}), 409


@bp.route('', methods=['GET'])
@jwt_required()
def list_all():
    items = modalidade_repo.get_all_modalidades()
    return jsonify(items), 200

@bp.route('/<int:id>', methods=['PATCH'])
@admin_required()
def update(id):
    data = request.get_json()
    if not data or 'nome' not in data:
        return jsonify({'error': 'O campo "nome" é obrigatório'}), 400
    
    if modalidade_repo.find_modalidade_by_id(id) is None:
        return jsonify({'error': 'Modalidade não encontrada'}), 404
        
    try:
        updated_item = modalidade_repo.update_modalidade(id, data['nome'])
        return jsonify(updated_item), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar modalidade: {e}'}), 409

@bp.route('/<int:id>', methods=['DELETE'])
@admin_required()
def delete(id):
    if modalidade_repo.find_modalidade_by_id(id) is None:
        return jsonify({'error': 'Modalidade não encontrada'}), 404

    contratos_associados, _ = contrato_repo.get_all_contratos(filters={'modalidade_id': id})
    if contratos_associados:
        return jsonify({
            'error': 'Esta modalidade não pode ser excluída pois está associada a um ou mais contratos.',
        }), 409 
    
    modalidade_repo.delete_modalidade(id)
    return '', 204