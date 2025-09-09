# app/routes/usuario_routes.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.repository import usuario_repo
from flask_jwt_extended import jwt_required, get_jwt
from app.auth_decorators import admin_required

bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@bp.route('', methods=['POST'])
@admin_required()
def create():
    data = request.get_json()
    if not data or not all(k in data for k in ('nome', 'email', 'senha')):
        return jsonify({'error': 'Dados incompletos'}), 400
    
    nome, email, senha = data['nome'], data['email'], data['senha']
    cpf, matricula, perfil_id = data.get('cpf'), data.get('matricula'), data.get('perfil_id', 1)
    senha_hash = generate_password_hash(senha)

    try:
        new_user = usuario_repo.create_user(nome, email, cpf, matricula, senha_hash, perfil_id)
        return jsonify(new_user), 201
    except Exception as e:
        return jsonify({'error': f'Erro ao criar usuário: {e}'}), 409

@bp.route('', methods=['GET'])
@admin_required()
def list_all():
    users = usuario_repo.get_all_users()
    return jsonify(users), 200

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_by_id(id):
    user = usuario_repo.find_user_by_id(id)
    if user is None:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    return jsonify(user), 200

@bp.route('/<int:id>', methods=['PATCH'])
@admin_required()
def update(id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados para atualização não fornecidos'}), 400
    if usuario_repo.find_user_by_id(id) is None:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    try:
        updated_user = usuario_repo.update_user(id, data)
        return jsonify(updated_user), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar usuário: {e}'}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@admin_required()
def delete(id):
    if usuario_repo.find_user_by_id(id) is None:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    try:
        usuario_repo.delete_user(id)
        return '', 204
    except Exception as e:
        return jsonify({'error': f'Erro ao deletar usuário: {e}'}), 500

@bp.route('/<int:id>/resetar-senha', methods=['PATCH'])
@admin_required()
def admin_reset_password(id):
    data = request.get_json()
    if not data or 'nova_senha' not in data:
        return jsonify({'error': 'A nova senha não foi fornecida'}), 400
    
    if usuario_repo.find_user_by_id(id) is None:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    try:
        nova_senha_hash = generate_password_hash(data['nova_senha'])
        usuario_repo.update_password(id, nova_senha_hash)
        return jsonify({'message': 'Senha resetada com sucesso pelo administrador.'}), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao resetar senha: {e}'}), 500

@bp.route('/<int:id>/alterar-senha', methods=['PATCH'])
@jwt_required()
def user_change_password(id):
    data = request.get_json()
    if not data or not all(k in data for k in ('senha_antiga', 'nova_senha')):
        return jsonify({'error': 'Senha antiga e nova são obrigatórias'}), 400
    
    try:
        user = usuario_repo.find_user_for_auth(id)
        if user is None:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        if not check_password_hash(user['senha'], data['senha_antiga']):
            return jsonify({'error': 'Senha antiga incorreta'}), 401
        
        nova_senha_hash = generate_password_hash(data['nova_senha'])
        usuario_repo.update_password(id, nova_senha_hash)
        
        return jsonify({'message': 'Senha alterada com sucesso.'}), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao alterar senha: {e}'}), 500