"""
Teste final do sistema DevStationPlatform (sem requests)
"""

import sys
import os
import urllib.request
import urllib.error
import ssl

def print_status(message, status="info"):
    """Print com status"""
    if status == "success":
        prefix = "[SUCESSO]"
    elif status == "error":
        prefix = "[ERRO]"
    elif status == "warning":
        prefix = "[AVISO]"
    else:
        prefix = "[INFO]"

    print(f"{prefix} {message}")

def test_web_interface():
    """Testar interface web sem requests"""
    print_status("Testando interface web...")

    try:
        url = "http://localhost:8080"

        # Criar contexto SSL para ignorar certificados (apenas para teste local)
        context = ssl._create_unverified_context()

        # Testar acesso
        try:
            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req, timeout=5, context=context)
            status_code = response.getcode()
            print_status(f"Status: {status_code}")

            if status_code == 200:
                print_status("Interface web acessível", "success")

                # Ler conteúdo
                html = response.read().decode('utf-8', errors='ignore').lower()

                # Verificar se é página de login
                has_login_elements = any(keyword in html for keyword in
                    ['usuário', 'senha', 'login', 'password', 'username'])

                if has_login_elements:
                    print_status("Página de login detectada", "success")
                    return True
                else:
                    print_status("Página não parece ser de login", "warning")
                    return False
            else:
                print_status(f"Status inesperado: {status_code}", "error")
                return False

        except urllib.error.URLError as e:
            if isinstance(e.reason, TimeoutError):
                print_status("Timeout ao acessar interface", "error")
            else:
                print_status(f"Não foi possível conectar: {e}", "error")
            return False
        except Exception as e:
            print_status(f"Erro ao acessar: {e}", "error")
            return False

    except Exception as e:
        print_status(f"Erro na interface: {e}", "error")
        return False

def main():
    print("=" * 60)
    print("TESTE FINAL - DevStationPlatform")
    print("=" * 60)

    print_status("Iniciando testes...")

    # Testar interface web
    web_ok = test_web_interface()

    print("\n" + "=" * 60)
    print("RESULTADO DOS TESTES")
    print("=" * 60)

    if web_ok:
        print_status("✅ INTERFACE WEB: Acessível e com página de login", "success")
    else:
        print_status("❌ INTERFACE WEB: Com problemas", "error")

    print("\n" + "=" * 60)
    print("INSTRUÇÕES FINAIS")
    print("=" * 60)

    print("\n1. ACESSAR A APLICAÇÃO:")
    print("   URL: http://localhost:8080")

    print("\n2. CREDENCIAIS PARA LOGIN:")
    print("   • admin / admin123")
    print("   • developer / dev123")

    print("\n3. PRÓXIMOS PASSOS:")
    print("   a. Acessar a URL acima no navegador")
    print("   b. Fazer login com uma das credenciais")
    print("   c. Verificar se redireciona para o dashboard")
    print("   d. Testar menu lateral e funcionalidades")

    print("\n4. SE O LOGIN NÃO FUNCIONAR:")
    print("   • Verificar se a aplicação está rodando")
    print("   • Tentar reiniciar: python main.py")
    print("   • Verificar logs de erro no terminal")

    print("\n" + "=" * 60)

    if web_ok:
        print_status("✅ SISTEMA PRONTO PARA USO!", "success")
        return 0
    else:
        print_status("⚠️ ALGUNS PROBLEMAS DETECTADOS", "warning")
        return 1

if __name__ == "__main__":
    sys.exit(main())