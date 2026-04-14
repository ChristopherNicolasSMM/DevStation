"""
Teste final do sistema DevStationPlatform
"""

import sys
import os
import time

def print_status(message, status="info"):
    """Print com status colorido"""
    if status == "success":
        prefix = "✅"
    elif status == "error":
        prefix = "❌"
    elif status == "warning":
        prefix = "⚠️"
    else:
        prefix = "📋"

    print(f"{prefix} {message}")

def test_backend():
    """Testar backend (autenticação)"""
    print_status("Testando backend...")

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        # Testar import dos modelos
        from core.models.base import db_manager
        from core.models.user import User

        session = db_manager.get_session()

        # Verificar usuários
        admin_user = session.query(User).filter_by(username="admin").first()
        dev_user = session.query(User).filter_by(username="developer").first()

        if not admin_user:
            print_status("Usuário admin não encontrado", "error")
            return False

        if not dev_user:
            print_status("Usuário developer não encontrado", "error")
            return False

        print_status(f"Usuário admin encontrado: {admin_user.username}", "success")
        print_status(f"Usuário developer encontrado: {dev_user.username}", "success")

        # Testar senhas
        print_status("Testando senhas...")

        test_cases = [
            (admin_user, "admin123", True, "admin com senha correta"),
            (admin_user, "wrong123", False, "admin com senha errada"),
            (dev_user, "dev123", True, "developer com senha correta"),
            (dev_user, "wrong123", False, "developer com senha errada"),
        ]

        all_passed = True
        for user, password, expected, description in test_cases:
            result = user.verify_password(password)
            passed = result == expected

            if passed:
                print_status(f"{description}: {'✅ Válida' if result else '✅ Inválida'}", "success")
            else:
                print_status(f"{description}: {'❌ ERRO'}", "error")
                all_passed = False

        session.close()
        return all_passed

    except Exception as e:
        print_status(f"Erro no backend: {e}", "error")
        return False

def test_web_interface():
    """Testar interface web"""
    print_status("Testando interface web...")

    try:
        import requests

        url = "http://localhost:8080"

        # Testar acesso
        try:
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                print_status("Interface web acessível", "success")

                # Verificar se é página de login
                html = response.text.lower()
                has_login_elements = any(keyword in html for keyword in
                    ['usuário', 'senha', 'login', 'password', 'username'])

                if has_login_elements:
                    print_status("Página de login detectada", "success")
                    return True
                else:
                    print_status("Página não parece ser de login", "warning")
                    return False
            else:
                print_status(f"Status inesperado: {response.status_code}", "error")
                return False

        except requests.exceptions.Timeout:
            print_status("Timeout ao acessar interface", "error")
            return False
        except requests.exceptions.ConnectionError:
            print_status("Não foi possível conectar", "error")
            return False

    except ImportError:
        print_status("Módulo requests não instalado", "warning")
        return None  # Não é erro crítico
    except Exception as e:
        print_status(f"Erro na interface: {e}", "error")
        return False

def main():
    print("=" * 60)
    print("TESTE FINAL - DevStationPlatform")
    print("=" * 60)

    print_status("Iniciando testes...")

    # Testar backend
    backend_ok = test_backend()

    # Testar interface web
    web_ok = test_web_interface()

    print("\n" + "=" * 60)
    print("RESULTADO DOS TESTES")
    print("=" * 60)

    if backend_ok:
        print_status("✅ BACKEND: Funcionando corretamente", "success")
    else:
        print_status("❌ BACKEND: Com problemas", "error")

    if web_ok is True:
        print_status("✅ INTERFACE WEB: Acessível e com página de login", "success")
    elif web_ok is False:
        print_status("❌ INTERFACE WEB: Com problemas", "error")
    else:
        print_status("⚠️  INTERFACE WEB: Não testada (requests não instalado)", "warning")

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

    if backend_ok and (web_ok is True or web_ok is None):
        print_status("✅ SISTEMA PRONTO PARA USO!", "success")
        return 0
    else:
        print_status("⚠️  ALGUNS PROBLEMAS DETECTADOS", "warning")
        return 1

if __name__ == "__main__":
    sys.exit(main())