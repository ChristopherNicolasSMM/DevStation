"""
Configurações do Usuário - DevStationPlatform
Tema, idioma, senha — sem DetachedInstanceError, tema via ui.dark_mode()
"""

from nicegui import ui, app as nicegui_app
from ui.components.layout import create_page_layout, data_card
from ui.app import get_current_user
from core.models.user import User
from core.models.base import db_manager
from datetime import datetime


def _load_user(user_id):
    session = db_manager.get_session()
    try:
        u = session.query(User).filter(User.id == user_id).first()
        if not u:
            return None
        return {
            'id':         u.id,
            'username':   u.username,
            'email':      u.email or '',
            'full_name':  u.full_name or '',
            'is_active':  u.is_active,
            'theme':      u.theme or 'dark',
            'language':   u.language or 'pt_BR',
            'preferences': dict(u.preferences or {}),
            'created_at': u.created_at.strftime('%d/%m/%Y') if u.created_at else '—',
        }
    finally:
        session.close()


@create_page_layout("Configurações")
def render():
    user_data = get_current_user()
    if not user_data:
        return

    user_id = user_data.get('id')
    ud = _load_user(user_id)
    if not ud:
        ui.label('Usuário não encontrado.').classes('text-red-400')
        return

    # dark_mode handler para troca de tema real no NiceGUI
    dark_mode = ui.dark_mode(value=(ud['theme'] == 'dark'))

    # ── Header ────────────────────────────────────────────────────────────
    with ui.row().classes('items-center justify-between w-full mb-6'):
        with ui.column().classes('gap-0'):
            ui.label('Configurações').classes('text-white text-2xl font-bold')
            ui.label('Preferências, aparência e segurança').classes('text-[#8b949e] text-sm')

    with ui.row().classes('gap-6 w-full items-start'):

        # ── Coluna esquerda ───────────────────────────────────────────────
        with ui.column().classes('flex-1 gap-6'):

            # Aparência
            with data_card('Aparência'):
                with ui.column().classes('gap-4 w-full'):
                    ui.label('Tema').classes(
                        'text-[#c9d1d9] text-sm font-semibold uppercase tracking-wider')

                    with ui.row().classes('gap-3'):
                        for key, label, icon_name in [
                            ('dark',  'Escuro', 'dark_mode'),
                            ('light', 'Claro',  'light_mode'),
                        ]:
                            is_cur = ud['theme'] == key
                            border = 'border-blue-500 border-2' if is_cur else 'border-[#30363d]'
                            bg     = 'bg-[#0d1117]' if key == 'dark' else 'bg-[#f0f0f0]'
                            with ui.card().classes(
                                f'{bg} border {border} p-4 w-36 cursor-pointer rounded-xl'
                            ).on('click', lambda k=key: apply_theme(k)):
                                with ui.column().classes('items-center gap-2'):
                                    ui.icon(icon_name).classes('text-2xl text-[#8b949e]')
                                    txt_cls = 'text-white' if key == 'dark' else 'text-[#1a1a1a]'
                                    ui.label(label).classes(f'{txt_cls} text-sm font-medium')
                                    if is_cur:
                                        ui.badge('Ativo').props('color=blue-5')

                    ui.separator().classes('bg-[#30363d] my-2')

                    ui.label('Idioma').classes(
                        'text-[#c9d1d9] text-sm font-semibold uppercase tracking-wider')
                    lang_sel = ui.select(
                        {'pt_BR': '🇧🇷 Português (BR)',
                         'en_US': '🇺🇸 English (US)',
                         'es_ES': '🇪🇸 Español'},
                        value=ud['language']
                    ).classes('w-64').props('outlined dense dark color=blue-4')

                    ui.button('Salvar Idioma', icon='language',
                              on_click=lambda: save_language()) \
                        .props('color=blue-6 no-caps')

            # Segurança
            with data_card('Segurança — Alterar Senha'):
                with ui.column().classes('gap-4 w-full max-w-md'):
                    f_cur  = ui.input('Senha Atual', password=True,
                                      password_toggle_button=True) \
                        .classes('w-full').props('outlined dense dark color=blue-4')
                    f_new  = ui.input('Nova Senha', password=True,
                                      password_toggle_button=True) \
                        .classes('w-full').props('outlined dense dark color=blue-4')
                    f_conf = ui.input('Confirmar Nova Senha', password=True,
                                      password_toggle_button=True) \
                        .classes('w-full').props('outlined dense dark color=blue-4')

                    strength_lbl = ui.label('').classes('text-sm')
                    f_new.on('input', lambda: _check_strength(f_new.value, strength_lbl))

                    pwd_err = ui.label('').classes('text-red-400 text-sm')

                    ui.button('Alterar Senha', icon='lock',
                              on_click=lambda: change_password()) \
                        .props('color=blue-6 no-caps')

            # Notificações
            with data_card('Notificações'):
                with ui.column().classes('gap-3'):
                    prefs = ud['preferences']
                    for label, key in [
                        ('Notificações de login',  'notif_login'),
                        ('Alertas de erro',        'notif_error'),
                        ('Resumo diário',          'notif_daily'),
                    ]:
                        cb = ui.checkbox(label, value=prefs.get(key, True)) \
                            .classes('text-sm text-[#c9d1d9]')
                        cb.on('update:model-value',
                              lambda v, k=key, c=cb: save_pref(k, c.value))

        # ── Coluna direita ────────────────────────────────────────────────
        with ui.column().classes('w-80 gap-6'):

            with data_card('Resumo da Conta'):
                for label, val in [
                    ('Usuário',    ud['username']),
                    ('E-mail',     ud['email'] or '—'),
                    ('Status',     '✅ Ativo' if ud['is_active'] else '❌ Inativo'),
                    ('Criado em',  ud['created_at']),
                ]:
                    with ui.row().classes(
                        'items-center justify-between py-1 border-b border-[#30363d] last:border-0'
                    ):
                        ui.label(label).classes('text-[#8b949e] text-sm')
                        ui.label(val).classes('text-white text-sm')

                ui.separator().classes('bg-[#30363d] my-2')
                ui.button('Ver Meu Perfil', icon='person',
                          on_click=lambda: ui.navigate.to('/profile')) \
                    .props('flat no-caps color=blue-4').classes('w-full')

            with data_card('Sessão Atual'):
                token = nicegui_app.storage.user.get('token', '')
                if token:
                    ui.label(f'Token: ...{token[-12:]}') \
                        .classes('text-[#8b949e] text-xs font-mono mb-2')
                ui.button('Encerrar Sessão', icon='logout',
                          on_click=lambda: do_logout()) \
                    .props('flat no-caps color=red-4').classes('w-full')

    # ── Funções ───────────────────────────────────────────────────────────
    def apply_theme(key):
        """Aplica o tema via ui.dark_mode (API oficial NiceGUI) e persiste no DB."""
        if key == 'dark':
            dark_mode.enable()
        else:
            dark_mode.disable()
        session = db_manager.get_session()
        try:
            u = session.query(User).filter(User.id == user_id).first()
            if u:
                u.theme = key; session.commit()
            ud['theme'] = key
            ui.notify(f'Tema "{key}" aplicado!', type='positive')
        except Exception as e:
            session.rollback(); ui.notify(f'Erro: {e}', type='negative')
        finally:
            session.close()

    def save_language():
        session = db_manager.get_session()
        try:
            u = session.query(User).filter(User.id == user_id).first()
            if u:
                u.language = lang_sel.value; session.commit()
            ui.notify('Idioma salvo!', type='positive')
        except Exception as e:
            session.rollback(); ui.notify(f'Erro: {e}', type='negative')
        finally:
            session.close()

    def change_password():
        pwd_err.set_text('')
        if not f_cur.value:
            pwd_err.set_text('Informe a senha atual.'); return
        if not f_new.value:
            pwd_err.set_text('Informe a nova senha.'); return
        if len(f_new.value) < 6:
            pwd_err.set_text('Mínimo 6 caracteres.'); return
        if f_new.value != f_conf.value:
            pwd_err.set_text('As senhas não coincidem.'); return
        session = db_manager.get_session()
        try:
            u = session.query(User).filter(User.id == user_id).first()
            if not u.verify_password(f_cur.value):
                pwd_err.set_text('Senha atual incorreta.'); return
            u.set_password(f_new.value)
            u.updated_at = datetime.now()
            session.commit()
            ui.notify('Senha alterada!', type='positive')
            f_cur.set_value(''); f_new.set_value(''); f_conf.set_value('')
            strength_lbl.set_text('')
        except Exception as e:
            session.rollback(); pwd_err.set_text(f'Erro: {e}')
        finally:
            session.close()

    def save_pref(key, val):
        session = db_manager.get_session()
        try:
            u = session.query(User).filter(User.id == user_id).first()
            if u:
                prefs = dict(u.preferences or {})
                prefs[key] = val; u.preferences = prefs; session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

    def do_logout():
        from ui.app import logout_user
        logout_user()
        ui.navigate.to('/login')


def _check_strength(pwd, label):
    if not pwd:
        label.set_text(''); return
    score = sum([
        len(pwd) >= 8,
        any(c.isupper() for c in pwd),
        any(c.islower() for c in pwd),
        any(c.isdigit() for c in pwd),
        any(c in '!@#$%^&*()_+-=' for c in pwd),
    ])
    texts  = ['', '⚠ Muito fraca', '⚠ Fraca', '✓ Razoável', '✓ Boa', '✓✓ Forte']
    colors = ['', 'text-red-500',  'text-orange-400', 'text-yellow-400',
              'text-blue-400', 'text-green-400']
    label.set_text(texts[score])
    label.classes(colors[score],
                  remove='text-red-500 text-orange-400 text-yellow-400 text-blue-400 text-green-400')
