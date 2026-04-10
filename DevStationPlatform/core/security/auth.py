"""
Authentication module — Login, Logout, Session management
Flet 0.84 · Dark/Light theme
"""

import flet as ft
from core.security.rbac import rbac


class AuthScreen:
    """Tela de login com suporte a dark/light e API Flet 0.84."""

    def __init__(self, page: ft.Page, on_login_success):
        self.page = page
        self.on_login_success = on_login_success
        self.username_field = None
        self.password_field = None
        self.error_text = None
        self._loading = False

    # ── Tokens de cor (responde ao theme_mode da page) ──────────
    @property
    def _dark(self) -> bool:
        return self.page.theme_mode == ft.ThemeMode.DARK

    @property
    def _bg(self): return ft.Colors.GREY_900 if self._dark else ft.Colors.GREY_100
    @property
    def _card(self): return ft.Colors.GREY_800 if self._dark else ft.Colors.WHITE
    @property
    def _text(self): return ft.Colors.GREY_50 if self._dark else ft.Colors.GREY_900
    @property
    def _sub(self): return ft.Colors.GREY_400 if self._dark else ft.Colors.GREY_600
    @property
    def _border(self): return ft.Colors.GREY_700 if self._dark else ft.Colors.GREY_300
    @property
    def _primary(self): return ft.Colors.BLUE_300 if self._dark else ft.Colors.BLUE_700

    # ── Build ────────────────────────────────────────────────────

    def build(self) -> ft.Container:
        self.username_field = ft.TextField(
            label="Usuário",
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            width=320,
            autofocus=True,
            border_color=self._border,
            focused_border_color=self._primary,
            color=self._text,
            label_style=ft.TextStyle(color=self._sub),
            cursor_color=self._primary,
            on_submit=self.do_login,
        )

        self.password_field = ft.TextField(
            label="Senha",
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            width=320,
            password=True,
            can_reveal_password=True,
            border_color=self._border,
            focused_border_color=self._primary,
            color=self._text,
            label_style=ft.TextStyle(color=self._sub),
            cursor_color=self._primary,
            on_submit=self.do_login,
        )

        self.error_text = ft.Text("", color=ft.Colors.RED_400, size=12)

        login_btn = ft.Container(
            content=ft.FilledButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.LOGIN, color=ft.Colors.WHITE, size=18),
                        ft.Text("Entrar", color=ft.Colors.WHITE, size=15, weight=ft.FontWeight.W_600),
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                    tight=True,
                ),
                bgcolor=self._primary,
                on_click=self.do_login,
                width=320,
            ),
            width=320,
        )

        # Dica de credenciais (só em dev/debug)
        hint = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Credenciais de demonstração:", size=11, color=self._sub,
                            weight=ft.FontWeight.W_500),
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text("admin / admin123", size=11,
                                                color=self._text, font_family="monospace"),
                                bgcolor=ft.Colors.GREY_200 if not self._dark else ft.Colors.GREY_700,
                                border_radius=4,
                                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                            ),
                            ft.Container(
                                content=ft.Text("developer / dev123", size=11,
                                                color=self._text, font_family="monospace"),
                                bgcolor=ft.Colors.GREY_200 if not self._dark else ft.Colors.GREY_700,
                                border_radius=4,
                                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                            ),
                        ],
                        spacing=8, wrap=True,
                    ),
                ],
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.BLUE_50 if not self._dark else ft.Colors.BLUE_900,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            width=320,
            border=ft.Border.all(1, ft.Colors.BLUE_100 if not self._dark else ft.Colors.BLUE_800),
        )

        # Botão de toggle do tema
        theme_icon = ft.Icons.DARK_MODE if not self._dark else ft.Icons.LIGHT_MODE
        theme_btn = ft.IconButton(
            icon=theme_icon,
            icon_color=self._sub,
            tooltip="Alternar tema",
            on_click=self._toggle_theme,
        )

        # Card principal
        login_card = ft.Container(
            content=ft.Column(
                [
                    # Logo
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=ft.Text("DS", size=28, weight=ft.FontWeight.BOLD,
                                                    color=ft.Colors.WHITE),
                                    bgcolor=self._primary,
                                    border_radius=14,
                                    width=56, height=56,
                                    alignment=ft.Alignment(0, 0),
                                ),
                                ft.Text("DevStation Platform", size=22, weight=ft.FontWeight.BOLD,
                                        color=self._text),
                                ft.Text("Plataforma RAD Inspirada em SAP",
                                        size=13, color=self._sub),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        padding=ft.Padding.only(bottom=8),
                    ),
                    ft.Divider(height=1, color=self._border),
                    ft.Container(height=4),
                    self.username_field,
                    self.password_field,
                    self.error_text,
                    login_btn,
                    ft.Container(height=4),
                    hint,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
                tight=True,
            ),
            padding=36,
            bgcolor=self._card,
            border_radius=16,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=24,
                color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            width=420,
        )

        return ft.Container(
            content=ft.Stack(
                [
                    # Fundo
                    ft.Container(expand=True, bgcolor=self._bg),
                    # Card centralizado
                    ft.Container(
                        content=login_card,
                        expand=True,
                        alignment=ft.Alignment(0, 0),
                    ),
                    # Botão de tema no canto superior direito
                    ft.Container(
                        content=theme_btn,
                        top=12, right=12,
                    ),
                    # Versão no rodapé
                    ft.Container(
                        content=ft.Text(
                            "DevStationPlatform v1.0 · Sprint 3",
                            size=11, color=self._sub,
                        ),
                        bottom=16,
                        alignment=ft.Alignment(0, 0),
                        width=1280,
                    ),
                ],
                expand=True,
            ),
            expand=True,
        )

    # ── Handlers ─────────────────────────────────

    def do_login(self, e):
        if self._loading:
            return
        username = self.username_field.value or ""
        password = self.password_field.value or ""

        if not username or not password:
            self.error_text.value = "Preencha usuário e senha!"
            self.page.update()
            return

        self._loading = True
        self.error_text.value = ""
        self.page.update()

        result = rbac.authenticate(username, password)

        self._loading = False
        if result:
            self.error_text.value = ""
            self.page.data = {
                "auth_token": result["token"],
                "user": result["user"],
            }
            self.on_login_success(result["user"])
        else:
            self.error_text.value = "❌  Usuário ou senha inválidos."
            self.page.update()

    def _toggle_theme(self, e):
        self.page.theme_mode = (
            ft.ThemeMode.DARK
            if self.page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        self.page.clean()
        self.page.add(self.build())
        self.page.update()


# ─────────────────────────────────────────────────────────────

def logout(page: ft.Page):
    if page.data and "auth_token" in page.data:
        rbac.logout(page.data["auth_token"])
    page.data = None
    page.clean()
    login_screen = AuthScreen(page, lambda user: _rebuild_app(page, user))
    page.add(login_screen.build())
    page.update()


def _rebuild_app(page: ft.Page, user_data):
    page.clean()
    from main import build_main_app
    build_main_app(page, user_data)


def get_current_user(page: ft.Page):
    try:
        if page.data and "auth_token" in page.data:
            return rbac.validate_token(page.data["auth_token"])
    except Exception:
        pass
    return None
