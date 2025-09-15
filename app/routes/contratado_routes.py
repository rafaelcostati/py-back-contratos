# app/routes/contratado_routes.py
from flask import Blueprint, request, jsonify
from app.repository import contratado_repo, contrato_repo
from flask_jwt_extended import jwt_required
from app.auth_decorators import admin_required
import math

bp = Blueprint('contratados', __name__, url_prefix='/contratados')

@bp.route('', methods=['POST'])
@admin_required()
def create():
    data = request.get_json()
    if not data or 'nome' not in data or 'email' not in data:
        return jsonify({'error': 'Nome e email são obrigatórios'}), 400
    
    nome = data['nome']
    email = data['email']
    cnpj = data.get('cnpj')
    cpf = data.get('cpf')
    telefone = data.get('telefone')
    
    try:
        new_contratado = contratado_repo.create_contratado(nome, email, cnpj, cpf, telefone)
        return jsonify(new_contratado), 201
    except Exception as e:
        return jsonify({'error': f'Erro ao criar contratado: {e}'}), 409

@bp.route('', methods=['GET'])
@jwt_required()
def list_all():
    filters = {}
    nome_query = request.args.get('nome')
    if nome_query:
        filters['nome'] = nome_query
    
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
    except (ValueError, TypeError):
        return jsonify({'error': 'Parâmetros de paginação inválidos. Devem ser números inteiros.'}), 400

    page = max(1, page)
    per_page = max(1, per_page)
    offset = (page - 1) * per_page
    
    contratados, total_items = contratado_repo.get_all_contratados(
        filters=filters,
        limit=per_page,
        offset=offset
    )
    
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1

    return jsonify({
        'data': contratados,
        'pagination': {
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page
        }
    }), 200

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_by_id(id):
    contratado = contratado_repo.find_contratado_by_id(id)
    if not contratado:
        return jsonify({'error': 'Contratado não encontrado'}), 404
    return jsonify(contratado), 200

@bp.route('/<int:id>', methods=['PATCH'])
@admin_required()
def update(id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados para atualização não fornecidos'}), 400
    
    if contratado_repo.find_contratado_by_id(id) is None:
        return jsonify({'error': 'Contratado não encontrado'}), 404
        
    try:
        updated_contratado = contratado_repo.update_contratado(id, data)
        return jsonify(updated_contratado), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar contratado: {e}'}), 409

@bp.route('/<int:id>', methods=['DELETE'])
@admin_required()
def delete(id):
    if contratado_repo.find_contratado_by_id(id) is None:
        return jsonify({'error': 'Contratado não encontrado'}), 404

    contratos_associados, total_items = contrato_repo.get_all_contratos(filters={'contratado_id': id})
    if total_items > 0:
        return jsonify({
            'error': 'Este contratado não pode ser excluído pois está associado a um ou mais contratos.',
            'contratos': [{'id': c['id'], 'nr_contrato': c['nr_contrato']} for c in contratos_associados]
        }), 409 

    contratado_repo.delete_contratado(id)
    return '', 204