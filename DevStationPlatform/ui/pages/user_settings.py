"""
Configurações do Usuário - DevStationPlatform
Preferências, tema, idioma e segurança
"""

from nicegui import ui, app as nicegui_app
from ui.components.layout import create_page_layout, data_card
from ui.app import get_current_user
from core.models.user import User
from core.models.base import db_manager
from datetime import datetime


@create_page_layout("Configurações")
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

    user = load_user()

    # ── Header ─────────────────────────────────────────────────────────────
    with ui.row().classes('items-center justify-between w-full mb-6'):
        with ui.column().classes('gap-0'):
            ui.label('Configurações').classes('text-white text-2xl font-bold')
            ui.label('Gerencie suas preferências e segurança').classes('text-[#8b949e] text-sm')

    with ui.row().classes('gap-6 w-full items-start'):

        # ── Coluna esquerda ────────────────────────────────────────────────
        with ui.column().classes('flex-1 gap-6'):

            # ── Aparência ──────────────────────────────────────────────────
            with data_card('Aparência'):
                with ui.column().classes('gap-4 w-full'):
                    ui.label('Tema').classes('text-[#c9d1d9] text-sm font-semibold uppercase tracking-wider')
                    with ui.row().classes('gap-3'):
                        for theme_key, theme_label, bg, border in [
                            ('dark',  'Escuro',  'bg-[#0e1117]', 'border-blue-500'),
                            ('light', 'Claro',   'bg-[#f6f8fa]', 'border-[#30363d]'),
                        ]:
                            current = user.theme == theme_key if user else theme_key == 'dark'
                            with ui.card().classes(
                                f'{bg} border-2 {border if current else "border-[#30363d]"} '
                                f'p-4 w-36 cursor-pointer rounded-xl'
                            ).on('click', lambda k=theme_key: save_theme(k)):
                                with ui.column().classes('items-center gap-2'):
                                    ui.icon('dark_mode' if theme_key == 'dark' else 'light_mode') \
                                        .classes('text-2xl text-[#8b949e]')
                                    ui.label(theme_label).classes('text-white text-sm')
                                    if current:
                                        ui.badge('Ativo').props('color=blue-5')

                    ui.separator().classes('bg-[#30363d] my-2')

                    ui.label('Idioma').classes('text-[#c9d1d9] text-sm font-semibold uppercase tracking-wider')
                    lang_select = ui.select(
                        {'pt_BR': '🇧🇷 Português (BR)', 'en_US': '🇺🇸 English (US)', 'es_ES': '🇪🇸 Español'},
                        value=user.language if user else 'pt_BR',
                        label='Idioma do Sistema'
                    ).classes('w-64').props('outlined dense dark color=blue-4')

                    ui.button('Salvar Aparência', icon='palette',
                              on_click=lambda: save_appearance()).props('color=blue-6 no-caps')

            # ── Segurança ──────────────────────────────────────────────────
            with data_card('Segurança — Alterar Senha'):
                with ui.column().classes('gap-4 w-full'):
                    f_current = ui.input('Senha Atual', password=True, password_toggle_button=True) \
                        .classes('w-full max-w-md').props('outlined dense dark color=blue-4')
                    f_new     = ui.input('Nova Senha', password=True, password_toggle_button=True) \
                        .classes('w-full max-w-md').props('outlined dense dark color=blue-4')
                    f_confirm = ui.input('Confirmar Nova Senha', password=True, password_toggle_button=True) \
                        .classes('w-full max-w-md').props('outlined dense dark color=blue-4')

                    pwd_strength = ui.label('').classes('text-sm')
                    f_new.on('input', lambda: check_strength())

                    pwd_err = ui.label('').classes('text-red-400 text-sm')

                    ui.button('Alterar Senha', icon='lock',
                              on_click=lambda: change_password()).props('color=blue-6 no-caps')

        # ── Coluna direita ─────────────────────────────────────────────────
        with ui.column().classes('w-80 gap-6'):

            with data_card('Conta'):
                with ui.column().classes('gap-3'):
                    rows = [
                        ('Usuário',     user.username if user else '—'),
                        ('E-mail',      user.email or '—' if user else '—'),
                        ('Status',      '✅ Ativo' if user and user.is_active else '❌ Inativo'),
                        ('Criado em',   user.created_at.strftime('%d/%m/%Y') if user and user.created_at else '—'),
                    ]
                    for label, val in rows:
                        with ui.row().classes('items-center justify-between py-1 border-b border-[#30363d] last:border-0'):
                            ui.label(label).classes('text-[#8b949e] text-sm')
                            ui.label(val).classes('text-white text-sm')

                    ui.separator().classes('bg-[#30363d] my-2')
                    ui.button('Ver Meu Perfil', icon='person',
                              on_click=lambda: ui.navigate.to('/profile')) \
                        .props('flat no-caps color=blue-4').classes('w-full')

            with data_card('Sessão Atual'):
                with ui.column().classes('gap-3'):
                    ui.label('Sessão iniciada nesta aba.').classes('text-[#8b949e] text-sm')
                    token_display = nicegui_app.storage.user.get('token', '')
                    if token_display:
                        ui.label(f'Token: ...{token_display[-12:]}').classes('text-[#8b949e] text-xs font-mono')
                    ui.separator().classes('bg-[#30363d]')
                    ui.button('Encerrar Sessão', icon='logout',
                              on_click=lambda: do_logout()) \
                        .props('flat no-caps color=red-4').classes('w-full')

            with data_card('Notificações'):
                with ui.column().classes('gap-3'):
                    ui.label('Configurações de notificação') \
                        .classes('text-[#8b949e] text-xs')
                    for label, key in [
                        ('Notificações de login',  'notif_login'),
                        ('Alertas de erro',        'notif_error'),
                        ('Resumo diário',           'notif_daily'),
                    ]:
                        prefs = (user.preferences or {}) if user else {}
                        val = prefs.get(key, True)
                        cb = ui.checkbox(label, value=val).classes('text-sm')
                        cb.on('update:model-value',
                              lambda v, k=key, c=cb: save_pref(k, c.value))

    # ── funções ────────────────────────────────────────────────────────────
    def save_theme(theme_key):
        session = db_manager.get_session()
        try:
            u = session.query(User).filter(User.id == user_id).first()
            if u:
                u.theme = theme_key
                session.commit()
            ui.notify(f'Tema "{theme_key}" salvo!', type='positive')
            ui.navigate.reload()
        except Exception as e:
            session.rollback()
            ui.notify(f'Erro: {e}', type='negative')
        finally:
            session.close()

    def save_appearance():
        session = db_manager.get_session()
        try:
            u = session.query(User).filter(User.id == user_id).first()
            if u:
                u.language = lang_select.value
                session.commit()
            ui.notify('Preferências salvas!', type='positive')
        except Exception as e:
            session.rollback()
            ui.notify(f'Erro: {e}', type='negative')
        finally:
            session.close()

    def check_strength():
        pwd = f_new.value
        if not pwd:
            pwd_strength.set_text('')
            return
        score = sum([
            len(pwd) >= 8,
            any(c.isupper() for c in pwd),
            any(c.islower() for c in pwd),
            any(c.isdigit() for c in pwd),
            any(c in '!@#$%^&*()_+-=' for c in pwd),
        ])
        labels = ['', '⚠ Muito fraca', '⚠ Fraca', '✓ Razoável', '✓ Boa', '✓ Forte']
        colors = ['', 'text-red-500', 'text-orange-400', 'text-yellow-400', 'text-blue-400', 'text-green-400']
        pwd_strength.set_text(labels[score])
        pwd_strength.classes(colors[score], remove='text-red-500 text-orange-400 text-yellow-400 text-blue-400 text-green-400')

    def change_password():
        pwd_err.set_text('')
        if not f_current.value:
            pwd_err.set_text('Informe a senha atual.')
            return
        if not f_new.value:
            pwd_err.set_text('Informe a nova senha.')
            return
        if f_new.value != f_confirm.value:
            pwd_err.set_text('As senhas não coincidem.')
            return
        if len(f_new.value) < 6:
            pwd_err.set_text('A nova senha deve ter pelo menos 6 caracteres.')
            return
        session = db_manager.get_session()
        try:
            u = session.query(User).filter(User.id == user_id).first()
            if not u.verify_password(f_current.value):
                pwd_err.set_text('Senha atual incorreta.')
                return
            u.set_password(f_new.value)
            u.updated_at = datetime.now()
            session.commit()
            ui.notify('Senha alterada com sucesso!', type='positive')
            f_current.set_value('')
            f_new.set_value('')
            f_confirm.set_value('')
            pwd_strength.set_text('')
        except Exception as e:
            session.rollback()
            pwd_err.set_text(f'Erro: {e}')
        finally:
            session.close()

    def save_pref(key, value):
        session = db_manager.get_session()
        try:
            u = session.query(User).filter(User.id == user_id).first()
            if u:
                prefs = dict(u.preferences or {})
                prefs[key] = value
                u.preferences = prefs
                session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

    def do_logout():
        from ui.app import logout_user
        logout_user()
        ui.navigate.to('/login')
