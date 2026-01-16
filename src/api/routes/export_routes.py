"""
Rotas API REST para exportação.
"""

from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from services.export_service import ExportService
from services.permission_service import PermissionService, PermissionType
from io import BytesIO

export_api_bp = Blueprint('export_api', __name__)


@export_api_bp.route('/tables/<int:table_config_id>/export/excel', methods=['GET'])
@login_required
def export_excel(table_config_id):
    """Exporta dados para Excel."""
    if not PermissionService.has_table_permission(
        current_user, table_config_id, PermissionType.READ
    ):
        return jsonify({'error': 'Sem permissão'}), 403
    
    # Obter filtros da query string
    filters = {}
    for key, value in request.args.items():
        if key not in ['format', 'fields'] and value:
            filters[key] = value
    
    # Obter campos visíveis
    visible_fields = request.args.get('fields')
    if visible_fields:
        visible_fields = visible_fields.split(',')
    
    try:
        output = ExportService.export_to_excel(
            table_config_id, filters=filters, visible_fields=visible_fields
        )
        
        from model.table_config import TableConfig
        table_config = TableConfig.query.get_or_404(table_config_id)
        filename = f"{table_config.name}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@export_api_bp.route('/tables/<int:table_config_id>/export/csv', methods=['GET'])
@login_required
def export_csv(table_config_id):
    """Exporta dados para CSV."""
    if not PermissionService.has_table_permission(
        current_user, table_config_id, PermissionType.READ
    ):
        return jsonify({'error': 'Sem permissão'}), 403
    
    filters = {}
    for key, value in request.args.items():
        if key not in ['format', 'fields'] and value:
            filters[key] = value
    
    visible_fields = request.args.get('fields')
    if visible_fields:
        visible_fields = visible_fields.split(',')
    
    try:
        csv_data = ExportService.export_to_csv(
            table_config_id, filters=filters, visible_fields=visible_fields
        )
        
        from model.table_config import TableConfig
        table_config = TableConfig.query.get_or_404(table_config_id)
        filename = f"{table_config.name}.csv"
        
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@export_api_bp.route('/tables/<int:table_config_id>/export/pdf', methods=['GET'])
@login_required
def export_pdf(table_config_id):
    """Exporta dados para PDF."""
    if not PermissionService.has_table_permission(
        current_user, table_config_id, PermissionType.READ
    ):
        return jsonify({'error': 'Sem permissão'}), 403
    
    filters = {}
    for key, value in request.args.items():
        if key not in ['format', 'fields', 'title'] and value:
            filters[key] = value
    
    visible_fields = request.args.get('fields')
    if visible_fields:
        visible_fields = visible_fields.split(',')
    
    title = request.args.get('title')
    
    try:
        output = ExportService.export_to_pdf(
            table_config_id, filters=filters, visible_fields=visible_fields, title=title
        )
        
        from model.table_config import TableConfig
        table_config = TableConfig.query.get_or_404(table_config_id)
        filename = f"{table_config.name}.pdf"
        
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
