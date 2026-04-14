"""
Teste direto de login usando o RBAC
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== Teste Direto de Login ===")

try:
    # Importar o RBAC
    from core.security.rbac import authenticate

    print("1. Testando autenticação do usuário admin...")

    # Testar credenciais corretas
    print("   Testando: admin / admin123")
    user = authenticate("admin", "admin123")

    if user:
        print(f"   ✅ Login bem-sucedido!")
        print(f"   Usuário: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Perfis: {[p.code for p in user.profiles]}")
    else:
        print("   ❌ Falha na autenticação")

    print("\n2. Testando autenticação do usuário developer...")

    # Testar credenciais corretas
    print("   Testando: developer / dev123")
    user = authenticate("developer", "dev123")

    if user:
        print(f"   ✅ Login bem-sucedido!")
        print(f"   Usuário: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Perfis: {[p.code for p in user.profiles]}")
    else:
        print("   ❌ Falha na autenticação")

    print("\n3. Testando credenciais incorretas...")

    # Testar credenciais incorretas
    print("   Testando: admin / senhaerrada")
    user = authenticate("admin", "senhaerrada")

    if user:
        print("   ❌ ERRO: Login deveria ter falhado!")
    else:
        print("   ✅ Login falhou corretamente")

    print("\n✅ Teste completo!")

except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()