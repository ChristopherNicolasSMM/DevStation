"""
Tela de login - DevStationPlatform
Estilo dark theme conforme HTML de referência
"""

from nicegui import ui
from ui.app import AuthService, login_user


def render():
    """Renderizar tela de login"""

    def do_login():
        """Processar login"""
        user = username.value.strip()
        pwd = password.value.strip()

        if not user or not pwd:
            error_message.set_text('Preencha usuário e senha!')
            return

        login_button.props('loading')
        error_message.set_text('')

        try:
            user_data = AuthService.authenticate(user, pwd)
            if user_data:
                login_user(user_data, user_data.get('token'))
                ui.navigate.to('/dashboard')
            else:
                error_message.set_text('❌ Usuário ou senha inválidos.')
        except Exception as e:
            error_message.set_text(f'❌ Erro: {str(e)}')
        finally:
            login_button.props(remove='loading')

    # Layout da tela de login — todos os elementos criados DENTRO do contexto correto
    with ui.column().classes('w-full h-screen items-center justify-center bg-gradient-to-br from-[#0e1117] to-[#161b22] p-4'):
        # Card de login centralizado
        with ui.card().classes('w-full max-w-md bg-[#161b22]/90 backdrop-blur-sm border border-[#30363d] rounded-2xl shadow-2xl p-8'):

            # Logo
            with ui.column().classes('items-center mb-10'):
                with ui.row().classes('items-center gap-4 mb-3'):
                    with ui.card().classes('w-16 h-16 bg-gradient-to-br from-[#58a6ff] to-[#1f6feb] rounded-2xl items-center justify-center shadow-lg'):
                        ui.label('DS').classes('text-white text-3xl font-bold')
                    ui.label('DevStation Platform').classes('text-white text-2xl font-bold tracking-tight')
                ui.label('Plataforma RAD Inspirada em SAP').classes('text-[#8b949e] text-sm font-medium')

            ui.separator().classes('bg-[#30363d] mb-6 opacity-50')

            # Formulário — inputs criados aqui dentro para renderizar no lugar certo
            with ui.column().classes('gap-6 w-full'):

                # Campo de usuário
                with ui.column().classes('gap-2 w-full'):
                    ui.label('Usuário').classes('text-[#c9d1d9] text-sm font-semibold uppercase tracking-wider')
                    username = ui.input(placeholder='Digite seu usuário') \
                        .classes('w-full') \
                        .props('outlined dense color=blue-4 bg-color=grey-10 dark autocomplete=username')
                    username.on('keydown.enter', do_login)

                # Campo de senha
                with ui.column().classes('gap-2 w-full'):
                    ui.label('Senha').classes('text-[#c9d1d9] text-sm font-semibold uppercase tracking-wider')
                    password = ui.input(placeholder='Digite sua senha', password=True, password_toggle_button=True) \
                        .classes('w-full') \
                        .props('outlined dense color=blue-4 bg-color=grey-10 dark autocomplete=current-password')
                    password.on('keydown.enter', do_login)

                # Mensagem de erro
                error_message = ui.label('').classes('text-red-400 text-sm text-center min-h-[20px]')

                # Botão de login
                login_button = ui.button('Entrar', on_click=do_login, icon='login') \
                    .classes('w-full text-white font-semibold rounded-lg text-base shadow-lg') \
                    .props('color=blue-6 no-caps')

            # Credenciais de demonstração
            with ui.card().classes('w-full mt-8 bg-[#0d1117]/80 border border-[#30363d] rounded-xl p-5'):
                with ui.column().classes('gap-3'):
                    ui.label('Credenciais de demonstração:').classes('text-[#8b949e] text-xs font-semibold uppercase tracking-wider')
                    ui.label('admin / admin123').classes('bg-[#161b22] text-white text-sm font-mono px-4 py-3 rounded-lg w-full text-center border border-[#30363d]')
                    ui.label('developer / dev123').classes('bg-[#161b22] text-white text-sm font-mono px-4 py-3 rounded-lg w-full text-center border border-[#30363d]')

        # Rodapé
        ui.label('DevStationPlatform v1.0 · Sprint 3').classes('mt-8 text-[#8b949e] text-xs font-medium')
