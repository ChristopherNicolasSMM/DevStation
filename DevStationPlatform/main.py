"""
DevStationPlatform - Main Entry Point
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import flet as ft
from core import config, plugin_manager, menu_manager
from core.models.base import db_manager
from core.models.user import User
from core.security.auth import AuthScreen, get_current_user, logout


def setup_database():
    """Initialize database with default data"""
    db_manager.create_tables()
    session = db_manager.get_session()
    
    if session.query(User).count() == 0:
        seed_default_data(session)
    
    session.close()


def seed_default_data(session):
    """Seed database with default profiles and permissions"""
    from core.models.user import Profile, Permission
    
    # Create default permissions
    default_permissions = config.get("security.default_permissions", [])
    permissions_created = {}
    
    for perm_data in default_permissions:
        perm = Permission(
            code=perm_data["code"],
            name=perm_data["name"],
            category=perm_data.get("category", "GENERAL"),
            is_system=True
        )
        session.add(perm)
        session.flush()
        permissions_created[perm.code] = perm
    
    # Create default profiles
    default_profiles = config.get("security.default_profiles", [])
    profiles = {}
    
    for profile_data in default_profiles:
        profile = Profile(
            code=profile_data["code"],
            name=profile_data["name"],
            description=profile_data.get("description", ""),
            is_system=True,
            priority=profile_data.get("priority", 0)
        )
        session.add(profile)
        session.flush()
        profiles[profile.code] = profile
    
    # Set up inheritance
    for profile_data in default_profiles:
        inherit_from = profile_data.get("inherit_from", [])
        if inherit_from:
            profile = profiles[profile_data["code"]]
            for parent_code in inherit_from:
                if parent_code in profiles:
                    profile.parents.append(profiles[parent_code])
    
    # Assign permissions to ADMIN
    admin_profile = profiles.get("ADMIN")
    if admin_profile:
        admin_profile.permissions = list(permissions_created.values())
    
    # Create admin user
    admin = User(
        username="admin",
        email="admin@devstation.com",
        full_name="Administrator",
        is_active=True,
        is_system=True
    )
    admin.set_password("admin123")
    if admin_profile:
        admin.profiles.append(admin_profile)
    session.add(admin)
    
    # Create demo developer
    developer = User(
        username="developer",
        email="developer@devstation.com",
        full_name="Developer User",
        is_active=True
    )
    developer.set_password("dev123")
    dev_profile = profiles.get("DEVELOPER")
    if dev_profile:
        developer.profiles.append(dev_profile)
    session.add(developer)
    
    session.commit()
    print("✅ Database seeded!")


def build_main_app(page: ft.Page, user_data: dict):
    """Constrói a aplicação principal após login"""
    page.title = f"{config.app_name} - {user_data.get('full_name', user_data.get('username'))}"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1280
    page.window_height = 720
    page.padding = 20
    
    # Drawer menu (sidebar)
    drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(height=12),
            ft.NavigationDrawerDestination(
                icon=ft.icons.DASHBOARD,
                label="Dashboard",
                selected_icon=ft.icons.DASHBOARD_OUTLINED,
            ),
            ft.Divider(thickness=1),
            ft.NavigationDrawerDestination(
                icon=ft.icons.CODE,
                label="Query Console",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.icons.TABLE_VIEW,
                label="Table Browser",
            ),
            ft.Divider(thickness=1),
            ft.NavigationDrawerDestination(
                icon=ft.icons.ADMIN_PANEL_SETTINGS,
                label="Administração",
            ),
            ft.Container(expand=True),
            ft.NavigationDrawerDestination(
                icon=ft.icons.LOGOUT,
                label="Sair",
                on_click=lambda e: logout(page),
            ),
        ],
    )
    
    # AppBar
    page.appbar = ft.AppBar(
        title=ft.Text(f"DevStationPlatform"),
        center_title=False,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
        actions=[
            ft.IconButton(icon=ft.icons.PERSON, tooltip=user_data.get('username')),
            ft.IconButton(icon=ft.icons.SETTINGS, tooltip="Configurações"),
        ],
        leading=ft.IconButton(icon=ft.icons.MENU, on_click=lambda e: page.open(drawer)),
    )
    
    # Main content
    content = ft.Container(
        content=ft.Column(
            [
                ft.Text(f"Bem-vindo, {user_data.get('full_name', user_data.get('username'))}!", 
                       size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Dashboard principal da plataforma", size=14, color=ft.Colors.GREY_600),
                ft.Divider(),
                ft.Text("📊 Status do Sistema:", weight=ft.FontWeight.BOLD, size=16),
                ft.Text("✅ Core Engine: ONLINE"),
                ft.Text("✅ Database: CONECTADO"),
                ft.Text("✅ Security Module: ATIVO"),
                ft.Divider(),
                ft.Text("📋 Informações do Usuário:", weight=ft.FontWeight.BOLD, size=16),
                ft.Text(f"• Usuário: {user_data.get('username')}"),
                ft.Text(f"• Email: {user_data.get('email')}"),
                ft.Text(f"• Perfis: {', '.join(user_data.get('profiles', []))}"),
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=30,
        expand=True,
    )
    
    page.add(content)
    page.drawer = drawer
    page.update()


def main(page: ft.Page):
    """Main entry point - shows login screen"""
    page.title = config.app_name
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1280
    page.window_height = 720
    page.padding = 0
    
    # Setup database
    print("📦 Setting up database...")
    setup_database()
    
    # Discover plugins
    print("🔍 Discovering plugins...")
    plugins = plugin_manager.discover_plugins()
    print(f"   Discovered {len(plugins)} plugins")
    
    # Load menu
    print("📋 Loading menu...")
    menu_manager.load_from_config(config._config)
    
    # Check if already authenticated
    user = get_current_user(page)
    if user:
        build_main_app(page, user.to_dict())
    else:
        # Show login screen
        login_screen = AuthScreen(page, lambda user_data: build_main_app(page, user_data))
        page.add(login_screen.build())
        page.update()
    
    print("\n" + "="*50)
    print("🎯 DevStationPlatform está rodando!")
    print("="*50)


if __name__ == "__main__":
    ft.app(target=main)