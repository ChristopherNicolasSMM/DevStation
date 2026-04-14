"""
Teste simples para diagnosticar problemas de importação
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testando imports...")

try:
    # Testar import do db_manager
    print("1. Importando db_manager...")
    from core.models.base import db_manager
    print("   ✅ db_manager importado")

    # Testar import do User
    print("2. Importando User...")
    from core.models.user import User
    print("   ✅ User importado")

    # Testar import do rbac
    print("3. Importando rbac...")
    from core.security.rbac import rbac
    print("   ✅ rbac importado")

    # Testar autenticação
    print("4. Testando autenticação...")

    # Primeiro criar tabelas se necessário
    print("   Criando tabelas...")
    db_manager.create_tables()

    # Verificar se há usuários
    session = db_manager.get_session()
    user_count = session.query(User).count()
    print(f"   Usuários no banco: {user_count}")

    if user_count == 0:
        print("   ⚠️ Nenhum usuário encontrado")
    else:
        print("   ✅ Usuários encontrados")

    session.close()

    print("\n✅ Todos os imports funcionaram!")

except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()