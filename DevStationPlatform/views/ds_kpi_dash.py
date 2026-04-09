"""
DS_KPI_DASH - Dashboard de KPIs
Sprint 3 - Sistema de KPIs
Perfil mínimo: BANALYST
"""

import flet as ft
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


def _score_color(score: int) -> str:
    if score >= 80:
        return CLR_SUCCESS
    if score >= 50:
        return CLR_WARN
    return CLR_ERROR


def _rt_color(ms: float) -> str:
    if ms < 200:
        return CLR_SUCCESS
    if ms < 1000:
        return CLR_WARN
    return CLR_ERROR


class KpiDashView:
    """
    Tela DS_KPI_DASH — dashboard de métricas de performance e uso.
    """

    def __init__(self, page: ft.Page, user_data: dict):
        self.page = page
        self.user = user_data
        self._data: dict = {}

        # Referências para atualização parcial
        self._score_text: ft.Text | None = None
        self._kpi_cards_row: ft.Row | None = None
        self._top_tx_col: ft.Column | None = None
        self._hourly_bars: ft.Row | None = None
        self._action_col: ft.Column | None = None

    def build(self) -> ft.Container:
        self._data = kpi_collector.get_dashboard_data()

        refresh_btn = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Atualizar métricas",
            icon_color=CLR_PRIMARY,
            on_click=self._on_refresh,
        )

        # ── Cabeçalho ──
        header = ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("DS_KPI_DASH — Dashboard de KPIs", size=20, weight=ft.FontWeight.BOLD, color=CLR_TEXT),
                        ft.Text("Métricas de uso, performance e qualidade do sistema.", size=13, color=CLR_SUB),
                    ],
                    spacing=2,
                    expand=True,
                ),
                refresh_btn,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # ── Score geral ──
        score = self._data.get("kpi_score", 0)
        self._score_text = ft.Text(
            f"{score}",
            size=54,
            weight=ft.FontWeight.BOLD,
            color=_score_color(score),
        )

        score_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("KPI Score", size=13, color=CLR_SUB, weight=ft.FontWeight.W_500),
                    self._score_text,
                    ft.Text("/ 100", size=13, color=CLR_SUB),
                    ft.ProgressBar(
                        value=score / 100,
                        color=_score_color(score),
                        bgcolor=ft.Colors.GREY_200,
                        height=8,
                        border_radius=4,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
            bgcolor=CLR_CARD,
            border=ft.border.all(1, CLR_BORDER),
            border_radius=12,
            padding=24,
            width=180,
            alignment=ft.alignment.center,
        )

        # ── Cards de métricas ──
        self._kpi_cards_row = ft.Row(
            self._build_metric_cards(),
            spacing=12,
            expand=True,
        )

        top_section = ft.Row(
            [score_card, self._kpi_cards_row],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        # ── Transações mais usadas ──
        self._top_tx_col = ft.Column(
            self._build_top_transactions(),
            spacing=6,
        )

        top_tx_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("🔝 Transações Mais Usadas", size=14, weight=ft.FontWeight.BOLD, color=CLR_TEXT),
                    ft.Divider(height=1, color=CLR_BORDER),
                    self._top_tx_col,
                ],
                spacing=10,
            ),
            bgcolor=CLR_CARD,
            border=ft.border.all(1, CLR_BORDER),
            border_radius=10,
            padding=20,
            expand=2,
        )

        # ── Distribuição por ação ──
        self._action_col = ft.Column(
            self._build_action_dist(),
            spacing=8,
        )

        action_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("⚡ Distribuição por Ação", size=14, weight=ft.FontWeight.BOLD, color=CLR_TEXT),
                    ft.Divider(height=1, color=CLR_BORDER),
                    self._action_col,
                ],
                spacing=10,
            ),
            bgcolor=CLR_CARD,
            border=ft.border.all(1, CLR_BORDER),
            border_radius=10,
            padding=20,
            expand=1,
        )

        # ── Distribuição por hora ──
        self._hourly_bars = self._build_hourly_chart()
        hourly_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("🕐 Atividade nas Últimas 24h (por hora)", size=14, weight=ft.FontWeight.BOLD, color=CLR_TEXT),
                    ft.Divider(height=1, color=CLR_BORDER),
                    ft.Container(
                        content=self._hourly_bars,
                        height=110,
                    ),
                ],
                spacing=10,
            ),
            bgcolor=CLR_CARD,
            border=ft.border.all(1, CLR_BORDER),
            border_radius=10,
            padding=20,
        )

        bottom_row = ft.Row(
            [top_tx_card, action_card],
            spacing=12,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        main_col = ft.Column(
            [
                header,
                ft.Divider(height=1, color=CLR_BORDER),
                top_section,
                hourly_card,
                bottom_row,
            ],
            spacing=14,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        return ft.Container(
            content=main_col,
            padding=24,
            bgcolor=CLR_BG,
            expand=True,
        )

    # ── Metric cards ──────────────────────────────

    def _build_metric_cards(self) -> list:
        d = self._data
        return [
            self._metric_card("Total de Ações", str(d.get("total_transactions", 0)), ft.Icons.RECEIPT_LONG, CLR_PRIMARY),
            self._metric_card("Ações Hoje", str(d.get("transactions_today", 0)), ft.Icons.TODAY, ft.Colors.INDIGO_500),
            self._metric_card("Usuários Ativos", str(d.get("active_users_session", 0)), ft.Icons.PEOPLE, ft.Colors.TEAL_500),
            self._metric_card("Tempo Médio", f"{d.get('avg_response_time_ms', 0):.0f}ms", ft.Icons.SPEED, _rt_color(d.get("avg_response_time_ms", 0))),
            self._metric_card("Taxa de Erro", f"{d.get('error_rate_pct', 0):.1f}%", ft.Icons.WARNING_AMBER, CLR_ERROR if d.get("error_rate_pct", 0) > 5 else CLR_SUCCESS),
        ]

    def _metric_card(self, label: str, value: str, icon, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(icon, color=color, size=20),
                            ft.Text(label, size=11, color=CLR_SUB),
                        ],
                        spacing=6,
                    ),
                    ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=CLR_TEXT),
                ],
                spacing=6,
                tight=True,
            ),
            bgcolor=CLR_CARD,
            border=ft.border.all(1, CLR_BORDER),
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=18, vertical=14),
            expand=True,
        )

    # ── Top transactions ──────────────────────────

    def _build_top_transactions(self) -> list:
        top = self._data.get("top_transactions", [])
        if not top:
            return [ft.Text("Nenhuma transação registrada ainda.", color=CLR_SUB, size=13)]

        max_count = max(r["count"] for r in top) if top else 1
        rows = []
        for item in top:
            pct = item["count"] / max_count
            err_badge = None
            if item["errors"] > 0:
                err_badge = ft.Container(
                    content=ft.Text(f"{item['errors']} erros", size=10, color=ft.Colors.WHITE),
                    bgcolor=CLR_ERROR,
                    border_radius=4,
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                )

            row_controls = [
                ft.Text(item["code"], size=12, color=CLR_PRIMARY, width=160, weight=ft.FontWeight.W_500),
                ft.ProgressBar(value=pct, color=CLR_PRIMARY, bgcolor=ft.Colors.GREY_100, height=8, border_radius=4, expand=True),
                ft.Text(str(item["count"]), size=12, color=CLR_TEXT, width=40, text_align=ft.TextAlign.RIGHT),
                ft.Text(f"{item['avg_ms']}ms", size=11, color=_rt_color(item["avg_ms"]), width=60, text_align=ft.TextAlign.RIGHT),
            ]
            if err_badge:
                row_controls.append(err_badge)

            rows.append(ft.Row(row_controls, spacing=10))
        return rows

    # ── Hourly chart ──────────────────────────────

    def _build_hourly_chart(self) -> ft.Row:
        hourly = {item["hour"]: item["count"] for item in self._data.get("hourly_distribution", [])}
        if not hourly:
            return ft.Row(
                [ft.Text("Sem dados de distribuição horária.", color=CLR_SUB, size=13)],
                expand=True,
            )

        max_count = max(hourly.values()) if hourly else 1
        bars = []
        for h in range(24):
            count = hourly.get(h, 0)
            height = max(4, int((count / max_count) * 80)) if count > 0 else 4
            color = CLR_PRIMARY if count > 0 else ft.Colors.GREY_200
            bars.append(
                ft.Tooltip(
                    message=f"{h:02d}h — {count} ações",
                    content=ft.Column(
                        [
                            ft.Container(width=16, height=height, bgcolor=color, border_radius=3),
                            ft.Text(f"{h:02d}", size=9, color=CLR_SUB, text_align=ft.TextAlign.CENTER, width=16),
                        ],
                        spacing=2,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            )

        return ft.Row(bars, spacing=4, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.END)

    # ── Action distribution ───────────────────────

    def _build_action_dist(self) -> list:
        actions = self._data.get("action_distribution", [])
        if not actions:
            return [ft.Text("Sem dados.", color=CLR_SUB, size=13)]

        total = sum(a["count"] for a in actions)
        if total == 0:
            return [ft.Text("Sem dados.", color=CLR_SUB, size=13)]

        action_colors = {
            "CREATE": CLR_SUCCESS, "UPDATE": CLR_WARN, "DELETE": CLR_ERROR,
            "READ": ft.Colors.BLUE_400, "EXECUTE": ft.Colors.PURPLE_400,
            "EXPORT": ft.Colors.TEAL_500, "LOGIN": ft.Colors.GREEN_300,
        }
        rows = []
        for item in sorted(actions, key=lambda x: x["count"], reverse=True):
            pct = item["count"] / total
            color = action_colors.get(item["action"], ft.Colors.GREY_400)
            rows.append(
                ft.Row(
                    [
                        ft.Container(width=10, height=10, bgcolor=color, border_radius=2),
                        ft.Text(item["action"], size=12, color=CLR_TEXT, width=80),
                        ft.ProgressBar(value=pct, color=color, bgcolor=ft.Colors.GREY_100, height=8, border_radius=4, expand=True),
                        ft.Text(f"{item['count']}", size=12, color=CLR_TEXT, width=35, text_align=ft.TextAlign.RIGHT),
                    ],
                    spacing=8,
                )
            )
        return rows

    # ── Refresh ───────────────────────────────────

    def _on_refresh(self, e):
        self._data = kpi_collector.get_dashboard_data()

        # Atualiza score
        score = self._data.get("kpi_score", 0)
        self._score_text.value = str(score)
        self._score_text.color = _score_color(score)
        self._score_text.update()

        # Atualiza metric cards
        self._kpi_cards_row.controls = self._build_metric_cards()
        self._kpi_cards_row.update()

        # Atualiza top tx
        self._top_tx_col.controls = self._build_top_transactions()
        self._top_tx_col.update()

        # Atualiza action dist
        self._action_col.controls = self._build_action_dist()
        self._action_col.update()

        # Atualiza hourly
        self._hourly_bars.controls = self._build_hourly_chart().controls
        self._hourly_bars.update()
