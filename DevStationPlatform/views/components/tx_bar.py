"""
DS_TransactionBar — Barra de navegação por código de transação (estilo SAP).

O usuário digita o código (ex: DS_AUDIT) e pressiona Enter para navegar.
Mantém histórico das últimas N transações executadas.

from views.components.tx_bar import TransactionBar
"""

import flet as ft
from typing import Callable, Optional
from collections import deque
from core.transaction import registry, TransactionMetadata
from core.theme import Theme
from views.components.style import Size, Semantic


# Mapa de código → chave interna de view
_BUILTIN_MAP = {
    "DS_DASH":     "dashboard",
    "DS_AUDIT":    "audit",
    "DS_CHG":      "changelog",
    "DS_KPI_DASH": "kpi",
    "DS_USERS":    "users",
    "DS_QUERY":    "query",
    "DS_PLUGINS":  "plugins",
}

# Metadados das transações built-in (para autocomplete e tooltips)
_BUILTIN_META = {
    "DS_DASH":     ("Dashboard",            "dashboard"),
    "DS_AUDIT":    ("Console de Auditoria", "audit"),
    "DS_CHG":      ("ChangeLog Viewer",     "changelog"),
    "DS_KPI_DASH": ("Dashboard de KPIs",   "kpi"),
    "DS_USERS":    ("Gestão de Usuários",  "users"),
    "DS_QUERY":    ("Query Console",        "query"),
    "DS_PLUGINS":  ("Plugin Manager",       "plugins"),
}

HISTORY_MAX = 20


