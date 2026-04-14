"""
Perfil do Usuário - DevStationPlatform
Todos os dados serializados dentro da sessão para evitar DetachedInstanceError
"""

from nicegui import ui, app as nicegui_app
from ui.components.layout import create_page_layout, data_card
from ui.app import get_current_user
from core.models.user import User
from core.models.audit import AuditLog
from core.models.base import db_manager
from datetime import datetime

PROFILE_COLORS = {
    'ADMIN': 'bg-red-600', 'DEV_ALL': 'bg-orange-600',
    'CORE_DEV': 'bg-purple-600', 'DEVELOPER': 'bg-indigo-600',
    'BANALYST': 'bg-blue-600', 'PUSER': 'bg-teal-600', 'USER': 'bg-gray-600',
}
BADGE_COLORS = {
    'ADMIN': 'red-6', 'DEV_ALL': 'deep-orange-6', 'CORE_DEV': 'purple-6',
    'DEVELOPER': 'indigo-6', 'BANALYST': 'blue-6', 'PUSER': 'teal-6', 'USER': 'grey-6',
}


def _load_user_dict(user_id):
    """Retorna todos os dados do usuário como dict enquanto sessão está aberta."""
    session = db_manager.get_session()
    try:
        u = session.query(User).filter(User.id == user_id).first()
        if not u:
            return None
        profiles = [p.code for p in (u.profiles or [])]
        all_perms = set()
        for p in (u.profiles or []):
            for perm in (p.permissions or []):
                all_perms.add(perm.code)
        return {
            'id':          u.id,
            'username':    u.username,
            'full_name':   u.full_name or '',
            'email':       u.email or '',
            'is_active':   u.is_active,
            'is_locked':   u.is_locked,
            'is_system':   u.is_system,
            'theme':       u.theme or 'dark',
            'language':    u.language or 'pt_BR',
            'last_login':  u.last_login.strftime('%d/%m/%Y %H:%M') if u.last_login else '—',
            'created_at':  u.created_at.strftime('%d/%m/%Y %H:%M') if u.created_at else '—',
            'created_by':  u.created_by or '—',
            'login_attempts': u.login_attempts or 0,
            'profiles':    profiles,
            'all_perms':   list(all_perms),
        }
    finally:
        session.close()


def _load_activity(user_id, limit=10):
    session = db_manager.get_session()
    try:
        logs = (session.query(AuditLog)
                .filter(AuditLog.user_id == user_id)
                .order_by(AuditLog.timestamp.desc())
                .limit(limit).all())
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


def _load_stats(user_id):
    session = db_manager.get_session()
    try:
        total  = session.query(AuditLog).filter(AuditLog.user_id == user_id).count()
        errors = session.query(AuditLog).filter(
            AuditLog.user_id == user_id, AuditLog.success == False).count()
        logins = session.query(AuditLog).filter(
            AuditLog.user_id == user_id, AuditLog.action_type == 'LOGIN').count()
        return total, logins, errors
    finally:
        session.close()


