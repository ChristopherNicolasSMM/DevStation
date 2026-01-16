"""
Controlador CRUD genérico para tabelas dinâmicas.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from db.database import db
from model.table_config import TableConfig
from services.crud_service import CRUDService
from services.permission_service import PermissionService, PermissionType
from services.layout_service import LayoutService
from math import ceil

crud_bp = Blueprint('crud', __name__)


@crud_bp.route('/tables/<int:table_config_id>')
@login_required
def list_table(table_config_id):
    """Lista registros de uma tabela."""
    # Verificar permissão
    if not PermissionService.has_table_permission(
        current_user, table_config_id, PermissionType.READ
    ):
        flash('Sem permissão para acessar esta tabela', 'error')
        return redirect(url_for('web.dashboard'))
    
    table_config = TableConfig.query.get_or_404(table_config_id)
    
    # Obter layout ativo
    active_layout = LayoutService.get_active_layout(
        table_config_id,
        user_id=current_user.id if current_user.is_authenticated else None,
        group_id=current_user.group_id if current_user.is_authenticated and current_user.group else None
    )
    
    # Obter parâmetros de paginação e filtros (layout tem prioridade)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', active_layout.per_page if active_layout else 20, type=int)
    order_by = request.args.get('order_by', active_layout.order_by if active_layout else None)
    order_dir = request.args.get('order_dir', active_layout.order_dir if active_layout else 'asc')
    
    # Obter filtros da query string (mesclar com layout)
    filters = active_layout.filters.copy() if active_layout and active_layout.filters else {}
    for key, value in request.args.items():
        if key not in ['page', 'per_page', 'order_by', 'order_dir'] and value:
            filters[key] = value
    
    # Obter campos visíveis do layout
    visible_fields = active_layout.visible_fields if active_layout and active_layout.visible_fields else None
    
    try:
        records, total, page, per_page = CRUDService.list_records(
            table_config_id, page, per_page, filters, order_by, order_dir
        )
        
        total_pages = ceil(total / per_page) if total > 0 else 1
        
        # Obter layouts disponíveis
        from model.layout import Layout
        layouts = LayoutService.list_layouts(table_config_id, user_id=current_user.id if current_user.is_authenticated else None)
        
        return render_template(
            'crud/list.html',
            table=table_config,
            records=records,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            filters=filters,
            order_by=order_by,
            order_dir=order_dir,
            active_layout=active_layout,
            layouts=layouts,
            visible_fields=visible_fields
        )
    except Exception as e:
        flash(f'Erro ao listar registros: {str(e)}', 'error')
        return redirect(url_for('web.dashboard'))


@crud_bp.route('/tables/<int:table_config_id>/create', methods=['GET', 'POST'])
@login_required
def create_record(table_config_id):
    """Cria um novo registro."""
    # Verificar permissão
    if not PermissionService.has_table_permission(
        current_user, table_config_id, PermissionType.CREATE
    ):
        flash('Sem permissão para criar registros nesta tabela', 'error')
        return redirect(url_for('crud.list_table', table_config_id=table_config_id))
    
    table_config = TableConfig.query.get_or_404(table_config_id)
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        try:
            record = CRUDService.create_record(table_config_id, data)
            flash('Registro criado com sucesso', 'success')
            return redirect(url_for('crud.list_table', table_config_id=table_config_id))
        except Exception as e:
            flash(f'Erro ao criar registro: {str(e)}', 'error')
    
    # Obter campos editáveis
    editable_fields = PermissionService.get_editable_fields(current_user, table_config)
    
    return render_template(
        'crud/create.html',
        table=table_config,
        fields=editable_fields
    )


@crud_bp.route('/tables/<int:table_config_id>/<int:record_id>')
@login_required
def view_record(table_config_id, record_id):
    """Visualiza um registro."""
    # Verificar permissão
    if not PermissionService.has_table_permission(
        current_user, table_config_id, PermissionType.READ
    ):
        flash('Sem permissão para visualizar este registro', 'error')
        return redirect(url_for('crud.list_table', table_config_id=table_config_id))
    
    table_config = TableConfig.query.get_or_404(table_config_id)
    
    try:
        record = CRUDService.get_record(table_config_id, record_id)
        visible_fields = PermissionService.get_visible_fields(current_user, table_config)
        
        return render_template(
            'crud/view.html',
            table=table_config,
            record=record,
            fields=visible_fields
        )
    except Exception as e:
        flash(f'Erro ao visualizar registro: {str(e)}', 'error')
        return redirect(url_for('crud.list_table', table_config_id=table_config_id))


@crud_bp.route('/tables/<int:table_config_id>/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_record(table_config_id, record_id):
    """Edita um registro."""
    # Verificar permissão
    if not PermissionService.has_table_permission(
        current_user, table_config_id, PermissionType.UPDATE
    ):
        flash('Sem permissão para editar registros nesta tabela', 'error')
        return redirect(url_for('crud.list_table', table_config_id=table_config_id))
    
    table_config = TableConfig.query.get_or_404(table_config_id)
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        try:
            record = CRUDService.update_record(table_config_id, record_id, data)
            flash('Registro atualizado com sucesso', 'success')
            return redirect(url_for('crud.view_record', table_config_id=table_config_id, record_id=record_id))
        except Exception as e:
            flash(f'Erro ao atualizar registro: {str(e)}', 'error')
    
    try:
        record = CRUDService.get_record(table_config_id, record_id)
        editable_fields = PermissionService.get_editable_fields(current_user, table_config)
        
        return render_template(
            'crud/edit.html',
            table=table_config,
            record=record,
            fields=editable_fields
        )
    except Exception as e:
        flash(f'Erro ao carregar registro: {str(e)}', 'error')
        return redirect(url_for('crud.list_table', table_config_id=table_config_id))


@crud_bp.route('/tables/<int:table_config_id>/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_record(table_config_id, record_id):
    """Remove um registro."""
    # Verificar permissão
    if not PermissionService.has_table_permission(
        current_user, table_config_id, PermissionType.DELETE
    ):
        flash('Sem permissão para excluir registros desta tabela', 'error')
        return redirect(url_for('crud.list_table', table_config_id=table_config_id))
    
    try:
        CRUDService.delete_record(table_config_id, record_id)
        flash('Registro excluído com sucesso', 'success')
    except Exception as e:
        flash(f'Erro ao excluir registro: {str(e)}', 'error')
    
    return redirect(url_for('crud.list_table', table_config_id=table_config_id))
