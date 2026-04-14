"""
Teste simples de autenticação
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔧 Testando autenticação...")

try:
    # Importar apenas o necessário
    from core.models.base import db_manager
    print("✅ Database manager importado")

    # Verificar tabelas
    from sqlalchemy import inspect
    inspector = inspect(db_manager.engine)
    tables = inspector.get_table_names()
    print(f"✅ Tabelas: {tables}")

    # Verificar se há usuários
    from core.models.user import User
    session = db_manager.get_session()
    user_count = session.query(User).count()
    print(f"👤 Usuários no banco: {user_count}")

    if user_count == 0:
        print("⚠️  Criando usuário admin...")

        from core.models.user import Profile, Permission

        # Criar permissão
        perm = Permission(
            code="test.permission",
            name="Permissão de Teste",
            category="test",
            description="Permissão para teste"
        )
        session.add(perm)
        session.flush()

        # Criar perfil
        profile = Profile(
            code="TEST",
            name="Perfil de Teste",
            description="Perfil para teste",
            is_system=True,
            priority=10
        )
        profile.permissions = [perm]
        session.add(profile)
        session.flush()

        # Criar usuário
        user = User(
            username="test",
            email="test@devstation.local",
            full_name="Usuário de Teste",
            is_active=True
        )
        user.set_password("test123")
        user.profiles = [profile]
        session.add(user)
        session.commit()

        print("✅ Usuário criado: test / test123")

    # Testar autenticação
    print("\n🔐 Testando autenticação...")
    from core.security.rbac import rbac

    # Testar com credenciais incorretas primeiro
    result = rbac.authenticate("wrong", "wrong")
    print(f"❌ Credenciais erradas: {'Falhou como esperado' if not result else 'ERRO - deveria falhar'}")

    # Testar com credenciais corretas
    users = session.query(User).all()
    for user in users:
        print(f"\n🔑 Testando usuário: {user.username}")
        result = rbac.authenticate(user.username, "test123" if user.username == "test" else "admin123" if user.username == "admin" else "dev123")
        if result:
            print(f"✅ Autenticação bem-sucedida!")
            print(f"   Token: {result['token'][:30]}...")
            print(f"   Usuário: {result['user'].get('username')}")
        else:
            print(f"❌ Autenticação falhou")

    session.close()

except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()