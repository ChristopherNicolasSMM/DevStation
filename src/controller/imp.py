"""
Controlador de upload e auditoria de Excel.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from db.database import db
from model.table_config import TableConfig
from model.excel_mapping import ExcelMapping
from model.import_log import ImportLog
from services.excel_service import ExcelService
from services.permission_service import PermissionService, PermissionType
from services.audit_service import AuditService
from services.audit_service import AuditAction
from pathlib import Path

import_bp = Blueprint('import', __name__)


@import_bp.route('/tables/<int:table_config_id>/import', methods=['GET', 'POST'])
@login_required
def upload_file(table_config_id):
    """Upload de arquivo Excel."""
    table_config = TableConfig.query.get_or_404(table_config_id)
    
    # Verificar permissão de criação (para upload)
    if not PermissionService.has_table_permission(
        current_user, table_config_id, PermissionType.CREATE
    ):
        flash('Sem permissão para fazer upload nesta tabela', 'error')
        return redirect(url_for('web.dashboard'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo enviado', 'error')
            return redirect(url_for('import.upload_file', table_config_id=table_config_id))
        
        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('import.upload_file', table_config_id=table_config_id))
        
        # Verificar mapeamento
        excel_mapping = ExcelMapping.query.filter_by(table_config_id=table_config_id).first()
        if not excel_mapping:
            flash('Configure o mapeamento Excel antes de fazer upload', 'error')
            return redirect(url_for('admin.edit_table', id=table_config_id))
        
        try:
            # Salvar arquivo
            file_path = ExcelService.save_uploaded_file(file, table_config_id)
            
            # Processar arquivo
            import_log = ExcelService.process_excel_file(table_config_id, file_path)
            
            if import_log.status == 'failed':
                flash(f'Erro ao processar arquivo: {import_log.error_message}', 'error')
                return redirect(url_for('import.upload_file', table_config_id=table_config_id))
            
            return redirect(url_for('import.review_import', import_log_id=import_log.id))
            
        except Exception as e:
            flash(f'Erro ao fazer upload: {str(e)}', 'error')
            return redirect(url_for('import.upload_file', table_config_id=table_config_id))
    
    # Obter histórico de importações
    import_logs = ImportLog.query.filter_by(table_config_id=table_config_id)\
        .order_by(ImportLog.uploaded_at.desc()).limit(10).all()
    
    return render_template('import/upload.html', table=table_config, import_logs=import_logs)


@import_bp.route('/import/<int:import_log_id>/review')
@login_required
def review_import(import_log_id):
    """Revisa divergências detectadas."""
    import_log = ImportLog.query.get_or_404(import_log_id)
    table_config = TableConfig.query.get_or_404(import_log.table_config_id)
    
    # Verificar permissão (auditor ou admin pode aprovar)
    can_approve = (
        current_user.is_admin or
        (current_user.group and current_user.group.name == 'Auditor')
    )
    
    if not can_approve:
        flash('Apenas auditores podem aprovar alterações', 'error')
        return redirect(url_for('import.upload_file', table_config_id=table_config.id))
    
    return render_template('import/review.html', import_log=import_log, table=table_config)


@import_bp.route('/import/<int:import_log_id>/approve', methods=['POST'])
@login_required
def approve_import(import_log_id):
    """Aprova e aplica alterações."""
    import_log = ImportLog.query.get_or_404(import_log_id)
    
    # Verificar permissão
    can_approve = (
        current_user.is_admin or
        (current_user.group and current_user.group.name == 'Auditor')
    )
    
    if not can_approve:
        return jsonify({'error': 'Sem permissão para aprovar'}), 403
    
    data = request.get_json()
    approved_items = data.get('approved_items', [])
    
    if not approved_items:
        return jsonify({'error': 'Nenhum item aprovado'}), 400
    
    try:
        stats = ExcelService.apply_approved_changes(import_log_id, approved_items)
        
        # Registrar no audit log
        AuditService.log_action(
            table_config_id=import_log.table_config_id,
            record_id=0,  # Importação geral
            action=AuditAction.APPROVE,
            import_log_id=import_log_id,
            notes=f"Aprovadas {stats['created']} criações e {stats['updated']} atualizações"
        )
        
        return jsonify({
            'message': 'Alterações aplicadas com sucesso',
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@import_bp.route('/import/<int:import_log_id>/reject', methods=['POST'])
@login_required
def reject_import(import_log_id):
    """Rejeita importação."""
    import_log = ImportLog.query.get_or_404(import_log_id)
    
    # Verificar permissão
    can_approve = (
        current_user.is_admin or
        (current_user.group and current_user.group.name == 'Auditor')
    )
    
    if not can_approve:
        return jsonify({'error': 'Sem permissão para rejeitar'}), 403
    
    data = request.get_json()
    reason = data.get('reason', '')
    
    import_log.status = 'rejected'
    db.session.commit()
    
    # Registrar no audit log
    AuditService.log_action(
        table_config_id=import_log.table_config_id,
        record_id=0,
        action=AuditAction.REJECT,
        import_log_id=import_log_id,
        notes=f"Rejeitado: {reason}"
    )
    
    return jsonify({'message': 'Importação rejeitada'}), 200
