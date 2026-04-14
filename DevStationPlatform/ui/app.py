"""
DevStationPlatform - App principal NiceGUI
Sistema de rotas, autenticação e layout base
"""

from nicegui import ui, app
from typing import Optional, Dict, Any
import asyncio

# Importar serviços do backend
from core.config import Config
from core.security.rbac import rbac
from core.audit_logger import audit_logger
from core.kpi.collector import kpi_collector

# Instância singleton da configuração
config = Config()


class AuthService:
    """Serviço de autenticação - integração com backend RBAC"""

    @staticmethod
    def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autenticar usuário usando RBAC existente"""
        result = rbac.authenticate(username, password)
        if result:
            return {
                "id": result["user"].get("id"),
                "username": result["user"].get("username"),
                "full_name": result["user"].get("full_name"),
                "email": result["user"].get("email"),
                "profiles": result["user"].get("profiles", []),
                "token": result.get("token")
            }
        return None

    @staticmethod
    def validate_token(token: str) -> Optional[Dict[str, Any]]:
        """Validar token de sessão"""
        user = rbac.validate_token(token)
        if user:
            return user.to_dict() if hasattr(user, 'to_dict') else user
        return None

    @staticmethod
    def logout(token: str):
        """Encerrar sessão"""
        rbac.logout(token)


def init_storage():
    """Inicializar storage de sessão"""
    if not app.storage.user.get('authenticated'):
        app.storage.user.update({
            'authenticated': False,
            'user_data': {},
            'token': None
        })


def create_app():
    """Configurar e criar aplicação NiceGUI"""

    # Importar páginas (evitar import circular)
    from ui.pages import (login, dashboard, admin_users, admin_profiles, admin_audit,
                          tools_query, tools_table, designer,
                          user_profile, user_settings, tools_plugins)

    # Registrar rotas
    @ui.page('/')
    def index():
        """Redirecionar para login ou dashboard"""
        init_storage()
        if app.storage.user.get('authenticated'):
            ui.navigate.to('/dashboard')
        else:
            ui.navigate.to('/login')

    @ui.page('/login')
    def login_page():
        """Tela de login"""
        init_storage()
        login.render()

    @ui.page('/dashboard')
    def dashboard_page():
        """Dashboard principal"""
        init_storage()
        if not app.storage.user.get('authenticated'):
            ui.navigate.to('/login')
            return
        dashboard.render()

    @ui.page('/admin/users')
    def admin_users_page():
        """Gestão de usuários"""
        init_storage()
        if not app.storage.user.get('authenticated'):
            ui.navigate.to('/login')
            return
        admin_users.render()

    @ui.page('/admin/profiles')
    def admin_profiles_page():
        """Gestão de perfis"""
        init_storage()
        if not app.storage.user.get('authenticated'):
            ui.navigate.to('/login')
            return
        admin_profiles.render()

    @ui.page('/admin/audit')
    def admin_audit_page():
        """Visualização de logs"""
        init_storage()
        if not app.storage.user.get('authenticated'):
            ui.navigate.to('/login')
            return
        admin_audit.render()

    @ui.page('/tools/query')
    def tools_query_page():
        """Console SQL (DS_QUERY)"""
        init_storage()
        if not app.storage.user.get('authenticated'):
            ui.navigate.to('/login')
            return
        tools_query.render()

    @ui.page('/tools/table')
    def tools_table_page():
        """Navegador de tabelas (DS_TAB)"""
        init_storage()
        if not app.storage.user.get('authenticated'):
            ui.navigate.to('/login')
            return
        tools_table.render()

    @ui.page('/designer')
    def designer_page():
        """UI Designer (DS_DESIGNER)"""
        init_storage()
        if not app.storage.user.get('authenticated'):
            ui.navigate.to('/login')
            return
        designer.render()


    @ui.page('/profile')
    def profile_page():
        init_storage()
        if not app.storage.user.get('authenticated'):
            ui.navigate.to('/login'); return
        user_profile.render()

    @ui.page('/settings')
    def settings_page():
        init_storage()
        if not app.storage.user.get('authenticated'):
            ui.navigate.to('/login'); return
        user_settings.render()


    @ui.page('/tools/plugins')
    def tools_plugins_page():
        """Gerenciador de Plugins (DS_PLUGINS)"""
        init_storage()
        if not app.storage.user.get('authenticated'):
            ui.navigate.to('/login'); return
        tools_plugins.render()

    # Middleware de autenticação
    @app.middleware
    async def auth_middleware(request, call_next):
        """Middleware para verificar autenticação"""
        # Permitir acesso a login e recursos estáticos
        if request.url.path in ['/login', '/_nicegui', '/__nicegui']:
            return await call_next(request)

        init_storage()
        if not app.storage.user.get('authenticated'):
            # Redirecionar para login
            from starlette.responses import RedirectResponse
            return RedirectResponse('/login')

        return await call_next(request)

    # Configurar tema global (compartilhado entre todas as páginas)
    ui.add_head_html("""
    <style>
    :root {
        --ds-bg: #0e1117;
        --ds-surface: #161b22;
        --ds-accent: #58a6ff;
        --ds-text: #c9d1d9;
        --ds-text-secondary: #8b949e;
        --ds-border: #30363d;
        --ds-success: #238636;
        --ds-warning: #d29922;
        --ds-error: #f85149;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        margin: 0;
        background-color: var(--ds-bg);
        color: var(--ds-text);
    }

    .ds-card {
        background-color: var(--ds-surface);
        border: 1px solid var(--ds-border);
        border-radius: 6px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }

    .ds-btn-primary {
        background-color: var(--ds-accent) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
    }

    .ds-btn-secondary {
        background-color: var(--ds-surface) !important;
        color: var(--ds-text) !important;
        border: 1px solid var(--ds-border) !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
    }

    .ds-sidebar {
        background-color: #1976D2 !important;
        color: white !important;
    }

    .ds-header {
        background-color: var(--ds-surface) !important;
        border-bottom: 1px solid var(--ds-border) !important;
    }

    .ds-table {
        background-color: var(--ds-surface) !important;
        border: 1px solid var(--ds-border) !important;
        border-radius: 6px !important;
        overflow: hidden !important;
    }

    .ds-table th {
        background-color: rgba(255,255,255,0.05) !important;
        color: var(--ds-text) !important;
        font-weight: 600 !important;
        border-bottom: 1px solid var(--ds-border) !important;
    }

    .ds-table tr:hover {
        background-color: rgba(255,255,255,0.05) !important;
    }

    /* Force dark on all Quasar dialog overlays */
    .q-dialog .q-card { background-color: var(--ds-surface) !important; }
    .q-dialog .q-item { color: var(--ds-text) !important; }

    /* Inputs dark override */
    .q-field__control { background-color: var(--ds-bg) !important; }
    .q-field__native, .q-field__input { color: var(--ds-text) !important; }
    .q-field__label { color: var(--ds-text-secondary) !important; }

    /* Table rows dark */
    .q-table tbody tr { color: var(--ds-text) !important; }
    .q-table tbody td { border-bottom: 1px solid var(--ds-border) !important; }
    .q-table thead th { background: rgba(255,255,255,0.04) !important; color: var(--ds-text-secondary) !important; }
    </style>
    """, shared=True)

    print("[OK] App NiceGUI configurado com sucesso!")
    print(f"[INFO] Aplicação: {config.app_name}")
    print(f"[URL] http://localhost:8080")


# Utilitários de autenticação
def login_user(user_data: Dict[str, Any], token: str):
    """Realizar login do usuário"""
    init_storage()
    app.storage.user.update({
        'authenticated': True,
        'user_data': user_data,
        'token': token
    })

    # Registrar login no audit log
    audit_logger.log(
        user_id=user_data.get("id", 0),
        user_name=user_data.get("username", "?"),
        user_profiles=", ".join(user_data.get("profiles", [])),
        transaction_code="DS_AUTH", action_type="LOGIN",
        object_type="SESSION", object_name="Sessão iniciada",
        kpi_tags=["auth"],
    )
    kpi_collector.record_transaction("DS_AUTH", 0, True, user_data.get("id", 0))


def logout_user():
    """Realizar logout do usuário"""
    init_storage()
    token = app.storage.user.get('token')
    if token:
        AuthService.logout(token)

    user_data = app.storage.user.get('user_data', {})

    # Registrar logout no audit log
    audit_logger.log(
        user_id=user_data.get("id", 0),
        user_name=user_data.get("username", "?"),
        user_profiles=", ".join(user_data.get("profiles", [])),
        transaction_code="DS_AUTH", action_type="LOGOUT",
        object_type="SESSION", object_name="Sessão encerrada",
    )

    # Limpar sessão
    app.storage.user.clear()
    app.storage.user.update({
        'authenticated': False,
        'user_data': {},
        'token': None
    })


def get_current_user() -> Optional[Dict[str, Any]]:
    """Obter dados do usuário atual"""
    init_storage()
    if app.storage.user.get('authenticated'):
        return app.storage.user.get('user_data')
    return None


def requires_permission(permission_code: str):
    """Decorador para verificar permissões"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_data = get_current_user()
            if not user_data:
                ui.navigate.to('/login')
                return

            # TODO: Implementar verificação de permissão usando RBAC
            # Por enquanto, apenas verifica se está autenticado
            return await func(*args, **kwargs)
        return wrapper
    return decorator