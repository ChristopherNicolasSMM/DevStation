#!/usr/bin/env python
"""
Script de execução do DevStation.
Permite iniciar a aplicação a partir da raiz do projeto.
"""

import sys
import os
import argparse
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from flask import Flask

# Adicionar src ao path para imports funcionarem
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# Mudar para o diretório src para garantir que os caminhos relativos funcionem
original_cwd = os.getcwd()
os.chdir(src_path)

# Ajustar variável de ambiente para o .env estar no lugar certo
env_path = project_root / "src" / ".env"
if env_path.exists():
    os.environ["ENV_FILE"] = str(env_path)


def start():
    """Inicia o servidor Flask."""
    print("🚀 Iniciando DevStation...")
    print(f"📁 Diretório de trabalho: {os.getcwd()}")
    print("-" * 60)
    
    # Importar e executar main.py
    try:
        import main
        
        if hasattr(main, 'app'):
            app = main.app
            
            host = os.getenv("HOST", "0.0.0.0")
            port = int(os.getenv("PORT", 5000))
            debug = os.getenv("DEBUG", "True").lower() == "true"
            
            print(f"🌐 Servidor iniciando em http://{host}:{port}")
            print(f"🔧 Debug: {debug}")
            print(f"📝 Logs: logs/application.log")
            print("-" * 60)
            print("✅ DevStation rodando! Pressione Ctrl+C para parar.")
            print("-" * 60)
            
            app.run(host=host, port=port, debug=debug, use_reloader=False)
        else:
            print("❌ Erro: Aplicação Flask não foi criada corretamente.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor interrompido pelo usuário.")
        os.chdir(original_cwd)
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro ao iniciar o servidor: {e}")
        import traceback
        traceback.print_exc()
        os.chdir(original_cwd)
        sys.exit(1)


def show_help():
    """Mostra ajuda sobre os comandos disponíveis."""
    print("""
🔧 DevStation - Script de Execução

Uso:
    python run.py <comando> [opções]

Comandos disponíveis:
    start       Inicia o servidor Flask
    help        Mostra esta mensagem de ajuda

Exemplos:
    python run.py start
    python run.py help

Variáveis de ambiente:
    HOST        Host do servidor (padrão: 0.0.0.0)
    PORT        Porta do servidor (padrão: 5000)
    DEBUG       Modo debug (padrão: True)
    FLASK_ENV   Ambiente (DEV/PRD)
    """)


def main():
    """Função principal do script."""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start()
    elif command == "help" or command == "--help" or command == "-h":
        show_help()
    else:
        print(f"❌ Comando desconhecido: {command}")
        print("\nUse 'python run.py help' para ver os comandos disponíveis.")
        sys.exit(1)


if __name__ == "__main__":
    main()