class TransactionBar:
    """
    Barra superior de transações SAP-style.

    - Campo de input para código de transação
    - Autocomplete com sugestões inline
    - Histórico das últimas execuções
    - Botão de histórico em dropdown
    - Badge com a transação atual
    """

    def __init__(
        self,
        page: ft.Page,
        user_data: dict,
        on_navigate: Callable[[str], None],   # callback(view_key)
        on_navigate_tx: Callable[[str], None] = None,  # callback(tx_code) para NDS_
    ):
        self.page = page
        self.user = user_data
        self.on_navigate = on_navigate
        self.on_navigate_tx = on_navigate_tx
        self.t = Theme.of(page)
        self._history: deque = deque(maxlen=HISTORY_MAX)
        self._current_code: str = "DS_DASH"

        # UI refs
        self._input: Optional[ft.TextField] = None
        self._current_label: Optional[ft.Text] = None
        self._current_badge: Optional[ft.Container] = None
        self._suggestions: Optional[ft.Column] = None
        self._suggestions_overlay: Optional[ft.Container] = None
        self._history_col: Optional[ft.Column] = None

    # ── Build ─────────────────────────────────────

    def build(self) -> ft.Container:
        t = self.t

        self._current_badge = ft.Container(
            content=ft.Text(
                self._current_code,
                size=Size.TEXT_SM,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.W_600,
                font_family="monospace",
            ),
            bgcolor=Semantic.TX_STANDARD,
            border_radius=Size.RADIUS_SM,
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        )

        self._current_label = ft.Text(
            _BUILTIN_META.get(self._current_code, ("—", ""))[0],
            size=Size.TEXT_BASE,
            color=t.subtext,
        )

        self._input = ft.TextField(
            hint_text="Transação… (ex: DS_AUDIT)",
            width=240,
            dense=True,
            height=36,
            border_color=ft.Colors.BLUE_800,
            focused_border_color=ft.Colors.BLUE_300,
            color=ft.Colors.WHITE,
            hint_style=ft.TextStyle(color=ft.Colors.BLUE_300),
            cursor_color=ft.Colors.BLUE_200,
            text_size=Size.TEXT_SM,
            on_change=self._on_input_change,
            on_submit=self._on_submit,
            capitalization=ft.TextCapitalization.CHARACTERS,
            bgcolor=ft.Colors.BLUE_800,
            border_radius=Size.RADIUS_SM,
        )

        execute_btn = ft.IconButton(
            icon=ft.Icons.PLAY_ARROW,
            icon_color=ft.Colors.BLUE_200,
            icon_size=18,
            tooltip="Executar transação (Enter)",
            on_click=lambda e: self._on_submit(e),
        )

        # Botão de histórico
        history_btn = ft.IconButton(
            icon=ft.Icons.HISTORY,
            icon_color=ft.Colors.BLUE_200,
            icon_size=18,
            tooltip="Histórico de transações",
            on_click=self._show_history_dialog,
        )

        # Sugestões inline (overlay)
        self._suggestions = ft.Column([], spacing=0, visible=False)
        self._suggestions_overlay = ft.Container(
            content=self._suggestions,
            bgcolor=ft.Colors.BLUE_900,
            border=ft.Border.all(1, ft.Colors.BLUE_700),
            border_radius=ft.BorderRadius.only(
                bottom_left=Size.RADIUS_MD,
                bottom_right=Size.RADIUS_MD,
            ),
            visible=False,
        )

        # Input + overlay em Stack
        input_stack = ft.Stack(
            [
                ft.Container(content=self._input),
                ft.Container(
                    content=self._suggestions_overlay,
                    top=36, left=0, width=240,
                ),
            ],
            width=240,
        )

        return ft.Container(
            content=ft.Row(
                [
                    # Transação atual
                    ft.Row(
                        [
                            self._current_badge,
                            self._current_label,
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.VerticalDivider(width=1, color=ft.Colors.BLUE_800),
                    # Input
                    input_stack,
                    execute_btn,
                    history_btn,
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.BLUE_950 if not t.is_dark else ft.Colors.GREY_900,
            padding=ft.Padding.symmetric(horizontal=Size.PAD_MD, vertical=6),
            border=ft.Border.only(bottom=ft.BorderSide(1, ft.Colors.BLUE_800)),
        )

    # ── Autocomplete ──────────────────────────────

    def _get_suggestions(self, text: str) -> list:
        """Retorna lista de (code, name) que coincidem com o texto."""
        q = text.upper().strip()
        if not q:
            return []
        results = []
        # Built-in
        for code, (name, _) in _BUILTIN_META.items():
            if q in code:
                results.append((code, name, "DS"))
        # Registry (NDS_ e DS_ registradas dinamicamente)
        for code, meta in registry.get_all_transactions().items():
            if code not in _BUILTIN_META and q in code:
                prefix = "DS" if meta.is_standard else "NDS"
                results.append((code, meta.name, prefix))
        return results[:6]

    def _on_input_change(self, e):
        text = (self._input.value or "").strip()
        suggestions = self._get_suggestions(text)

        self._suggestions.controls.clear()
        if suggestions and text:
            t = self.t
            for code, name, prefix in suggestions:
                color = Semantic.TX_STANDARD if prefix == "DS" else Semantic.TX_CUSTOM
                self._suggestions.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Text(code, size=Size.TEXT_XS,
                                                    color=ft.Colors.WHITE,
                                                    font_family="monospace"),
                                    bgcolor=color, border_radius=3,
                                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                ),
                                ft.Text(name, size=Size.TEXT_XS, color=ft.Colors.BLUE_100),
                            ],
                            spacing=8,
                        ),
                        padding=ft.Padding.symmetric(horizontal=10, vertical=7),
                        border=ft.Border.only(bottom=ft.BorderSide(1, ft.Colors.BLUE_800)),
                        on_click=lambda e, c=code: self._select_suggestion(c),
                        on_hover=lambda e: (
                            setattr(e.control, "bgcolor",
                                    ft.Colors.BLUE_800 if e.data == "true" else ft.Colors.TRANSPARENT),
                            e.control.update(),
                        ),
                    )
                )
            self._suggestions.visible = True
            self._suggestions_overlay.visible = True
        else:
            self._suggestions.visible = False
            self._suggestions_overlay.visible = False

        self._suggestions_overlay.update()

    def _select_suggestion(self, code: str):
        self._input.value = code
        self._input.update()
        self._suggestions.visible = False
        self._suggestions_overlay.visible = False
        self._suggestions_overlay.update()
        self._execute(code)

    # ── Execute ───────────────────────────────────

    def _on_submit(self, e=None):
        code = (self._input.value or "").strip().upper()
        if not code:
            return
        self._execute(code)

    def _execute(self, code: str):
        # Limpa input e sugestões
        self._input.value = ""
        self._suggestions.visible = False
        self._suggestions_overlay.visible = False
        self._input.update()
        self._suggestions_overlay.update()

        # Adiciona ao histórico
        self._history.appendleft(code)

        # Atualiza badge atual
        is_standard = not code.startswith("NDS_")
        badge_color = Semantic.TX_STANDARD if is_standard else Semantic.TX_CUSTOM
        self._current_code = code
        self._current_badge.content.value = code
        self._current_badge.bgcolor = badge_color
        self._current_badge.update()

        # Atualiza label
        meta_name = _BUILTIN_META.get(code, (None, ""))[0]
        if not meta_name:
            reg = registry.get_transaction(code)
            meta_name = reg.name if reg else code
        self._current_label.value = meta_name or code
        self._current_label.update()

        # Navega
        view_key = _BUILTIN_MAP.get(code)
        if view_key:
            self.on_navigate(view_key)
        elif code.startswith("NDS_") and self.on_navigate_tx:
            self.on_navigate_tx(code)
        else:
            # Tenta registry
            reg = registry.get_transaction(code)
            if reg:
                view_key = code.lower()
                self.on_navigate(view_key)
            else:
                self._show_not_found(code)

    def _show_not_found(self, code: str):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"❌  Transação '{code}' não encontrada."),
            bgcolor=ft.Colors.RED_800,
            open=True,
        )
        self.page.update()

    # ── Histórico dialog ──────────────────────────

    def _show_history_dialog(self, e):
        t = self.t
        if not self._history:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Histórico vazio."),
                open=True,
            )
            self.page.update()
            return

        def make_row(code: str):
            is_std = not code.startswith("NDS_")
            badge_color = Semantic.TX_STANDARD if is_std else Semantic.TX_CUSTOM
            name = _BUILTIN_META.get(code, (code, ""))[0]
            reg = registry.get_transaction(code)
            if reg and not name:
                name = reg.name

            def nav(e, c=code):
                dlg.open = False
                self.page.update()
                self._execute(c)

            return ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(code, size=Size.TEXT_XS, color=ft.Colors.WHITE,
                                            font_family="monospace"),
                            bgcolor=badge_color, border_radius=3,
                            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                        ),
                        ft.Text(name or "—", size=Size.TEXT_MD, color=t.text, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.PLAY_ARROW,
                            icon_color=t.primary,
                            icon_size=16,
                            tooltip="Executar",
                            on_click=nav,
                        ),
                    ],
                    spacing=10,
                ),
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                border=ft.Border.only(bottom=ft.BorderSide(1, t.border)),
                bgcolor=t.card,
            )

        dlg = ft.AlertDialog(
            title=ft.Text("Histórico de Transações", color=t.text),
            content=ft.Container(
                content=ft.Column(
                    [make_row(c) for c in self._history],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=420,
                height=320,
                bgcolor=t.card,
            ),
            actions=[
                ft.TextButton(
                    "Fechar",
                    on_click=lambda e: (setattr(dlg, "open", False), self.page.update()),
                ),
            ],
            bgcolor=t.card,
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    # ── API pública ───────────────────────────────

    def set_current(self, view_key: str):
        """Atualiza o badge de transação atual ao navegar pela sidebar."""
        code = next(
            (c for c, k in _BUILTIN_MAP.items() if k == view_key),
            view_key.upper(),
        )
        self._current_code = code
        is_std = not code.startswith("NDS_")
        self._current_badge.content.value = code
        self._current_badge.bgcolor = Semantic.TX_STANDARD if is_std else Semantic.TX_CUSTOM
        self._current_badge.update()

        name = _BUILTIN_META.get(code, (code, ""))[0]
        self._current_label.value = name
        self._current_label.update()

    def refresh_theme(self):
        self.t = Theme.of(self.page)
