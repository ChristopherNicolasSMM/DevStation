"""
DS_PROFILES — Gestão de Perfis e Permissões
Hierarquia, CRUD de perfis e atribuição de permissões
"""

from nicegui import ui
from ui.components.layout import create_page_layout, data_card
from ui.app import get_current_user
from core.models.user import User, Profile, Permission
from core.models.base import db_manager
from datetime import datetime


HIERARCHY_ORDER = ["USER", "PUSER", "BANALYST", "DEVELOPER", "CORE_DEV", "DEV_ALL", "ADMIN"]
PROFILE_BADGE_COLOR = {
    "USER": "grey-6", "PUSER": "teal-6", "BANALYST": "blue-6",
    "DEVELOPER": "indigo-6", "CORE_DEV": "purple-6", "DEV_ALL": "deep-orange-6", "ADMIN": "red-6",
}


@create_page_layout("DS_PROFILES — Gestão de Perfis")
def render():
    user_data = get_current_user()
    if not user_data:
        return

    # ── DB helpers ────────────────────────────────────────────────────────
    def fetch_profiles():
        session = db_manager.get_session()
        try:
            return session.query(Profile).order_by(Profile.priority.desc(), Profile.code).all()
        finally:
            session.close()

    def fetch_permissions():
        session = db_manager.get_session()
        try:
            return session.query(Permission).order_by(Permission.category, Permission.code).all()
        finally:
            session.close()

    def perm_categories(perms):
        cats = {}
        for p in perms:
            cat = p.category or 'Outros'
            cats.setdefault(cat, []).append(p)
        return cats

    # ── Dialog de perfil ──────────────────────────────────────────────────
    def open_profile_dialog(profile=None):
        is_edit   = profile is not None
        all_perms = fetch_permissions()
        cats      = perm_categories(all_perms)

        cur_perm_ids = set(p.id for p in profile.permissions) if is_edit and profile.permissions else set()

        with ui.dialog() as dlg, ui.card().classes('w-[640px] bg-[#161b22] border border-[#30363d] p-6'):
            with ui.row().classes('items-center gap-3 mb-4'):
                ui.icon('security').classes('text-blue-400 text-2xl')
                ui.label('Editar Perfil' if is_edit else 'Novo Perfil') \
                    .classes('text-white text-lg font-bold')

            with ui.tabs().classes('w-full') as tabs:
                tab_info  = ui.tab('Dados',       icon='info')
                tab_perms = ui.tab('Permissões',  icon='lock')

            with ui.tab_panels(tabs, value=tab_info).classes('w-full pt-2'):

                with ui.tab_panel(tab_info):
                    with ui.column().classes('gap-3 w-full'):
                        f_code  = ui.input('Código *', value=profile.code if is_edit else '') \
                            .classes('w-full').props('outlined dense dark color=blue-4')
                        f_name  = ui.input('Nome *', value=profile.name if is_edit else '') \
                            .classes('w-full').props('outlined dense dark color=blue-4')
                        f_desc  = ui.input('Descrição', value=profile.description or '' if is_edit else '') \
                            .classes('w-full').props('outlined dense dark color=blue-4')
                        f_prio  = ui.number('Prioridade / Nível',
                                            value=profile.priority if is_edit else 0, min=0, max=99) \
                            .classes('w-48').props('outlined dense dark color=blue-4')
                        with ui.row().classes('gap-6'):
                            f_active = ui.checkbox('Perfil Ativo',   value=profile.is_active  if is_edit else True)
                            f_system = ui.checkbox('Perfil Sistema', value=profile.is_system  if is_edit else False)

                with ui.tab_panel(tab_perms):
                    ui.label('Marque as permissões concedidas a este perfil:') \
                        .classes('text-[#8b949e] text-sm mb-2')

                    perm_checks = {}
                    with ui.scroll_area().classes('h-72 w-full border border-[#30363d] rounded p-2'):
                        for cat_name, cat_perms in cats.items():
                            ui.label(cat_name.upper()) \
                                .classes('text-[#8b949e] text-xs font-bold uppercase mt-2 mb-1')
                            with ui.column().classes('gap-1 ml-2'):
                                for perm in cat_perms:
                                    cb = ui.checkbox(
                                        f'{perm.code}',
                                        value=perm.id in cur_perm_ids
                                    ).classes('text-xs')
                                    with ui.tooltip():
                                        ui.label(perm.description or perm.name or perm.code) \
                                            .classes('text-xs')
                                    perm_checks[perm.id] = cb

            err = ui.label('').classes('text-red-400 text-sm mt-2')

            def save():
                if not f_code.value or not f_name.value:
                    err.set_text('Código e Nome são obrigatórios.'); return
                selected_ids = [pid for pid, cb in perm_checks.items() if cb.value]
                session = db_manager.get_session()
                try:
                    if is_edit:
                        p = session.query(Profile).filter(Profile.id == profile.id).first()
                    else:
                        p = Profile(); session.add(p)
                    p.code        = f_code.value.upper().strip()
                    p.name        = f_name.value.strip()
                    p.description = f_desc.value.strip()
                    p.priority    = int(f_prio.value or 0)
                    p.is_active   = f_active.value
                    p.is_system   = f_system.value
                    p.updated_at  = datetime.now()
                    p.permissions = session.query(Permission) \
                        .filter(Permission.id.in_(selected_ids)).all()
                    session.commit()
                    ui.notify('Perfil salvo!', type='positive')
                    dlg.close(); refresh()
                except Exception as e:
                    session.rollback(); err.set_text(f'Erro: {e}')
                finally:
                    session.close()

            with ui.row().classes('gap-2 justify-end mt-4 border-t border-[#30363d] pt-4'):
                ui.button('Cancelar', on_click=dlg.close).props('flat color=grey-5 no-caps')
                ui.button('Salvar',   on_click=save).props('color=blue-6 no-caps')
        dlg.open()

    def open_delete_dialog(profile):
        with ui.dialog() as dlg, ui.card().classes('w-[400px] bg-[#161b22] border border-[#30363d] p-6'):
            ui.label('Confirmar Exclusão').classes('text-white text-lg font-bold mb-2')
            with ui.row().classes('items-center gap-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg mb-4'):
                ui.icon('warning').classes('text-red-400 text-2xl')
                ui.label(f'Excluir perfil "{profile.code}"?').classes('text-[#c9d1d9] text-sm')

            def do_delete():
                if profile.is_system:
                    ui.notify('Perfis do sistema não podem ser excluídos.', type='warning'); return
                session = db_manager.get_session()
                try:
                    p = session.query(Profile).filter(Profile.id == profile.id).first()
                    if p: session.delete(p); session.commit()
                    ui.notify('Perfil excluído.', type='positive')
                    dlg.close(); refresh()
                except Exception as e:
                    session.rollback(); ui.notify(f'Erro: {e}', type='negative')
                finally:
                    session.close()

            with ui.row().classes('gap-2 justify-end'):
                ui.button('Cancelar', on_click=dlg.close).props('flat color=grey-5 no-caps')
                ui.button('Excluir',  on_click=do_delete).props('color=red-6 no-caps')
        dlg.open()

    # ── Layout ────────────────────────────────────────────────────────────
    with ui.row().classes('items-center justify-between w-full mb-4'):
        with ui.column().classes('gap-0'):
            ui.label('Perfis de Acesso (DS_PROFILES)').classes('text-white text-2xl font-bold')
            ui.label('Gerencie perfis e permissões do sistema').classes('text-[#8b949e] text-sm')
        ui.button('Novo Perfil', icon='add_circle', on_click=lambda: open_profile_dialog()) \
            .props('color=blue-6 no-caps')

    content_col = ui.column().classes('w-full gap-6')

    def refresh():
        profiles = fetch_profiles()
        all_perms = fetch_permissions()
        content_col.clear()

        with content_col:
            # ── Hierarquia visual ─────────────────────────────────────────
            with data_card('Hierarquia de Perfis'):
                with ui.row().classes('gap-0 items-stretch flex-wrap'):
                    known = {p.code: p for p in profiles}
                    steps = [c for c in HIERARCHY_ORDER if c in known] + \
                            [p.code for p in profiles if p.code not in HIERARCHY_ORDER]
                    for i, code in enumerate(steps):
                        p = known.get(code)
                        color = PROFILE_BADGE_COLOR.get(code, 'grey-6')
                        pcount = len(p.permissions) if p and p.permissions else 0
                        ucount = len(p.users) if p and p.users else 0
                        with ui.column().classes('items-center'):
                            with ui.card().classes('border border-[#30363d] px-4 py-3 m-1 min-w-[110px] items-center'):
                                ui.badge(code).props(f'color={color}').classes('mb-1')
                                ui.label(p.name if p else code) \
                                    .classes('text-white text-xs text-center')
                                with ui.row().classes('gap-2 mt-1'):
                                    ui.label(f'{pcount}p').classes('text-[#8b949e] text-xs')
                                    ui.label(f'{ucount}u').classes('text-[#8b949e] text-xs')
                        if i < len(steps) - 1:
                            with ui.column().classes('justify-center'):
                                ui.icon('chevron_right').classes('text-[#30363d] text-xl mt-3')

            # ── Cards de perfis ───────────────────────────────────────────
            with ui.row().classes('gap-4 flex-wrap'):
                for profile in profiles:
                    color   = PROFILE_BADGE_COLOR.get(profile.code, 'grey-6')
                    pcount  = len(profile.permissions) if profile.permissions else 0
                    ucount  = len(profile.users) if profile.users else 0
                    perms_c = perm_categories([p for p in (profile.permissions or [])])

                    with ui.card().classes('bg-[#161b22] border border-[#30363d] p-5 w-80'):
                        # Header do card
                        with ui.row().classes('items-start justify-between mb-3'):
                            with ui.column().classes('gap-1'):
                                ui.badge(profile.code).props(f'color={color}')
                                ui.label(profile.name).classes('text-white text-sm font-semibold mt-1')
                                if profile.description:
                                    ui.label(profile.description) \
                                        .classes('text-[#8b949e] text-xs')
                            with ui.row().classes('gap-1'):
                                ui.button(icon='edit',
                                          on_click=lambda p=profile: open_profile_dialog(p)) \
                                    .props('flat dense color=blue-4')
                                ui.button(icon='delete',
                                          on_click=lambda p=profile: open_delete_dialog(p)) \
                                    .props('flat dense color=red-4')

                        ui.separator().classes('bg-[#30363d] my-2')

                        # Stats
                        with ui.row().classes('gap-4 mb-2'):
                            with ui.column().classes('items-center gap-0'):
                                ui.label(str(pcount)).classes('text-blue-400 text-lg font-bold')
                                ui.label('permissões').classes('text-[#8b949e] text-xs')
                            with ui.column().classes('items-center gap-0'):
                                ui.label(str(ucount)).classes('text-green-400 text-lg font-bold')
                                ui.label('usuários').classes('text-[#8b949e] text-xs')
                            with ui.column().classes('items-center gap-0'):
                                ui.label(str(profile.priority or 0)).classes('text-white text-lg font-bold')
                                ui.label('nível').classes('text-[#8b949e] text-xs')

                        # Permissões por categoria
                        if perms_c:
                            with ui.expansion('Permissões', icon='lock').classes('w-full'):
                                for cat_name, cat_perms in perms_c.items():
                                    ui.label(cat_name).classes('text-[#8b949e] text-xs uppercase font-bold mt-1')
                                    for perm in cat_perms:
                                        with ui.row().classes('items-center gap-1'):
                                            ui.icon('check').classes('text-green-400 text-xs')
                                            ui.label(perm.code).classes('text-white text-xs font-mono')

                        # Badges de flags
                        with ui.row().classes('gap-1 mt-2'):
                            if profile.is_system:
                                ui.badge('Sistema').props('color=blue-4 outline')
                            if not profile.is_active:
                                ui.badge('Inativo').props('color=red-4 outline')

            # ── Tabela de permissões do sistema ───────────────────────────
            all_p = fetch_permissions()
            if all_p:
                cats = perm_categories(all_p)
                with data_card('Todas as Permissões do Sistema'):
                    with ui.tabs().classes('w-full') as ptabs:
                        cat_tabs = {cat: ui.tab(cat) for cat in cats}

                    with ui.tab_panels(ptabs, value=list(cat_tabs.values())[0] if cat_tabs else None).classes('w-full'):
                        for cat_name, cat_tab in cat_tabs.items():
                            with ui.tab_panel(cat_tab):
                                pcols = [
                                    {'name': 'code',        'label': 'Código',       'field': 'code',        'align': 'left', 'sortable': True},
                                    {'name': 'name',        'label': 'Nome',         'field': 'name',        'align': 'left'},
                                    {'name': 'description', 'label': 'Descrição',    'field': 'description', 'align': 'left'},
                                    {'name': 'profiles',    'label': 'Perfis',       'field': 'profiles',    'align': 'left'},
                                    {'name': 'system',      'label': 'Sistema',      'field': 'system',      'align': 'center'},
                                ]
                                prows = []
                                for perm in cats.get(cat_name, []):
                                    prof_codes = [
                                        p.code for p in profiles
                                        if perm in (p.permissions or [])
                                    ]
                                    prows.append({
                                        'code':        perm.code,
                                        'name':        perm.name or '—',
                                        'description': perm.description or '—',
                                        'profiles':    ', '.join(prof_codes) or '—',
                                        'system':      perm.is_system,
                                    })
                                t = ui.table(columns=pcols, rows=prows) \
                                    .classes('w-full ds-table text-xs').props('dense')
                                t.add_slot('body-cell-system', '''
                                    <q-td :props="props" class="text-center">
                                        <q-icon :name="props.value ? \'check_circle\' : \'radio_button_unchecked\'"
                                                :color="props.value ? \'blue-4\' : \'grey-7\'"/>
                                    </q-td>
                                ''')

    refresh()
