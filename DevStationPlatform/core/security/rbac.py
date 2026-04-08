"""
RBAC - Role Based Access Control
Sistema de controle de acesso baseado em perfis dinâmicos
"""

from functools import wraps
from typing import List, Set, Optional, Callable, Any
from enum import Enum
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

from core.models.base import db_manager
from core.security.models import User, Profile, Permission, Session

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
JWT_SECRET = "devstation_secret_key_change_in_production"  # TODO: Move to config
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


class PermissionCode(str, Enum):
    """Standard permission codes for the system"""
    
    # Transactions
    TRANSACTION_EXECUTE = "transaction.execute"
    TRANSACTION_CREATE = "transaction.create"
    TRANSACTION_MODIFY_DS = "transaction.modify.ds"
    TRANSACTION_DELETE = "transaction.delete"
    
    # Plugins
    PLUGIN_INSTALL = "plugin.install"
    PLUGIN_DEVELOP = "plugin.develop"
    PLUGIN_PUBLISH = "plugin.publish"
    PLUGIN_DELETE = "plugin.delete"
    
    # Data
    DATA_QUERY = "data.query"
    DATA_EXPORT = "data.export"
    DATA_IMPORT = "data.import"
    DATA_DELETE = "data.delete"
    
    # Admin
    ADMIN_USERS = "admin.users"
    ADMIN_PROFILES = "admin.profiles"
    ADMIN_PERMISSIONS = "admin.permissions"
    ADMIN_AUDIT = "admin.audit"
    ADMIN_BACKUP = "admin.backup"
    ADMIN_CONFIG = "admin.config"
    
    # IA
    IA_CONSULT = "ia.consult"
    IA_TRAIN = "ia.train"
    IA_MANAGE = "ia.manage"
    
    # Workflows
    WORKFLOW_EXECUTE = "workflow.execute"
    WORKFLOW_CREATE = "workflow.create"
    WORKFLOW_PUBLISH = "workflow.publish"
    WORKFLOW_DELETE = "workflow.delete"
    
    # APIs
    API_CONSUME = "api.consume"
    API_CREATE = "api.create"
    API_EXPOSE = "api.expose"
    API_DELETE = "api.delete"
    
    # System
    SYSTEM_VIEW_LOGS = "system.view_logs"
    SYSTEM_MANAGE_CACHE = "system.manage_cache"
    SYSTEM_VIEW_STATUS = "system.view_status"


