"""
Script para gerar executável .exe do DevStation usando PyInstaller.
"""

import os
import sys
import shutil
from pathlib import Path


def build_exe():
    """Gera o executável .exe do DevStation."""
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    
    print("🔧 Preparando build do DevStation...")
    
    # Verificar se PyInstaller está instalado
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller não está instalado. Instale com: pip install PyInstaller")
        sys.exit(1)
    
    # Criar diretório de build
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"
    
    # Limpar builds anteriores
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--name=DevStation",
        "--onefile",
        "--windowed",  # Sem console (use --console se quiser ver logs)
        f"--add-data={src_path / 'templates'};templates",
        f"--add-data={src_path / 'static'};static",
        f"--add-data={src_path / 'config.env.modelo'};.",
        "--hidden-import=flask",
        "--hidden-import=sqlalchemy",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=reportlab",
        f"{src_path / 'main.py'}",
    ]
    
    print("📦 Executando PyInstaller...")
    print(f"Comando: {' '.join(cmd)}")
    
    os.chdir(project_root)
    os.system(" ".join(cmd))
    
    print("\n✅ Build concluído!")
    print(f"📁 Executável em: {dist_dir / 'DevStation.exe'}")


if __name__ == "__main__":
    build_exe()
