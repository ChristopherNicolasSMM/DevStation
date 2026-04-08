"""
Dynamic profile management - create, edit, delete profiles at runtime
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from core.models.user import Profile, Permission, User
from core.models.base import db_manager


class ProfileManager:
    """
    Manages dynamic profiles.
    Profiles can be created, edited, deleted at runtime.
    Supports inheritance between profiles.
    """
    
    def __init__(self):
        self._session: Optional[Session] = None
    
    def _get_session(self) -> Session:
        """Get database session"""
        if self._session is None:
            self._session = db_manager.get_session()
        return self._session
    
    def create_profile(
        self,
        code: str,
        name: str,
        description: str = "",
        permissions: List[str] = None,
        parents: List[str] = None,
        priority: int = 0,
        created_by: str = "system"
    ) -> Profile:
        """
        Create a new custom profile.
        Profiles can be created with any code (not just predefined ones).
        """
        session = self._get_session()
        
        # Check if profile already exists
        existing = session.query(Profile).filter(Profile.code == code).first()
        if existing:
            raise ValueError(f"Profile with code {code} already exists")
        
        # Create new profile
        profile = Profile(
            code=code,
            name=name,
            description=description,
            is_system=False,  # Custom profiles are not system
            is_active=True,
            priority=priority,
            created_by=created_by
        )
        
        session.add(profile)
        session.flush()  # Get ID
        
        # Add permissions
        if permissions:
            perms = session.query(Permission).filter(Permission.code.in_(permissions)).all()
            profile.permissions = perms
        
        # Add parent profiles (inheritance)
        if parents:
            parent_profiles = session.query(Profile).filter(Profile.code.in_(parents)).all()
            profile.parents = parent_profiles
        
        session.commit()
        return profile
    
    def edit_profile(
        self,
        code: str,
        name: str = None,
        description: str = None,
        permissions: List[str] = None,
        parents: List[str] = None,
        priority: int = None,
        is_active: bool = None
    ) -> Profile:
        """Edit an existing profile (including system profiles)"""
        session = self._get_session()
        
        profile = session.query(Profile).filter(Profile.code == code).first()
        if not profile:
            raise ValueError(f"Profile {code} not found")
        
        if name is not None:
            profile.name = name
        if description is not None:
            profile.description = description
        if priority is not None:
            profile.priority = priority
        if is_active is not None:
            profile.is_active = is_active
        
        # Update permissions
        if permissions is not None:
            perms = session.query(Permission).filter(Permission.code.in_(permissions)).all()
            profile.permissions = perms
        
        # Update parent inheritance
        if parents is not None:
            parent_profiles = session.query(Profile).filter(Profile.code.in_(parents)).all()
            profile.parents = parent_profiles
        
        session.commit()
        return profile
    
    def delete_profile(self, code: str) -> bool:
        """Delete a profile (only non-system profiles)"""
        session = self._get_session()
        
        profile = session.query(Profile).filter(Profile.code == code).first()
        if not profile:
            return False
        
        if profile.is_system:
            raise ValueError(f"Cannot delete system profile {code}")
        
        # Remove from users
        for user in profile.users:
            user.profiles.remove(profile)
        
        session.delete(profile)
        session.commit()
        return True
    
    def get_profile(self, code: str) -> Optional[Profile]:
        """Get profile by code"""
        session = self._get_session()
        return session.query(Profile).filter(Profile.code == code).first()
    
    def get_all_profiles(self, include_system: bool = True) -> List[Profile]:
        """Get all profiles"""
        session = self._get_session()
        query = session.query(Profile)
        if not include_system:
            query = query.filter(Profile.is_system == False)
        return query.order_by(Profile.priority.desc()).all()
    
    def create_permission(
        self,
        code: str,
        name: str,
        category: str = "CUSTOM",
        description: str = ""
    ) -> Permission:
        """Create a new custom permission"""
        session = self._get_session()
        
        existing = session.query(Permission).filter(Permission.code == code).first()
        if existing:
            raise ValueError(f"Permission {code} already exists")
        
        permission = Permission(
            code=code,
            name=name,
            category=category,
            description=description,
            is_system=False
        )
        
        session.add(permission)
        session.commit()
        return permission
    
    def get_all_permissions(self) -> List[Permission]:
        """Get all available permissions"""
        session = self._get_session()
        return session.query(Permission).order_by(Permission.category, Permission.code).all()
    
    def assign_profile_to_user(self, username: str, profile_code: str) -> User:
        """Assign a profile to a user"""
        session = self._get_session()
        
        user = session.query(User).filter(User.username == username).first()
        if not user:
            raise ValueError(f"User {username} not found")
        
        profile = self.get_profile(profile_code)
        if not profile:
            raise ValueError(f"Profile {profile_code} not found")
        
        if profile not in user.profiles:
            user.profiles.append(profile)
            session.commit()
        
        return user
    
    def remove_profile_from_user(self, username: str, profile_code: str) -> User:
        """Remove a profile from a user"""
        session = self._get_session()
        
        user = session.query(User).filter(User.username == username).first()
        if not user:
            raise ValueError(f"User {username} not found")
        
        profile = self.get_profile(profile_code)
        if profile and profile in user.profiles:
            user.profiles.remove(profile)
            session.commit()
        
        return user
    
    def get_users_by_profile(self, profile_code: str) -> List[User]:
        """Get all users with a specific profile"""
        session = self._get_session()
        profile = self.get_profile(profile_code)
        if profile:
            return profile.users
        return []