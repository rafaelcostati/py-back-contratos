# app/routes/relatorio_routes.py
import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.repository import relatorio_repo, arquivo_repo, contrato_repo, status_pendencia_repo, usuario_repo, status_relatorio_repo, pendencia_repo
from flask_jwt_extended import jwt_required
from app.auth_decorators import admin_required, fiscal_required
from app.email_utils import send_email


bp = Blueprint('relatorios', __name__, url_prefix='/contratos/<int:contrato_id>/relatorios')

# Helper para verificar extensões de arquivo permitidas
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _handle_file_upload(contrato_id, file_key):
    """Função auxiliar interna para lidar com o processo de upload de arquivo."""
    if file_key not in request.files:
        raise ValueError(f"Nenhum arquivo encontrado com a chave '{file_key}'")
        
    file = request.files[file_key]
    if file.filename == '':
        raise ValueError("Nome do arquivo não pode ser vazio")

    if not allowed_file(file.filename):
        raise ValueError("Tipo de arquivo não permitido")

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    file.save(filepath)
    file_size = os.path.getsize(filepath)

    new_arquivo = arquivo_repo.create_arquivo(
        nome_arquivo=filename,
        path_armazenamento=filepath,
        tipo_arquivo=file.mimetype,
        tamanho_bytes=file_size,
        contrato_id=contrato_id
    )
    return new_arquivo

@bp.route('', methods=['POST'])
@fiscal_required()
def submit_relatorio(contrato_id):
    """Endpoint para um fiscal submeter um relatório EM RESPOSTA A UMA PENDÊNCIA."""
    if contrato_repo.find_contrato_by_id(contrato_id) is None:
        return jsonify({'error': 'Contrato não encontrado'}), 404
        
    form_data = request.form
    # VALIDAÇÃO DA REGRA DE NEGÓCIO: O fiscal DEVE informar a pendência.
    if 'pendencia_id' not in form_data:
        return jsonify({'error': 'É obrigatório informar o ID da pendência (pendencia_id) à qual este relatório responde.'}), 400

    required_fields = ['mes_competencia', 'fiscal_usuario_id']
    if not all(field in form_data for field in required_fields):
        return jsonify({'error': f'Campos de formulário obrigatórios: {required_fields}'}), 400

    filepath = None
    try:
        # Busca os IDs dos status que vamos setar automaticamente
        status_relatorio_pendente = status_relatorio_repo.find_statusrelatorio_by_name('Pendente de Análise')
        status_pendencia_concluida = status_pendencia_repo.find_statuspendencia_by_name('Concluída')
        
        if not status_relatorio_pendente or not status_pendencia_concluida:
            return jsonify({'error': 'Status padrão ("Pendente de Análise", "Concluída") não encontrados no banco. Execute o seeder.'}), 500

        new_arquivo = _handle_file_upload(contrato_id, file_key='arquivo')
        filepath = new_arquivo['path_armazenamento']

        relatorio_data = {
            'contrato_id': contrato_id,
            'arquivo_id': new_arquivo['id'],
            'fiscal_usuario_id': form_data['fiscal_usuario_id'],
            'mes_competencia': form_data['mes_competencia'],
            'observacoes_fiscal': form_data.get('observacoes_fiscal'),
            'pendencia_id': form_data.get('pendencia_id'),
            # LÓGICA CORRIGIDA: O status é definido automaticamente, ignorando qualquer coisa que o fiscal envie.
            'status_id': status_relatorio_pendente['id']
        }
        
        new_relatorio = relatorio_repo.create_relatorio(relatorio_data)
        
        # LÓGICA CORRIGIDA: Após o envio, a pendência original é marcada como "Concluída".
        pendencia_repo.update_pendencia_status(relatorio_data['pendencia_id'], status_pendencia_concluida['id'])

        return jsonify(new_relatorio), 201

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Erro ao processar o relatório: {e}'}), 500

