# app/routes/contrato_routes.py
from flask import Blueprint, request, jsonify
from app.repository import contrato_repo, contratado_repo, modalidade_repo, status_repo, usuario_repo

bp = Blueprint('contratos', __name__, url_prefix='/contratos')

@bp.route('', methods=['POST'])
def create():
    data = request.get_json()
    
    # Validações dos campos obrigatórios para um CONTRATO
    required_fields = ['nr_contrato', 'objeto', 'data_inicio', 'data_fim', 'contratado_id', 'modalidade_id', 'status_id', 'gestor_id', 'fiscal_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'O campo "{field}" é obrigatório'}), 400

    # Valida se os IDs fornecidos existem nas tabelas correspondentes
    if contratado_repo.find_contratado_by_id(data['contratado_id']) is None:
        return jsonify({'error': 'Contratado não encontrado'}), 404
    if modalidade_repo.find_modalidade_by_id(data['modalidade_id']) is None:
        return jsonify({'error': 'Modalidade não encontrada'}), 404
    if status_repo.find_status_by_id(data['status_id']) is None:
        return jsonify({'error': 'Status não encontrado'}), 404
    if usuario_repo.find_user_by_id(data['gestor_id']) is None:
        return jsonify({'error': 'Gestor não encontrado'}), 404
    if usuario_repo.find_user_by_id(data['fiscal_id']) is None:
        return jsonify({'error': 'Fiscal não encontrado'}), 404
        
    try:
        new_contrato = contrato_repo.create_contrato(data)
        return jsonify(new_contrato), 201
    except Exception as e:
        return jsonify({'error': f'Erro ao criar contrato: {e}'}), 409

@bp.route('', methods=['GET'])
def list_all():
    filters = {
        'gestor_id': request.args.get('gestor_id'),
        'fiscal_id': request.args.get('fiscal_id')
    }
    active_filters = {k: v for k, v in filters.items() if v is not None}
    
    contratos = contrato_repo.get_all_contratos(active_filters)
    return jsonify(contratos), 200

@bp.route('/<int:id>', methods=['GET'])
def get_by_id(id):
    contrato = contrato_repo.find_contrato_by_id(id)
    if not contrato:
        return jsonify({'error': 'Contrato não encontrado'}), 404
    return jsonify(contrato), 200

@bp.route('/<int:id>', methods=['PATCH'])
def update(id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados para atualização não fornecidos'}), 400
    
    if contrato_repo.find_contrato_by_id(id) is None:
        return jsonify({'error': 'Contrato não encontrado'}), 404
        
    try:
        updated_contrato = contrato_repo.update_contrato(id, data)
        return jsonify(updated_contrato), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar contrato: {e}'}), 409

@bp.route('/<int:id>', methods=['DELETE'])
def delete(id):
    if contrato_repo.find_contrato_by_id(id) is None:
        return jsonify({'error': 'Contrato não encontrado'}), 404
        
    contrato_repo.delete_contrato(id)
    return '', 204