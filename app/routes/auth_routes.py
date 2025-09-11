# app/routes/auth_routes.py
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from app.repository import usuario_repo, perfil_repo

bp = Blueprint('auth', __name__, url_prefix='/auth')

BLACKLIST = set()

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'senha' not in data:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    email = data['email']
    senha = data['senha']

    # Busca o usuário pelo email, incluindo a senha
    usuario = usuario_repo.find_user_by_email_for_auth(email)

    # Verifica se o usuário existe e se a senha está correta
    if not usuario or not check_password_hash(usuario['senha'], senha):
        return jsonify({"error": "Credenciais inválidas"}), 401

    # Busca o nome do perfil para incluir no token e na resposta
    perfil = perfil_repo.find_perfil_by_id(usuario['perfil_id'])
    perfil_nome = perfil['nome'] if perfil else 'Desconhecido'
    
    # Cria o payload (carga útil) do token com informações adicionais
    additional_claims = {"perfil": perfil_nome}
    access_token = create_access_token(identity=str(usuario['id']), additional_claims=additional_claims)

    
    # Retorna o token e os dados do usuário
    return jsonify({
        "token": access_token,
        "usuario": {
            "id": usuario['id'],
            "nome": usuario['nome'],
            "perfil": perfil_nome
        }
    })

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Adiciona o token atual a uma blacklist para invalidá-lo.
    """
    jti = get_jwt()['jti']
    BLACKLIST.add(jti)
    return jsonify({"msg": "Logout bem-sucedido"}), 200