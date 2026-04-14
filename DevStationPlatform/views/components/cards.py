"""
DS_Cards — Cards de métricas, KPI e info reutilizáveis.

from views.components.cards import StatCard, MetricCard, KpiScoreCard, InfoCard
"""

import flet as ft
from core.theme import Theme
from views.components.style import Size, score_color, response_color


# ── StatCard ─────────────────────────────────────────────────

class StatCard:
    """
    Card compacto: ícone + valor + label.
    Usado nas linhas de resumo de dashboards.
    """

    @staticmethod
    def make(
        label: str,
        value: str,
        icon,
        color: str,
        t: Theme,
        expand: bool = True,
    ) -> ft.Container:
        val_text = ft.Text(
            str(value), size=Size.TEXT_2XL,
            weight=ft.FontWeight.BOLD, color=t.text,
        )
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, color=ft.Colors.WHITE, size=Size.ICON_MD),
                        bgcolor=color,
                        border_radius=Size.RADIUS_MD,
                        width=44, height=44,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(
                        [
                            val_text,
                            ft.Text(label, size=Size.TEXT_XS, color=t.subtext),
                        ],
                        spacing=2, tight=True,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=t.card,
            border=ft.Border.all(1, t.border),
            border_radius=Size.RADIUS_LG,
            padding=ft.Padding.symmetric(horizontal=18, vertical=14),
            expand=expand,
        ), val_text   # retorna (container, text_ref) para permitir atualização


# ── MetricCard ───────────────────────────────────────────────

class MetricCard:
    """
    Card de métrica vertical: ícone + valor grande + label.
    Usado no DS_KPI_DASH.
    """

    @staticmethod
    def make(label: str, value: str, icon, color: str, t: Theme) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(icon, color=color, size=Size.ICON_MD),
                            ft.Text(label, size=Size.TEXT_XS, color=t.subtext),
                        ],
                        spacing=6,
                    ),
                    ft.Text(
                        str(value), size=Size.TEXT_3XL,
                        weight=ft.FontWeight.BOLD, color=t.text,
                    ),
                ],
                spacing=6, tight=True,
            ),
            bgcolor=t.card,
            border=ft.Border.all(1, t.border),
            border_radius=Size.RADIUS_LG,
            padding=ft.Padding.symmetric(horizontal=18, vertical=14),
            expand=True,
        )


# ── KpiScoreCard ─────────────────────────────────────────────

class KpiScoreCard:
    """Card circular de KPI Score com barra de progresso."""

    @staticmethod
    def make(score: int, t: Theme) -> ft.Container:
        color = score_color(score, t)
        score_text = ft.Text(
            str(score), size=52,
            weight=ft.FontWeight.BOLD, color=color,
        )
        score_bar = ft.ProgressBar(
            value=score / 100, color=color,
            bgcolor=ft.Colors.GREY_200 if not t.is_dark else ft.Colors.GREY_700,
            height=8, border_radius=4,
        )
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("KPI Score", size=Size.TEXT_SM, color=t.subtext,
                            weight=ft.FontWeight.W_500),
                    score_text,
                    ft.Text("/ 100", size=Size.TEXT_BASE, color=t.subtext),
                    score_bar,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
            bgcolor=t.card,
            border=ft.Border.all(1, t.border),
            border_radius=Size.RADIUS_XL,
            padding=ft.Padding.symmetric(horizontal=20, vertical=20),
            width=170,
            alignment=ft.Alignment(0, 0),
        ), score_text, score_bar   # (container, text_ref, bar_ref)


# ── InfoCard ─────────────────────────────────────────────────

class InfoCard:
    """Card genérico de título + lista de pares label/valor."""

    @staticmethod
    def make(
        title: str,
        rows: list,   # [(label, value, color?), ...]
        t: Theme,
        icon: str = None,
        expand: bool = True,
    ) -> ft.Container:
        header_controls = []
        if icon:
            header_controls.append(ft.Icon(icon, color=t.primary, size=Size.ICON_SM))
        header_controls.append(
            ft.Text(title, size=Size.TEXT_LG, weight=ft.FontWeight.BOLD, color=t.text)
        )

        row_widgets = []
        for item in rows:
            label = item[0]
            value = item[1]
            color = item[2] if len(item) > 2 else None
            row_widgets.append(
                ft.Row(
                    [
                        ft.Text(label, size=Size.TEXT_BASE, color=t.subtext, expand=True),
                        ft.Text(
                            str(value), size=Size.TEXT_MD,
                            weight=ft.FontWeight.BOLD,
                            color=color or t.text,
                        ),
                    ],
                    spacing=8,
                )
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(header_controls, spacing=8,
                           vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Divider(height=1, color=t.border),
                    *row_widgets,
                ],
                spacing=10,
            ),
            bgcolor=t.card,
            border=ft.Border.all(1, t.border),
            border_radius=Size.RADIUS_LG,
            padding=Size.PAD_LG,
            expand=expand,
        )
