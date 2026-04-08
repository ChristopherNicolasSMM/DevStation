"""
Authentication module - Login, Logout, Session management
"""

import flet as ft
from core.security.rbac import rbac


class AuthScreen:
    """Tela de login"""
    
    def __init__(self, page: ft.Page, on_login_success):
        self.page = page
        self.on_login_success = on_login_success
        self.username_field = None
        self.password_field = None
        self.error_text = None
    
    def build(self):
        """Constroi a tela de login"""
        self.username_field = ft.TextField(
            label="Usuário",
            width=300,
            autofocus=True
        )
        
        self.password_field = ft.TextField(
            label="Senha",
            width=300,
            password=True,
            can_reveal_password=True,
            on_submit=self.do_login
        )
        
        self.error_text = ft.Text("", color=ft.Colors.RED, size=12)
        
        login_button = ft.ElevatedButton(
            content=ft.Text("Entrar"),
            width=300,
            on_click=self.do_login
        )
        
        # Logo ou título
        title = ft.Text(
            "DevStationPlatform",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700
        )
        
        subtitle = ft.Text(
            "Plataforma RAD Inspirada em SAP",
            size=16,
            color=ft.Colors.GREY_600
        )
        
        # Card de login
        login_card = ft.Container(
            content=ft.Column(
                [
                    title,
                    subtitle,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.username_field,
                    self.password_field,
                    self.error_text,
                    login_button,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            ),
            padding=40,
            bgcolor=ft.Colors.WHITE,
            border_radius=20,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.GREY_300,
            ),
            width=400,
        )
        
        # Container centralizado
        return ft.Container(
            content=login_card,
            expand=True,
            bgcolor=ft.Colors.GREY_50,
        )
    
    def do_login(self, e):
        """Executa o login"""
        username = self.username_field.value
        password = self.password_field.value
        
        if not username or not password:
            self.error_text.value = "Preencha usuário e senha!"
            self.page.update()
            return
        
        # Autenticar
        result = rbac.authenticate(username, password)
        
        if result:
            # Login bem sucedido - usando page.data
            self.error_text.value = ""
            self.page.data = {
                "auth_token": result["token"],
                "user": result["user"]
            }
            self.on_login_success(result["user"])
        else:
            self.error_text.value = "Usuário ou senha inválidos!"
            self.page.update()


def logout(page: ft.Page):
    """Função de logout"""
    if page.data and "auth_token" in page.data:
        rbac.logout(page.data["auth_token"])
    
    page.data = None
    page.clean()
    
    # Mostrar tela de login
    login_screen = AuthScreen(page, lambda user: rebuild_app(page, user))
    page.add(login_screen.build())
    page.update()


def rebuild_app(page: ft.Page, user_data):
    """Reconstroi a aplicação após login"""
    page.clean()
    from main import build_main_app
    build_main_app(page, user_data)


def get_current_user(page: ft.Page):
    """Obtém o usuário atual da sessão"""
    try:
        if page.data and "auth_token" in page.data:
            token = page.data["auth_token"]
            return rbac.validate_token(token)
    except:
        pass
    return None