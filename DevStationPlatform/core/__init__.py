"""
DevStationPlatform - Core Module
Plataforma RAD Inspirada em SAP com Rastreabilidade Total
"""

__version__ = "1.0.0"
__author__ = "DevStation Team"

from core.config import Config
from core.plugin_manager import PluginManager
from core.transaction import Transaction, transaction
from core.menu_manager import MenuManager

# Singleton instances
config = Config()
plugin_manager = PluginManager()
menu_manager = MenuManager()

__all__ = [
    "Config",
    "PluginManager", 
    "Transaction",
    "transaction",
    "MenuManager",
    "config",
    "plugin_manager",
    "menu_manager"
]