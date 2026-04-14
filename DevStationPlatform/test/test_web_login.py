"""
Teste de login através da interface web
"""

import requests
import json

def test_login():
    print("=== Teste de Login via Interface Web ===")

    base_url = "http://localhost:8080"

    # Primeiro, acessar a página inicial para ver se está funcionando
    print("1. Acessando página inicial...")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Tamanho da resposta: {len(response.text)} caracteres")

        # Verificar se é a página de login
        if "login" in response.text.lower() or "usuário" in response.text.lower():
            print("   ✅ Página de login detectada")
        else:
            print("   ⚠️ Página não parece ser de login")

    except Exception as e:
        print(f"   ❌ Erro ao acessar página: {e}")
        return

    # Testar login via API se existir
    print("\n2. Testando endpoint de login...")

    # Tentar diferentes endpoints de login comuns
    login_endpoints = [
        "/api/login",
        "/login",
        "/auth/login",
        "/api/auth/login"
    ]

    for endpoint in login_endpoints:
        try:
            url = base_url + endpoint
            print(f"   Testando {endpoint}...")

            # Tentar fazer POST com credenciais
            data = {
                "username": "admin",
                "password": "admin123"
            }

            response = requests.post(url, json=data, timeout=10)
            print(f"     Status: {response.status_code}")

            if response.status_code == 200:
                print(f"     ✅ Login bem-sucedido!")
                result = response.json()
                print(f"     Token: {result.get('token', 'N/A')[:30]}...")
                return
            elif response.status_code == 401:
                print(f"     ❌ Credenciais inválidas")
            elif response.status_code == 404:
                print(f"     ⚠️ Endpoint não encontrado")
            else:
                print(f"     ⚠️ Status inesperado: {response.status_code}")

        except Exception as e:
            print(f"     ⚠️ Erro: {e}")

    print("\n3. Verificando estrutura da página de login...")
    try:
        response = requests.get(base_url, timeout=10)
        html = response.text.lower()

        # Procurar elementos de formulário
        if '<form' in html:
            print("   ✅ Formulário encontrado na página")

            # Procurar campos de input
            if 'username' in html or 'user' in html:
                print("   ✅ Campo de usuário detectado")
            if 'password' in html or 'pass' in html:
                print("   ✅ Campo de senha detectado")
            if 'submit' in html or 'login' in html or 'entrar' in html:
                print("   ✅ Botão de login detectado")
        else:
            print("   ⚠️ Nenhum formulário encontrado")

    except Exception as e:
        print(f"   ❌ Erro: {e}")

    print("\n✅ Teste completo!")
    print("\nAcesse manualmente: http://localhost:8080")
    print("Credenciais para teste:")
    print("  Usuário: admin | Senha: admin123")
    print("  Usuário: developer | Senha: dev123")

if __name__ == "__main__":
    test_login()