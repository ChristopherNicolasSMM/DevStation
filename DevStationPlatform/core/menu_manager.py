"""
Hierarchical menu management system
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class MenuItem:
    """Represents a menu item"""
    label: str
    icon: str = ""
    path: str = ""
    transaction: str = ""
    permissions: List[str] = field(default_factory=list)
    children: List['MenuItem'] = field(default_factory=list)
    is_visible: bool = True
    
    def has_permission(self, user_permissions: set) -> bool:
        """Check if user has permission to see this menu item"""
        if not self.permissions:
            return True
        return any(p in user_permissions for p in self.permissions)


class MenuManager:
    """Manages the application menu structure"""
    
    def __init__(self):
        self._menu_structure: List[MenuItem] = []
        self._menu_by_path: Dict[str, MenuItem] = {}
        
    def load_from_config(self, config: dict):
        """Load menu structure from configuration"""
        menu_config = config.get("menu", {}).get("structure", [])
        self._menu_structure = self._parse_menu_items(menu_config)
        
    def _parse_menu_items(self, items: List[dict]) -> List[MenuItem]:
        """Parse menu items from configuration dict"""
        menu_items = []
        
        for item in items:
            menu_item = MenuItem(
                label=item.get("label", ""),
                icon=item.get("icon", ""),
                path=item.get("path", ""),
                transaction=item.get("transaction", ""),
                permissions=item.get("permissions", []),
                children=self._parse_menu_items(item.get("children", []))
            )
            
            if menu_item.path:
                self._menu_by_path[menu_item.path] = menu_item
            
            menu_items.append(menu_item)
        
        return menu_items
    
    def get_menu_for_user(self, user_permissions: set) -> List[MenuItem]:
        """Get filtered menu based on user permissions"""
        return self._filter_menu(self._menu_structure, user_permissions)
    
    def _filter_menu(self, items: List[MenuItem], user_permissions: set) -> List[MenuItem]:
        """Recursively filter menu items by permissions"""
        filtered = []
        
        for item in items:
            if not item.has_permission(user_permissions):
                continue
            
            filtered_item = MenuItem(
                label=item.label,
                icon=item.icon,
                path=item.path,
                transaction=item.transaction,
                permissions=item.permissions,
                children=self._filter_menu(item.children, user_permissions),
                is_visible=True
            )
            
            filtered.append(filtered_item)
        
        return filtered
    
    def find_by_path(self, path: str) -> Optional[MenuItem]:
        """Find menu item by path"""
        return self._menu_by_path.get(path)
    
    def add_menu_item(self, parent_path: Optional[str], item: MenuItem):
        """Add a menu item dynamically"""
        if parent_path:
            parent = self.find_by_path(parent_path)
            if parent:
                parent.children.append(item)
        else:
            self._menu_structure.append(item)
        
        if item.path:
            self._menu_by_path[item.path] = item