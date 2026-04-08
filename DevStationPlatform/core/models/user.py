"""
User, Profile and Permission models
All association tables are defined here to avoid duplication
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from passlib.context import CryptContext
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from typing import List, Set, Optional

from core.models.base import Base

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================================================
# ASSOCIATION TABLES - Defined once here to avoid duplication
# ============================================================================

# User <-> Profile association (many-to-many)
user_profile_association = Table(
    'user_profile',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('profile_id', Integer, ForeignKey('profiles.id', ondelete='CASCADE')),
    extend_existing=True  # Allow redefinition if already exists
)

# Profile <-> Permission association (many-to-many)
profile_permission_association = Table(
    'profile_permission',
    Base.metadata,
    Column('profile_id', Integer, ForeignKey('profiles.id', ondelete='CASCADE')),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE')),
    extend_existing=True
)

# Profile inheritance (self-referential many-to-many)
profile_inheritance = Table(
    'profile_inheritance',
    Base.metadata,
    Column('parent_profile_id', Integer, ForeignKey('profiles.id', ondelete='CASCADE')),
    Column('child_profile_id', Integer, ForeignKey('profiles.id', ondelete='CASCADE')),
    extend_existing=True
)


# ============================================================================
# MODEL CLASSES
# ============================================================================

class User(Base):
    """System User Model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False)
    full_name = Column(String(200))
    password_hash = Column(String(200), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    is_system = Column(Boolean, default=False)
    
    # Audit
    last_login = Column(DateTime)
    login_attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(String(100))
    
    # Preferences
    theme = Column(String(50), default="light")
    language = Column(String(10), default="pt_BR")
    preferences = Column(JSON, default=dict)
    
    # Relationships
    profiles = relationship(
        "Profile", 
        secondary=user_profile_association, 
        back_populates="users"
    )
    

    def set_password(self, password: str):
        """Hash and set password"""
        # Garantir que a senha não ultrapasse 72 bytes
        if isinstance(password, str):
            password_bytes = password.encode('utf-8')[:72]
            password = password_bytes.decode('utf-8', errors='ignore')
        self.password_hash = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(password, self.password_hash)
    
    def has_permission(self, permission_code: str) -> bool:
        """Check if user has a specific permission"""
        for profile in self.profiles:
            if profile.has_permission(permission_code):
                return True
        return False
    
    def get_all_permissions(self) -> Set[str]:
        """Get all permissions from all user profiles"""
        permissions = set()
        for profile in self.profiles:
            permissions.update(profile.get_all_permissions())
        return permissions
    
    def get_highest_priority_profile(self) -> Optional['Profile']:
        """Get the profile with highest priority"""
        if not self.profiles:
            return None
        return max(self.profiles, key=lambda p: p.priority)
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_locked": self.is_locked,
            "profiles": [p.code for p in self.profiles],
            "theme": self.theme,
            "language": self.language,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Profile(Base):
    """
    Access Profile - Dynamic, can be created/edited/deleted at runtime
    """
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    
    # Configuration
    is_system = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(String(100))
    
    # Custom attributes
    custom_attributes = Column(JSON, default=dict)
    
    # Relationships
    permissions = relationship(
        "Permission", 
        secondary=profile_permission_association, 
        back_populates="profiles"
    )
    users = relationship(
        "User", 
        secondary=user_profile_association, 
        back_populates="profiles"
    )
    
    # Self-referential inheritance
    parents = relationship(
        "Profile",
        secondary=profile_inheritance,
        primaryjoin=id == profile_inheritance.c.child_profile_id,
        secondaryjoin=id == profile_inheritance.c.parent_profile_id,
        backref="children"
    )
    
    def get_all_permissions(self) -> Set[str]:
        """Get all permissions including inherited ones"""
        permissions = set()
        
        # Direct permissions
        for perm in self.permissions:
            permissions.add(perm.code)
        
        # Inherited from parents
        for parent in self.parents:
            permissions.update(parent.get_all_permissions())
        
        return permissions
    
    def has_permission(self, permission_code: str) -> bool:
        """Check if profile has specific permission"""
        return permission_code in self.get_all_permissions()
    
    def to_dict(self) -> dict:
        """Convert profile to dictionary"""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "is_system": self.is_system,
            "is_active": self.is_active,
            "priority": self.priority,
            "permissions": [p.code for p in self.permissions],
            "parents": [p.code for p in self.parents]
        }


class Permission(Base):
    """Individual permission that can be assigned to profiles"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), index=True)
    description = Column(String(500))
    
    # Configuration
    is_system = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    profiles = relationship(
        "Profile", 
        secondary=profile_permission_association, 
        back_populates="permissions"
    )
    
    def to_dict(self) -> dict:
        """Convert permission to dictionary"""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "is_system": self.is_system,
            "is_active": self.is_active
        }


class Session(Base):
    """User session model for tracking active sessions"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(128), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session data
    token = Column(String(500))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationship
    user = relationship("User")
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at if self.expires_at else False
    
    def to_dict(self) -> dict:
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "is_active": self.is_active
        }