"""
Teste simples da interface web
"""

try:
    import requests
    import sys

    print("Testando interface web...")

    url = "http://localhost:8080"

    try:
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Tamanho: {len(response.text)} caracteres")

        # Verificar conteúdo
        if response.status_code == 200:
            print("✅ Aplicação está respondendo!")

            # Verificar se é página de login
            html = response.text.lower()
            if any(keyword in html for keyword in ['login', 'usuário', 'senha', 'password', 'username']):
                print("✅ Página de login detectada")
            else:
                print("⚠️  Página não parece ser de login")

            # Mostrar título se existir
            import re
            title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
            if title_match:
                print(f"Título: {title_match.group(1)}")

        else:
            print(f"⚠️  Status inesperado: {response.status_code}")

    except requests.exceptions.Timeout:
        print("❌ Timeout ao acessar a aplicação")
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à aplicação")
    except Exception as e:
        print(f"❌ Erro: {e}")

except ImportError:
    print("❌ Módulo requests não instalado")
    print("Instale com: pip install requests")
except Exception as e:
    print(f"❌ Erro geral: {e}")