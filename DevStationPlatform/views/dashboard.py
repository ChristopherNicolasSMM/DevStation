"""
Dashboard Principal - Tela inicial após login
"""

import flet as ft
from datetime import datetime
from core.audit_logger import audit_logger
from core.kpi.collector import kpi_collector


CLR_BG = ft.Colors.GREY_50
CLR_CARD = ft.Colors.WHITE
CLR_PRIMARY = ft.Colors.BLUE_700
CLR_SUCCESS = ft.Colors.GREEN_600
CLR_ERROR = ft.Colors.RED_600
CLR_WARN = ft.Colors.ORANGE_600
CLR_TEXT = ft.Colors.GREY_900
CLR_SUB = ft.Colors.GREY_600
CLR_BORDER = ft.Colors.GREY_200


class DashboardView:
    """Tela principal com resumo do sistema."""

    def __init__(self, page: ft.Page, user_data: dict):
        self.page = page
        self.user = user_data

    def build(self) -> ft.Container:
        stats = audit_logger.get_audit_stats()
        kpi_data = kpi_collector.get_dashboard_data()
        score = kpi_data.get("kpi_score", 0)
        recent = audit_logger.get_recent_audit(5)
        hour = datetime.now().hour
        greeting = "Bom dia" if hour < 12 else ("Boa tarde" if hour < 18 else "Boa noite")
        name = self.user.get("full_name") or self.user.get("username", "")
        profiles = ", ".join(self.user.get("profiles", []))

        # ── Saudação ──
        welcome = ft.Container(
            content=ft.Column(
                [
                    ft.Text(f"{greeting}, {name}! 👋", size=26, weight=ft.FontWeight.BOLD, color=CLR_TEXT),
                    ft.Text(f"Perfil: {profiles} · {datetime.now().strftime('%d/%m/%Y %H:%M')}", size=13, color=CLR_SUB),
                ],
                spacing=4,
            ),
            bgcolor=CLR_CARD,
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=24, vertical=18),
            border=ft.border.all(1, CLR_BORDER),
        )

        # ── Status do sistema ──
        status_items = [
            ("Core Engine",    "ONLINE",    ft.Icons.CIRCLE, CLR_SUCCESS),
            ("Banco de Dados", "CONECTADO", ft.Icons.STORAGE, CLR_SUCCESS),
            ("Segurança",      "ATIVO",     ft.Icons.LOCK, CLR_SUCCESS),
            ("Auditoria",      "ATIVA",     ft.Icons.RECEIPT_LONG, CLR_SUCCESS),
            ("KPI Collector",  "RODANDO",   ft.Icons.INSIGHTS, CLR_SUCCESS),
        ]

        status_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("🖥️ Status do Sistema", size=14, weight=ft.FontWeight.BOLD, color=CLR_TEXT),
                    ft.Divider(height=1, color=CLR_BORDER),
                    *[
                        ft.Row(
                            [
                                ft.Icon(icon, color=color, size=16),
                                ft.Text(label, size=13, color=CLR_TEXT, expand=True),
                                ft.Container(
                                    content=ft.Text(status, size=11, color=ft.Colors.WHITE),
                                    bgcolor=color,
                                    border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                ),
                            ],
                            spacing=8,
                        )
                        for label, status, icon, color in status_items
                    ],
                ],
                spacing=10,
            ),
            bgcolor=CLR_CARD,
            border=ft.border.all(1, CLR_BORDER),
            border_radius=10,
            padding=20,
            expand=1,
        )

        # ── KPI resumo ──
        score_color = CLR_SUCCESS if score >= 80 else (CLR_WARN if score >= 50 else CLR_ERROR)
        kpi_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("📊 Resumo de KPIs", size=14, weight=ft.FontWeight.BOLD, color=CLR_TEXT),
                    ft.Divider(height=1, color=CLR_BORDER),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("KPI Score", size=11, color=CLR_SUB),
                                    ft.Text(str(score), size=42, weight=ft.FontWeight.BOLD, color=score_color),
                                    ft.Text("/ 100", size=12, color=CLR_SUB),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2,
                            ),
                            ft.VerticalDivider(width=1, color=CLR_BORDER),
                            ft.Column(
                                [
                                    self._mini_stat("Total de Ações", str(stats["total_actions"])),
                                    self._mini_stat("Erros Registrados", str(stats["total_errors"]), CLR_ERROR),
                                    self._mini_stat("Modificações", str(stats["total_changes"])),
                                    self._mini_stat("Taxa de Sucesso", f"{stats['success_rate']}%", CLR_SUCCESS),
                                ],
                                spacing=8,
                                expand=True,
                            ),
                        ],
                        spacing=20,
                    ),
                ],
                spacing=10,
            ),
            bgcolor=CLR_CARD,
            border=ft.border.all(1, CLR_BORDER),
            border_radius=10,
            padding=20,
            expand=1,
        )

        info_row = ft.Row([status_card, kpi_card], spacing=12)

        # ── Atividade recente ──
        recent_rows = []
        for r in recent:
            ts = r.get("timestamp", "")
            try:
                ts = datetime.fromisoformat(ts).strftime("%H:%M:%S")
            except Exception:
                pass
            success = r.get("success", True)
            recent_rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE if success else ft.Icons.CANCEL,
                                color=CLR_SUCCESS if success else CLR_ERROR,
                                size=16,
                            ),
                            ft.Text(ts, size=11, color=CLR_SUB, width=70),
                            ft.Text(r.get("user_name", "—"), size=12, color=CLR_TEXT, width=120),
                            ft.Text(r.get("transaction_code", "—"), size=12, color=CLR_PRIMARY, width=120),
                            ft.Text(r.get("action_type", "—"), size=12, color=CLR_TEXT, width=80),
                            ft.Text(r.get("object_name") or r.get("object_type", "—"), size=12, color=CLR_SUB, expand=True, overflow=ft.TextOverflow.ELLIPSIS),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, CLR_BORDER)),
                )
            )

        if not recent_rows:
            recent_rows.append(
                ft.Container(
                    content=ft.Text("Nenhuma ação registrada ainda.", color=CLR_SUB, size=13),
                    padding=20,
                    alignment=ft.alignment.center,
                )
            )

        recent_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("🕐 Atividade Recente", size=14, weight=ft.FontWeight.BOLD, color=CLR_TEXT),
                    ft.Divider(height=1, color=CLR_BORDER),
                    *recent_rows,
                ],
                spacing=0,
            ),
            bgcolor=CLR_CARD,
            border=ft.border.all(1, CLR_BORDER),
            border_radius=10,
            padding=20,
        )

        # ── Atalhos ──
        shortcuts = [
            ("🔍 DS_AUDIT",    "Console de Auditoria", "audit"),
            ("📋 DS_CHG",      "ChangeLog Viewer",     "changelog"),
            ("📊 DS_KPI_DASH", "Dashboard de KPIs",    "kpi"),
        ]
        shortcut_row = ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(title, size=14, weight=ft.FontWeight.W_600, color=CLR_PRIMARY),
                            ft.Text(desc, size=12, color=CLR_SUB),
                        ],
                        spacing=4, tight=True,
                    ),
                    bgcolor=CLR_CARD,
                    border=ft.border.all(1, CLR_PRIMARY),
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=20, vertical=14),
                    expand=True,
                    on_hover=lambda e: (setattr(e.control, "bgcolor", ft.Colors.BLUE_50 if e.data == "true" else CLR_CARD), e.control.update()),
                )
                for title, desc, _ in shortcuts
            ],
            spacing=12,
        )

        return ft.Container(
            content=ft.Column(
                [welcome, info_row, recent_card, shortcut_row],
                spacing=14,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=24,
            bgcolor=CLR_BG,
            expand=True,
        )

    def _mini_stat(self, label: str, value: str, color: str = None) -> ft.Row:
        return ft.Row(
            [
                ft.Text(label, size=12, color=CLR_SUB, expand=True),
                ft.Text(value, size=13, weight=ft.FontWeight.BOLD, color=color or CLR_TEXT),
            ],
            spacing=8,
        )
