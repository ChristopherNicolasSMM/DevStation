"""
Controlador de rotas web principais.
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Página inicial."""
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))
    return redirect(url_for('auth.login'))

@web_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal."""
    from model.table_config import TableConfig
    from model.user import User, UserGroup
    from model.import_log import ImportLog
    from sqlalchemy import func
    
    # Estatísticas
    total_tables = TableConfig.query.filter_by(is_active=True).count()
    total_users = User.query.count()
    total_groups = UserGroup.query.count()
    
    # Importações recentes
    recent_imports = ImportLog.query.order_by(ImportLog.uploaded_at.desc()).limit(5).all()
    
    # Estatísticas de importações
    import_stats = db.session.query(
        func.count(ImportLog.id).label('total'),
        func.sum(ImportLog.new_records).label('new_records'),
        func.sum(ImportLog.updated_records).label('updated_records')
    ).first()
    
    stats = {
        'total_tables': total_tables,
        'total_users': total_users,
        'total_groups': total_groups,
        'total_imports': import_stats.total if import_stats else 0,
        'total_new_records': import_stats.new_records if import_stats and import_stats.new_records else 0,
        'total_updated_records': import_stats.updated_records if import_stats and import_stats.updated_records else 0,
    }
    
    return render_template('web/dashboard.html', user=current_user, stats=stats, recent_imports=recent_imports)
