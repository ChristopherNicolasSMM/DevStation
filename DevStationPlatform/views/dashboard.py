"""
Dashboard Principal — tela inicial após login
Flet 0.84
"""

import flet as ft
from datetime import datetime
from core.audit_logger import audit_logger
from core.kpi.collector import kpi_collector
from core.theme import Theme


class DashboardView:
    def __init__(self, page: ft.Page, user_data: dict):
        self.page = page
        self.user = user_data
        self.t = Theme.of(page)

    def build(self) -> ft.Container:
        t = self.t
        stats   = audit_logger.get_audit_stats()
        kpi_d   = kpi_collector.get_dashboard_data()
        score   = kpi_d.get("kpi_score", 0)
        recent  = audit_logger.get_recent_audit(5)

        hour = datetime.now().hour
        greeting = "Bom dia" if hour < 12 else ("Boa tarde" if hour < 18 else "Boa noite")
        name     = self.user.get("full_name") or self.user.get("username", "")
        profiles = ", ".join(self.user.get("profiles", []))

        # ── Saudação ──
        welcome = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(f"{greeting}, {name}! 👋", size=24, weight=ft.FontWeight.BOLD, color=t.text),
                            ft.Text(
                                f"Perfil: {profiles}  ·  {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                                size=13, color=t.subtext,
                            ),
                        ],
                        spacing=4, tight=True, expand=True,
                    ),
                ],
            ),
            bgcolor=t.card,
            border=ft.Border.all(1, t.border),
            border_radius=12,
            padding=ft.Padding.symmetric(horizontal=24, vertical=18),
        )

        # ── Status do sistema ──
        def status_row(label, status, icon, color):
            return ft.Row(
                [
                    ft.Icon(icon, color=color, size=16),
                    ft.Text(label, size=13, color=t.text, expand=True),
                    ft.Container(
                        content=ft.Text(status, size=11, color=ft.Colors.WHITE),
                        bgcolor=color, border_radius=4,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                    ),
                ],
                spacing=8,
            )

        system_status = [
            ("Core Engine",    "ONLINE",    ft.Icons.CIRCLE,        t.success),
            ("Banco de Dados", "CONECTADO", ft.Icons.STORAGE,       t.success),
            ("Segurança",      "ATIVO",     ft.Icons.LOCK,          t.success),
            ("Auditoria",      "ATIVA",     ft.Icons.RECEIPT_LONG,  t.success),
            ("KPI Collector",  "RODANDO",   ft.Icons.INSIGHTS,      t.success),
        ]

        status_card = t.card_container(
            content=ft.Column(
                [
                    ft.Text("🖥️ Status do Sistema", size=14, weight=ft.FontWeight.BOLD, color=t.text),
                    t.divider(),
                    *[status_row(*s) for s in system_status],
                ],
                spacing=10,
            ),
            padding=20,
            expand=1,
        )

        # ── KPI resumo ──
        sc_color = t.success if score >= 80 else (t.warning if score >= 50 else t.error)

        def mini_stat(label, value, color=None):
            return ft.Row(
                [
                    ft.Text(label, size=12, color=t.subtext, expand=True),
                    ft.Text(str(value), size=13, weight=ft.FontWeight.BOLD,
                            color=color or t.text),
                ],
                spacing=8,
            )

        kpi_card = t.card_container(
            content=ft.Column(
                [
                    ft.Text("📊 Resumo de KPIs", size=14, weight=ft.FontWeight.BOLD, color=t.text),
                    t.divider(),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("KPI Score", size=11, color=t.subtext),
                                    ft.Text(str(score), size=40, weight=ft.FontWeight.BOLD, color=sc_color),
                                    ft.Text("/ 100", size=12, color=t.subtext),
                                    ft.ProgressBar(
                                        value=score / 100, color=sc_color,
                                        bgcolor=ft.Colors.GREY_200 if not t.is_dark else ft.Colors.GREY_700,
                                        height=8, border_radius=4,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=4, width=130,
                            ),
                            ft.VerticalDivider(width=1, color=t.border),
                            ft.Column(
                                [
                                    mini_stat("Total de Ações",   stats["total_actions"]),
                                    mini_stat("Erros",             stats["total_errors"],  t.error),
                                    mini_stat("Modificações",      stats["total_changes"]),
                                    mini_stat("Taxa de Sucesso",   f"{stats['success_rate']}%", t.success),
                                ],
                                spacing=10, expand=True,
                            ),
                        ],
                        spacing=20,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                ],
                spacing=10,
            ),
            padding=20,
            expand=1,
        )

        info_row = ft.Row([status_card, kpi_card], spacing=12)

        # ── Atividade recente ──
        def fmt_ts(iso):
            try:
                return datetime.fromisoformat(iso).strftime("%H:%M:%S")
            except Exception:
                return iso or "—"

        recent_rows = []
        for r in recent:
            success = r.get("success", True)
            recent_rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE if success else ft.Icons.CANCEL,
                                color=t.success if success else t.error, size=16,
                            ),
                            ft.Text(fmt_ts(r.get("timestamp","")), size=11, color=t.subtext, width=70),
                            ft.Text(r.get("user_name","—"),         size=12, color=t.text,   width=120),
                            ft.Text(r.get("transaction_code","—"),  size=12, color=t.primary, width=120),
                            ft.Text(r.get("action_type","—"),       size=12, color=t.text,   width=80),
                            ft.Text(
                                r.get("object_name") or r.get("object_type","—"),
                                size=12, color=t.subtext, expand=True,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                    border=ft.Border.only(bottom=ft.BorderSide(1, t.border)),
                )
            )

        if not recent_rows:
            recent_rows.append(
                ft.Container(
                    content=ft.Text("Nenhuma ação registrada ainda.", color=t.subtext, size=13),
                    padding=20, alignment=ft.Alignment(0, 0),
                )
            )

        recent_card = t.card_container(
            content=ft.Column(
                [
                    ft.Text("🕐 Atividade Recente", size=14, weight=ft.FontWeight.BOLD, color=t.text),
                    t.divider(),
                    *recent_rows,
                ],
                spacing=0,
            ),
            padding=20,
        )

        return ft.Container(
            content=ft.Column(
                [welcome, info_row, recent_card],
                spacing=14,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=24,
            bgcolor=t.bg,
            expand=True,
        )