class RBACManager:
    """
    RBAC Manager - Handles authentication, authorization, and session management
    """
    
    def __init__(self):
        self._current_user: Optional[User] = None
    
    def authenticate(self, username: str, password: str, ip_address: str = None) -> Optional[dict]:
        """
        Authenticate a user and create a session
        Returns token and user info or None if authentication fails
        """
        session_db = db_manager.get_session()
        
        # Find user
        user = session_db.query(User).filter(User.username == username).first()
        
        if not user:
            return None
        
        # Check if user is locked
        if user.is_locked:
            return None
        
        # Verify password
        if not user.verify_password(password):
            user.login_attempts += 1
            if user.login_attempts >= 5:
                user.is_locked = True
            session_db.commit()
            return None
        
        # Reset login attempts on success
        user.login_attempts = 0
        user.last_login = datetime.utcnow()
        session_db.commit()
        
        # Generate JWT token
        token = self._generate_token(user)
        
        # Create session record
        user_session = Session(
            session_id=self._generate_session_id(),
            user_id=user.id,
            token=token,
            ip_address=ip_address,
            expires_at=datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        )
        session_db.add(user_session)
        session_db.commit()
        
        self._current_user = user
        
        return {
            "token": token,
            "user": user.to_dict(),
            "expires_in": JWT_EXPIRATION_HOURS * 3600
        }
    
    def validate_token(self, token: str) -> Optional[User]:
        """
        Validate JWT token and return user if valid
        """
        try:
            # Decode token
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("user_id")
            
            if not user_id:
                return None
            
            # Check session in database
            session_db = db_manager.get_session()
            user_session = session_db.query(Session).filter(
                Session.token == token,
                Session.is_active == True
            ).first()
            
            if not user_session or user_session.is_expired():
                return None
            
            # Update last activity
            user_session.last_activity = datetime.utcnow()
            session_db.commit()
            
            # Get user
            user = session_db.query(User).filter(User.id == user_id).first()
            self._current_user = user
            return user
            
        except jwt.InvalidTokenError:
            return None
    
    def logout(self, token: str) -> bool:
        """
        Invalidate user session
        """
        session_db = db_manager.get_session()
        user_session = session_db.query(Session).filter(Session.token == token).first()
        
        if user_session:
            user_session.is_active = False
            session_db.commit()
            return True
        
        return False
    
    def check_permission(self, user: User, permission_code: str) -> bool:
        """
        Check if user has a specific permission
        """
        if not user or not user.is_active:
            return False
        
        return user.has_permission(permission_code)
    
    def get_user_permissions(self, user: User) -> Set[str]:
        """
        Get all permissions for a user
        """
        if not user:
            return set()
        return user.get_all_permissions()
    
    def has_any_permission(self, user: User, permissions: List[str]) -> bool:
        """
        Check if user has any of the listed permissions
        """
        user_perms = self.get_user_permissions(user)
        return any(p in user_perms for p in permissions)
    
    def has_all_permissions(self, user: User, permissions: List[str]) -> bool:
        """
        Check if user has all of the listed permissions
        """
        user_perms = self.get_user_permissions(user)
        return all(p in user_perms for p in permissions)
    
    def _generate_token(self, user: User) -> str:
        """
        Generate JWT token for user
        """
        payload = {
            "user_id": user.id,
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def _generate_session_id(self) -> str:
        """
        Generate unique session ID
        """
        import uuid
        return str(uuid.uuid4())
    
    @property
    def current_user(self) -> Optional[User]:
        """Get current authenticated user"""
        return self._current_user


# Global RBAC instance
rbac = RBACManager()


# Decorators for permission checking
def require_permission(permission_code: str):
    """
    Decorator to require a specific permission
    Usage: @require_permission("admin.users")
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = rbac.current_user
            if not user or not rbac.check_permission(user, permission_code):
                raise PermissionError(f"Permission denied: {permission_code}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(permission_codes: List[str]):
    """
    Decorator to require any of the listed permissions
    Usage: @require_any_permission(["admin.users", "admin.profiles"])
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = rbac.current_user
            if not user or not rbac.has_any_permission(user, permission_codes):
                raise PermissionError(f"Permission denied. Need one of: {permission_codes}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_all_permissions(permission_codes: List[str]):
    """
    Decorator to require all of the listed permissions
    Usage: @require_all_permissions(["admin.users", "admin.audit"])
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = rbac.current_user
            if not user or not rbac.has_all_permissions(user, permission_codes):
                raise PermissionError(f"Permission denied. Need all of: {permission_codes}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_authenticated(func: Callable):
    """
    Decorator to require authentication
    Usage: @require_authenticated
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not rbac.current_user:
            raise PermissionError("Authentication required")
        return func(*args, **kwargs)
    return wrapper


def require_profile(profile_code: str):
    """
    Decorator to require a specific profile
    Usage: @require_profile("ADMIN")
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = rbac.current_user
            if not user:
                raise PermissionError("Authentication required")
            
            has_profile = any(p.code == profile_code for p in user.profiles)
            if not has_profile:
                raise PermissionError(f"Profile {profile_code} required")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Helper functions for profile management
def create_custom_profile(
    code: str,
    name: str,
    description: str = "",
    permissions: List[str] = None,
    parents: List[str] = None,
    priority: int = 0
) -> Profile:
    """
    Create a custom profile at runtime
    """
    from core.security.profile_manager import ProfileManager
    
    manager = ProfileManager()
    return manager.create_profile(
        code=code,
        name=name,
        description=description,
        permissions=permissions,
        parents=parents,
        priority=priority
    )


def create_custom_permission(
    code: str,
    name: str,
    category: str = "CUSTOM",
    description: str = ""
) -> Permission:
    """
    Create a custom permission at runtime
    """
    from core.security.profile_manager import ProfileManager
    
    manager = ProfileManager()
    return manager.create_permission(
        code=code,
        name=name,
        category=category,
        description=description
    )


# Pre-defined permission groups for easy reference
class PermissionGroups:
    """Pre-defined permission groups for common scenarios"""
    
    # Full access for developers
    DEV_FULL = [
        PermissionCode.TRANSACTION_EXECUTE,
        PermissionCode.TRANSACTION_CREATE,
        PermissionCode.PLUGIN_INSTALL,
        PermissionCode.PLUGIN_DEVELOP,
        PermissionCode.PLUGIN_PUBLISH,
        PermissionCode.DATA_QUERY,
        PermissionCode.DATA_EXPORT,
        PermissionCode.DATA_IMPORT,
        PermissionCode.WORKFLOW_CREATE,
        PermissionCode.WORKFLOW_PUBLISH,
        PermissionCode.API_CREATE,
        PermissionCode.API_EXPOSE,
        PermissionCode.IA_CONSULT,
    ]
    
    # Read-only access
    READ_ONLY = [
        PermissionCode.TRANSACTION_EXECUTE,
        PermissionCode.DATA_QUERY,
        PermissionCode.WORKFLOW_EXECUTE,
        PermissionCode.API_CONSUME,
    ]
    
    # Admin access
    ADMIN_FULL = [
        PermissionCode.ADMIN_USERS,
        PermissionCode.ADMIN_PROFILES,
        PermissionCode.ADMIN_PERMISSIONS,
        PermissionCode.ADMIN_AUDIT,
        PermissionCode.ADMIN_BACKUP,
        PermissionCode.ADMIN_CONFIG,
        PermissionCode.SYSTEM_VIEW_LOGS,
        PermissionCode.SYSTEM_MANAGE_CACHE,
        PermissionCode.SYSTEM_VIEW_STATUS,
    ]
    
    # Analyst access
    ANALYST = [
        PermissionCode.TRANSACTION_EXECUTE,
        PermissionCode.DATA_QUERY,
        PermissionCode.DATA_EXPORT,
        PermissionCode.WORKFLOW_EXECUTE,
        PermissionCode.WORKFLOW_CREATE,
        PermissionCode.API_CONSUME,
    ]