"""
DS_KPI_DASH — Dashboard de KPIs
Sprint 3 · Flet 0.84
Perfil mínimo: BANALYST
"""

import flet as ft
from typing import Optional
from core.kpi.collector import kpi_collector
from core.theme import Theme


def _score_color(score: int, t: "Theme") -> str:
    if score >= 80: return t.success
    if score >= 50: return t.warning
    return t.error


def _rt_color(ms: float, t: "Theme") -> str:
    if ms < 200: return t.success
    if ms < 1000: return t.warning
    return t.error


ACTION_COLORS = {
    "CREATE":  ft.Colors.GREEN_600,
    "UPDATE":  ft.Colors.ORANGE_600,
    "DELETE":  ft.Colors.RED_600,
    "READ":    ft.Colors.BLUE_400,
    "EXECUTE": ft.Colors.PURPLE_400,
    "EXPORT":  ft.Colors.TEAL_500,
    "LOGIN":   ft.Colors.GREEN_400,
    "LOGOUT":  ft.Colors.GREY_400,
}


class KpiDashView:
    def __init__(self, page: ft.Page, user_data: dict):
        self.page = page
        self.user = user_data
        self.t = Theme.of(page)
        self._data: dict = {}
        # Refs para refresh parcial
        self._score_text: Optional[ft.Text] = None
        self._score_bar:  Optional[ft.ProgressBar] = None
        self._metric_cards: Optional[ft.Row] = None
        self._top_tx_col:   Optional[ft.Column] = None
        self._hourly_row:   Optional[ft.Row] = None
        self._action_col:   Optional[ft.Column] = None

    def build(self) -> ft.Container:
        t = self.t
        self._data = kpi_collector.get_dashboard_data()

        # ── Score card ──
        score = self._data.get("kpi_score", 0)
        sc_color = _score_color(score, t)
        self._score_text = ft.Text(str(score), size=52, weight=ft.FontWeight.BOLD, color=sc_color)
        self._score_bar  = ft.ProgressBar(
            value=score / 100, color=sc_color,
            bgcolor=ft.Colors.GREY_200 if not t.is_dark else ft.Colors.GREY_700,
            height=8, border_radius=4,
        )
        score_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("KPI Score", size=13, color=t.subtext, weight=ft.FontWeight.W_500),
                    self._score_text,
                    ft.Text("/ 100", size=12, color=t.subtext),
                    self._score_bar,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
            bgcolor=t.card,
            border=ft.Border.all(1, t.border),
            border_radius=12,
            padding=ft.Padding.symmetric(horizontal=20, vertical=20),
            width=170,
            alignment=ft.Alignment(0, 0),
        )

        # ── Metric cards ──
        self._metric_cards = ft.Row(self._build_metric_cards(), spacing=12, expand=True)
        top_section = ft.Row(
            [score_card, self._metric_cards],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        # ── Top transactions ──
        self._top_tx_col = ft.Column(self._build_top_transactions(), spacing=8)
        top_tx_card = t.card_container(
            content=ft.Column(
                [
                    ft.Text("🔝 Transações Mais Usadas", size=14, weight=ft.FontWeight.BOLD, color=t.text),
                    t.divider(),
                    self._top_tx_col,
                ],
                spacing=10,
            ),
            padding=20,
            expand=2,
        )

        # ── Action distribution ──
        self._action_col = ft.Column(self._build_action_dist(), spacing=8)
        action_card = t.card_container(
            content=ft.Column(
                [
                    ft.Text("⚡ Por Tipo de Ação", size=14, weight=ft.FontWeight.BOLD, color=t.text),
                    t.divider(),
                    self._action_col,
                ],
                spacing=10,
            ),
            padding=20,
            expand=1,
        )

        # ── Hourly chart ──
        self._hourly_row = ft.Row(
            self._build_hourly_bars(),
            spacing=3,
            vertical_alignment=ft.CrossAxisAlignment.END,
        )
        hourly_card = t.card_container(
            content=ft.Column(
                [
                    ft.Text("🕐 Atividade por Hora (últimas 24h)", size=14, weight=ft.FontWeight.BOLD, color=t.text),
                    t.divider(),
                    ft.Container(content=self._hourly_row, height=110),
                ],
                spacing=10,
            ),
            padding=20,
        )

        bottom_row = ft.Row([top_tx_card, action_card], spacing=12, expand=True,
                            vertical_alignment=ft.CrossAxisAlignment.START)

        refresh_btn = ft.IconButton(
            icon=ft.Icons.REFRESH, icon_color=t.primary,
            tooltip="Atualizar métricas", on_click=self._on_refresh,
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            t.section_header("DS_KPI_DASH — Dashboard de KPIs",
                                             "Métricas de uso, performance e qualidade do sistema."),
                            refresh_btn,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    t.divider(),
                    top_section,
                    hourly_card,
                    bottom_row,
                ],
                spacing=14,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=24,
            bgcolor=t.bg,
            expand=True,
        )

    # ─── Builders ────────────────────────────────

    def _build_metric_cards(self) -> list:
        t = self.t
        d = self._data
        avg_rt = d.get("avg_response_time_ms", 0)
        err_rt = d.get("error_rate_pct", 0)
        items = [
            ("Total de Ações",  str(d.get("total_transactions", 0)),     ft.Icons.RECEIPT_LONG,       t.primary),
            ("Ações Hoje",      str(d.get("transactions_today", 0)),     ft.Icons.TODAY,              ft.Colors.INDIGO_400),
            ("Usuários Ativos", str(d.get("active_users_session", 0)),   ft.Icons.PEOPLE,             ft.Colors.TEAL_500),
            ("Tempo Médio",     f"{avg_rt:.0f}ms",                       ft.Icons.SPEED,              _rt_color(avg_rt, t)),
            ("Taxa de Erro",    f"{err_rt:.1f}%",                        ft.Icons.WARNING_AMBER,      t.error if err_rt > 5 else t.success),
        ]
        cards = []
        for label, value, icon, color in items:
            cards.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([ft.Icon(icon, color=color, size=18), ft.Text(label, size=11, color=t.subtext)], spacing=6),
                            ft.Text(value, size=26, weight=ft.FontWeight.BOLD, color=t.text),
                        ],
                        spacing=6, tight=True,
                    ),
                    bgcolor=t.card,
                    border=ft.Border.all(1, t.border),
                    border_radius=10,
                    padding=ft.Padding.symmetric(horizontal=18, vertical=14),
                    expand=True,
                )
            )
        return cards

    def _build_top_transactions(self) -> list:
        t = self.t
        top = self._data.get("top_transactions", [])
        if not top:
            return [ft.Text("Nenhuma transação registrada ainda.", color=t.subtext, size=13)]
        max_count = max(r["count"] for r in top) if top else 1
        rows = []
        for item in top:
            pct = item["count"] / max_count
            err_badge = None
            if item.get("errors", 0) > 0:
                err_badge = ft.Container(
                    content=ft.Text(f"{item['errors']} err", size=10, color=ft.Colors.WHITE),
                    bgcolor=t.error, border_radius=4,
                    padding=ft.Padding.symmetric(horizontal=5, vertical=2),
                )
            row_ctrl = [
                ft.Text(item["code"], size=12, color=t.primary, width=170, weight=ft.FontWeight.W_500),
                ft.ProgressBar(
                    value=pct, color=t.primary,
                    bgcolor=ft.Colors.GREY_100 if not t.is_dark else ft.Colors.GREY_700,
                    height=8, border_radius=4, expand=True,
                ),
                ft.Text(str(item["count"]), size=12, color=t.text, width=38, text_align=ft.TextAlign.RIGHT),
                ft.Text(f"{item['avg_ms']}ms", size=11, color=_rt_color(item["avg_ms"], t), width=60, text_align=ft.TextAlign.RIGHT),
            ]
            if err_badge:
                row_ctrl.append(err_badge)
            rows.append(ft.Row(row_ctrl, spacing=10))
        return rows

    def _build_hourly_bars(self) -> list:
        t = self.t
        hourly = {item["hour"]: item["count"] for item in self._data.get("hourly_distribution", [])}
        if not hourly:
            return [ft.Text("Sem dados horários.", color=t.subtext, size=12)]
        max_c = max(hourly.values()) if hourly else 1
        bars = []
        for h in range(24):
            count = hourly.get(h, 0)
            bar_h = max(4, int((count / max_c) * 80)) if count > 0 else 4
            color = t.primary if count > 0 else (ft.Colors.GREY_300 if not t.is_dark else ft.Colors.GREY_700)
            bars.append(
                ft.Column(
                    [
                        ft.Container(
                            width=16, height=bar_h, bgcolor=color, border_radius=3,
                            tooltip=f"{h:02d}h — {count}",
                        ),
                        ft.Text(f"{h:02d}", size=9, color=t.subtext, text_align=ft.TextAlign.CENTER, width=16),
                    ],
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        return bars

    def _build_action_dist(self) -> list:
        t = self.t
        actions = self._data.get("action_distribution", [])
        if not actions:
            return [ft.Text("Sem dados.", color=t.subtext, size=13)]
        total = sum(a["count"] for a in actions)
        if total == 0:
            return [ft.Text("Sem dados.", color=t.subtext, size=13)]
        rows = []
        for item in sorted(actions, key=lambda x: x["count"], reverse=True):
            pct = item["count"] / total
            color = ACTION_COLORS.get(item["action"], ft.Colors.GREY_400)
            rows.append(
                ft.Row(
                    [
                        ft.Container(width=10, height=10, bgcolor=color, border_radius=2),
                        ft.Text(item["action"], size=12, color=t.text, width=80),
                        ft.ProgressBar(
                            value=pct, color=color,
                            bgcolor=ft.Colors.GREY_100 if not t.is_dark else ft.Colors.GREY_700,
                            height=8, border_radius=4, expand=True,
                        ),
                        ft.Text(str(item["count"]), size=12, color=t.text, width=35, text_align=ft.TextAlign.RIGHT),
                    ],
                    spacing=8,
                )
            )
        return rows

    # ─── Refresh ─────────────────────────────────

    def _on_refresh(self, e):
        t = self.t
        self._data = kpi_collector.get_dashboard_data()
        score = self._data.get("kpi_score", 0)
        sc_color = _score_color(score, t)

        self._score_text.value = str(score)
        self._score_text.color = sc_color
        self._score_text.update()

        self._score_bar.value = score / 100
        self._score_bar.color = sc_color
        self._score_bar.update()

        self._metric_cards.controls = self._build_metric_cards()
        self._metric_cards.update()

        self._top_tx_col.controls = self._build_top_transactions()
        self._top_tx_col.update()

        self._action_col.controls = self._build_action_dist()
        self._action_col.update()

        self._hourly_row.controls = self._build_hourly_bars()
        self._hourly_row.update()
