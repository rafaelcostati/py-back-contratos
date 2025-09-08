# app/routes/contrato_routes.py
from flask import Blueprint, request, jsonify
from app.repository import contrato_repo, contratado_repo, modalidade_repo, status_repo, usuario_repo

bp = Blueprint('contratos', __name__, url_prefix='/contratos')

@bp.route('', methods=['POST'])
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
def list_all():
    contratados = contratado_repo.get_all_contratados()
    return jsonify(contratados), 200

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