"""
DS_CHG - ChangeLog Viewer
Sprint 2 - Rastreabilidade Total
Perfil mínimo: DEVELOPER
"""

import flet as ft
from datetime import datetime
from core.audit_logger import audit_logger
from core.models.base import db_manager
from core.models.audit import ChangeLog


CLR_BG = ft.Colors.GREY_50
CLR_CARD = ft.Colors.WHITE
CLR_PRIMARY = ft.Colors.BLUE_700
CLR_SUCCESS = ft.Colors.GREEN_600
CLR_ERROR = ft.Colors.RED_600
CLR_WARN = ft.Colors.ORANGE_600
CLR_TEXT = ft.Colors.GREY_900
CLR_SUB = ft.Colors.GREY_600
CLR_BORDER = ft.Colors.GREY_200


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
        "MOVE": ft.Colors.PURPLE_400,
    }.get(change_type, ft.Colors.GREY_500)


def _kpi_color(impact: str) -> str:
    return {
        "POSITIVE": ft.Colors.GREEN_600,
        "NEGATIVE": ft.Colors.RED_600,
        "NEUTRAL": ft.Colors.GREY_500,
    }.get(impact, ft.Colors.GREY_500)


def _badge(text: str, color: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(text, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
        bgcolor=color,
        border_radius=4,
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
    )


class ChangeLogView:
    """
    Tela DS_CHG — histórico de modificações do sistema.
    """

    def __init__(self, page: ft.Page, user_data: dict):
        self.page = page
        self.user = user_data
        self._all_rows: list = []
        self._filter_type = "TODOS"
        self._search_text = ""
        self._lv: ft.ListView | None = None
        self._type_dd: ft.Dropdown | None = None
        self._search_tf: ft.TextField | None = None
        self._selected_row: dict | None = None
        self._detail_panel: ft.Container | None = None

    def build(self) -> ft.Container:
        self._all_rows = self._load_changes()

        self._search_tf = ft.TextField(
            label="Buscar autor / código / ticket…",
            prefix_icon=ft.Icons.SEARCH,
            width=300,
            height=44,
            on_change=self._on_filter,
            border_color=CLR_BORDER,
            focused_border_color=CLR_PRIMARY,
        )

        self._type_dd = ft.Dropdown(
            label="Tipo de Mudança",
            width=180,
            value="TODOS",
            options=[
                ft.dropdown.Option("TODOS"),
                ft.dropdown.Option("CREATE"),
                ft.dropdown.Option("MODIFY"),
                ft.dropdown.Option("DELETE"),
                ft.dropdown.Option("RENAME"),
                ft.dropdown.Option("MOVE"),
            ],
            on_change=self._on_filter,
        )

        # botão de novo ChangeLog manual
        new_btn = ft.ElevatedButton(
            text="+ Registrar Mudança",
            icon=ft.Icons.ADD,
            bgcolor=CLR_PRIMARY,
            color=ft.Colors.WHITE,
            on_click=self._show_new_dialog,
        )

        header_row = ft.Container(
            content=ft.Row(
                [
                    ft.Text("ID",         size=12, weight=ft.FontWeight.BOLD, color=CLR_SUB, width=120),
                    ft.Text("Data",       size=12, weight=ft.FontWeight.BOLD, color=CLR_SUB, width=130),
                    ft.Text("Autor",      size=12, weight=ft.FontWeight.BOLD, color=CLR_SUB, width=130),
                    ft.Text("Tipo",       size=12, weight=ft.FontWeight.BOLD, color=CLR_SUB, width=90),
                    ft.Text("Objeto",     size=12, weight=ft.FontWeight.BOLD, color=CLR_SUB, width=120),
                    ft.Text("Resumo",     size=12, weight=ft.FontWeight.BOLD, color=CLR_SUB, expand=True),
                    ft.Text("Versão",     size=12, weight=ft.FontWeight.BOLD, color=CLR_SUB, width=80),
                    ft.Text("Impacto",    size=12, weight=ft.FontWeight.BOLD, color=CLR_SUB, width=80),
                ],
            ),
            bgcolor=ft.Colors.GREY_100,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border_radius=ft.border_radius.only(top_left=8, top_right=8),
        )

        self._lv = ft.ListView(spacing=0, expand=True)
        self._rebuild_list()

        table_card = ft.Container(
            content=ft.Column([header_row, self._lv], spacing=0, expand=True),
            border=ft.border.all(1, CLR_BORDER),
            border_radius=8,
            expand=True,
        )

        self._detail_panel = ft.Container(
            content=ft.Text("Clique em uma linha para ver detalhes.", color=CLR_SUB, size=13),
            bgcolor=CLR_CARD,
            border=ft.border.all(1, CLR_BORDER),
            border_radius=8,
            padding=16,
            visible=True,
            height=140,
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("DS_CHG — ChangeLog Viewer", size=20, weight=ft.FontWeight.BOLD, color=CLR_TEXT),
                                    ft.Text("Histórico de modificações estruturais do sistema.", size=13, color=CLR_SUB),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            new_btn,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(height=1, color=CLR_BORDER),
                    ft.Row([self._search_tf, self._type_dd], spacing=10),
                    table_card,
                    self._detail_panel,
                ],
                spacing=12,
                expand=True,
            ),
            padding=24,
            bgcolor=CLR_BG,
            expand=True,
        )

    # ── Data ──────────────────────────────────────

    def _load_changes(self) -> list:
        try:
            session = db_manager.get_session()
            rows = session.query(ChangeLog).order_by(ChangeLog.timestamp.desc()).limit(200).all()
            result = [r.to_dict() for r in rows]
            session.close()
            return result
        except Exception:
            return []

    # ── Row ───────────────────────────────────────

    def _build_row(self, row: dict) -> ft.Container:
        chg_type = row.get("change_type", "—")
        impact = row.get("kpi_impact", "NEUTRAL")
        version = row.get("version_after", "—") or "—"

        def on_click(e, r=row):
            self._show_detail(r)

        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(row.get("change_id", "—"), size=12, color=CLR_PRIMARY, width=120, weight=ft.FontWeight.W_500),
                    ft.Text(_fmt_ts(row.get("timestamp", "")), size=12, color=CLR_TEXT, width=130),
                    ft.Text(row.get("author_name", "—"), size=12, color=CLR_TEXT, width=130, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Row([_badge(chg_type, _change_color(chg_type))], width=90),
                    ft.Text(row.get("object_type", "—"), size=12, color=CLR_TEXT, width=120),
                    ft.Text(row.get("change_summary", "—"), size=12, color=CLR_TEXT, expand=True, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(version, size=12, color=CLR_TEXT, width=80),
                    ft.Row([_badge(impact, _kpi_color(impact))], width=80),
                ],
                spacing=0,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border=ft.border.only(bottom=ft.border.BorderSide(1, CLR_BORDER)),
            bgcolor=CLR_CARD,
            on_click=on_click,
            on_hover=lambda e: (setattr(e.control, "bgcolor", ft.Colors.BLUE_50 if e.data == "true" else CLR_CARD), e.control.update()),
        )

    # ── Detail ────────────────────────────────────

    def _show_detail(self, row: dict):
        ticket = row.get("ticket_id") or "—"
        branch = row.get("branch_name") or "—"
        desc = row.get("change_description") or "Sem descrição."
        self._detail_panel.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(f"🔖 {row.get('change_id')}", weight=ft.FontWeight.BOLD, color=CLR_TEXT),
                        ft.Text(f"Ticket: {ticket}", size=12, color=CLR_PRIMARY),
                        ft.Text(f"Branch: {branch}", size=12, color=CLR_SUB),
                        ft.Text(f"Git: {row.get('git_commit_hash') or '—'}", size=12, color=CLR_SUB),
                    ],
                    spacing=16,
                ),
                ft.Text(desc, size=13, color=CLR_TEXT),
            ],
            spacing=6,
        )
        self._detail_panel.update()

    # ── Filters ───────────────────────────────────

    def _filtered(self) -> list:
        rows = self._all_rows
        if self._filter_type != "TODOS":
            rows = [r for r in rows if r.get("change_type") == self._filter_type]
        if self._search_text:
            q = self._search_text.lower()
            rows = [
                r for r in rows
                if q in (r.get("author_name") or "").lower()
                or q in (r.get("object_code") or "").lower()
                or q in (r.get("ticket_id") or "").lower()
                or q in (r.get("change_summary") or "").lower()
            ]
        return rows

    def _rebuild_list(self):
        filtered = self._filtered()
        self._lv.controls.clear()
        if not filtered:
            self._lv.controls.append(
                ft.Container(
                    content=ft.Text("Nenhuma modificação registrada.", color=CLR_SUB, size=13),
                    padding=30, alignment=ft.alignment.center,
                )
            )
        else:
            for r in filtered:
                self._lv.controls.append(self._build_row(r))

    def _on_filter(self, e):
        self._filter_type = self._type_dd.value or "TODOS"
        self._search_text = self._search_tf.value or ""
        self._rebuild_list()
        self._lv.update()

    # ── Dialog novo registro ──────────────────────

    def _show_new_dialog(self, e):
        summary_tf = ft.TextField(label="Resumo da mudança", width=380)
        code_tf = ft.TextField(label="Código do objeto (ex: DS_AUDIT)", width=200)
        type_dd = ft.Dropdown(
            label="Tipo",
            width=150,
            value="MODIFY",
            options=[ft.dropdown.Option(t) for t in ["CREATE", "MODIFY", "DELETE", "RENAME", "MOVE"]],
        )
        ticket_tf = ft.TextField(label="Ticket", width=150)

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
            self.page.snack_bar = ft.SnackBar(ft.Text(f"✅ {chg_id} registrado!"), open=True)
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Registrar Mudança Manual"),
            content=ft.Column(
                [summary_tf, ft.Row([code_tf, type_dd], spacing=10), ticket_tf],
                spacing=12, tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: (setattr(dlg, "open", False), self.page.update())),
                ft.ElevatedButton("Salvar", bgcolor=CLR_PRIMARY, color=ft.Colors.WHITE, on_click=save),
            ],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
