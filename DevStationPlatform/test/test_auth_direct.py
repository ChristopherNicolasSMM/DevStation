"""
Teste direto de autenticação sem importar rbac
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testando autenticação diretamente...")

try:
    # Importar apenas o necessário
    from core.models.base import db_manager
    from core.models.user import User

    print("1. Obtendo sessão...")
    session = db_manager.get_session()

    print("2. Buscando usuário admin...")
    admin_user = session.query(User).filter_by(username="admin").first()

    if not admin_user:
        print("❌ Usuário admin não encontrado!")
        # Criar usuário admin
        print("   Criando usuário admin...")

        from core.models.user import Profile, Permission

        # Criar permissão
        perm = Permission(
            code="dashboard.view",
            name="Visualizar Dashboard",
            category="dashboard",
            description="Acesso ao dashboard principal",
            is_system=True
        )
        session.add(perm)
        session.flush()

        # Criar perfil admin
        admin_profile = Profile(
            code="ADMIN",
            name="Administrador",
            description="Perfil de administrador",
            is_system=True,
            priority=100
        )
        admin_profile.permissions = [perm]
        session.add(admin_profile)
        session.flush()

        # Criar usuário
        admin_user = User(
            username="admin",
            email="admin@devstation.local",
            full_name="Administrador do Sistema",
            is_active=True,
            theme="dark",
            language="pt_BR"
        )
        admin_user.password_hash = "admin123"  # Senha em texto puro
        admin_user.profiles = [admin_profile]

        session.add(admin_user)
        session.commit()
        print("   ✅ Usuário admin criado!")

    print(f"3. Usuário encontrado: {admin_user.username}")
    print(f"   Hash da senha: {admin_user.password_hash}")

    # Testar verificação de senha
    print("4. Testando verificação de senha...")

    # Testar senha correta
    test_password = "admin123"
    print(f"   Testando senha: '{test_password}'")

    # Chamar método verify_password diretamente
    is_valid = admin_user.verify_password(test_password)
    print(f"   Resultado: {'✅ Válida' if is_valid else '❌ Inválida'}")

    # Testar senha incorreta
    wrong_password = "wrong123"
    print(f"   Testando senha errada: '{wrong_password}'")
    is_valid_wrong = admin_user.verify_password(wrong_password)
    print(f"   Resultado: {'❌ ERRO - deveria ser inválida' if is_valid_wrong else '✅ Inválida (correto)'}")

    session.close()

    print("\n✅ Teste completo!")

except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()