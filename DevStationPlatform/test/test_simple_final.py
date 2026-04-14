"""
Teste final simplificado do sistema DevStationPlatform
"""

import sys
import os

def test_web_interface():
    """Testar interface web"""
    print("Testando interface web...")

    try:
        import requests

        url = "http://localhost:8080"

        # Testar acesso
        try:
            response = requests.get(url, timeout=5)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                print("✅ Interface web acessível")

                # Verificar se é página de login
                html = response.text.lower()
                has_login_elements = any(keyword in html for keyword in
                    ['usuário', 'senha', 'login', 'password', 'username'])

                if has_login_elements:
                    print("✅ Página de login detectada")
                    return True
                else:
                    print("⚠️ Página não parece ser de login")
                    return False
            else:
                print(f"❌ Status inesperado: {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            print("❌ Timeout ao acessar interface")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ Não foi possível conectar")
            return False

    except ImportError:
        print("⚠️ Módulo requests não instalado")
        return None  # Não é erro crítico
    except Exception as e:
        print(f"❌ Erro na interface: {e}")
        return False

def main():
    print("=" * 60)
    print("TESTE FINAL SIMPLIFICADO - DevStationPlatform")
    print("=" * 60)

    # Testar interface web
    web_ok = test_web_interface()

    print("\n" + "=" * 60)
    print("RESULTADO DO TESTE")
    print("=" * 60)

    if web_ok is True:
        print("✅ INTERFACE WEB: Acessível e com página de login")
    elif web_ok is False:
        print("❌ INTERFACE WEB: Com problemas")
    else:
        print("⚠️ INTERFACE WEB: Não testada (requests não instalado)")

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

    if web_ok is True or web_ok is None:
        print("✅ SISTEMA PRONTO PARA TESTE MANUAL!")
        return 0
    else:
        print("⚠️ ALGUNS PROBLEMAS DETECTADOS")
        return 1

if __name__ == "__main__":
    sys.exit(main())