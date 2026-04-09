"""
DevStationPlatform - Main Entry Point
Sprint 2 + Sprint 3 integrados: Auditoria, ChangeLog, KPI Dashboard
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


CLR_PRIMARY = ft.Colors.BLUE_700
CLR_PRIMARY_DARK = ft.Colors.BLUE_900
CLR_BG = ft.Colors.GREY_50

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

    default_permissions = config.get("security.default_permissions", [])
    permissions_created = {}
    for perm_data in default_permissions:
        perm = Permission(
            code=perm_data["code"],
            name=perm_data["name"],
            category=perm_data.get("category", "GENERAL"),
            is_system=True,
        )
        session.add(perm)
        session.flush()
        permissions_created[perm.code] = perm

    default_profiles = config.get("security.default_profiles", [])
    profiles = {}
    for profile_data in default_profiles:
        profile = Profile(
            code=profile_data["code"],
            name=profile_data["name"],
            description=profile_data.get("description", ""),
            is_system=True,
            priority=profile_data.get("priority", 0),
        )
        session.add(profile)
        session.flush()
        profiles[profile.code] = profile

    for profile_data in default_profiles:
        for parent_code in profile_data.get("inherit_from", []):
            if parent_code in profiles:
                profiles[profile_data["code"]].parents.append(profiles[parent_code])

    admin_profile = profiles.get("ADMIN")
    if admin_profile:
        admin_profile.permissions = list(permissions_created.values())

    admin = User(
        username="admin", email="admin@devstation.com",
        full_name="Administrator", is_active=True, is_system=True,
    )
    admin.set_password("admin123")
    if admin_profile:
        admin.profiles.append(admin_profile)
    session.add(admin)

    developer = User(
        username="developer", email="developer@devstation.com",
        full_name="Developer User", is_active=True,
    )
    developer.set_password("dev123")
    dev_profile = profiles.get("DEVELOPER")
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
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1280
    page.window_height = 780
    page.padding = 0
    page.bgcolor = CLR_BG

    audit_logger.log(
        user_id=user_data.get("id", 0),
        user_name=user_data.get("username", "?"),
        user_profiles=", ".join(user_data.get("profiles", [])),
        transaction_code="DS_AUTH", action_type="LOGIN",
        object_type="SESSION", object_name="Sessão iniciada",
        kpi_tags=["auth"],
    )
    kpi_collector.record_transaction("DS_AUTH", 0, True, user_data.get("id", 0))

    content_area = ft.Container(expand=True, bgcolor=CLR_BG)
    _active_view: list = [_VIEW_DASHBOARD]

    nav_items = [
        {"key": _VIEW_DASHBOARD, "icon": ft.Icons.DASHBOARD_OUTLINED,    "icon_sel": ft.Icons.DASHBOARD,    "label": "Dashboard",    "desc": "",             "min_profile": None},
        {"key": _VIEW_AUDIT,     "icon": ft.Icons.RECEIPT_LONG_OUTLINED,  "icon_sel": ft.Icons.RECEIPT_LONG, "label": "DS_AUDIT",     "desc": "Auditoria",    "min_profile": "ADMIN"},
        {"key": _VIEW_CHANGELOG, "icon": ft.Icons.EDIT_NOTE_OUTLINED,     "icon_sel": ft.Icons.EDIT_NOTE,    "label": "DS_CHG",       "desc": "ChangeLog",    "min_profile": "DEVELOPER"},
        {"key": _VIEW_KPI,       "icon": ft.Icons.INSIGHTS_OUTLINED,      "icon_sel": ft.Icons.INSIGHTS,     "label": "DS_KPI_DASH",  "desc": "KPIs",         "min_profile": "BANALYST"},
    ]

    sidebar_buttons: dict = {}

    def _has_access(min_profile):
        if min_profile is None:
            return True
        hierarchy = ["USER", "PUSER", "BANALYST", "DEVELOPER", "CORE_DEV", "DEV_ALL", "ADMIN"]
        min_idx = hierarchy.index(min_profile) if min_profile in hierarchy else 999
        for p in user_data.get("profiles", []):
            if p in hierarchy and hierarchy.index(p) >= min_idx:
                return True
        return False

    def _load_view(view_key: str):
        _active_view[0] = view_key
        for key, btn in sidebar_buttons.items():
            btn.bgcolor = ft.Colors.BLUE_800 if key == view_key else ft.Colors.TRANSPARENT
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
            view = ft.Container(content=ft.Text(f"View '{view_key}' não implementada."), padding=40)

        content_area.content = view
        content_area.update()

    def _make_nav_button(item: dict) -> ft.Container:
        accessible = _has_access(item["min_profile"])
        is_active = item["key"] == _VIEW_DASHBOARD

        def on_click(e, key=item["key"], acc=accessible):
            if not acc:
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"❌ Perfil insuficiente para {key}"),
                    bgcolor=ft.Colors.RED_700, open=True,
                )
                page.update()
                return
            _load_view(key)

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
            padding=ft.padding.symmetric(horizontal=14, vertical=10),
            on_click=on_click,
            opacity=1.0 if accessible else 0.5,
        )

        def on_hover(e, key=item["key"]):
            if key != _active_view[0]:
                e.control.bgcolor = ft.Colors.BLUE_800 if e.data == "true" else ft.Colors.TRANSPARENT
                e.control.update()

        btn.on_hover = on_hover
        sidebar_buttons[item["key"]] = btn
        return btn

    nav_buttons = [_make_nav_button(item) for item in nav_items]

    user_info = ft.Container(
        content=ft.Column(
            [
                ft.Divider(height=1, color=ft.Colors.BLUE_600),
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(
                                (user_data.get("username") or "?")[0].upper(),
                                size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD,
                            ),
                            bgcolor=ft.Colors.BLUE_400,
                            border_radius=50, width=34, height=34,
                            alignment=ft.alignment.center,
                        ),
                        ft.Column(
                            [
                                ft.Text(user_data.get("username", "—"), size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                ft.Text(", ".join(user_data.get("profiles", [])), size=10, color=ft.Colors.BLUE_200),
                            ],
                            spacing=1, tight=True, expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT, icon_color=ft.Colors.BLUE_200,
                            tooltip="Sair",
                            on_click=lambda e: _do_logout(),
                        ),
                    ],
                    spacing=8,
                ),
            ],
            spacing=8,
        ),
        padding=ft.padding.symmetric(horizontal=10, vertical=8),
    )

    sidebar = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("DevStation", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text("Platform v1.0", size=10, color=ft.Colors.BLUE_200),
                        ],
                        spacing=0, tight=True,
                    ),
                    padding=ft.padding.symmetric(horizontal=14, vertical=18),
                ),
                ft.Divider(height=1, color=ft.Colors.BLUE_600),
                ft.Container(height=6),
                ft.Container(
                    content=ft.Column(nav_buttons, spacing=2),
                    padding=ft.padding.symmetric(horizontal=8),
                    expand=True,
                ),
                user_info,
            ],
            spacing=0, expand=True,
        ),
        bgcolor=CLR_PRIMARY_DARK,
        width=210,
    )

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


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

def main(page: ft.Page):
    page.title = config.app_name
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1280
    page.window_height = 780
    page.padding = 0
    page.bgcolor = CLR_BG

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
        login_screen = AuthScreen(page, lambda user_data: build_main_app(page, user_data))
        page.add(login_screen.build())
        page.update()

    print("\n" + "=" * 50)
    print("🎯 DevStationPlatform — Sprints 1-3 ativos ✅")
    print("=" * 50)


if __name__ == "__main__":
    ft.app(target=main)
