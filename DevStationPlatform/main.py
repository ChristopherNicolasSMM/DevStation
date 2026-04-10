"""
DevStationPlatform — Main Entry Point
Sprints 1-3 · Flet 0.84
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import flet as ft
from core import config, plugin_manager, menu_manager
from core.models.base import db_manager
from core.models.user import User
from core.security.auth import AuthScreen, get_current_user, logout
from core.audit_logger import audit_logger
from core.kpi.collector import kpi_collector
from core.theme import Theme

_VIEW_DASHBOARD = "dashboard"
_VIEW_AUDIT     = "audit"
_VIEW_CHANGELOG = "changelog"
_VIEW_KPI       = "kpi"


# ─────────────────────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────────────────────

def setup_database():
    db_manager.create_tables()
    session = db_manager.get_session()
    if session.query(User).count() == 0:
        _seed_default_data(session)
    session.close()


def _seed_default_data(session):
    from core.models.user import Profile, Permission

    permissions_created = {}
    for perm_data in config.get("security.default_permissions", []):
        perm = Permission(
            code=perm_data["code"], name=perm_data["name"],
            category=perm_data.get("category", "GENERAL"), is_system=True,
        )
        session.add(perm)
        session.flush()
        permissions_created[perm.code] = perm

    profiles = {}
    for pd in config.get("security.default_profiles", []):
        p = Profile(
            code=pd["code"], name=pd["name"],
            description=pd.get("description", ""),
            is_system=True, priority=pd.get("priority", 0),
        )
        session.add(p)
        session.flush()
        profiles[p.code] = p

    for pd in config.get("security.default_profiles", []):
        for parent_code in pd.get("inherit_from", []):
            if parent_code in profiles:
                profiles[pd["code"]].parents.append(profiles[parent_code])

    admin_profile = profiles.get("ADMIN")
    if admin_profile:
        admin_profile.permissions = list(permissions_created.values())

    admin = User(username="admin", email="admin@devstation.com",
                 full_name="Administrator", is_active=True, is_system=True)
    admin.set_password("admin123")
    if admin_profile:
        admin.profiles.append(admin_profile)
    session.add(admin)

    dev_profile = profiles.get("DEVELOPER")
    developer = User(username="developer", email="developer@devstation.com",
                     full_name="Developer User", is_active=True)
    developer.set_password("dev123")
    if dev_profile:
        developer.profiles.append(dev_profile)
    session.add(developer)

    session.commit()
    audit_logger.log_change(
        author_id=0, author_name="system", author_profile="ADMIN",
        object_type="DATABASE", object_code="SEED",
        change_type="CREATE",
        change_summary="Banco de dados inicializado com dados padrão.",
        version_after="1.0.0", kpi_impact="POSITIVE",
    )
    print("✅ Database seeded!")


# ─────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────

def build_main_app(page: ft.Page, user_data: dict):
    page.title = f"{config.app_name} · {user_data.get('full_name', user_data.get('username'))}"
    page.window_width  = 1280
    page.window_height = 780
    page.padding = 0

    # Registra login
    audit_logger.log(
        user_id=user_data.get("id", 0),
        user_name=user_data.get("username", "?"),
        user_profiles=", ".join(user_data.get("profiles", [])),
        transaction_code="DS_AUTH", action_type="LOGIN",
        object_type="SESSION", object_name="Sessão iniciada",
        kpi_tags=["auth"],
    )
    kpi_collector.record_transaction("DS_AUTH", 0, True, user_data.get("id", 0))

    # Estado
    _active_view: list = [_VIEW_DASHBOARD]
    sidebar_btns: dict = {}
    content_area = ft.Container(expand=True)

    def _t() -> Theme:
        return Theme.of(page)

    # ── Navegação ─────────────────────────────────

    NAV_ITEMS = [
        {"key": _VIEW_DASHBOARD, "icon": ft.Icons.DASHBOARD_OUTLINED,   "icon_sel": ft.Icons.DASHBOARD,    "label": "Dashboard",   "desc": "",           "min_profile": None},
        {"key": _VIEW_AUDIT,     "icon": ft.Icons.RECEIPT_LONG_OUTLINED, "icon_sel": ft.Icons.RECEIPT_LONG, "label": "DS_AUDIT",    "desc": "Auditoria",  "min_profile": "ADMIN"},
        {"key": _VIEW_CHANGELOG, "icon": ft.Icons.EDIT_NOTE_OUTLINED,    "icon_sel": ft.Icons.EDIT_NOTE,    "label": "DS_CHG",      "desc": "ChangeLog",  "min_profile": "DEVELOPER"},
        {"key": _VIEW_KPI,       "icon": ft.Icons.INSIGHTS_OUTLINED,     "icon_sel": ft.Icons.INSIGHTS,     "label": "DS_KPI_DASH", "desc": "KPIs",       "min_profile": "BANALYST"},
    ]

    def _has_access(min_profile) -> bool:
        if min_profile is None:
            return True
        hierarchy = ["USER","PUSER","BANALYST","DEVELOPER","CORE_DEV","DEV_ALL","ADMIN"]
        min_idx = hierarchy.index(min_profile) if min_profile in hierarchy else 999
        return any(
            p in hierarchy and hierarchy.index(p) >= min_idx
            for p in user_data.get("profiles", [])
        )

    def _load_view(view_key: str):
        _active_view[0] = view_key
        t = _t()
        for key, btn in sidebar_btns.items():
            btn.bgcolor = t.sidebar_active if key == view_key else ft.Colors.TRANSPARENT
            btn.update()

        if view_key == _VIEW_DASHBOARD:
            from views.dashboard import DashboardView
            view = DashboardView(page, user_data).build()
        elif view_key == _VIEW_AUDIT:
            from views.ds_audit import AuditView
            view = AuditView(page, user_data).build()
        elif view_key == _VIEW_CHANGELOG:
            from views.ds_chg import ChangeLogView
            view = ChangeLogView(page, user_data).build()
        elif view_key == _VIEW_KPI:
            from views.ds_kpi_dash import KpiDashView
            view = KpiDashView(page, user_data).build()
        else:
            t2 = _t()
            view = ft.Container(
                content=ft.Text(f"View '{view_key}' não implementada.", color=t2.subtext),
                padding=40,
            )

        content_area.bgcolor = _t().bg
        content_area.content = view
        content_area.update()

    # ── Sidebar buttons ──────────────────────────

    def _make_nav_btn(item: dict) -> ft.Container:
        accessible = _has_access(item["min_profile"])
        is_active  = item["key"] == _VIEW_DASHBOARD

        def on_click(e, key=item["key"], acc=accessible):
            if not acc:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ Perfil insuficiente para {key}"),
                    bgcolor=ft.Colors.RED_700, open=True,
                )
                page.update()
                return
            _load_view(key)

        def on_hover(e, key=item["key"]):
            if key != _active_view[0]:
                e.control.bgcolor = ft.Colors.BLUE_800 if e.data == "true" else ft.Colors.TRANSPARENT
                e.control.update()

        label_col = ft.Column(
            [
                ft.Text(item["label"], size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                *(
                    [ft.Text(item["desc"], size=10, color=ft.Colors.BLUE_200)]
                    if item["desc"] else []
                ),
            ],
            spacing=1, tight=True,
        )

        btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        item["icon_sel"] if is_active else item["icon"],
                        color=ft.Colors.WHITE if accessible else ft.Colors.BLUE_300,
                        size=20,
                    ),
                    label_col,
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.BLUE_800 if is_active else ft.Colors.TRANSPARENT,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            on_click=on_click,
            on_hover=on_hover,
            opacity=1.0 if accessible else 0.45,
        )
        sidebar_btns[item["key"]] = btn
        return btn

    nav_buttons = [_make_nav_btn(item) for item in NAV_ITEMS]

    # ── Theme toggle ─────────────────────────────

    theme_icon_ref = ft.Ref[ft.IconButton]()

    def _toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        if theme_icon_ref.current:
            theme_icon_ref.current.icon = (
                ft.Icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE
            )
            theme_icon_ref.current.update()
        _load_view(_active_view[0])   # re-render view with new theme

    # ── User footer ───────────────────────────────

    def _do_logout():
        audit_logger.log(
            user_id=user_data.get("id", 0),
            user_name=user_data.get("username", "?"),
            user_profiles=", ".join(user_data.get("profiles", [])),
            transaction_code="DS_AUTH", action_type="LOGOUT",
            object_type="SESSION", object_name="Sessão encerrada",
            kpi_tags=["auth"],
        )
        logout(page)

    avatar_letter = (user_data.get("username") or "?")[0].upper()
    user_footer = ft.Container(
        content=ft.Column(
            [
                ft.Divider(height=1, color=ft.Colors.BLUE_800),
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(avatar_letter, size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            bgcolor=ft.Colors.BLUE_500,
                            border_radius=50, width=34, height=34,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column(
                            [
                                ft.Text(user_data.get("username","—"), size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                ft.Text(", ".join(user_data.get("profiles",[])), size=10, color=ft.Colors.BLUE_200),
                            ],
                            spacing=1, tight=True, expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT, icon_color=ft.Colors.BLUE_300,
                            tooltip="Sair", on_click=lambda e: _do_logout(),
                        ),
                    ],
                    spacing=8,
                ),
            ],
            spacing=8,
        ),
        padding=ft.Padding.symmetric(horizontal=10, vertical=8),
    )

    # ── Sidebar assembly ─────────────────────────

    sidebar = ft.Container(
        content=ft.Column(
            [
                # Logo + theme toggle
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("DevStation", size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                    ft.Text("Platform v1.0", size=10, color=ft.Colors.BLUE_200),
                                ],
                                spacing=0, tight=True, expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DARK_MODE,
                                icon_color=ft.Colors.BLUE_200,
                                icon_size=18,
                                ref=theme_icon_ref,
                                tooltip="Alternar tema",
                                on_click=_toggle_theme,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding.symmetric(horizontal=14, vertical=16),
                ),
                ft.Divider(height=1, color=ft.Colors.BLUE_800),
                ft.Container(height=6),
                # Nav items
                ft.Container(
                    content=ft.Column(nav_buttons, spacing=2),
                    padding=ft.Padding.symmetric(horizontal=8),
                    expand=True,
                ),
                user_footer,
            ],
            spacing=0, expand=True,
        ),
        bgcolor=ft.Colors.BLUE_900,
        width=210,
    )

    # ── Layout ────────────────────────────────────
    page.clean()
    page.appbar = None
    page.add(
        ft.Row(
            [sidebar, content_area],
            spacing=0, expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )
    )

    _load_view(_VIEW_DASHBOARD)
    page.update()


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

def main(page: ft.Page):
    page.title        = config.app_name
    page.theme_mode   = ft.ThemeMode.LIGHT
    page.window_width  = 1280
    page.window_height = 780
    page.padding      = 0
    page.bgcolor      = ft.Colors.GREY_50

    print("📦 Configurando banco de dados...")
    setup_database()

    print("🔍 Descobrindo plugins...")
    plugins = plugin_manager.discover_plugins()
    print(f"   {len(plugins)} plugin(s) encontrado(s)")

    print("📋 Carregando menu...")
    menu_manager.load_from_config(config._config)

    user = get_current_user(page)
    if user:
        build_main_app(page, user.to_dict())
    else:
        login_screen = AuthScreen(page, lambda ud: build_main_app(page, ud))
        page.add(login_screen.build())
        page.update()

    print("\n" + "=" * 50)
    print("🎯 DevStationPlatform — Sprints 1-3 ativos ✅")
    print("=" * 50)


if __name__ == "__main__":
    ft.app(target=main)
