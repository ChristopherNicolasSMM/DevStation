"""
Verificar banco de dados e criar usuários se necessário
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Verificando banco de dados...")

try:
    from core.models.base import db_manager
    from core.models.user import User, Profile, Permission

    # Criar sessão
    session = db_manager.get_session()

    # Verificar se há usuários
    user_count = session.query(User).count()
    print(f"Usuarios no banco: {user_count}")

    if user_count == 0:
        print("Criando usuario admin...")

        # Criar permissão
        perm = Permission(
            code="dashboard.view",
            name="Visualizar Dashboard",
            category="dashboard",
            description="Acesso ao dashboard",
            is_system=True
        )
        session.add(perm)
        session.flush()

        # Criar perfil
        profile = Profile(
            code="ADMIN",
            name="Administrador",
            description="Perfil de administrador",
            is_system=True,
            priority=100
        )
        profile.permissions = [perm]
        session.add(profile)
        session.flush()

        # Criar usuário
        user = User(
            username="admin",
            email="admin@devstation.local",
            full_name="Administrador",
            is_active=True
        )
        user.set_password("admin123")
        user.profiles = [profile]
        session.add(user)

        session.commit()
        print("Usuario admin criado: admin / admin123")

    # Listar usuários
    users = session.query(User).all()
    print("\nUsuarios cadastrados:")
    for u in users:
        print(f"  - {u.username} ({u.email})")

    session.close()

except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()