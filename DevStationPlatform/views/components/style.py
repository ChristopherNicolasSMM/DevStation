"""
DS_Style — Tokens de estilo herdáveis para todos os componentes.
Importar apenas este módulo garante consistência visual.

Uso:
    from views.components.style import DSStyle, action_color, kpi_color
"""

import flet as ft
from core.theme import Theme


# ── Tamanhos fixos ────────────────────────────────────────────
class Size:
    TEXT_XS   = 10
    TEXT_SM   = 11
    TEXT_BASE = 12
    TEXT_MD   = 13
    TEXT_LG   = 14
    TEXT_XL   = 16
    TEXT_2XL  = 20
    TEXT_3XL  = 24
    TEXT_HERO = 32

    ICON_SM   = 16
    ICON_MD   = 20
    ICON_LG   = 24

    RADIUS_SM = 4
    RADIUS_MD = 8
    RADIUS_LG = 12
    RADIUS_XL = 16

    PAD_XS  = 4
    PAD_SM  = 8
    PAD_MD  = 14
    PAD_LG  = 20
    PAD_XL  = 24
    PAD_2XL = 32

    AVATAR = 34
    BADGE_H = 22


# ── Paleta semântica (independente de tema) ───────────────────
class Semantic:
    SUCCESS  = ft.Colors.GREEN_600
    ERROR    = ft.Colors.RED_600
    WARNING  = ft.Colors.ORANGE_600
    INFO     = ft.Colors.BLUE_400
    PURPLE   = ft.Colors.PURPLE_400
    TEAL     = ft.Colors.TEAL_500
    INDIGO   = ft.Colors.INDIGO_400

    # Ações SAP-style
    ACTION_CREATE  = ft.Colors.GREEN_600
    ACTION_UPDATE  = ft.Colors.ORANGE_600
    ACTION_DELETE  = ft.Colors.RED_600
    ACTION_READ    = ft.Colors.BLUE_400
    ACTION_EXECUTE = ft.Colors.PURPLE_400
    ACTION_EXPORT  = ft.Colors.TEAL_500
    ACTION_LOGIN   = ft.Colors.GREEN_500
    ACTION_LOGOUT  = ft.Colors.GREY_500

    # KPI impact
    KPI_POSITIVE = ft.Colors.GREEN_600
    KPI_NEGATIVE = ft.Colors.RED_600
    KPI_NEUTRAL  = ft.Colors.GREY_500

    # Perfis
    PROFILE_ADMIN    = ft.Colors.RED_700
    PROFILE_DEV_ALL  = ft.Colors.PURPLE_700
    PROFILE_CORE_DEV = ft.Colors.INDIGO_700
    PROFILE_DEV      = ft.Colors.BLUE_700
    PROFILE_BANALYST = ft.Colors.TEAL_700
    PROFILE_PUSER    = ft.Colors.GREEN_700
    PROFILE_USER     = ft.Colors.GREY_600

    # Transações
    TX_STANDARD = ft.Colors.BLUE_700
    TX_CUSTOM   = ft.Colors.PURPLE_600


# ── Helpers de cor ────────────────────────────────────────────

def action_color(action: str) -> str:
    return getattr(Semantic, f"ACTION_{action.upper()}", ft.Colors.GREY_500)


def profile_color(profile: str) -> str:
    return getattr(Semantic, f"PROFILE_{profile.upper()}", ft.Colors.GREY_500)


def kpi_impact_color(impact: str) -> str:
    return getattr(Semantic, f"KPI_{impact.upper()}", Semantic.KPI_NEUTRAL)


def response_color(ms: float, t: Theme) -> str:
    if ms < 200:  return t.success
    if ms < 1000: return t.warning
    return t.error


def score_color(score: int, t: Theme) -> str:
    if score >= 80: return t.success
    if score >= 50: return t.warning
    return t.error


# ── DSStyle: fábrica de containers/containers com tema ────────

class DSStyle:
    """
    Classe base que encapsula o tema e fornece
    construtores de layout padronizados.

    Herdar desta classe em qualquer View ou Component:
        class MyView(DSStyle):
            def __init__(self, page, user_data):
                super().__init__(page)
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.t = Theme.of(page)

    # ── Layout helpers ────────────────────────────────────────

    def page_container(self, content) -> ft.Container:
        """Container raiz de uma tela."""
        return ft.Container(
            content=content,
            padding=Size.PAD_XL,
            bgcolor=self.t.bg,
            expand=True,
        )

    def card(self, content, padding: int = Size.PAD_LG, **kw) -> ft.Container:
        """Card padrão com borda e fundo."""
        return ft.Container(
            content=content,
            bgcolor=self.t.card,
            border=ft.Border.all(1, self.t.border),
            border_radius=Size.RADIUS_LG,
            padding=padding,
            **kw,
        )

    def section(self, title: str, subtitle: str = "", actions: list = None) -> ft.Row:
        """Cabeçalho de seção com título + ações opcionais."""
        left = ft.Column(
            [
                ft.Text(title,    size=Size.TEXT_2XL, weight=ft.FontWeight.BOLD, color=self.t.text),
                *(
                    [ft.Text(subtitle, size=Size.TEXT_MD, color=self.t.subtext)]
                    if subtitle else []
                ),
            ],
            spacing=2, tight=True, expand=True,
        )
        row_controls = [left]
        if actions:
            row_controls += actions
        return ft.Row(
            row_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def divider(self) -> ft.Divider:
        return ft.Divider(height=1, color=self.t.border)

    def col_header(self, cols: list) -> ft.Container:
        """Cabeçalho de tabela com lista de (label, width|expand)."""
        controls = []
        for item in cols:
            label, width = item if len(item) == 2 else (item[0], None)
            kw = {"expand": True} if width is None else {"width": width}
            controls.append(
                ft.Text(label, size=Size.TEXT_XS, weight=ft.FontWeight.BOLD,
                        color=self.t.subtext, **kw)
            )
        return ft.Container(
            content=ft.Row(controls, spacing=0),
            bgcolor=ft.Colors.GREY_100 if not self.t.is_dark else ft.Colors.GREY_800,
            padding=ft.Padding.symmetric(horizontal=Size.PAD_MD, vertical=9),
            border_radius=ft.BorderRadius.only(top_left=Size.RADIUS_MD, top_right=Size.RADIUS_MD),
        )

    def table_card(self, header: ft.Container, lv: ft.ListView) -> ft.Container:
        return ft.Container(
            content=ft.Column([header, lv], spacing=0, expand=True),
            border=ft.Border.all(1, self.t.border),
            border_radius=Size.RADIUS_MD,
            expand=True,
        )

    def empty_state(self, message: str, icon=ft.Icons.INBOX) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=40, color=self.t.subtext),
                    ft.Text(message, color=self.t.subtext, size=Size.TEXT_MD),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=40,
            alignment=ft.Alignment(0, 0),
        )
