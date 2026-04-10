"""
Theme Manager — dark/light com tokens de design para Flet 0.84
"""
import flet as ft
from typing import Optional


class Theme:
    """
    Token de cores que se adapta ao modo do tema da Page.
    Uso: t = Theme(page)  →  t.bg, t.card, t.primary …
    """

    def __init__(self, page: Optional[ft.Page] = None, dark: bool = False):
        self._dark = dark
        if page is not None:
            self._dark = page.theme_mode == ft.ThemeMode.DARK

    # ── Factory helpers ──────────────────────────
    @classmethod
    def of(cls, page: ft.Page) -> "Theme":
        return cls(page=page)

    @classmethod
    def dark(cls) -> "Theme":
        return cls(dark=True)

    @classmethod
    def light(cls) -> "Theme":
        return cls(dark=False)

    # ── Tokens ───────────────────────────────────
    @property
    def is_dark(self) -> bool:
        return self._dark

    @property
    def bg(self) -> str:
        return ft.Colors.GREY_900 if self._dark else ft.Colors.GREY_50

    @property
    def surface(self) -> str:
        return ft.Colors.GREY_800 if self._dark else ft.Colors.WHITE

    @property
    def card(self) -> str:
        return ft.Colors.GREY_800 if self._dark else ft.Colors.WHITE

    @property
    def border(self) -> str:
        return ft.Colors.GREY_700 if self._dark else ft.Colors.GREY_200

    @property
    def divider(self) -> str:
        return ft.Colors.GREY_700 if self._dark else ft.Colors.GREY_200

    @property
    def text(self) -> str:
        return ft.Colors.GREY_50 if self._dark else ft.Colors.GREY_900

    @property
    def subtext(self) -> str:
        return ft.Colors.GREY_400 if self._dark else ft.Colors.GREY_600

    @property
    def primary(self) -> str:
        return ft.Colors.BLUE_300 if self._dark else ft.Colors.BLUE_700

    @property
    def primary_dark(self) -> str:
        return ft.Colors.BLUE_800 if self._dark else ft.Colors.BLUE_900

    @property
    def hover(self) -> str:
        return ft.Colors.BLUE_900 if self._dark else ft.Colors.BLUE_50

    @property
    def success(self) -> str:
        return ft.Colors.GREEN_400 if self._dark else ft.Colors.GREEN_600

    @property
    def error(self) -> str:
        return ft.Colors.RED_400 if self._dark else ft.Colors.RED_600

    @property
    def warning(self) -> str:
        return ft.Colors.ORANGE_400 if self._dark else ft.Colors.ORANGE_600

    @property
    def sidebar_bg(self) -> str:
        return ft.Colors.GREY_900 if self._dark else ft.Colors.BLUE_900

    @property
    def sidebar_active(self) -> str:
        return ft.Colors.BLUE_700 if self._dark else ft.Colors.BLUE_800

    @property
    def sidebar_text(self) -> str:
        return ft.Colors.GREY_100

    @property
    def sidebar_subtext(self) -> str:
        return ft.Colors.BLUE_200 if not self._dark else ft.Colors.GREY_500

    @property
    def sidebar_divider(self) -> str:
        return ft.Colors.BLUE_800 if not self._dark else ft.Colors.GREY_700

    @property
    def sidebar_hover(self) -> str:
        return ft.Colors.BLUE_800 if not self._dark else ft.Colors.GREY_800

    # ── Helpers de construção ─────────────────────
    def card_container(self, content, **kwargs) -> ft.Container:
        """Container com estilo de card."""
        return ft.Container(
            content=content,
            bgcolor=self.card,
            border=ft.Border.all(1, self.border),
            border_radius=10,
            **kwargs,
        )

    def section_header(self, title: str, subtitle: str = "") -> ft.Column:
        controls = [ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=self.text)]
        if subtitle:
            controls.append(ft.Text(subtitle, size=13, color=self.subtext))
        return ft.Column(controls, spacing=2)

    def divider(self) -> ft.Divider:
        return ft.Divider(height=1, color=self.border)

    def badge(self, text: str, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Text(text, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=color,
            border_radius=4,
            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
        )
