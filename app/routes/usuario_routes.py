# app/routes/usuario_routes.py
from flask import Blueprint, request, jsonify
# Importamos check_password_hash para verificar a senha antiga
from werkzeug.security import generate_password_hash, check_password_hash
from app.repository import usuario_repo

bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

# --- ROTAS EXISTENTES (CRUD) ---
@bp.route('/', methods=['POST'])
def create():
    data = request.get_json()
    if not data or not all(k in data for k in ('nome', 'email', 'senha')):
        return jsonify({'error': 'Dados incompletos'}), 400
    
    nome, email, senha = data['nome'], data['email'], data['senha']
    cpf, matricula, perfil_id = data.get('cpf'), data.get('matricula'), data.get('perfil_id', 1)
    senha_hash = generate_password_hash(senha)

    try:
        # Capturamos o novo usuário que a função do repositório agora retorna
        new_user = usuario_repo.create_user(nome, email, cpf, matricula, senha_hash, perfil_id)
        # Retornamos o objeto do novo usuário como JSON
        return jsonify(new_user), 201
    except Exception as e:
        return jsonify({'error': f'Erro ao criar usuário: {e}'}), 409

@bp.route('/', methods=['GET'])
def list_all():
    users = usuario_repo.get_all_users()
    return jsonify(users), 200

@bp.route('/<int:id>', methods=['GET'])
def get_by_id(id):
    user = usuario_repo.find_user_by_id(id)
    if user is None:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    return jsonify(user), 200

@bp.route('/<int:id>', methods=['PATCH'])
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
def delete(id):
    if usuario_repo.find_user_by_id(id) is None:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    try:
        usuario_repo.delete_user(id)
        return '', 204
    except Exception as e:
        return jsonify({'error': f'Erro ao deletar usuário: {e}'}), 500

# --- NOVAS ROTAS PARA GESTÃO DE SENHA ---

@bp.route('/<int:id>/resetar-senha', methods=['PATCH'])
def admin_reset_password(id):
    """
    Endpoint para um Admin resetar a senha de qualquer usuário.
    """
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
def user_change_password(id):
    """
    Endpoint para um usuário alterar a própria senha.
    NOTA: Atualmente, passamos o ID na URL. Com JWT, o ID virá do token.
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('senha_antiga', 'nova_senha')):
        return jsonify({'error': 'Senha antiga e nova são obrigatórias'}), 400
    
    try:
        user = usuario_repo.find_user_for_auth(id)
        if user is None:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        # Verifica se a senha antiga fornecida está correta
        if not check_password_hash(user['senha'], data['senha_antiga']):
            return jsonify({'error': 'Senha antiga incorreta'}), 401 # 401 Unauthorized
        
        # Se estiver correta, atualiza para a nova senha
        nova_senha_hash = generate_password_hash(data['nova_senha'])
        usuario_repo.update_password(id, nova_senha_hash)
        
        return jsonify({'message': 'Senha alterada com sucesso.'}), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao alterar senha: {e}'}), 500