@create_page_layout("Meu Perfil")
def render():
    user_data = get_current_user()
    if not user_data:
        return

    user_id = user_data.get('id')
    ud = _load_user_dict(user_id)
    if not ud:
        ui.label('Usuário não encontrado.').classes('text-red-400')
        return

    profiles  = ud['profiles']
    all_perms = set(ud['all_perms'])
    initial   = ud['username'][0].upper()
    avatar_bg = next((PROFILE_COLORS[p] for p in profiles if p in PROFILE_COLORS), 'bg-blue-600')

    # ── Cabeçalho ────────────────────────────────────────────────────────
    with ui.row().classes('items-start gap-8 w-full mb-6'):
        with ui.column().classes('items-center gap-2'):
            with ui.card().classes(
                f'w-24 h-24 {avatar_bg} rounded-full items-center justify-center shadow-lg'
            ):
                ui.label(initial).classes('text-white text-4xl font-bold')
            for code in profiles[:2]:
                ui.badge(code).props(f'color={BADGE_COLORS.get(code, "blue-5")}')

        with ui.column().classes('gap-1 flex-1'):
            ui.label(ud['full_name'] or ud['username']).classes('text-white text-3xl font-bold')
            ui.label(f'@{ud["username"]}').classes('text-[#8b949e] text-lg')
            ui.label(ud['email']).classes('text-[#8b949e]')
            with ui.row().classes('gap-2 mt-1'):
                ui.badge('Ativo' if ud['is_active'] else 'Inativo') \
                    .props(f'color={"green" if ud["is_active"] else "red"}')
                if ud['is_system']:
                    ui.badge('Sistema').props('color=blue-5')
                if ud['is_locked']:
                    ui.badge('Bloqueado').props('color=orange')

        ui.button('Editar Perfil', icon='edit',
                  on_click=lambda: open_edit_dialog()) \
            .props('color=blue-6 no-caps')

    # ── Grid ─────────────────────────────────────────────────────────────
    with ui.row().classes('gap-6 w-full items-start'):

        # Esquerda
        with ui.column().classes('flex-1 gap-6'):
            with data_card('Informações da Conta'):
                rows = [
                    ('ID',              str(ud['id'])),
                    ('Username',        ud['username']),
                    ('E-mail',          ud['email'] or '—'),
                    ('Nome Completo',   ud['full_name'] or '—'),
                    ('Idioma',          ud['language']),
                    ('Tema',            ud['theme']),
                    ('Criado em',       ud['created_at']),
                    ('Último Login',    ud['last_login']),
                    ('Criado por',      ud['created_by']),
                ]
                with ui.column().classes('gap-0 w-full'):
                    for label, val in rows:
                        with ui.row().classes(
                            'items-center justify-between py-2 border-b border-[#30363d] last:border-0'
                        ):
                            ui.label(label).classes('text-[#8b949e] text-sm w-40 shrink-0')
                            ui.label(val).classes('text-white text-sm font-medium')

            activity = _load_activity(user_id)
            with data_card('Atividade Recente'):
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
                    t = ui.table(columns=cols, rows=activity) \
                        .classes('w-full ds-table text-xs').props('dense')
                    t.add_slot('body-cell-ok', '''
                        <q-td :props="props" class="text-center">
                            <q-badge :color="props.value ? \'green\' : \'red\'"
                                     :label="props.value ? \'✓\' : \'✗\'"/>
                        </q-td>
                    ''')

        # Direita
        with ui.column().classes('w-72 gap-6'):
            with data_card('Perfis de Acesso'):
                if not profiles:
                    ui.label('Nenhum perfil.').classes('text-[#8b949e] text-sm')
                else:
                    PERM_GROUPS = {
                        'Transações': ['transaction.execute', 'transaction.create'],
                        'Dados':      ['data.query', 'data.export', 'data.import'],
                        'Admin':      ['admin.users', 'admin.audit'],
                        'IA':         ['ia.consult', 'ia.train'],
                    }
                    for code in profiles:
                        with ui.card().classes('border border-[#30363d] bg-[#0d1117] p-3 mb-2'):
                            ui.badge(code).props(f'color={BADGE_COLORS.get(code, "blue-5")}').classes('mb-2')
                            with ui.column().classes('gap-1'):
                                for grp, perms in PERM_GROUPS.items():
                                    has = any(p in all_perms for p in perms)
                                    with ui.row().classes('items-center gap-1'):
                                        ui.icon(
                                            'check_circle' if has else 'cancel'
                                        ).classes(
                                            ('text-green-400' if has else 'text-[#30363d]') + ' text-sm'
                                        )
                                        ui.label(grp).classes(
                                            ('text-[#c9d1d9]' if has else 'text-[#30363d]') + ' text-xs'
                                        )

            total, logins, errors = _load_stats(user_id)
            with data_card('Estatísticas'):
                for label, val, cls in [
                    ('Total de Ações', total,  'text-white'),
                    ('Logins',         logins, 'text-green-400'),
                    ('Erros',          errors, 'text-red-400'),
                ]:
                    with ui.row().classes(
                        'items-center justify-between py-2 border-b border-[#30363d] last:border-0'
                    ):
                        ui.label(label).classes('text-[#8b949e] text-sm')
                        ui.label(str(val)).classes(f'{cls} font-bold')

    # ── Dialog de edição ──────────────────────────────────────────────────
    def open_edit_dialog():
        with ui.dialog() as dlg, \
             ui.card().classes('w-[500px] bg-[#161b22] border border-[#30363d] p-6'):
            ui.label('Editar Perfil').classes('text-white text-lg font-bold mb-4')
            f_name  = ui.input('Nome Completo', value=ud['full_name']) \
                .classes('w-full').props('outlined dense dark color=blue-4')
            f_email = ui.input('E-mail', value=ud['email']) \
                .classes('w-full').props('outlined dense dark color=blue-4')
            ui.separator().classes('bg-[#30363d] my-2')
            ui.label('Alterar Senha (deixe em branco para manter)') \
                .classes('text-[#8b949e] text-xs')
            f_pwd  = ui.input('Nova Senha', password=True, password_toggle_button=True) \
                .classes('w-full').props('outlined dense dark color=blue-4')
            f_pwd2 = ui.input('Confirmar Senha', password=True, password_toggle_button=True) \
                .classes('w-full').props('outlined dense dark color=blue-4')
            err = ui.label('').classes('text-red-400 text-sm')

            def save():
                if f_pwd.value and f_pwd.value != f_pwd2.value:
                    err.set_text('As senhas não coincidem.'); return
                session = db_manager.get_session()
                try:
                    u = session.query(User).filter(User.id == user_id).first()
                    u.full_name  = f_name.value
                    u.email      = f_email.value
                    u.updated_at = datetime.now()
                    if f_pwd.value:
                        u.set_password(f_pwd.value)
                    session.commit()
                    nicegui_app.storage.user.update({
                        'user_data': {
                            **nicegui_app.storage.user.get('user_data', {}),
                            'full_name': f_name.value,
                            'email':     f_email.value,
                        }
                    })
                    ui.notify('Perfil atualizado!', type='positive')
                    dlg.close()
                    ui.navigate.reload()
                except Exception as e:
                    session.rollback(); err.set_text(f'Erro: {e}')
                finally:
                    session.close()

            with ui.row().classes('gap-2 justify-end mt-4'):
                ui.button('Cancelar', on_click=dlg.close).props('flat color=grey-5 no-caps')
                ui.button('Salvar',   on_click=save).props('color=blue-6 no-caps')
        dlg.open()
