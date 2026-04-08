"""
Dynamic Profile Management - Create/Edit/Delete profiles at runtime
Gerenciamento dinâmico de perfis - Cria/Edita/Remove perfis em tempo real
"""

from typing import List, Dict, Any, Optional, Set
from sqlalchemy.orm import Session

from core.models.base import db_manager
from core.security.models import Profile, Permission, User


class DynamicProfileManager:
    """
    Gerencia perfis de forma dinâmica em tempo de execução.
    Permite criar, editar, excluir e consultar perfis sem necessidade de reinicialização.
    """
    
    def __init__(self):
        self._cache = {}
        self._cache_valid = False
    
    def _get_session(self) -> Session:
        """Get database session"""
        return db_manager.get_session()
    
    def _invalidate_cache(self):
        """Invalidate profile cache"""
        self._cache_valid = False
        self._cache = {}
    
    def _refresh_cache(self):
        """Refresh profile cache"""
        if self._cache_valid:
            return
        
        session = self._get_session()
        profiles = session.query(Profile).filter(Profile.is_active == True).all()
        
        for profile in profiles:
            self._cache[profile.code] = {
                "id": profile.id,
                "code": profile.code,
                "name": profile.name,
                "description": profile.description,
                "priority": profile.priority,
                "permissions": profile.get_all_permissions(),
                "is_system": profile.is_system
            }
        
        self._cache_valid = True
    
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
        Create a new custom profile dynamically
        
        Args:
            code: Unique profile code (e.g., "SUPER_USER", "EXTERNAL_PARTNER")
            name: Display name
            description: Profile description
            permissions: List of permission codes to assign
            parents: List of parent profile codes to inherit from
            priority: Priority level (higher = more important)
            created_by: Who created this profile
        
        Returns:
            Created Profile object
        """
        session = self._get_session()
        
        # Check if profile already exists
        existing = session.query(Profile).filter(Profile.code == code).first()
        if existing:
            raise ValueError(f"Profile with code '{code}' already exists")
        
        # Create new profile
        profile = Profile(
            code=code,
            name=name,
            description=description,
            is_system=False,
            is_active=True,
            priority=priority,
            created_by=created_by
        )
        
        session.add(profile)
        session.flush()
        
        # Add permissions
        if permissions:
            perms = session.query(Permission).filter(Permission.code.in_(permissions)).all()
            profile.permissions = perms
        
        # Add parent profiles (inheritance)
        if parents:
            parent_profiles = session.query(Profile).filter(Profile.code.in_(parents)).all()
            profile.parents = parent_profiles
        
        session.commit()
        self._invalidate_cache()
        
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
        """
        Edit an existing profile dynamically
        
        Args:
            code: Profile code to edit
            name: New name (optional)
            description: New description (optional)
            permissions: New list of permission codes (optional)
            parents: New list of parent profile codes (optional)
            priority: New priority (optional)
            is_active: New active status (optional)
        
        Returns:
            Updated Profile object
        """
        session = self._get_session()
        
        profile = session.query(Profile).filter(Profile.code == code).first()
        if not profile:
            raise ValueError(f"Profile '{code}' not found")
        
        # Update fields
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
        self._invalidate_cache()
        
        return profile
    
    def delete_profile(self, code: str, force: bool = False) -> bool:
        """
        Delete a profile dynamically
        
        Args:
            code: Profile code to delete
            force: Force delete even if users have this profile
        
        Returns:
            True if deleted successfully
        """
        session = self._get_session()
        
        profile = session.query(Profile).filter(Profile.code == code).first()
        if not profile:
            return False
        
        # Cannot delete system profiles
        if profile.is_system and not force:
            raise ValueError(f"Cannot delete system profile '{code}'. Use force=True to override.")
        
        # Remove profile from users
        for user in profile.users:
            user.profiles.remove(profile)
        
        session.delete(profile)
        session.commit()
        self._invalidate_cache()
        
        return True
    
    def get_profile(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Get profile details by code
        
        Returns:
            Profile dictionary or None if not found
        """
        self._refresh_cache()
        return self._cache.get(code)
    
    def get_all_profiles(self, include_system: bool = True) -> List[Dict[str, Any]]:
        """
        Get all profiles
        
        Args:
            include_system: Include system profiles in results
        
        Returns:
            List of profile dictionaries
        """
        self._refresh_cache()
        
        profiles = list(self._cache.values())
        if not include_system:
            profiles = [p for p in profiles if not p.get("is_system", False)]
        
        return sorted(profiles, key=lambda x: x.get("priority", 0), reverse=True)
    
    def get_profile_permissions(self, code: str) -> Set[str]:
        """
        Get all permissions for a profile (including inherited)
        
        Returns:
            Set of permission codes
        """
        profile = self.get_profile(code)
        if profile:
            return profile.get("permissions", set())
        return set()
    
    def assign_profile_to_user(self, username: str, profile_code: str) -> User:
        """
        Assign a profile to a user dynamically
        
        Args:
            username: Username
            profile_code: Profile code to assign
        
        Returns:
            Updated User object
        """
        session = self._get_session()
        
        user = session.query(User).filter(User.username == username).first()
        if not user:
            raise ValueError(f"User '{username}' not found")
        
        profile = session.query(Profile).filter(Profile.code == profile_code).first()
        if not profile:
            raise ValueError(f"Profile '{profile_code}' not found")
        
        if profile not in user.profiles:
            user.profiles.append(profile)
            session.commit()
        
        self._invalidate_cache()
        return user
    
    def remove_profile_from_user(self, username: str, profile_code: str) -> User:
        """
        Remove a profile from a user dynamically
        
        Args:
            username: Username
            profile_code: Profile code to remove
        
        Returns:
            Updated User object
        """
        session = self._get_session()
        
        user = session.query(User).filter(User.username == username).first()
        if not user:
            raise ValueError(f"User '{username}' not found")
        
        profile = session.query(Profile).filter(Profile.code == profile_code).first()
        if profile and profile in user.profiles:
            user.profiles.remove(profile)
            session.commit()
        
        self._invalidate_cache()
        return user
    
    def get_users_by_profile(self, profile_code: str) -> List[User]:
        """
        Get all users that have a specific profile
        
        Returns:
            List of User objects
        """
        session = self._get_session()
        profile = session.query(Profile).filter(Profile.code == profile_code).first()
        
        if profile:
            return profile.users
        return []
    
    def clone_profile(
        self,
        source_code: str,
        new_code: str,
        new_name: str = None
    ) -> Profile:
        """
        Clone an existing profile to create a new one
        
        Args:
            source_code: Source profile code to clone
            new_code: New profile code
            new_name: New profile name (optional, uses source name if not provided)
        
        Returns:
            Newly created Profile object
        """
        session = self._get_session()
        
        source = session.query(Profile).filter(Profile.code == source_code).first()
        if not source:
            raise ValueError(f"Source profile '{source_code}' not found")
        
        # Clone profile data
        new_profile = Profile(
            code=new_code,
            name=new_name or f"{source.name} (Clone)",
            description=f"Cloned from {source_code}",
            is_system=False,
            is_active=True,
            priority=source.priority,
            created_by="system"
        )
        
        session.add(new_profile)
        session.flush()
        
        # Clone permissions
        new_profile.permissions = source.permissions.copy()
        
        # Clone parent relationships
        new_profile.parents = source.parents.copy()
        
        session.commit()
        self._invalidate_cache()
        
        return new_profile
    
    def get_profile_hierarchy(self, profile_code: str) -> Dict[str, Any]:
        """
        Get the inheritance hierarchy for a profile
        
        Returns:
            Dictionary with profile and its parents/children
        """
        session = self._get_session()
        
        profile = session.query(Profile).filter(Profile.code == profile_code).first()
        if not profile:
            return {}
        
        def get_parents(p, level=0):
            return [{"code": parent.code, "name": parent.name, "level": level} 
                    for parent in p.parents]
        
        def get_children(p, level=0):
            return [{"code": child.code, "name": child.name, "level": level} 
                    for child in p.children]
        
        return {
            "profile": {
                "code": profile.code,
                "name": profile.name,
                "description": profile.description,
                "priority": profile.priority
            },
            "parents": get_parents(profile),
            "children": get_children(profile),
            "all_permissions": list(profile.get_all_permissions())
        }