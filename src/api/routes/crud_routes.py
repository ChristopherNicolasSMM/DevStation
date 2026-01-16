"""
Rotas API REST para CRUD genérico.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.crud_service import CRUDService
from services.permission_service import PermissionService, PermissionType
from model.table_config import TableConfig

crud_api_bp = Blueprint('crud_api', __name__)


@crud_api_bp.route('/tables/<int:table_config_id>/records', methods=['GET'])
@login_required
def list_records(table_config_id):
    """API: Lista registros de uma tabela."""
    if not PermissionService.has_table_permission(
        current_user, table_config_id, PermissionType.READ
    ):
        return jsonify({'error': 'Sem permissão'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    order_by = request.args.get('order_by')
    order_dir = request.args.get('order_dir', 'asc')
    
    filters = {}
    for key, value in request.args.items():
        if key not in ['page', 'per_page', 'order_by', 'order_dir'] and value:
            filters[key] = value
    
    try:
        records, total, page, per_page = CRUDService.list_records(
            table_config_id, page, per_page, filters, order_by, order_dir
        )
        
        return jsonify({
            'records': records,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@crud_api_bp.route('/tables/<int:table_config_id>/records', methods=['POST'])
@login_required
def create_record(table_config_id):
    """API: Cria um novo registro."""
    if not PermissionService.has_table_permission(
        current_user, table_config_id, PermissionType.CREATE
    ):
        return jsonify({'error': 'Sem permissão'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400
    
    try:
        record = CRUDService.create_record(table_config_id, data)
        return jsonify({'message': 'Registro criado com sucesso', 'record': record}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@crud_api_bp.route('/tables/<int:table_config_id>/records/<int:record_id>', methods=['GET'])
@login_required
def get_record(table_config_id, record_id):
    """API: Obtém um registro específico."""
    if not PermissionService.has_table_permission(
        current_user, table_config_id, PermissionType.READ
    ):
        return jsonify({'error': 'Sem permissão'}), 403
    
    try:
        record = CRUDService.get_record(table_config_id, record_id)
        return jsonify({'record': record}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@crud_api_bp.route('/tables/<int:table_config_id>/records/<int:record_id>', methods=['PUT'])
@login_required
def update_record(table_config_id, record_id):
    """API: Atualiza um registro."""
    if not PermissionService.has_table_permission(
        current_user, table_config_id, PermissionType.UPDATE
    ):
        return jsonify({'error': 'Sem permissão'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400
    
    try:
        record = CRUDService.update_record(table_config_id, record_id, data)
        return jsonify({'message': 'Registro atualizado com sucesso', 'record': record}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@crud_api_bp.route('/tables/<int:table_config_id>/records/<int:record_id>', methods=['DELETE'])
@login_required
def delete_record(table_config_id, record_id):
    """API: Remove um registro."""
    if not PermissionService.has_table_permission(
        current_user, table_config_id, PermissionType.DELETE
    ):
        return jsonify({'error': 'Sem permissão'}), 403
    
    try:
        CRUDService.delete_record(table_config_id, record_id)
        return jsonify({'message': 'Registro excluído com sucesso'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
