"""
Layout base - Sidebar, header e estrutura principal
Estilo conforme HTML de referência
"""

from nicegui import ui
from typing import Optional, Callable
from ui.app import get_current_user, logout_user


class MainLayout:
    """Layout principal com sidebar e header"""

    def __init__(self, title: str = "DevStationPlatform"):
        self.title = title
        self.user_data = get_current_user()
        self.sidebar_items = []
        self.current_page = "dashboard"
        self._define_menu_items()

    def _define_menu_items(self):
        """Definir itens do menu baseado nas permissões do usuário"""
        profiles = self.user_data.get('profiles', []) if self.user_data else []
        HIERARCHY = ["USER", "PUSER", "BANALYST", "DEVELOPER", "CORE_DEV", "DEV_ALL", "ADMIN"]

        def has_access(min_profile: Optional[str]) -> bool:
            if min_profile is None:
                return True
            min_idx = HIERARCHY.index(min_profile) if min_profile in HIERARCHY else 999
            return any(
                p in HIERARCHY and HIERARCHY.index(p) >= min_idx
                for p in profiles
            )

        self.sidebar_items = [
            {"key": "dashboard",  "icon": "dashboard",       "label": "Dashboard",    "route": "/dashboard",       "min": None},
            {"key": "audit",      "icon": "receipt_long",    "label": "DS_AUDIT",     "route": "/admin/audit",     "min": "ADMIN"},
            {"key": "users",      "icon": "people",          "label": "DS_USERS",     "route": "/admin/users",     "min": "ADMIN"},
            {"key": "profiles",   "icon": "security",        "label": "DS_PROFILES",  "route": "/admin/profiles",  "min": "ADMIN"},
            {"key": "query",      "icon": "terminal",        "label": "DS_QUERY",     "route": "/tools/query",     "min": "DEVELOPER"},
            {"key": "plugins",    "icon": "extension",       "label": "DS_PLUGINS",   "route": "/tools/plugins",   "min": "DEVELOPER"},
            {"key": "designer",   "icon": "design_services", "label": "DS_DESIGNER",  "route": "/designer",        "min": "DEVELOPER"},
        ]
        self.sidebar_items = [i for i in self.sidebar_items if has_access(i.get("min"))]

    def build_sidebar(self):
        """Construir sidebar (menu lateral)"""
        with ui.left_drawer(fixed=True).classes('bg-[#1976D2] text-white w-64'):
            # Logo
            with ui.row().classes('items-center p-4 gap-3'):
                with ui.card().classes('w-8 h-8 bg-white/25 rounded items-center justify-center'):
                    ui.label('DS').classes('text-white text-sm font-bold')
                with ui.column().classes('gap-0'):
                    ui.label('DevStation').classes('text-white text-sm font-bold')
                    ui.label('Platform v1.0').classes('text-white/55 text-xs')

            ui.separator().classes('bg-white/15')

            # Menu items
            with ui.column().classes('p-2 gap-1'):
                for item in self.sidebar_items:
                    is_active = self.current_page == item["key"]
                    with ui.button(
                        on_click=lambda r=item["route"]: ui.navigate.to(r)
                    ).classes(
                        f'w-full justify-start {"bg-white/20" if is_active else "bg-transparent"} '
                        'hover:bg-white/15 rounded-lg px-3 py-2'
                    ):
                        ui.icon(item["icon"]).classes('text-white text-base')
                        ui.label(item["label"]).classes('text-white text-sm font-medium')

            # Rodapé do sidebar com info do usuário + logout
            with ui.column().classes('absolute bottom-0 left-0 right-0 p-4 border-t border-white/15'):
                with ui.row().classes('items-center gap-3'):
                    username = self.user_data.get('username', '?') if self.user_data else '?'
                    with ui.card().classes('w-8 h-8 bg-blue-400 rounded-full items-center justify-center'):
                        ui.label(username[0].upper()).classes('text-white text-sm font-bold')
                    with ui.column().classes('gap-0 flex-1'):
                        ui.label(username).classes('text-white text-sm font-medium')
                        if self.user_data:
                            profiles = self.user_data.get('profiles', [])
                            ui.label(', '.join(profiles)).classes('text-white/55 text-xs')
                    ui.button(icon='logout', on_click=self._do_logout).props('flat dense').classes('text-white')

    def build_header(self):
        """Construir header (topo)"""
        with ui.header(fixed=True).classes('bg-[#161b22] border-b border-[#30363d] h-16'):
            with ui.row().classes('items-center w-full px-6 h-full'):
                ui.label(self.title).classes('text-white text-lg font-semibold')
                ui.space()

                with ui.row().classes('items-center gap-2'):
                    # Notificações
                    ui.button(icon='notifications').props('flat dense color=white')
                    # Tema
                    ui.button(icon='dark_mode').props('flat dense color=white')

                    # Menu do usuário — botão fora do menu, menu dentro do botão
                    if self.user_data:
                        username = self.user_data.get('username', '')
                        with ui.button(icon='person').props('flat dense color=white'):
                            ui.label(username).classes('text-white text-sm ml-1')
                            with ui.menu().classes('bg-[#161b22] border border-[#30363d]'):
                                ui.menu_item('Meu Perfil', on_click=lambda: ui.navigate.to('/profile'))
                                ui.menu_item('Configurações', on_click=lambda: ui.navigate.to('/settings'))
                                ui.separator()
                                ui.menu_item('Sair', on_click=self._do_logout)

    def build(self, content: Callable):
        """Construir layout completo"""
        self.build_sidebar()
        self.build_header()
        with ui.column().classes('pt-16 pl-64 w-full min-h-screen bg-[#0e1117] p-6'):
            content()

    def _do_logout(self):
        logout_user()
        ui.navigate.to('/login')


def create_page_layout(title: str = "DevStationPlatform"):
    """Decorador para criar página com layout"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            layout = MainLayout(title)
            layout.build(lambda: func(*args, **kwargs))
        return wrapper
    return decorator


# ── Componentes utilitários ──────────────────────────────────────────────────

def metric_card(title: str, value: str, icon: str, color: str = "blue"):
    """Card de métrica para dashboard"""
    color_classes = {
        "blue":   "bg-blue-500/10   border-blue-500/20   text-blue-400",
        "green":  "bg-green-500/10  border-green-500/20  text-green-400",
        "orange": "bg-orange-500/10 border-orange-500/20 text-orange-400",
        "red":    "bg-red-500/10    border-red-500/20    text-red-400",
        "purple": "bg-purple-500/10 border-purple-500/20 text-purple-400",
    }
    with ui.card().classes(f'border {color_classes.get(color, color_classes["blue"])} p-4'):
        with ui.row().classes('items-center justify-between'):
            with ui.column().classes('gap-1'):
                ui.label(title).classes('text-[#8b949e] text-sm')
                ui.label(value).classes('text-white text-2xl font-bold')
            ui.icon(icon).classes('text-2xl')


class data_card:
    """Context manager — card de dados com título"""
    def __init__(self, title: str):
        self.title = title
        self._card = None
        self._col = None

    def __enter__(self):
        self._card = ui.card().classes('bg-[#161b22] border border-[#30363d] w-full')
        self._card.__enter__()
        self._col = ui.column().classes('gap-4 w-full')
        self._col.__enter__()
        ui.label(self.title).classes('text-white text-lg font-semibold border-b border-[#30363d] pb-2')
        return self

    def __exit__(self, *args):
        self._col.__exit__(*args)
        self._card.__exit__(*args)
