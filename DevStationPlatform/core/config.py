"""
Central configuration management
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """Central configuration singleton"""
    
    _instance: Optional['Config'] = None
    _config: Dict[str, Any] = field(default_factory=dict)
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from YAML file"""
        config_path = Path(__file__).parent.parent / "config.yaml"
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        else:
            # Default configuration
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "app": {"name": "DevStationPlatform", "version": "1.0.0", "debug": True},
            "database": {"dialect": "sqlite", "database": "devstation.db"},
            "security": {"jwt_expiration_hours": 24},
            "plugins": {"autodiscover": True, "path": "plugins", "enabled": []}
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    @property
    def debug(self) -> bool:
        return self.get("app.debug", False)
    
    @property
    def app_name(self) -> str:
        return self.get("app.name", "DevStationPlatform")
    
    @property
    def database_url(self) -> str:
        dialect = self.get("database.dialect", "sqlite")
        database = self.get("database.database", "devstation.db")
        
        if dialect == "sqlite":
            return f"sqlite:///{database}"
        elif dialect == "postgresql":
            return f"postgresql://{self.get('database.user')}:{self.get('database.password')}@{self.get('database.host')}/{database}"
        else:
            return f"sqlite:///{database}"