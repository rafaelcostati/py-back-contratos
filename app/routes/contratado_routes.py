# app/routes/contratado_routes.py
from flask import Blueprint, request, jsonify
from app.repository import contratado_repo

bp = Blueprint('contratados', __name__, url_prefix='/contratados')

@bp.route('/', methods=['POST'])
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
        # Tratamento de erro para CNPJ/CPF/Email duplicados
        return jsonify({'error': f'Erro ao criar contratado: {e}'}), 409

@bp.route('/', methods=['GET'])
def list_all():
    contratados = contratado_repo.get_all_contratados()
    return jsonify(contratados), 200

@bp.route('/<int:id>', methods=['GET'])
def get_by_id(id):
    contratado = contratado_repo.find_contratado_by_id(id)
    if not contratado:
        return jsonify({'error': 'Contratado não encontrado'}), 404
    return jsonify(contratado), 200

@bp.route('/<int:id>', methods=['PATCH'])
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
def delete(id):
    if contratado_repo.find_contratado_by_id(id) is None:
        return jsonify({'error': 'Contratado não encontrado'}), 404
        
    contratado_repo.delete_contratado(id)
    return '', 204