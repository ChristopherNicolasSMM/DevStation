"""
DS_CHG — ChangeLog Viewer
Sprint 2 · Flet 0.84
Perfil mínimo: DEVELOPER
"""

import flet as ft
from datetime import datetime
from typing import Optional
from core.audit_logger import audit_logger
from core.models.base import db_manager
from core.models.audit import ChangeLog
from core.theme import Theme


def _fmt_ts(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return iso or "—"


def _change_color(change_type: str) -> str:
    return {
        "CREATE": ft.Colors.GREEN_600,
        "MODIFY": ft.Colors.ORANGE_600,
        "DELETE": ft.Colors.RED_600,
        "RENAME": ft.Colors.BLUE_500,
        "MOVE":   ft.Colors.PURPLE_400,
    }.get(change_type, ft.Colors.GREY_500)


def _kpi_color(impact: str) -> str:
    return {
        "POSITIVE": ft.Colors.GREEN_600,
        "NEGATIVE": ft.Colors.RED_600,
        "NEUTRAL":  ft.Colors.GREY_500,
    }.get(impact, ft.Colors.GREY_500)


class ChangeLogView:
    def __init__(self, page: ft.Page, user_data: dict):
        self.page = page
        self.user = user_data
        self.t = Theme.of(page)
        self._all_rows: list = []
        self._filter_type = "TODOS"
        self._search_text = ""
        self._lv: Optional[ft.ListView] = None
        self._type_dd: Optional[ft.Dropdown] = None
        self._search_tf: Optional[ft.TextField] = None
        self._detail_panel: Optional[ft.Container] = None

    def build(self) -> ft.Container:
        t = self.t
        self._all_rows = self._load_changes()

        self._search_tf = ft.TextField(
            label="Buscar autor / código / ticket…",
            prefix_icon=ft.Icons.SEARCH,
            width=300, dense=True,
            on_change=self._on_filter,
            border_color=t.border,
            focused_border_color=t.primary,
            color=t.text,
            label_style=ft.TextStyle(color=t.subtext),
        )

        self._type_dd = ft.Dropdown(
            label="Tipo",
            width=170,
            value="TODOS",
            options=[ft.dropdown.Option(o) for o in
                     ["TODOS","CREATE","MODIFY","DELETE","RENAME","MOVE"]],
            on_change=self._on_filter,
            color=t.text,
        )

        new_btn = ft.FilledButton(
            content=ft.Row([ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=18),
                            ft.Text("Registrar Mudança", color=ft.Colors.WHITE)],
                           spacing=6, tight=True),
            bgcolor=t.primary,
            on_click=self._show_new_dialog,
        )

        col_header = ft.Container(
            content=ft.Row(
                [
                    ft.Text("ID",       size=11, weight=ft.FontWeight.BOLD, color=t.subtext, width=130),
                    ft.Text("Data",     size=11, weight=ft.FontWeight.BOLD, color=t.subtext, width=130),
                    ft.Text("Autor",    size=11, weight=ft.FontWeight.BOLD, color=t.subtext, width=130),
                    ft.Text("Tipo",     size=11, weight=ft.FontWeight.BOLD, color=t.subtext, width=90),
                    ft.Text("Objeto",   size=11, weight=ft.FontWeight.BOLD, color=t.subtext, width=120),
                    ft.Text("Resumo",   size=11, weight=ft.FontWeight.BOLD, color=t.subtext, expand=True),
                    ft.Text("Versão",   size=11, weight=ft.FontWeight.BOLD, color=t.subtext, width=80),
                    ft.Text("Impacto",  size=11, weight=ft.FontWeight.BOLD, color=t.subtext, width=80),
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

        self._detail_panel = ft.Container(
            content=ft.Text("Clique em uma linha para ver detalhes.", color=t.subtext, size=13),
            bgcolor=t.card,
            border=ft.Border.all(1, t.border),
            border_radius=8,
            padding=16,
            height=120,
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            t.section_header("DS_CHG — ChangeLog Viewer",
                                             "Histórico de modificações estruturais do sistema."),
                            new_btn,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    t.divider(),
                    ft.Row([self._search_tf, self._type_dd], spacing=10),
                    table,
                    self._detail_panel,
                ],
                spacing=14,
                expand=True,
            ),
            padding=24,
            bgcolor=t.bg,
            expand=True,
        )

    # ─── Data ─────────────────────────────────────

    def _load_changes(self) -> list:
        try:
            session = db_manager.get_session()
            rows = session.query(ChangeLog).order_by(ChangeLog.timestamp.desc()).limit(200).all()
            result = [r.to_dict() for r in rows]
            session.close()
            return result
        except Exception:
            return []

    # ─── Row ──────────────────────────────────────

    def _build_row(self, row: dict) -> ft.Container:
        t = self.t
        chg_type = row.get("change_type", "—")
        impact = row.get("kpi_impact", "NEUTRAL")

        badge = lambda text, color: ft.Container(
            content=ft.Text(text, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=color, border_radius=4,
            padding=ft.Padding.symmetric(horizontal=7, vertical=3),
        )

        def on_hover(e):
            e.control.bgcolor = t.hover if e.data == "true" else t.card
            e.control.update()

        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(row.get("change_id", "—"),     size=12, color=t.primary,  width=130, weight=ft.FontWeight.W_500),
                    ft.Text(_fmt_ts(row.get("timestamp","")),size=12,color=t.text,    width=130),
                    ft.Text(row.get("author_name","—"),    size=12, color=t.text,     width=130, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Row([badge(chg_type, _change_color(chg_type))],               width=90),
                    ft.Text(row.get("object_type","—"),    size=12, color=t.text,     width=120),
                    ft.Text(row.get("change_summary","—"), size=12, color=t.text,     expand=True, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(row.get("version_after") or "—", size=12, color=t.subtext, width=80),
                    ft.Row([badge(impact, _kpi_color(impact))],                      width=80),
                ],
                spacing=0,
            ),
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            border=ft.Border.only(bottom=ft.BorderSide(1, t.border)),
            bgcolor=t.card,
            on_click=lambda e, r=row: self._show_detail(r),
            on_hover=on_hover,
        )

    def _show_detail(self, row: dict):
        t = self.t
        ticket  = row.get("ticket_id")  or "—"
        branch  = row.get("branch_name") or "—"
        git     = row.get("git_commit_hash") or "—"
        desc    = row.get("change_description") or "Sem descrição detalhada."
        self._detail_panel.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(row.get("change_id", ""), weight=ft.FontWeight.BOLD, color=t.text),
                        ft.Text(f"Ticket: {ticket}", size=12, color=t.primary),
                        ft.Text(f"Branch: {branch}", size=12, color=t.subtext),
                        ft.Text(f"Git: {git[:8]}…" if len(git) > 8 else f"Git: {git}", size=12, color=t.subtext),
                    ],
                    spacing=16, wrap=True,
                ),
                ft.Text(desc, size=13, color=t.text),
            ],
            spacing=6,
        )
        self._detail_panel.update()

    # ─── Filter ──────────────────────────────────

    def _filtered(self) -> list:
        rows = self._all_rows
        if self._filter_type != "TODOS":
            rows = [r for r in rows if r.get("change_type") == self._filter_type]
        if self._search_text:
            q = self._search_text.lower()
            rows = [r for r in rows if
                    q in (r.get("author_name") or "").lower()
                    or q in (r.get("object_code") or "").lower()
                    or q in (r.get("ticket_id") or "").lower()
                    or q in (r.get("change_summary") or "").lower()]
        return rows

    def _rebuild_list(self):
        t = self.t
        filtered = self._filtered()
        self._lv.controls.clear()
        if not filtered:
            self._lv.controls.append(
                ft.Container(
                    content=ft.Text("Nenhuma modificação registrada.", color=t.subtext, size=13),
                    padding=30, alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for r in filtered:
                self._lv.controls.append(self._build_row(r))

    def _on_filter(self, e):
        self._filter_type  = self._type_dd.value or "TODOS"
        self._search_text  = self._search_tf.value or ""
        self._rebuild_list()
        self._lv.update()

    # ─── Dialog ──────────────────────────────────

    def _show_new_dialog(self, e):
        t = self.t
        summary_tf = ft.TextField(label="Resumo", width=420, color=t.text)
        code_tf    = ft.TextField(label="Código do objeto", width=200, color=t.text)
        type_dd    = ft.Dropdown(
            label="Tipo", width=150, value="MODIFY",
            options=[ft.dropdown.Option(x) for x in ["CREATE","MODIFY","DELETE","RENAME","MOVE"]],
            color=t.text,
        )
        ticket_tf  = ft.TextField(label="Ticket", width=150, color=t.text)

        def save(e):
            chg_id = audit_logger.log_change(
                author_id=self.user.get("id", 0),
                author_name=self.user.get("username", "?"),
                author_profile=", ".join(self.user.get("profiles", [])),
                object_type="MANUAL",
                object_code=code_tf.value or "",
                change_type=type_dd.value or "MODIFY",
                change_summary=summary_tf.value or "Sem descrição",
                ticket_id=ticket_tf.value or "",
                version_after="manual",
                kpi_impact="NEUTRAL",
            )
            dlg.open = False
            self.page.update()
            self._all_rows = self._load_changes()
            self._rebuild_list()
            self._lv.update()
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✅ {chg_id} registrado!"), open=True
            )
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Registrar Mudança Manual", color=t.text),
            content=ft.Column(
                [summary_tf, ft.Row([code_tf, type_dd], spacing=10), ticket_tf],
                spacing=12, tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar",
                    on_click=lambda e: (setattr(dlg, "open", False), self.page.update())),
                ft.FilledButton(
                    content=ft.Text("Salvar", color=ft.Colors.WHITE),
                    bgcolor=t.primary,
                    on_click=save,
                ),
            ],
            bgcolor=t.card,
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
