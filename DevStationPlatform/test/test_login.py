"""
Teste simples de login
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔧 Testando login...")

try:
    from core.security.rbac import rbac

    # Testar autenticação
    print("\n🔐 Testando autenticação...")

    # Testar com credenciais incorretas
    result = rbac.authenticate("wrong", "wrong")
    print(f"❌ Credenciais erradas: {'Falhou como esperado' if not result else 'ERRO - deveria falhar'}")

    # Testar com admin
    print("\n🔑 Testando admin...")
    result = rbac.authenticate("admin", "admin123")
    if result:
        print(f"✅ Autenticação bem-sucedida!")
        print(f"   Token: {result['token'][:30]}...")
        print(f"   Usuário: {result['user'].get('username')}")
    else:
        print(f"❌ Autenticação falhou")

    # Testar com developer
    print("\n🔑 Testando developer...")
    result = rbac.authenticate("developer", "dev123")
    if result:
        print(f"✅ Autenticação bem-sucedida!")
        print(f"   Token: {result['token'][:30]}...")
        print(f"   Usuário: {result['user'].get('username')}")
    else:
        print(f"❌ Autenticação falhou")

except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()