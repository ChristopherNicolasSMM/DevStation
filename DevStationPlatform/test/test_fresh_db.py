"""
Testar autenticação com banco de dados novo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔧 Testando com banco de dados novo...")

try:
    # Alterar configuração para usar banco temporário
    from core.config import Config
    config = Config()
    config.set("database.database", "devstation_test.db")

    print(f"Usando banco: {config.database_url}")

    # Criar tabelas
    from core.models.base import db_manager
    print("Criando tabelas...")
    db_manager.create_tables()

    # Criar usuários
    from core.models.user import User, Profile, Permission

    session = db_manager.get_session()

    # Criar permissão básica
    perm = Permission(
        code="dashboard.view",
        name="Visualizar Dashboard",
        category="dashboard",
        description="Acesso ao dashboard principal",
        is_system=True
    )
    session.add(perm)
    session.flush()

    # Criar perfil de admin
    admin_profile = Profile(
        code="ADMIN",
        name="Administrador",
        description="Perfil de administrador",
        is_system=True,
        priority=100
    )
    admin_profile.permissions = [perm]

    # Criar perfil de desenvolvedor
    dev_profile = Profile(
        code="DEVELOPER",
        name="Desenvolvedor",
        description="Perfil de desenvolvedor",
        is_system=True,
        priority=50
    )
    dev_profile.permissions = [perm]

    session.add_all([admin_profile, dev_profile])
    session.flush()

    # Criar usuário admin
    admin_user = User(
        username="admin",
        email="admin@devstation.local",
        full_name="Administrador do Sistema",
        is_active=True,
        theme="dark",
        language="pt_BR"
    )
    admin_user.password_hash = "admin123"
    admin_user.profiles = [admin_profile]

    # Criar usuário developer
    dev_user = User(
        username="developer",
        email="developer@devstation.local",
        full_name="Desenvolvedor",
        is_active=True,
        theme="dark",
        language="pt_BR"
    )
    dev_user.password_hash = "dev123"
    dev_user.profiles = [dev_profile]

    session.add_all([admin_user, dev_user])
    session.commit()

    print("✅ Usuários criados!")
    print("  admin / admin123")
    print("  developer / dev123")

    # Testar autenticação
    from core.security.rbac import rbac

    print("\n🔐 Testando autenticação...")

    result = rbac.authenticate("admin", "admin123")
    if result:
        print(f"✅ Autenticação bem-sucedida!")
        print(f"   Token: {result['token'][:30]}...")
    else:
        print(f"❌ Autenticação falhou")

    session.close()

except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()