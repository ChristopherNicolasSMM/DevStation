"""
Pages package - Telas da aplicação
"""

from . import login
from . import dashboard
from . import admin_users
from . import admin_profiles
from . import admin_audit
from . import tools_query
from . import tools_table
from . import designer
from . import user_profile
from . import user_settings
from . import tools_plugins

__all__ = [
    'login', 'dashboard',
    'admin_users', 'admin_profiles', 'admin_audit',
    'tools_query', 'tools_table', 'designer',
    'user_profile', 'user_settings',
    'tools_plugins',
]
