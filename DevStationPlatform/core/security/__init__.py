"""
Security Module - RBAC, Authentication, Profile Management
"""

# Import models from core.models (single source of truth)
from core.models.user import User, Profile, Permission, Session

# Import RBAC components
from core.security.rbac import (
    rbac,
    RBACManager,
    PermissionCode,
    require_permission,
    require_any_permission,
    require_all_permissions,
    require_authenticated,
    require_profile,
    create_custom_profile,
    create_custom_permission,
    PermissionGroups
)

# Import managers
from core.security.profile_manager import ProfileManager
from core.security.dynamic_profiles import DynamicProfileManager

__all__ = [
    # Models
    "User",
    "Profile", 
    "Permission",
    "Session",
    
    # RBAC
    "rbac",
    "RBACManager",
    "PermissionCode",
    
    # Decorators
    "require_permission",
    "require_any_permission",
    "require_all_permissions",
    "require_authenticated",
    "require_profile",
    
    # Managers
    "ProfileManager",
    "DynamicProfileManager",
    
    # Helpers
    "create_custom_profile",
    "create_custom_permission",
    "PermissionGroups"
]