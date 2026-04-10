"""
DS_AUDIT — Console de Auditoria
Sprint 2 · Flet 0.84
Perfil mínimo: ADMIN
"""

import flet as ft
from datetime import datetime
from typing import Optional
from core.audit_logger import audit_logger
from core.theme import Theme


def _fmt_ts(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return iso or "—"


def _action_color(action: str, t: Theme) -> str:
    return {
        "CREATE":  ft.Colors.GREEN_600,
        "UPDATE":  ft.Colors.ORANGE_600,
        "DELETE":  ft.Colors.RED_600,
        "READ":    ft.Colors.BLUE_400,
        "EXECUTE": ft.Colors.PURPLE_400,
        "EXPORT":  ft.Colors.TEAL_500,
        "LOGIN":   ft.Colors.GREEN_500,
        "LOGOUT":  t.subtext,
    }.get(action, ft.Colors.GREY_500)


class AuditView:
    def __init__(self, page: ft.Page, user_data: dict):
        self.page = page
        self.user = user_data
        self.t = Theme.of(page)
        self._all_rows: list = []
        self._filter_action = "TODOS"
        self._filter_success = "TODOS"
        self._search_text = ""
        self._lv: Optional[ft.ListView] = None
        self._stats_values: list = []   # [Text refs]
        self._action_dd: Optional[ft.Dropdown] = None
        self._success_dd: Optional[ft.Dropdown] = None
        self._search_tf: Optional[ft.TextField] = None

    # ─── Build ────────────────────────────────────

    def build(self) -> ft.Container:
        t = self.t
        self._all_rows = audit_logger.get_recent_audit(300)
        stats = audit_logger.get_audit_stats()

        # ── Stat cards ──
        def stat_card(label, value, icon, color):
            val_text = ft.Text(str(value), size=22, weight=ft.FontWeight.BOLD, color=t.text)
            self._stats_values.append(val_text)
            return ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(icon, color=ft.Colors.WHITE, size=22),
                            bgcolor=color,
                            border_radius=8,
                            width=44, height=44,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column(
                            [val_text, ft.Text(label, size=11, color=t.subtext)],
                            spacing=2, tight=True,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=t.card,
                border=ft.Border.all(1, t.border),
                border_radius=10,
                padding=ft.Padding.symmetric(horizontal=18, vertical=14),
                expand=True,
            )

        stats_row = ft.Row(
            [
                stat_card("Total de Ações",  stats["total_actions"],  ft.Icons.RECEIPT_LONG,       t.primary),
                stat_card("Erros",            stats["total_errors"],   ft.Icons.ERROR_OUTLINE,       t.error),
                stat_card("Modificações",     stats["total_changes"],  ft.Icons.EDIT_NOTE,           t.warning),
                stat_card("Taxa de Sucesso",  f"{stats['success_rate']}%", ft.Icons.CHECK_CIRCLE_OUTLINE, t.success),
            ],
            spacing=12,
        )

        # ── Filtros ──
        self._search_tf = ft.TextField(
            label="Buscar usuário / transação / objeto…",
            prefix_icon=ft.Icons.SEARCH,
            width=320,
            dense=True,
            on_change=self._on_filter,
            border_color=t.border,
            focused_border_color=t.primary,
            color=t.text,
            label_style=ft.TextStyle(color=t.subtext),
        )

        self._action_dd = ft.Dropdown(
            label="Ação",
            width=160,
            value="TODOS",
            options=[ft.dropdown.Option(o) for o in
                     ["TODOS","CREATE","READ","UPDATE","DELETE","EXECUTE","EXPORT","LOGIN","LOGOUT"]],
            on_change=self._on_filter,
            color=t.text,
        )

        self._success_dd = ft.Dropdown(
            label="Status",
            width=140,
            value="TODOS",
            options=[ft.dropdown.Option(o) for o in ["TODOS","Sucesso","Erro"]],
            on_change=self._on_filter,
            color=t.text,
        )

        refresh_btn = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_color=t.primary,
            tooltip="Recarregar",
            on_click=self._on_refresh,
        )

        # ── Cabeçalho da tabela ──
        col_header = ft.Container(
            content=ft.Row(
                [
                    ft.Text("Data/Hora",   size=11, weight=ft.FontWeight.BOLD, color=t.subtext, width=140),
                    ft.Text("Usuário",     size=11, weight=ft.FontWeight.BOLD, color=t.subtext, width=130),
                    ft.Text("Transação",   size=11, weight=ft.FontWeight.BOLD, color=t.subtext, width=130),
                    ft.Text("Ação",        size=11, weight=ft.FontWeight.BOLD, color=t.subtext, width=90),
                    ft.Text("Objeto",      size=11, weight=ft.FontWeight.BOLD, color=t.subtext, expand=True),
                    ft.Text("Duração",     size=11, weight=ft.FontWeight.BOLD, color=t.subtext, width=80),
                    ft.Text("Status",      size=11, weight=ft.FontWeight.BOLD, color=t.subtext, width=60),
                ],
                spacing=0,
            ),
            bgcolor=ft.Colors.GREY_100 if not t.is_dark else ft.Colors.GREY_800,
            padding=ft.Padding.symmetric(horizontal=16, vertical=9),
            border_radius=ft.BorderRadius.only(top_left=8, top_right=8),
        )

        self._lv = ft.ListView(spacing=0, expand=True)
        self._rebuild_list()

        table = ft.Container(
            content=ft.Column([col_header, self._lv], spacing=0, expand=True),
            border=ft.Border.all(1, t.border),
            border_radius=8,
            expand=True,
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            t.section_header("DS_AUDIT — Console de Auditoria",
                                             "Rastreabilidade completa de todas as ações do sistema."),
                            refresh_btn,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    t.divider(),
                    stats_row,
                    ft.Row(
                        [self._search_tf, self._action_dd, self._success_dd],
                        spacing=10, wrap=True,
                    ),
                    table,
                ],
                spacing=14,
                expand=True,
            ),
            padding=24,
            bgcolor=t.bg,
            expand=True,
        )

    # ─── Row ─────────────────────────────────────

    def _build_row(self, row: dict) -> ft.Container:
        t = self.t
        success = row.get("success", True)
        duration = row.get("execution_time_ms") or 0
        dur_color = t.success if duration < 300 else (t.warning if duration < 1000 else t.error)

        status_icon = ft.Icon(
            ft.Icons.CHECK_CIRCLE if success else ft.Icons.CANCEL,
            color=t.success if success else t.error,
            size=16,
        )

        action = row.get("action_type", "—")
        action_badge = ft.Container(
            content=ft.Text(action, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=_action_color(action, t),
            border_radius=4,
            padding=ft.Padding.symmetric(horizontal=7, vertical=3),
        )

        def on_hover(e):
            e.control.bgcolor = t.hover if e.data == "true" else t.card
            e.control.update()

        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(_fmt_ts(row.get("timestamp", "")), size=12, color=t.text, width=140),
                    ft.Text(row.get("user_name", "—"),         size=12, color=t.text, width=130,
                            overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(row.get("transaction_code", "—"),  size=12, color=t.primary, width=130,
                            overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Row([action_badge], width=90),
                    ft.Text(
                        row.get("object_name") or row.get("object_type", "—"),
                        size=12, color=t.text, expand=True, overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(f"{duration}ms", size=12, color=dur_color, width=80),
                    ft.Container(content=status_icon, width=60),
                ],
                spacing=0,
            ),
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            border=ft.Border.only(bottom=ft.BorderSide(1, t.border)),
            bgcolor=t.card,
            on_hover=on_hover,
        )

    # ─── Filter ──────────────────────────────────

    def _filtered(self) -> list:
        rows = self._all_rows
        if self._filter_action != "TODOS":
            rows = [r for r in rows if r.get("action_type") == self._filter_action]
        if self._filter_success == "Sucesso":
            rows = [r for r in rows if r.get("success", True)]
        elif self._filter_success == "Erro":
            rows = [r for r in rows if not r.get("success", True)]
        if self._search_text:
            q = self._search_text.lower()
            rows = [r for r in rows if
                    q in (r.get("user_name") or "").lower()
                    or q in (r.get("transaction_code") or "").lower()
                    or q in (r.get("object_name") or "").lower()]
        return rows

    def _rebuild_list(self):
        t = self.t
        filtered = self._filtered()
        self._lv.controls.clear()
        if not filtered:
            self._lv.controls.append(
                ft.Container(
                    content=ft.Text("Nenhum registro encontrado.", color=t.subtext, size=13),
                    padding=30, alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for row in filtered:
                self._lv.controls.append(self._build_row(row))

    def _on_filter(self, e):
        self._filter_action = self._action_dd.value or "TODOS"
        self._filter_success = self._success_dd.value or "TODOS"
        self._search_text = self._search_tf.value or ""
        self._rebuild_list()
        self._lv.update()

    def _on_refresh(self, e):
        self._all_rows = audit_logger.get_recent_audit(300)
        stats = audit_logger.get_audit_stats()
        vals = [
            str(stats["total_actions"]),
            str(stats["total_errors"]),
            str(stats["total_changes"]),
            f"{stats['success_rate']}%",
        ]
        for i, v in enumerate(vals):
            if i < len(self._stats_values):
                self._stats_values[i].value = v
                self._stats_values[i].update()
        self._rebuild_list()
        self._lv.update()
