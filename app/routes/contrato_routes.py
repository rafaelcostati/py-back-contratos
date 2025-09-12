# app/routes/contrato_routes.py
import math
import os
from flask import Blueprint, request, jsonify, current_app
from app.email_utils import send_email
from app.repository import contrato_repo, contratado_repo, modalidade_repo, relatorio_repo, status_repo, usuario_repo, arquivo_repo
from flask_jwt_extended import jwt_required
from app.auth_decorators import admin_required

from .relatorio_routes import _handle_file_upload 

bp = Blueprint('contratos', __name__, url_prefix='/contratos')

@bp.route('', methods=['POST'])
@admin_required()
def create():
    data = request.form.to_dict()

    
    if not data:
        return jsonify({'error': 'Nenhum dado enviado'}), 400

    required_fields = ['nr_contrato', 'objeto', 'data_inicio', 'data_fim', 'contratado_id', 'modalidade_id', 'status_id', 'gestor_id', 'fiscal_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'O campo "{field}" é obrigatório'}), 400

    if contratado_repo.find_contratado_by_id(data['contratado_id']) is None: return jsonify({'error': 'Contratado não encontrado'}), 404
    if modalidade_repo.find_modalidade_by_id(data['modalidade_id']) is None: return jsonify({'error': 'Modalidade não encontrada'}), 404
    if status_repo.find_status_by_id(data['status_id']) is None: return jsonify({'error': 'Status não encontrado'}), 404
    if usuario_repo.find_user_by_id(data['gestor_id']) is None: return jsonify({'error': 'Gestor não encontrado'}), 404
    if usuario_repo.find_user_by_id(data['fiscal_id']) is None: return jsonify({'error': 'Fiscal não encontrado'}), 404
    
    gestor = usuario_repo.find_user_by_id(data['gestor_id'])
    fiscal = usuario_repo.find_user_by_id(data['fiscal_id'])
    
    try:
        new_contrato = contrato_repo.create_contrato(data)
        
       
        subject_gestor = "Você foi designado como Gestor de um novo contrato"
        body_gestor = f"""
        Olá, {gestor['nome']},

        Você foi designado como gestor do seguinte contrato:
        - Número: {new_contrato.get('nr_contrato')}
        - Objeto: {new_contrato.get('objeto')}

        Por favor, acesse o sistema SIGESCON para mais detalhes.
        """
        send_email(gestor['email'], subject_gestor, body_gestor)

        subject_fiscal = "Você foi designado como Fiscal de um novo contrato"
        body_fiscal = f"""
        Olá, {fiscal['nome']},

        Você foi designado como fiscal do seguinte contrato:
        - Número: {new_contrato.get('nr_contrato')}
        - Objeto: {new_contrato.get('objeto')}

        Por favor, acesse o sistema SIGESCON para mais detalhes.
        """
        send_email(fiscal['email'], subject_fiscal, body_fiscal)
        
        # ALTERADO: Lógica de upload simplificada
        if 'documentos_contrato' in request.files:
            files = request.files.getlist('documentos_contrato')

            for file in files:
                try:
                    original_filename, filepath = _handle_file_upload(new_contrato['id'], file)
                    file_size = os.path.getsize(filepath)

                    arquivo_repo.create_arquivo(
                        nome_arquivo=original_filename, 
                        path_armazenamento=filepath,    
                        tipo_arquivo=file.mimetype,
                        tamanho_bytes=file_size,
                        contrato_id=new_contrato['id']
                    )
                except ValueError as ve:
                   
                    current_app.logger.warning(f"Arquivo '{file.filename}' pulado: {ve}")
                    continue

        final_contrato = contrato_repo.find_contrato_by_id(new_contrato['id'])
        return jsonify(final_contrato), 201
        
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:

        return jsonify({'error': f'Erro ao criar contrato: {e}'}), 500


@bp.route('', methods=['GET'])
@jwt_required()
def list_all():
    filters = {
        'gestor_id': request.args.get('gestor_id'),
        'fiscal_id': request.args.get('fiscal_id'),
        'objeto': request.args.get('objeto'),
        'nr_contrato': request.args.get('nr_contrato'),
        'status_id': request.args.get('status_id'),
        'pae': request.args.get('pae'),
        'ano': request.args.get('ano')
    }
    active_filters = {k: v for k, v in filters.items() if v is not None}

    sort_by = request.args.get('sortBy', 'data_fim')
    order = request.args.get('order', 'desc').upper()

    allowed_sort_fields = {'data_inicio', 'data_fim'}
    if sort_by not in allowed_sort_fields:
        sort_by = 'data_fim'

    if order not in ['ASC', 'DESC']:
        order = 'DESC'
    
    order_by_clause = f"c.{sort_by} {order}"
    
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
    except (ValueError, TypeError):
        return jsonify({'error': 'Parâmetros de paginação inválidos. Devem ser números inteiros.'}), 400

    page = max(1, page)
    per_page = max(1, per_page)
    offset = (page - 1) * per_page
    
    contratos, total_items = contrato_repo.get_all_contratos(
        filters=active_filters,
        order_by=order_by_clause,
        limit=per_page,
        offset=offset
    )
    
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1

    return jsonify({
        'data': contratos,
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
    contrato = contrato_repo.find_contrato_by_id(id)
    if not contrato:
        return jsonify({'error': 'Contrato não encontrado'}), 404
    
    relatorios = relatorio_repo.get_relatorios_by_contrato_id(id)
    contrato['relatorios_fiscais'] = relatorios
    
    return jsonify(contrato), 200

@bp.route('/<int:id>', methods=['PATCH'])
@admin_required()
def update(id):
    if contrato_repo.find_contrato_by_id(id) is None:
        return jsonify({'error': 'Contrato não encontrado'}), 404

    data = request.form.to_dict()
    
    try:
        if data:
            contrato_repo.update_contrato(id, data)

        if 'documentos_contrato' in request.files:
            files = request.files.getlist('documentos_contrato')

            for file in files:
                try:
                    original_filename, filepath = _handle_file_upload(id, file) # Usa o ID do contrato existente
                    file_size = os.path.getsize(filepath)

                    arquivo_repo.create_arquivo(
                        nome_arquivo=original_filename,
                        path_armazenamento=filepath,
                        tipo_arquivo=file.mimetype,
                        tamanho_bytes=file_size,
                        contrato_id=id
                    )
                except ValueError as ve:
                    current_app.logger.warning(f"Arquivo '{file.filename}' pulado: {ve}")
                    continue
        
        updated_contrato = contrato_repo.find_contrato_by_id(id)
        return jsonify(updated_contrato), 200

    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar contrato: {e}'}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@admin_required()
def delete(id):
    if contrato_repo.find_contrato_by_id(id) is None: return jsonify({'error': 'Contrato não encontrado'}), 404
    contrato_repo.delete_contrato(id)
    return '', 204

@bp.route('/<int:contrato_id>/arquivos', methods=['GET'])
@jwt_required()
def list_contract_files(contrato_id):
    if contrato_repo.find_contrato_by_id(contrato_id) is None:
        return jsonify({'error': 'Contrato não encontrado'}), 404
    
    try:
        arquivos = arquivo_repo.find_arquivos_by_contrato_id(contrato_id)
        return jsonify(arquivos), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar arquivos do contrato: {e}'}), 500