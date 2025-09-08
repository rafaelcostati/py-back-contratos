# app/routes/pendencia_routes.py
from flask import Blueprint, request, jsonify
from app.repository import pendencia_repo, contrato_repo, usuario_repo, status_pendencia_repo

# O prefixo continua o mesmo
bp = Blueprint('pendencias', __name__, url_prefix='/contratos/<int:contrato_id>/pendencias')


@bp.route('', methods=['POST'])
def create(contrato_id):
    """Cria uma nova pendência para o contrato especificado na URL."""
    data = request.get_json()
    
    required_fields = ['descricao', 'data_prazo', 'status_pendencia_id', 'criado_por_usuario_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'O campo "{field}" é obrigatório'}), 400

    if contrato_repo.find_contrato_by_id(contrato_id) is None:
        return jsonify({'error': 'Contrato não encontrado'}), 404
    if usuario_repo.find_user_by_id(data['criado_por_usuario_id']) is None:
        return jsonify({'error': 'Usuário criador não encontrado'}), 404
    if status_pendencia_repo.find_statuspendencia_by_id(data['status_pendencia_id']) is None:
        return jsonify({'error': 'Status de pendência não encontrado'}), 404

    try:
        new_pendencia = pendencia_repo.create_pendencia(contrato_id, data)
        return jsonify(new_pendencia), 201
    except Exception as e:
        return jsonify({'error': f'Erro ao criar pendência: {e}'}), 500


@bp.route('', methods=['GET'])
def list_all(contrato_id):
    """Lista todas as pendências do contrato especificado na URL."""
    if contrato_repo.find_contrato_by_id(contrato_id) is None:
        return jsonify({'error': 'Contrato não encontrado'}), 404
        
    pendencias = pendencia_repo.get_pendencias_by_contrato_id(contrato_id)
    return jsonify(pendencias), 200