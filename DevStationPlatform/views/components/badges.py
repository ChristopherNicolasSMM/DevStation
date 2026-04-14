"""
DS_Badges — Componentes de badge, avatar e status reutilizáveis.

from views.components.badges import Badge, Avatar, StatusDot, ProfileChip
"""

import flet as ft
from views.components.style import Size, Semantic, action_color, profile_color


# ── Badge ─────────────────────────────────────────────────────

class Badge:
    """Badge colorido de texto."""

    @staticmethod
    def make(text: str, color: str, size: int = Size.TEXT_XS) -> ft.Container:
        return ft.Container(
            content=ft.Text(
                text, size=size, color=ft.Colors.WHITE,
                weight=ft.FontWeight.W_500,
            ),
            bgcolor=color,
            border_radius=Size.RADIUS_SM,
            padding=ft.Padding.symmetric(horizontal=Size.PAD_SM, vertical=3),
        )

    @staticmethod
    def action(action: str) -> ft.Container:
        return Badge.make(action, action_color(action))

    @staticmethod
    def profile(profile: str) -> ft.Container:
        return Badge.make(profile, profile_color(profile))

    @staticmethod
    def success(text: str = "OK") -> ft.Container:
        return Badge.make(text, Semantic.SUCCESS)

    @staticmethod
    def error(text: str = "ERRO") -> ft.Container:
        return Badge.make(text, Semantic.ERROR)

    @staticmethod
    def warning(text: str = "AVISO") -> ft.Container:
        return Badge.make(text, Semantic.WARNING)

    @staticmethod
    def tx_standard(code: str) -> ft.Container:
        return Badge.make(code, Semantic.TX_STANDARD, size=Size.TEXT_SM)

    @staticmethod
    def tx_custom(code: str) -> ft.Container:
        return Badge.make(code, Semantic.TX_CUSTOM, size=Size.TEXT_SM)


# ── Status dot ────────────────────────────────────────────────

class StatusDot:
    """Ponto colorido de status com label opcional."""

    @staticmethod
    def make(active: bool, label: str = "", size: int = 10) -> ft.Row:
        dot = ft.Container(
            width=size, height=size,
            bgcolor=Semantic.SUCCESS if active else ft.Colors.GREY_400,
            border_radius=size,
        )
        if not label:
            return ft.Row([dot], spacing=0)
        return ft.Row(
            [dot, ft.Text(label, size=Size.TEXT_XS, color=ft.Colors.GREY_600)],
            spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    @staticmethod
    def online()  -> ft.Row: return StatusDot.make(True,  "Online")
    @staticmethod
    def offline() -> ft.Row: return StatusDot.make(False, "Offline")


# ── Success / error icon ──────────────────────────────────────

class StatusIcon:
    @staticmethod
    def make(success: bool, size: int = Size.ICON_SM) -> ft.Icon:
        return ft.Icon(
            ft.Icons.CHECK_CIRCLE if success else ft.Icons.CANCEL,
            color=Semantic.SUCCESS if success else Semantic.ERROR,
            size=size,
        )


# ── Avatar ────────────────────────────────────────────────────

class Avatar:
    """Círculo com inicial do nome."""

    @staticmethod
    def make(
        name: str,
        size: int = Size.AVATAR,
        bgcolor: str = ft.Colors.BLUE_500,
        text_color: str = ft.Colors.WHITE,
    ) -> ft.Container:
        letter = (name or "?")[0].upper()
        return ft.Container(
            content=ft.Text(
                letter, size=size // 2,
                color=text_color, weight=ft.FontWeight.BOLD,
            ),
            bgcolor=bgcolor,
            border_radius=size,
            width=size, height=size,
            alignment=ft.Alignment(0, 0),
        )


# ── ProfileChip ───────────────────────────────────────────────

class ProfileChip:
    """Chip de perfil com cor semântica."""

    @staticmethod
    def make(profile_code: str) -> ft.Container:
        color = profile_color(profile_code)
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=6, height=6,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=6,
                    ),
                    ft.Text(
                        profile_code, size=Size.TEXT_XS,
                        color=ft.Colors.WHITE, weight=ft.FontWeight.W_500,
                    ),
                ],
                spacing=5,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=color,
            border_radius=Size.RADIUS_SM,
            padding=ft.Padding.symmetric(horizontal=Size.PAD_SM, vertical=3),
        )

    @staticmethod
    def row(profiles: list) -> ft.Row:
        return ft.Row(
            [ProfileChip.make(p) for p in profiles],
            spacing=4, wrap=True,
        )
