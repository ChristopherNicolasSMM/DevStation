"""
Controlador de administração do sistema.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from db.database import db
from model.table_config import TableConfig
from model.field_config import FieldConfig
from services.table_service import TableService

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator para verificar se o usuário é administrador."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'error')
            return redirect(url_for('web.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/tables')
@login_required
@admin_required
def tables():
    """Lista todas as tabelas configuradas."""
    tables = TableConfig.query.order_by(TableConfig.name).all()
    return render_template('admin/tables.html', tables=tables)


@admin_bp.route('/tables/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_table():
    """Cria uma nova tabela."""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        name = data.get('name')
        description = data.get('description', '')
        unique_key = data.get('unique_key', [])
        
        if not name:
            if request.is_json:
                return jsonify({'error': 'Nome é obrigatório'}), 400
            flash('Nome é obrigatório', 'error')
            return redirect(url_for('admin.create_table'))
        
        # Gerar nome da tabela no banco
        table_name = f"data_{name.lower().replace(' ', '_')}"
        
        # Verificar se já existe
        if TableConfig.query.filter_by(table_name=table_name).first():
            if request.is_json:
                return jsonify({'error': 'Tabela com este nome já existe'}), 400
            flash('Tabela com este nome já existe', 'error')
            return redirect(url_for('admin.create_table'))
        
        # Criar configuração
        table_config = TableConfig(
            name=name,
            description=description,
            table_name=table_name,
            unique_key=unique_key if isinstance(unique_key, list) else []
        )
        db.session.add(table_config)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Tabela criada com sucesso', 'table': table_config.to_dict()}), 201
        
        flash('Tabela criada com sucesso', 'success')
        return redirect(url_for('admin.edit_table', id=table_config.id))
    
    return render_template('admin/create_table.html')


@admin_bp.route('/tables/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_table(id):
    """Edita uma tabela existente."""
    table_config = TableConfig.query.get_or_404(id)
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        table_config.name = data.get('name', table_config.name)
        table_config.description = data.get('description', table_config.description)
        table_config.unique_key = data.get('unique_key', table_config.unique_key)
        table_config.is_active = data.get('is_active', table_config.is_active) if isinstance(data.get('is_active'), bool) else table_config.is_active
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Tabela atualizada com sucesso', 'table': table_config.to_dict()}), 200
        
        flash('Tabela atualizada com sucesso', 'success')
        return redirect(url_for('admin.edit_table', id=id))
    
    return render_template('admin/edit_table.html', table=table_config)


@admin_bp.route('/tables/<int:id>/fields', methods=['POST'])
@login_required
@admin_required
def add_field(id):
    """Adiciona um campo a uma tabela."""
    table_config = TableConfig.query.get_or_404(id)
    data = request.get_json() if request.is_json else request.form
    
    name = data.get('name')
    label = data.get('label', name)
    field_type = data.get('field_type', 'text')
    size = data.get('size')
    is_required = data.get('is_required', False)
    is_unique = data.get('is_unique', False)
    default_value = data.get('default_value')
    order = data.get('order', len(table_config.fields))
    
    if not name:
        if request.is_json:
            return jsonify({'error': 'Nome do campo é obrigatório'}), 400
        flash('Nome do campo é obrigatório', 'error')
        return redirect(url_for('admin.edit_table', id=id))
    
    # Verificar se campo já existe
    if FieldConfig.query.filter_by(table_config_id=id, name=name).first():
        if request.is_json:
            return jsonify({'error': 'Campo com este nome já existe'}), 400
        flash('Campo com este nome já existe', 'error')
        return redirect(url_for('admin.edit_table', id=id))
    
    field_config = FieldConfig(
        table_config_id=id,
        name=name,
        label=label,
        field_type=field_type,
        size=int(size) if size else None,
        is_required=bool(is_required),
        is_unique=bool(is_unique),
        default_value=default_value,
        order=order
    )
    
    db.session.add(field_config)
    db.session.commit()
    
    # Se a tabela já existe no banco, adicionar o campo
    if TableService.table_exists(table_config.table_name):
        try:
            TableService.add_field_to_table(table_config, field_config)
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': f'Erro ao adicionar campo na tabela: {str(e)}'}), 500
            flash(f'Erro ao adicionar campo na tabela: {str(e)}', 'error')
            return redirect(url_for('admin.edit_table', id=id))
    
    if request.is_json:
        return jsonify({'message': 'Campo adicionado com sucesso', 'field': field_config.to_dict()}), 201
    
    flash('Campo adicionado com sucesso', 'success')
    return redirect(url_for('admin.edit_table', id=id))


@admin_bp.route('/tables/<int:id>/excel-mapping', methods=['GET', 'POST'])
@login_required
@admin_required
def excel_mapping(id):
    """Configura mapeamento Excel para uma tabela."""
    table_config = TableConfig.query.get_or_404(id)
    from model.excel_mapping import ExcelMapping
    
    excel_mapping = ExcelMapping.query.filter_by(table_config_id=id).first()
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        has_header = data.get('has_header', True)
        start_row = int(data.get('start_row', 1))
        column_mapping = data.get('column_mapping', {})
        
        if isinstance(column_mapping, str):
            import json
            column_mapping = json.loads(column_mapping)
        
        if not excel_mapping:
            excel_mapping = ExcelMapping(
                table_config_id=id,
                has_header=bool(has_header),
                start_row=start_row,
                column_mapping=column_mapping
            )
            db.session.add(excel_mapping)
        else:
            excel_mapping.has_header = bool(has_header)
            excel_mapping.start_row = start_row
            excel_mapping.column_mapping = column_mapping
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Mapeamento salvo com sucesso', 'mapping': excel_mapping.to_dict()}), 200
        
        flash('Mapeamento salvo com sucesso', 'success')
        return redirect(url_for('admin.excel_mapping', id=id))
    
    return render_template('admin/excel_mapping.html', table=table_config, mapping=excel_mapping)


@admin_bp.route('/tables/<int:id>/create', methods=['POST'])
@login_required
@admin_required
def create_table_in_db(id):
    """Cria a tabela no banco de dados."""
    table_config = TableConfig.query.get_or_404(id)
    
    if not table_config.fields:
        if request.is_json:
            return jsonify({'error': 'Adicione pelo menos um campo antes de criar a tabela'}), 400
        flash('Adicione pelo menos um campo antes de criar a tabela', 'error')
        return redirect(url_for('admin.edit_table', id=id))
    
    try:
        TableService.create_table(table_config)
        
        if request.is_json:
            return jsonify({'message': 'Tabela criada no banco com sucesso'}), 200
        
        flash('Tabela criada no banco com sucesso', 'success')
        return redirect(url_for('admin.edit_table', id=id))
    except Exception as e:
        if request.is_json:
            return jsonify({'error': f'Erro ao criar tabela: {str(e)}'}), 500
        flash(f'Erro ao criar tabela: {str(e)}', 'error')
        return redirect(url_for('admin.edit_table', id=id))
