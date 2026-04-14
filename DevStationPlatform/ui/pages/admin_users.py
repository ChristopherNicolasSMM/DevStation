"""
DS_USERS — Gestão de Usuários
CRUD completo com atribuição de perfis
"""

from nicegui import ui
from ui.components.layout import create_page_layout, data_card
from ui.app import get_current_user
from core.models.user import User, Profile
from core.models.base import db_manager
from datetime import datetime


@create_page_layout("DS_USERS — Gestão de Usuários")
def render():
    user_data = get_current_user()
    if not user_data:
        return

    # ── DB helpers ────────────────────────────────────────────────────────
    def fetch_users(term='', status='Todos'):
        session = db_manager.get_session()
        try:
            q = session.query(User)
            if term:
                like = f'%{term}%'
                q = q.filter(User.username.ilike(like) | User.full_name.ilike(like) | User.email.ilike(like))
            if status == 'Ativos':
                q = q.filter(User.is_active == True)
            elif status == 'Inativos':
                q = q.filter(User.is_active == False)
            users = q.order_by(User.username).all()
            result = []
            for u in users:
                result.append({
                    'id':        u.id,
                    'username':  u.username,
                    'full_name': u.full_name or '—',
                    'email':     u.email or '—',
                    'profiles':  ', '.join([p.code for p in u.profiles]) if u.profiles else '—',
                    'active':    u.is_active,
                    'locked':    u.is_locked,
                    'system':    u.is_system,
                    'last_login':u.last_login.strftime('%d/%m/%Y %H:%M') if u.last_login else '—',
                    'created':   u.created_at.strftime('%d/%m/%Y') if u.created_at else '—',
                })
            return result
        finally:
            session.close()

    def fetch_profiles():
        session = db_manager.get_session()
        try:
            return [(p.id, p.code, p.name) for p in session.query(Profile).order_by(Profile.priority.desc()).all()]
        finally:
            session.close()

    def get_user_profile_ids(user_id):
        session = db_manager.get_session()
        try:
            u = session.query(User).filter(User.id == user_id).first()
            return [p.id for p in u.profiles] if u and u.profiles else []
        finally:
            session.close()

    def get_stats():
        session = db_manager.get_session()
        try:
            total   = session.query(User).count()
            active  = session.query(User).filter(User.is_active == True).count()
            locked  = session.query(User).filter(User.is_locked == True).count()
            system  = session.query(User).filter(User.is_system == True).count()
            return total, active, locked, system
        finally:
            session.close()

    # ── Diálogo criar / editar ────────────────────────────────────────────
    def open_user_dialog(user_id=None):
        is_edit = user_id is not None
        profiles = fetch_profiles()
        current_profile_ids = get_user_profile_ids(user_id) if is_edit else []

        # Busca dados do usuário para edição
        edit_data = {}
        if is_edit:
            session = db_manager.get_session()
            try:
                u = session.query(User).filter(User.id == user_id).first()
                if u:
                    edit_data = {
                        'username':  u.username,
                        'full_name': u.full_name or '',
                        'email':     u.email or '',
                        'is_active': u.is_active,
                        'is_locked': u.is_locked,
                    }
            finally:
                session.close()

        with ui.dialog() as dlg, ui.card().classes('w-[560px] bg-[#161b22] border border-[#30363d] p-6'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ui.icon('person_add' if not is_edit else 'edit').classes('text-blue-400 text-2xl')
                ui.label('Editar Usuário' if is_edit else 'Novo Usuário') \
                    .classes('text-white text-lg font-bold')

            with ui.tabs().classes('w-full') as tabs:
                tab_info  = ui.tab('Informações', icon='info')
                tab_perfs = ui.tab('Perfis',       icon='security')
                if is_edit:
                    tab_pwd = ui.tab('Senha',      icon='lock')

            with ui.tab_panels(tabs, value=tab_info).classes('w-full pt-2'):

                with ui.tab_panel(tab_info):
                    with ui.column().classes('gap-3 w-full'):
                        f_user = ui.input('Usuário *', value=edit_data.get('username', '')) \
                            .classes('w-full').props('outlined dense dark color=blue-4')
                        f_name = ui.input('Nome Completo', value=edit_data.get('full_name', '')) \
                            .classes('w-full').props('outlined dense dark color=blue-4')
                        f_email = ui.input('E-mail *', value=edit_data.get('email', '')) \
                            .classes('w-full').props('outlined dense dark color=blue-4')
                        if not is_edit:
                            f_pwd  = ui.input('Senha *', password=True, password_toggle_button=True) \
                                .classes('w-full').props('outlined dense dark color=blue-4')
                            f_pwd2 = ui.input('Confirmar Senha *', password=True, password_toggle_button=True) \
                                .classes('w-full').props('outlined dense dark color=blue-4')

                        with ui.row().classes('gap-6'):
                            f_active = ui.checkbox('Usuário Ativo',   value=edit_data.get('is_active', True))
                            f_locked = ui.checkbox('Conta Bloqueada', value=edit_data.get('is_locked', False))

                with ui.tab_panel(tab_perfs):
                    ui.label('Selecione os perfis de acesso do usuário:') \
                        .classes('text-[#8b949e] text-sm mb-3')
                    profile_checks = {}
                    with ui.scroll_area().classes('h-52 w-full'):
                        with ui.column().classes('gap-2'):
                            for p_id, p_code, p_name in profiles:
                                cb = ui.checkbox(
                                    f'{p_code} — {p_name}',
                                    value=p_id in current_profile_ids
                                )
                                profile_checks[p_id] = cb

                if is_edit:
                    with ui.tab_panel(tab_pwd):
                        with ui.column().classes('gap-3 w-full'):
                            ui.label('Redefina a senha deste usuário:') \
                                .classes('text-[#8b949e] text-sm')
                            f_np  = ui.input('Nova Senha', password=True, password_toggle_button=True) \
                                .classes('w-full').props('outlined dense dark color=blue-4')
                            f_np2 = ui.input('Confirmar Senha', password=True, password_toggle_button=True) \
                                .classes('w-full').props('outlined dense dark color=blue-4')

                            def change_pwd():
                                if not f_np.value:
                                    ui.notify('Informe a nova senha.', type='warning'); return
                                if f_np.value != f_np2.value:
                                    ui.notify('As senhas não coincidem.', type='warning'); return
                                session = db_manager.get_session()
                                try:
                                    u = session.query(User).filter(User.id == user_id).first()
                                    u.set_password(f_np.value)
                                    u.updated_at = datetime.now()
                                    session.commit()
                                    ui.notify('Senha alterada!', type='positive')
                                    f_np.set_value(''); f_np2.set_value('')
                                except Exception as e:
                                    session.rollback(); ui.notify(f'Erro: {e}', type='negative')
                                finally:
                                    session.close()
                            ui.button('Alterar Senha', icon='lock', on_click=change_pwd) \
                                .props('color=orange-7 no-caps').classes('mt-2')

            err = ui.label('').classes('text-red-400 text-sm mt-2')

            def save():
                if not f_user.value or not f_email.value:
                    err.set_text('Usuário e e-mail são obrigatórios.'); return
                if not is_edit and f_pwd.value != f_pwd2.value:
                    err.set_text('As senhas não coincidem.'); return

                selected_ids = [pid for pid, cb in profile_checks.items() if cb.value]
                session = db_manager.get_session()
                try:
                    if is_edit:
                        u = session.query(User).filter(User.id == user_id).first()
                    else:
                        u = User(); session.add(u)
                    u.username   = f_user.value.strip()
                    u.full_name  = f_name.value.strip()
                    u.email      = f_email.value.strip()
                    u.is_active  = f_active.value
                    u.is_locked  = f_locked.value
                    u.updated_at = datetime.now()
                    if not is_edit:
                        u.set_password(f_pwd.value)
                        u.created_at = datetime.now()

                    new_profiles = session.query(Profile).filter(Profile.id.in_(selected_ids)).all()
                    u.profiles = new_profiles
                    session.commit()
                    ui.notify('Usuário salvo!', type='positive')
                    dlg.close()
                    refresh()
                except Exception as e:
                    session.rollback(); err.set_text(f'Erro: {e}')
                finally:
                    session.close()

            with ui.row().classes('gap-2 justify-end mt-4 border-t border-[#30363d] pt-4'):
                ui.button('Cancelar', on_click=dlg.close).props('flat color=grey-5 no-caps')
                ui.button('Salvar',   on_click=save).props('color=blue-6 no-caps')
        dlg.open()

    def open_delete_dialog(user_id, username):
        with ui.dialog() as dlg, ui.card().classes('w-[400px] bg-[#161b22] border border-[#30363d] p-6'):
            ui.label('Confirmar Exclusão').classes('text-white text-lg font-bold mb-2')
            with ui.row().classes('items-center gap-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg mb-4'):
                ui.icon('warning').classes('text-red-400 text-2xl')
                ui.label(f'Excluir "{username}"? Esta ação não pode ser desfeita.') \
                    .classes('text-[#c9d1d9] text-sm')

            def do_delete():
                session = db_manager.get_session()
                try:
                    u = session.query(User).filter(User.id == user_id).first()
                    if u:
                        if u.is_system:
                            ui.notify('Não é possível excluir usuários do sistema.', type='warning')
                            return
                        session.delete(u)
                        session.commit()
                    ui.notify('Usuário excluído.', type='positive')
                    dlg.close(); refresh()
                except Exception as e:
                    session.rollback(); ui.notify(f'Erro: {e}', type='negative')
                finally:
                    session.close()

            with ui.row().classes('gap-2 justify-end'):
                ui.button('Cancelar', on_click=dlg.close).props('flat color=grey-5 no-caps')
                ui.button('Excluir',  on_click=do_delete).props('color=red-6 no-caps')
        dlg.open()

    # ── UI ────────────────────────────────────────────────────────────────
    with ui.row().classes('items-center justify-between w-full mb-4'):
        with ui.column().classes('gap-0'):
            ui.label('Gestão de Usuários (DS_USERS)').classes('text-white text-2xl font-bold')
            ui.label('Crie, edite e gerencie usuários do sistema').classes('text-[#8b949e] text-sm')
        ui.button('Novo Usuário', icon='person_add',
                  on_click=lambda: open_user_dialog()) \
            .props('color=blue-6 no-caps')

    # Filtros
    with ui.row().classes('items-center gap-3 mb-4'):
        inp_search = ui.input(placeholder='Buscar por nome, usuário ou e-mail...') \
            .classes('flex-1').props('outlined dense dark color=blue-4 clearable')
        inp_status = ui.select(['Todos', 'Ativos', 'Inativos'], value='Todos') \
            .classes('w-36').props('outlined dense dark color=blue-4')
        ui.button('Buscar', icon='search', on_click=lambda: refresh()) \
            .props('color=blue-6 no-caps')

    # KPI + tabela container
    kpi_row       = ui.row().classes('gap-4 mb-4')
    table_container = ui.column().classes('w-full')

    def refresh():
        users = fetch_users(inp_search.value, inp_status.value)
        total, active, locked, system = get_stats()

        kpi_row.clear()
        with kpi_row:
            for label, val, color in [
                ('Total',    total,          'text-white'),
                ('Ativos',   active,         'text-green-400'),
                ('Inativos', total - active, 'text-red-400'),
                ('Bloqueados',locked,        'text-orange-400'),
                ('Sistema',  system,         'text-blue-400'),
            ]:
                with ui.card().classes('bg-[#161b22] border border-[#30363d] px-5 py-3'):
                    ui.label(label).classes('text-[#8b949e] text-xs uppercase')
                    ui.label(str(val)).classes(f'{color} text-2xl font-bold')

        table_container.clear()
        with table_container:
            with data_card(f'Usuários — {len(users)} encontrado(s)'):
                if not users:
                    ui.label('Nenhum usuário encontrado.') \
                        .classes('text-[#8b949e] text-center py-8 w-full')
                    return

                cols = [
                    {'name': 'username',  'label': 'Usuário',      'field': 'username',  'align': 'left',   'sortable': True},
                    {'name': 'full_name', 'label': 'Nome',          'field': 'full_name', 'align': 'left',   'sortable': True},
                    {'name': 'email',     'label': 'E-mail',        'field': 'email',     'align': 'left'},
                    {'name': 'profiles',  'label': 'Perfis',        'field': 'profiles',  'align': 'left'},
                    {'name': 'status',    'label': 'Status',        'field': 'active',    'align': 'center'},
                    {'name': 'last_login','label': 'Último Login',  'field': 'last_login','align': 'left'},
                    {'name': 'actions',   'label': 'Ações',         'field': 'id',        'align': 'center'},
                ]
                id_map = {u['username']: u['id'] for u in users}

                tbl = ui.table(columns=cols, rows=users, row_key='username') \
                    .classes('w-full ds-table').props('dense')

                tbl.add_slot('body-cell-status', '''
                    <q-td :props="props" class="text-center">
                        <q-badge :color="props.row.active ? \'green\' : \'red\'"
                                 :label="props.row.active ? \'Ativo\' : \'Inativo\'"/>
                        <q-badge v-if="props.row.locked" color="orange" label="Bloqueado" class="ml-1"/>
                    </q-td>
                ''')
                tbl.add_slot('body-cell-actions', '''
                    <q-td :props="props" class="text-center">
                        <q-btn flat dense icon="edit"   color="blue-4"  @click="$parent.$emit(\'edit\',   props.row)"/>
                        <q-btn flat dense icon="person" color="teal-4"  @click="$parent.$emit(\'profile\',props.row)"/>
                        <q-btn flat dense icon="delete" color="red-4"   @click="$parent.$emit(\'delete\', props.row)"/>
                    </q-td>
                ''')
                tbl.on('edit',    lambda e: open_user_dialog(e.args.get('id')))
                tbl.on('profile', lambda e: ui.navigate.to(f'/admin/user/{e.args.get("id")}'))
                tbl.on('delete',  lambda e: open_delete_dialog(e.args.get('id'), e.args.get('username')))

    refresh()
