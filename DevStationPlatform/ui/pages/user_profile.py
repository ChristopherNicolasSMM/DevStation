"""
Perfil do Usuário - DevStationPlatform
Visualização e edição do perfil do usuário autenticado
"""

from nicegui import ui, app as nicegui_app
from ui.components.layout import create_page_layout, data_card
from ui.app import get_current_user
from core.models.user import User
from core.models.audit import AuditLog
from core.models.base import db_manager
from datetime import datetime


@create_page_layout("Meu Perfil")
def render():
    user_data = get_current_user()
    if not user_data:
        return

    user_id = user_data.get('id')

    def load_user():
        session = db_manager.get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()

    def load_recent_activity(limit=10):
        session = db_manager.get_session()
        try:
            logs = (
                session.query(AuditLog)
                .filter(AuditLog.user_id == user_id)
                .order_by(AuditLog.timestamp.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    'ts':     l.timestamp.strftime('%d/%m %H:%M') if l.timestamp else '—',
                    'action': l.action_type or '—',
                    'tx':     l.transaction_code or '—',
                    'obj':    l.object_name or '—',
                    'ok':     l.success,
                }
                for l in logs
            ]
        finally:
            session.close()

    user = load_user()

    # ── Avatar + nome ──────────────────────────────────────────────────────
    initial = (user.username[0] if user else '?').upper()
    profiles = [p.code for p in user.profiles] if user and user.profiles else []
    profile_colors = {
        'ADMIN': 'bg-red-500', 'DEV_ALL': 'bg-orange-500',
        'CORE_DEV': 'bg-purple-500', 'DEVELOPER': 'bg-indigo-500',
        'BANALYST': 'bg-blue-500', 'PUSER': 'bg-teal-500', 'USER': 'bg-gray-500',
    }
    avatar_color = next((profile_colors[p] for p in profiles if p in profile_colors), 'bg-blue-500')

    with ui.row().classes('items-start gap-8 w-full mb-6'):
        # Avatar
        with ui.column().classes('items-center gap-3'):
            with ui.card().classes(f'w-24 h-24 {avatar_color} rounded-full items-center justify-center shadow-lg'):
                ui.label(initial).classes('text-white text-4xl font-bold')
            for code in profiles[:2]:
                ui.badge(code).props(f'color={profile_colors.get(code, "blue-5")}')

        # Info principal
        with ui.column().classes('gap-2 flex-1'):
            ui.label(user.full_name or user.username if user else '—') \
                .classes('text-white text-3xl font-bold')
            ui.label(f'@{user.username}' if user else '—') \
                .classes('text-[#8b949e] text-lg')
            ui.label(user.email or '—' if user else '—') \
                .classes('text-[#8b949e]')
            with ui.row().classes('gap-2 mt-1'):
                status_color = 'green' if user and user.is_active else 'red'
                status_text  = 'Ativo' if user and user.is_active else 'Inativo'
                ui.badge(status_text).props(f'color={status_color}')
                if user and user.is_system:
                    ui.badge('Sistema').props('color=blue-5')
                if user and user.is_locked:
                    ui.badge('Bloqueado').props('color=orange')

        # Ação rápida
        ui.button('Editar Perfil', icon='edit',
                  on_click=lambda: open_edit_dialog(user)) \
            .props('color=blue-6 no-caps')

    # ── Grid principal ─────────────────────────────────────────────────────
    with ui.row().classes('gap-6 w-full items-start'):

        # Coluna esquerda
        with ui.column().classes('flex-1 gap-6'):

            with data_card('Informações da Conta'):
                rows = [
                    ('ID do Usuário',   str(user.id) if user else '—'),
                    ('Username',        user.username if user else '—'),
                    ('E-mail',          user.email or '—' if user else '—'),
                    ('Nome Completo',   user.full_name or '—' if user else '—'),
                    ('Idioma',          user.language or 'pt_BR' if user else '—'),
                    ('Tema',            user.theme or 'dark' if user else '—'),
                    ('Criado em',       user.created_at.strftime('%d/%m/%Y %H:%M') if user and user.created_at else '—'),
                    ('Último Login',    user.last_login.strftime('%d/%m/%Y %H:%M') if user and user.last_login else '—'),
                    ('Login Criado por',user.created_by or '—' if user else '—'),
                ]
                with ui.column().classes('gap-0 w-full'):
                    for label, val in rows:
                        with ui.row().classes('items-center justify-between py-2 border-b border-[#30363d] last:border-0'):
                            ui.label(label).classes('text-[#8b949e] text-sm w-40')
                            ui.label(val).classes('text-white text-sm font-medium')

            with data_card('Atividade Recente'):
                activity = load_recent_activity()
                if not activity:
                    ui.label('Nenhuma atividade registrada.').classes('text-[#8b949e] py-4')
                else:
                    cols = [
                        {'name': 'ts',     'label': 'Data/Hora', 'field': 'ts',     'align': 'left'},
                        {'name': 'action', 'label': 'Ação',      'field': 'action', 'align': 'center'},
                        {'name': 'tx',     'label': 'Transação', 'field': 'tx',     'align': 'left'},
                        {'name': 'obj',    'label': 'Objeto',    'field': 'obj',    'align': 'left'},
                        {'name': 'ok',     'label': 'Status',    'field': 'ok',     'align': 'center'},
                    ]
                    t = ui.table(columns=cols, rows=activity).classes('w-full ds-table text-xs').props('dense')
                    t.add_slot('body-cell-ok', '''
                        <q-td :props="props" class="text-center">
                            <q-badge :color="props.value ? \'green\' : \'red\'"
                                     :label="props.value ? \'✓\' : \'✗\'"/>
                        </q-td>
                    ''')

        # Coluna direita
        with ui.column().classes('w-72 gap-6'):

            with data_card('Perfis de Acesso'):
                if not profiles:
                    ui.label('Nenhum perfil atribuído.').classes('text-[#8b949e] text-sm')
                else:
                    PERM_GROUPS = {
                        'Transações': ['transaction.execute', 'transaction.create', 'transaction.modify.ds'],
                        'Dados':      ['data.query', 'data.export', 'data.import'],
                        'Admin':      ['admin.users', 'admin.audit', 'admin.backup'],
                        'IA':         ['ia.consult', 'ia.train'],
                    }
                    session = db_manager.get_session()
                    try:
                        u = session.query(User).filter(User.id == user_id).first()
                        all_perms = u.get_all_permissions() if u else set()
                    finally:
                        session.close()

                    for code in profiles:
                        color = profile_colors.get(code, 'bg-blue-500')
                        with ui.card().classes(f'border border-[#30363d] p-3 mb-2'):
                            with ui.row().classes('items-center gap-2 mb-2'):
                                ui.badge(code).props(f'color={profile_colors.get(code, "blue-5")}')
                            with ui.column().classes('gap-1'):
                                for grp, perms in PERM_GROUPS.items():
                                    has = any(p in all_perms for p in perms)
                                    icon = 'check_circle' if has else 'cancel'
                                    color_cls = 'text-green-400' if has else 'text-[#30363d]'
                                    with ui.row().classes(f'items-center gap-1'):
                                        ui.icon(icon).classes(f'{color_cls} text-sm')
                                        ui.label(grp).classes(f'{color_cls} text-xs')

            with data_card('Estatísticas'):
                session = db_manager.get_session()
                try:
                    total_actions = session.query(AuditLog).filter(AuditLog.user_id == user_id).count()
                    total_errors  = session.query(AuditLog).filter(
                        AuditLog.user_id == user_id, AuditLog.success == False).count()
                    logins = session.query(AuditLog).filter(
                        AuditLog.user_id == user_id, AuditLog.action_type == 'LOGIN').count()
                finally:
                    session.close()

                for label, val, cls in [
                    ('Total de Ações',  total_actions, 'text-white'),
                    ('Logins',          logins,        'text-green-400'),
                    ('Erros',           total_errors,  'text-red-400'),
                ]:
                    with ui.row().classes('items-center justify-between py-2 border-b border-[#30363d] last:border-0'):
                        ui.label(label).classes('text-[#8b949e] text-sm')
                        ui.label(str(val)).classes(f'{cls} font-bold')

    # ── Dialog de edição ───────────────────────────────────────────────────
    def open_edit_dialog(user_obj):
        if not user_obj:
            return
        with ui.dialog() as dlg, ui.card().classes('w-[500px] bg-[#161b22] border border-[#30363d] p-6'):
            ui.label('Editar Perfil').classes('text-white text-lg font-bold mb-4')

            f_name  = ui.input('Nome Completo', value=user_obj.full_name or '') \
                .classes('w-full').props('outlined dense dark color=blue-4')
            f_email = ui.input('E-mail', value=user_obj.email or '') \
                .classes('w-full').props('outlined dense dark color=blue-4')

            ui.separator().classes('bg-[#30363d] my-2')
            ui.label('Alterar Senha (deixe em branco para não alterar)') \
                .classes('text-[#8b949e] text-xs')
            f_pwd  = ui.input('Nova Senha', password=True, password_toggle_button=True) \
                .classes('w-full').props('outlined dense dark color=blue-4')
            f_pwd2 = ui.input('Confirmar Senha', password=True, password_toggle_button=True) \
                .classes('w-full').props('outlined dense dark color=blue-4')

            err = ui.label('').classes('text-red-400 text-sm')

            def save():
                if f_pwd.value and f_pwd.value != f_pwd2.value:
                    err.set_text('As senhas não coincidem.')
                    return
                session = db_manager.get_session()
                try:
                    u = session.query(User).filter(User.id == user_obj.id).first()
                    u.full_name  = f_name.value
                    u.email      = f_email.value
                    u.updated_at = datetime.now()
                    if f_pwd.value:
                        u.set_password(f_pwd.value)
                    session.commit()
                    # Atualiza storage de sessão
                    nicegui_app.storage.user.update({
                        'user_data': {**user_data,
                                      'full_name': f_name.value,
                                      'email': f_email.value}
                    })
                    ui.notify('Perfil atualizado!', type='positive')
                    dlg.close()
                    ui.navigate.reload()
                except Exception as e:
                    session.rollback()
                    err.set_text(f'Erro: {e}')
                finally:
                    session.close()

            with ui.row().classes('gap-2 justify-end mt-4'):
                ui.button('Cancelar', on_click=dlg.close).props('flat color=grey-5 no-caps')
                ui.button('Salvar',   on_click=save).props('color=blue-6 no-caps')
        dlg.open()
