"""
Script para iniciar a aplicação DevStationPlatform
"""

import subprocess
import sys
import os
import time

def main():
    print("=== Iniciando DevStationPlatform ===")

    # Primeiro, verificar se a aplicação já está rodando
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8080))
        sock.close()

        if result == 0:
            print("A aplicação já está rodando em http://localhost:8080")
            print("Acesse: http://localhost:8080")
            return
    except:
        pass

    # Iniciar a aplicação
    print("Iniciando aplicação...")

    # Usar o mesmo Python que está executando este script
    python_exe = sys.executable
    main_script = os.path.join(os.path.dirname(__file__), "main.py")

    # Iniciar em um processo separado
    process = subprocess.Popen(
        [python_exe, main_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )

    print(f"Processo iniciado com PID: {process.pid}")

    # Aguardar um pouco para a aplicação iniciar
    print("Aguardando inicialização...")
    time.sleep(5)

    # Verificar se está rodando
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8080))
        sock.close()

        if result == 0:
            print("\n✅ Aplicação iniciada com sucesso!")
            print("Acesse: http://localhost:8080")
            print("\nCredenciais para teste:")
            print("  Usuário: admin | Senha: admin123")
            print("  Usuário: developer | Senha: dev123")
            print("\nPressione Ctrl+C para parar a aplicação")

            # Manter o script rodando
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\nParando aplicação...")
                process.terminate()
                process.wait()
                print("Aplicação parada.")
        else:
            print("\n❌ Não foi possível conectar na porta 8080")
            print("Verifique os logs de erro.")
            process.terminate()

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        process.terminate()

if __name__ == "__main__":
    main()