"""
Teste simples de autenticação
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== Teste Simples de Autenticação ===")

try:
    print("1. Importando módulos...")
    from core.models.base import db_manager
    from core.models.user import User

    print("2. Obtendo sessão do banco...")
    session = db_manager.get_session()

    print("3. Buscando usuário admin...")
    admin_user = session.query(User).filter_by(username="admin").first()

    if not admin_user:
        print("❌ Usuário admin não encontrado!")
        sys.exit(1)

    print(f"✅ Usuário encontrado: {admin_user.username}")
    print(f"   Hash da senha: {admin_user.password_hash[:30]}...")

    print("\n4. Testando verificação de senha...")

    # Testar senha correta
    print("   Testando senha 'admin123'...")
    result = admin_user.verify_password("admin123")
    print(f"   Resultado: {'✅ Válida' if result else '❌ Inválida'}")

    # Testar senha incorreta
    print("   Testando senha 'wrong123'...")
    result = admin_user.verify_password("wrong123")
    print(f"   Resultado: {'❌ ERRO - deveria ser inválida' if result else '✅ Inválida (correto)'}")

    session.close()

    print("\n✅ Teste completo!")

except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()