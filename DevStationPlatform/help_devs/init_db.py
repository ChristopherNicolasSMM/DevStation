"""
Script para inicializar o banco de dados da DevStationPlatform
Cria tabelas e popula com usuários de demonstração
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.models.base import db_manager
from core.models.user import User, Profile, Permission
from datetime import datetime, timedelta

def init_database():
    """Inicializar banco de dados"""
    print("🔧 Inicializando banco de dados...")

    # Criar tabelas
    db_manager.create_tables()
    print("✅ Tabelas criadas com sucesso!")

    # Obter sessão
    session = db_manager.get_session()

    try:
        # Verificar se já existem dados
        user_count = session.query(User).count()
        if user_count > 0:
            print("⚠️  Banco de dados já possui dados. Pulando criação de usuários.")
            return

        print("📝 Criando usuários de demonstração...")

        # Criar permissões básicas
        permissions = [
            Permission(
                code="admin.access",
                name="Acesso Administrativo",
                category="admin",
                description="Acesso completo ao sistema",
                is_system=True
            ),
            Permission(
                code="user.view",
                name="Visualizar Usuários",
                category="users",
                description="Visualizar lista de usuários"
            ),
            Permission(
                code="user.edit",
                name="Editar Usuários",
                category="users",
                description="Criar, editar e excluir usuários"
            ),
            Permission(
                code="profile.view",
                name="Visualizar Perfis",
                category="profiles",
                description="Visualizar lista de perfis"
            ),
            Permission(
                code="profile.edit",
                name="Editar Perfis",
                category="profiles",
                description="Criar, editar e excluir perfis"
            ),
            Permission(
                code="dashboard.view",
                name="Visualizar Dashboard",
                category="dashboard",
                description="Acesso ao dashboard principal"
            ),
            Permission(
                code="tools.query",
                name="Console SQL",
                category="tools",
                description="Acesso ao console SQL (DS_QUERY)"
            ),
            Permission(
                code="tools.table",
                name="Navegador de Tabelas",
                category="tools",
                description="Acesso ao navegador de tabelas (DS_TAB)"
            ),
            Permission(
                code="designer.access",
                name="UI Designer",
                category="designer",
                description="Acesso ao UI Designer (DS_DESIGNER)"
            ),
        ]

        for perm in permissions:
            session.add(perm)

        session.flush()

        # Criar perfis
        admin_profile = Profile(
            code="ADMIN",
            name="Administrador",
            description="Perfil de administrador com acesso completo",
            is_system=True,
            priority=100
        )

        developer_profile = Profile(
            code="DEVELOPER",
            name="Desenvolvedor",
            description="Perfil de desenvolvedor com acesso a ferramentas",
            is_system=True,
            priority=50
        )

        user_profile = Profile(
            code="USER",
            name="Usuário",
            description="Perfil básico de usuário",
            is_system=True,
            priority=10
        )

        # Adicionar permissões aos perfis
        admin_profile.permissions = permissions  # Todas as permissões

        developer_profile.permissions = [
            perm for perm in permissions
            if perm.code in ["dashboard.view", "tools.query", "tools.table", "designer.access"]
        ]

        user_profile.permissions = [
            perm for perm in permissions
            if perm.code in ["dashboard.view"]
        ]

        session.add_all([admin_profile, developer_profile, user_profile])
        session.flush()

        # Criar usuários
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

        developer_user = User(
            username="developer",
            email="developer@devstation.local",
            full_name="Desenvolvedor",
            is_active=True,
            theme="dark",
            language="pt_BR"
        )
        developer_user.set_password("dev123")
        developer_user.profiles = [developer_profile]

        test_user = User(
            username="user",
            email="user@devstation.local",
            full_name="Usuário de Teste",
            is_active=True,
            theme="light",
            language="pt_BR"
        )
        test_user.set_password("user123")
        test_user.profiles = [user_profile]

        session.add_all([admin_user, developer_user, test_user])

        # Commit
        session.commit()

        print("✅ Usuários criados com sucesso!")
        print("\n📋 Credenciais de acesso:")
        print("  👑 Admin: admin / admin123")
        print("  💻 Developer: developer / dev123")
        print("  👤 User: user / user123")

    except Exception as e:
        session.rollback()
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    init_database()