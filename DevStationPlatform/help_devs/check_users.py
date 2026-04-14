"""
Script para verificar e criar usuários se necessário
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.models.base import db_manager
from core.models.user import User, Profile, Permission

def check_and_create_users():
    """Verificar e criar usuários se necessário"""
    print("🔍 Verificando banco de dados...")

    session = db_manager.get_session()

    try:
        # Verificar se tabelas existem
        from sqlalchemy import inspect
        inspector = inspect(db_manager.engine)
        tables = inspector.get_table_names()

        if not tables:
            print("❌ Nenhuma tabela encontrada. Execute primeiro:")
            print("  python -c \"from core.models.base import db_manager; db_manager.create_tables()\"")
            return False

        print(f"✅ Tabelas encontradas: {len(tables)}")

        # Verificar usuários
        user_count = session.query(User).count()
        print(f"👤 Usuários no banco: {user_count}")

        if user_count == 0:
            print("⚠️  Nenhum usuário encontrado. Criando usuários de teste...")

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
            admin_user.set_password("admin123")
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
            dev_user.set_password("dev123")
            dev_user.profiles = [dev_profile]

            session.add_all([admin_user, dev_user])
            session.commit()

            print("✅ Usuários criados com sucesso!")
            print("  👑 admin / admin123")
            print("  💻 developer / dev123")
            return True
        else:
            print("✅ Usuários já existem no banco.")
            # Listar usuários
            users = session.query(User).all()
            for user in users:
                print(f"  👤 {user.username} ({'ativo' if user.is_active else 'inativo'})")
            return True

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    check_and_create_users()