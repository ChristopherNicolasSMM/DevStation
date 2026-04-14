"""
DS_Controls — Botões, campos e linhas de tabela padronizados.

from views.components.controls import (
    DSButton, DSField, DSTableRow, DSSearchBar, DSFilterRow, DSDetailPanel
)
"""

import flet as ft
from core.theme import Theme
from views.components.style import Size


# ── DSButton ─────────────────────────────────────────────────

class DSButton:
    """Botões padronizados da plataforma."""

    @staticmethod
    def primary(label: str, icon=None, on_click=None, t: Theme = None) -> ft.FilledButton:
        color = t.primary if t else ft.Colors.BLUE_700
        controls = []
        if icon:
            controls.append(ft.Icon(icon, color=ft.Colors.WHITE, size=Size.ICON_SM))
        controls.append(ft.Text(label, color=ft.Colors.WHITE, size=Size.TEXT_MD))
        return ft.FilledButton(
            content=ft.Row(controls, spacing=6, tight=True),
            bgcolor=color,
            on_click=on_click,
        )

    @staticmethod
    def secondary(label: str, icon=None, on_click=None, t: Theme = None) -> ft.OutlinedButton:
        color = t.primary if t else ft.Colors.BLUE_700
        controls = []
        if icon:
            controls.append(ft.Icon(icon, color=color, size=Size.ICON_SM))
        controls.append(ft.Text(label, color=color, size=Size.TEXT_MD))
        return ft.OutlinedButton(
            content=ft.Row(controls, spacing=6, tight=True),
            on_click=on_click,
        )

    @staticmethod
    def danger(label: str, icon=None, on_click=None) -> ft.FilledButton:
        controls = []
        if icon:
            controls.append(ft.Icon(icon, color=ft.Colors.WHITE, size=Size.ICON_SM))
        controls.append(ft.Text(label, color=ft.Colors.WHITE, size=Size.TEXT_MD))
        return ft.FilledButton(
            content=ft.Row(controls, spacing=6, tight=True),
            bgcolor=ft.Colors.RED_600,
            on_click=on_click,
        )

    @staticmethod
    def icon(icon, tooltip: str = "", on_click=None, color: str = None, t: Theme = None) -> ft.IconButton:
        ic = color or (t.primary if t else ft.Colors.BLUE_700)
        return ft.IconButton(icon=icon, icon_color=ic, tooltip=tooltip, on_click=on_click)


# ── DSField ──────────────────────────────────────────────────

class DSField:
    """Campos de formulário padronizados."""

    @staticmethod
    def text(
        label: str,
        value: str = "",
        hint: str = "",
        icon=None,
        width: int = None,
        on_change=None,
        on_submit=None,
        password: bool = False,
        t: Theme = None,
    ) -> ft.TextField:
        kw = {}
        if width: kw["width"] = width
        if icon:  kw["prefix_icon"] = icon
        return ft.TextField(
            label=label,
            value=value,
            hint_text=hint,
            password=password,
            can_reveal_password=password,
            dense=True,
            border_color=t.border if t else ft.Colors.GREY_300,
            focused_border_color=t.primary if t else ft.Colors.BLUE_700,
            color=t.text if t else ft.Colors.GREY_900,
            label_style=ft.TextStyle(color=t.subtext if t else ft.Colors.GREY_600),
            cursor_color=t.primary if t else ft.Colors.BLUE_700,
            on_change=on_change,
            on_submit=on_submit,
            **kw,
        )

    @staticmethod
    def search(
        label: str = "Buscar…",
        width: int = 300,
        on_change=None,
        t: Theme = None,
    ) -> ft.TextField:
        return DSField.text(
            label=label,
            icon=ft.Icons.SEARCH,
            width=width,
            on_change=on_change,
            t=t,
        )

    @staticmethod
    def dropdown(
        label: str,
        options: list,
        value: str = None,
        width: int = 160,
        on_change=None,
        t: Theme = None,
    ) -> ft.Dropdown:
        return ft.Dropdown(
            label=label,
            value=value or options[0],
            options=[ft.dropdown.Option(o) for o in options],
            width=width,
            on_change=on_change,
            color=t.text if t else ft.Colors.GREY_900,
        )


# ── DSTableRow ───────────────────────────────────────────────

class DSTableRow:
    """Linha de tabela com hover e suporte a click."""

    @staticmethod
    def make(
        cells: list,     # list of ft.Control
        t: Theme,
        on_click=None,
        on_hover_extra=None,
    ) -> ft.Container:
        def on_hover(e):
            e.control.bgcolor = t.hover if e.data == "true" else t.card
            e.control.update()
            if on_hover_extra:
                on_hover_extra(e)

        return ft.Container(
            content=ft.Row(cells, spacing=0),
            padding=ft.Padding.symmetric(horizontal=Size.PAD_MD, vertical=10),
            border=ft.Border.only(bottom=ft.BorderSide(1, t.border)),
            bgcolor=t.card,
            on_click=on_click,
            on_hover=on_hover,
        )

    @staticmethod
    def cell_text(
        value: str,
        width: int = None,
        color: str = None,
        weight=None,
        t: Theme = None,
    ) -> ft.Text:
        kw = {}
        if width is not None: kw["width"] = width
        else: kw["expand"] = True
        return ft.Text(
            str(value) if value is not None else "—",
            size=Size.TEXT_BASE,
            color=color or (t.text if t else ft.Colors.GREY_900),
            weight=weight,
            overflow=ft.TextOverflow.ELLIPSIS,
            **kw,
        )


# ── DSDetailPanel ────────────────────────────────────────────

class DSDetailPanel:
    """Painel de detalhe que aparece ao selecionar uma linha."""

    @staticmethod
    def make(t: Theme, height: int = 120) -> ft.Container:
        return ft.Container(
            content=ft.Text(
                "Clique em uma linha para ver detalhes.",
                color=t.subtext, size=Size.TEXT_MD,
            ),
            bgcolor=t.card,
            border=ft.Border.all(1, t.border),
            border_radius=Size.RADIUS_MD,
            padding=Size.PAD_MD,
            height=height,
        )

    @staticmethod
    def update(panel: ft.Container, content: ft.Control):
        panel.content = content
        panel.update()


# ── DSFilterRow ──────────────────────────────────────────────

class DSFilterRow:
    """Linha de filtros padronizada (search + dropdowns + refresh)."""

    @staticmethod
    def make(
        controls: list,
        on_refresh=None,
        t: Theme = None,
    ) -> ft.Row:
        all_controls = list(controls)
        if on_refresh:
            all_controls.append(
                DSButton.icon(ft.Icons.REFRESH, "Recarregar", on_refresh, t=t)
            )
        return ft.Row(all_controls, spacing=10, wrap=True)
