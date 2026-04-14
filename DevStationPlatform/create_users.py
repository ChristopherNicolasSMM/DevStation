"""
Script simples para criar usuários de teste
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.models.base import db_manager
from core.models.user import User, Profile, Permission
from datetime import datetime

def create_test_users():
    """Criar usuários de teste"""
    print("Criando usuários de teste...")

    # Obter sessão
    session = db_manager.get_session()

    try:
        # Verificar se já existem usuários
        user_count = session.query(User).count()
        if user_count > 0:
            print(f"Já existem {user_count} usuários no banco de dados.")
            return

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
        # Usar senha em texto puro temporariamente para evitar problema com bcrypt
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

        print("✅ Usuários criados com sucesso!")
        print("  admin / admin123")
        print("  developer / dev123")

    except Exception as e:
        session.rollback()
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    create_test_users()