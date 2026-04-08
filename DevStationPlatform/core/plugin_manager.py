"""
Plugin management system - automatic discovery and loading
"""

import importlib
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
from dataclasses import dataclass, field


@dataclass
class PluginInfo:
    """Information about a loaded plugin"""
    name: str
    module: Any
    path: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    enabled: bool = True
    transactions: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)


class PluginManager:
    """Manages plugin discovery, loading and lifecycle"""
    
    def __init__(self):
        self._plugins: Dict[str, PluginInfo] = {}
        self._plugin_path: Path = Path(__file__).parent.parent / "plugins"
        
    def discover_plugins(self) -> List[PluginInfo]:
        """Discover available plugins in plugins directory"""
        discovered = []
        
        if not self._plugin_path.exists():
            self._plugin_path.mkdir(parents=True)
            return discovered
        
        for item in self._plugin_path.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                plugin_info = self._load_plugin_info(item)
                if plugin_info:
                    discovered.append(plugin_info)
                    self._plugins[plugin_info.name] = plugin_info
        
        return discovered
    
    def _load_plugin_info(self, plugin_dir: Path) -> Optional[PluginInfo]:
        """Load plugin information from its __init__.py"""
        init_file = plugin_dir / "__init__.py"
        
        if not init_file.exists():
            return None
        
        try:
            # Import plugin module
            module_name = f"plugins.{plugin_dir.name}"
            spec = importlib.util.spec_from_file_location(module_name, init_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Extract plugin metadata
            return PluginInfo(
                name=getattr(module, "__plugin_name__", plugin_dir.name),
                module=module,
                path=str(plugin_dir),
                version=getattr(module, "__version__", "1.0.0"),
                description=getattr(module, "__description__", ""),
                author=getattr(module, "__author__", ""),
                enabled=getattr(module, "__enabled__", True),
                transactions=getattr(module, "__transactions__", []),
                permissions=getattr(module, "__permissions__", [])
            )
        except Exception as e:
            print(f"Error loading plugin {plugin_dir.name}: {e}")
            return None
    
    def load_plugin(self, plugin_name: str) -> Optional[PluginInfo]:
        """Load a specific plugin by name"""
        if plugin_name in self._plugins:
            return self._plugins[plugin_name]
        
        plugin_dir = self._plugin_path / plugin_name
        if plugin_dir.exists():
            return self._load_plugin_info(plugin_dir)
        
        return None
    
    def get_plugin(self, name: str) -> Optional[PluginInfo]:
        """Get loaded plugin info"""
        return self._plugins.get(name)
    
    def get_all_plugins(self) -> List[PluginInfo]:
        """Get all loaded plugins"""
        return list(self._plugins.values())
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        if plugin_name in self._plugins:
            self._plugins[plugin_name].enabled = True
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        if plugin_name in self._plugins:
            self._plugins[plugin_name].enabled = False
            return True
        return False