@bp.route('/<int:relatorio_id>/analise', methods=['PATCH'])
@admin_required()
def analisar_relatorio(contrato_id, relatorio_id):
    """Endpoint para um Administrador aprovar ou rejeitar um relatório."""
    data = request.get_json()
    required = ['aprovador_usuario_id', 'status_id'] # ID do StatusRelatorio
    if not all(k in data for k in required):
        return jsonify({'error': 'Campos obrigatórios: aprovador_usuario_id, status_id'}), 400

    # Validações de existência
    if relatorio_repo.find_relatorio_by_id(relatorio_id) is None:
        return jsonify({'error': 'Relatório não encontrado'}), 404
    if usuario_repo.find_user_by_id(data['aprovador_usuario_id']) is None:
        return jsonify({'error': 'Usuário aprovador não encontrado'}), 404
    # Esta importação é necessária
    from app.repository import status_relatorio_repo
    if status_relatorio_repo.find_statusrelatorio_by_id(data['status_id']) is None:
        return jsonify({'error': 'Status de relatório não encontrado'}), 404

    try:
        observacoes = data.get('observacoes_aprovador')
        relatorio_atualizado = relatorio_repo.analise_relatorio(
            relatorio_id, data['aprovador_usuario_id'], data['status_id'], observacoes
        )
                # --- INÍCIO DA IMPLEMENTAÇÃO DO EMAIL ---
        status_rejeitado = status_relatorio_repo.find_statusrelatorio_by_name('Rejeitado com Pendência')
        
        # Envia email apenas se o status for 'Rejeitado com Pendência'
        if status_rejeitado and relatorio_atualizado['status_id'] == status_rejeitado['id']:
            relatorio_original = relatorio_repo.find_relatorio_by_id(relatorio_id)
            fiscal = usuario_repo.find_user_by_id(relatorio_original['fiscal_usuario_id'])
            contrato = contrato_repo.find_contrato_by_id(contrato_id)

            if fiscal and contrato:
                subject = f"Relatório Rejeitado - Contrato {contrato['nr_contrato']}"
                body = f"""
                Olá, {fiscal['nome']},

                O seu relatório referente ao mês de competência {relatorio_original['mes_competencia'].strftime('%m/%Y')} para o contrato '{contrato['nr_contrato']}' foi rejeitado.

                Motivo da rejeição:
                "{relatorio_atualizado['observacoes_aprovador']}"

                Por favor, realize as correções necessárias e reenvie o relatório através do sistema.
                """
                send_email(fiscal['email'], subject, body)
        # --- FIM DA IMPLEMENTAÇÃO DO EMAIL ---
        return jsonify(relatorio_atualizado), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao analisar relatório: {e}'}), 500

@bp.route('/<int:relatorio_id>', methods=['PUT'])
@fiscal_required()
def reenviar_relatorio(contrato_id, relatorio_id):
    """Endpoint para um Fiscal reenviar um relatório corrigido (com novo arquivo)."""
    # 1. Validações iniciais
    if relatorio_repo.find_relatorio_by_id(relatorio_id) is None:
        return jsonify({'error': 'Relatório a ser atualizado não encontrado'}), 404
    
    observacoes_fiscal = request.form.get('observacoes_fiscal')
    filepath = None
    try:
        # 2. Lida com o upload do novo arquivo
        new_arquivo = _handle_file_upload(contrato_id, file_key='arquivo')

        filepath = new_arquivo['path_armazenamento']
        
        # 3. Atualiza o registro do relatório existente com o ID do novo arquivo
        updated_relatorio = relatorio_repo.update_relatorio_reenvio(
            relatorio_id, 
            new_arquivo['id'], 
            observacoes_fiscal
        )
        
        # Aqui, a lógica de negócio poderia incluir apagar o arquivo antigo.
        # Por segurança, vamos manter os arquivos antigos por enquanto.

        return jsonify(updated_relatorio), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Erro ao reenviar o relatório: {e}'}), 500
    
@bp.route('', methods=['GET'])
@jwt_required()
def list_relatorios(contrato_id):
    """Lista todos os relatórios de um contrato específico."""
    if contrato_repo.find_contrato_by_id(contrato_id) is None:
        return jsonify({'error': 'Contrato não encontrado'}), 404
    
    try:
        relatorios = relatorio_repo.get_relatorios_by_contrato_id(contrato_id)
        return jsonify(relatorios), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar relatórios: {e}'}), 500