"""
DevStationPlatform - Ponto de entrada NiceGUI
Migração de Flet para NiceGUI - Sprint 1
"""

from nicegui import ui
from ui.app import create_app

if __name__ in {"__main__", "__mp_main__"}:
    create_app()
    ui.run(
        title="DevStationPlatform",
        favicon="🎯",
        dark=False,
        port=8080,
        reload=True,  # Hot reload para desenvolvimento
        storage_secret="devstation_secret_key_123"  # Chave para armazenamento de sessão
    )