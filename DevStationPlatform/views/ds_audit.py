"""
DS_AUDIT - Console de Auditoria
Sprint 2 - Rastreabilidade Total
Perfil mínimo: ADMIN
"""

import flet as ft
from datetime import datetime
from core.audit_logger import audit_logger


# ── Paleta ──────────────────────────────────────
CLR_BG = ft.Colors.GREY_50
CLR_CARD = ft.Colors.WHITE
CLR_PRIMARY = ft.Colors.BLUE_700
CLR_SUCCESS = ft.Colors.GREEN_600
CLR_ERROR = ft.Colors.RED_600
CLR_WARN = ft.Colors.ORANGE_600
CLR_TEXT = ft.Colors.GREY_900
CLR_SUB = ft.Colors.GREY_600
CLR_BORDER = ft.Colors.GREY_200


# ── Helpers ──────────────────────────────────────

def _badge(text: str, color: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(text, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
        bgcolor=color,
        border_radius=4,
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
    )


def _action_color(action: str) -> str:
    return {
        "CREATE": CLR_SUCCESS,
        "UPDATE": CLR_WARN,
        "DELETE": CLR_ERROR,
        "READ":   ft.Colors.BLUE_400,
        "EXECUTE": ft.Colors.PURPLE_400,
        "EXPORT": ft.Colors.TEAL_500,
        "LOGIN":  ft.Colors.GREEN_400,
        "LOGOUT": CLR_SUB,
    }.get(action, ft.Colors.GREY_500)


def _fmt_ts(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return iso or "—"


# ── View ─────────────────────────────────────────

class AuditView:
    """
    Tela DS_AUDIT — listagem filtrável de logs de auditoria.
    """

    def __init__(self, page: ft.Page, user_data: dict):
        self.page = page
        self.user = user_data
        self._all_rows: list = []
        self._filter_action = "TODOS"
        self._filter_success = "TODOS"
        self._search_text = ""

        # Referências de UI
        self._table_rows: list = []
        self._lv: ft.ListView | None = None
        self._stats_row: ft.Row | None = None
        self._action_dd: ft.Dropdown | None = None
        self._success_dd: ft.Dropdown | None = None
        self._search_tf: ft.TextField | None = None

    # ── Build ─────────────────────────────────────

    def build(self) -> ft.Container:
        self._all_rows = audit_logger.get_recent_audit(200)
        stats = audit_logger.get_audit_stats()

        # ── Estatísticas ──
        self._stats_row = ft.Row(
            [
                self._stat_card("Total de Ações", str(stats["total_actions"]), ft.Icons.RECEIPT_LONG, CLR_PRIMARY),
                self._stat_card("Erros", str(stats["total_errors"]), ft.Icons.ERROR_OUTLINE, CLR_ERROR),
                self._stat_card("Modificações", str(stats["total_changes"]), ft.Icons.EDIT_NOTE, CLR_WARN),
                self._stat_card("Taxa de Sucesso", f"{stats['success_rate']}%", ft.Icons.CHECK_CIRCLE_OUTLINE, CLR_SUCCESS),
            ],
            spacing=12,
        )

        # ── Filtros ──
        self._search_tf = ft.TextField(
            label="Buscar usuário / transação / objeto…",
            prefix_icon=ft.Icons.SEARCH,
            width=320,
            height=44,
            on_change=self._on_filter_change,
            border_color=CLR_BORDER,
            focused_border_color=CLR_PRIMARY,
        )

        self._action_dd = ft.Dropdown(
            label="Ação",
            width=160,
            value="TODOS",
            options=[
                ft.dropdown.Option("TODOS"),
                ft.dropdown.Option("CREATE"),
                ft.dropdown.Option("READ"),
                ft.dropdown.Option("UPDATE"),
                ft.dropdown.Option("DELETE"),
                ft.dropdown.Option("EXECUTE"),
                ft.dropdown.Option("EXPORT"),
                ft.dropdown.Option("LOGIN"),
                ft.dropdown.Option("LOGOUT"),
            ],
            on_change=self._on_filter_change,
        )

        self._success_dd = ft.Dropdown(
            label="Status",
            width=140,
            value="TODOS",
            options=[
                ft.dropdown.Option("TODOS"),
                ft.dropdown.Option("Sucesso"),
                ft.dropdown.Option("Erro"),
            ],
            on_change=self._on_filter_change,
        )

        refresh_btn = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Recarregar",
            icon_color=CLR_PRIMARY,
            on_click=self._on_refresh,
        )

        filter_row = ft.Row(
            [self._search_tf, self._action_dd, self._success_dd, refresh_btn],
            spacing=10,
            wrap=True,
        )

        # ── Cabeçalho da tabela ──
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Text("Data/Hora",     size=12, weight=ft.FontWeight.BOLD, color=CLR_SUB, width=140),
                    ft.Text("Usuário",       size=12, weight=ft.FontWeight.BOLD, color=CLR_SUB, width=130),
                    ft.Text("Transação",     size=12, weight=ft.FontWeight.BOLD, color=CLR_SUB, width=130),
                    ft.Text("Ação",         size=12, weight=ft.FontWeight.BOLD, color=CLR_SUB, width=90),
                    ft.Text("Objeto",        size=12, weight=ft.FontWeight.BOLD, color=CLR_SUB, expand=True),
                    ft.Text("Duração",       size=12, weight=ft.FontWeight.BOLD, color=CLR_SUB, width=80),
                    ft.Text("Status",        size=12, weight=ft.FontWeight.BOLD, color=CLR_SUB, width=70),
                ],
                spacing=0,
            ),
            bgcolor=ft.Colors.GREY_100,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border_radius=ft.border_radius.only(top_left=8, top_right=8),
        )

        # ── ListView ──
        self._lv = ft.ListView(spacing=0, expand=True)
        self._rebuild_list()

        table_card = ft.Container(
            content=ft.Column([header, self._lv], spacing=0, expand=True),
            border=ft.border.all(1, CLR_BORDER),
            border_radius=8,
            expand=True,
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("DS_AUDIT — Console de Auditoria", size=20, weight=ft.FontWeight.BOLD, color=CLR_TEXT),
                    ft.Text("Rastreabilidade completa de todas as ações do sistema.", size=13, color=CLR_SUB),
                    ft.Divider(height=1, color=CLR_BORDER),
                    self._stats_row,
                    ft.Container(height=4),
                    filter_row,
                    ft.Container(height=4),
                    table_card,
                ],
                spacing=12,
                expand=True,
            ),
            padding=24,
            bgcolor=CLR_BG,
            expand=True,
        )

    # ── Stat card ─────────────────────────────────

    def _stat_card(self, label: str, value: str, icon, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, color=ft.Colors.WHITE, size=22),
                        bgcolor=color,
                        border_radius=8,
                        padding=10,
                        width=46,
                        height=46,
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=CLR_TEXT),
                            ft.Text(label, size=11, color=CLR_SUB),
                        ],
                        spacing=2,
                        tight=True,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=CLR_CARD,
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=18, vertical=14),
            border=ft.border.all(1, CLR_BORDER),
            expand=True,
        )

    # ── List item ──────────────────────────────────

    def _build_row(self, row: dict) -> ft.Container:
        success = row.get("success", True)
        status_icon = ft.Icon(
            ft.Icons.CHECK_CIRCLE if success else ft.Icons.CANCEL,
            color=CLR_SUCCESS if success else CLR_ERROR,
            size=16,
        )
        duration = row.get("execution_time_ms") or 0
        dur_color = CLR_SUCCESS if duration < 300 else (CLR_WARN if duration < 1000 else CLR_ERROR)

        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(_fmt_ts(row.get("timestamp", "")), size=12, color=CLR_TEXT, width=140),
                    ft.Text(row.get("user_name", "—"), size=12, color=CLR_TEXT, width=130, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(row.get("transaction_code", "—"), size=12, color=CLR_PRIMARY, width=130, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Row(
                        [_badge(row.get("action_type", "—"), _action_color(row.get("action_type", "")))],
                        width=90,
                    ),
                    ft.Text(
                        row.get("object_name") or row.get("object_type", "—"),
                        size=12,
                        color=CLR_TEXT,
                        expand=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(f"{duration}ms", size=12, color=dur_color, width=80),
                    ft.Container(content=status_icon, width=70),
                ],
                spacing=0,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border=ft.border.only(bottom=ft.border.BorderSide(1, CLR_BORDER)),
            bgcolor=CLR_CARD,
            on_hover=lambda e: self._on_row_hover(e),
        )

    def _on_row_hover(self, e: ft.ControlEvent):
        e.control.bgcolor = ft.Colors.BLUE_50 if e.data == "true" else CLR_CARD
        e.control.update()

    # ── Filtragem ─────────────────────────────────

    def _filtered_rows(self) -> list:
        rows = self._all_rows
        if self._filter_action != "TODOS":
            rows = [r for r in rows if r.get("action_type") == self._filter_action]
        if self._filter_success == "Sucesso":
            rows = [r for r in rows if r.get("success", True)]
        elif self._filter_success == "Erro":
            rows = [r for r in rows if not r.get("success", True)]
        if self._search_text:
            q = self._search_text.lower()
            rows = [
                r for r in rows
                if q in (r.get("user_name") or "").lower()
                or q in (r.get("transaction_code") or "").lower()
                or q in (r.get("object_name") or "").lower()
            ]
        return rows

    def _rebuild_list(self):
        filtered = self._filtered_rows()
        self._lv.controls.clear()
        if not filtered:
            self._lv.controls.append(
                ft.Container(
                    content=ft.Text("Nenhum registro encontrado.", color=CLR_SUB, size=13),
                    padding=30,
                    alignment=ft.alignment.center,
                )
            )
        else:
            for row in filtered:
                self._lv.controls.append(self._build_row(row))

    def _on_filter_change(self, e: ft.ControlEvent):
        self._filter_action = self._action_dd.value or "TODOS"
        self._filter_success = self._success_dd.value or "TODOS"
        self._search_text = self._search_tf.value or ""
        self._rebuild_list()
        self._lv.update()

    def _on_refresh(self, e):
        self._all_rows = audit_logger.get_recent_audit(200)
        stats = audit_logger.get_audit_stats()
        # Atualiza stat cards
        cards = self._stats_row.controls
        cards[0].content.controls[1].controls[0].value = str(stats["total_actions"])
        cards[1].content.controls[1].controls[0].value = str(stats["total_errors"])
        cards[2].content.controls[1].controls[0].value = str(stats["total_changes"])
        cards[3].content.controls[1].controls[0].value = f"{stats['success_rate']}%"
        self._stats_row.update()
        self._rebuild_list()
        self._lv.update()
