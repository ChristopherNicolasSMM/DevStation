"""
Utilitário para configuração automática do ambiente de desenvolvimento.
"""

import os
from db.database import db
from model.user import User, UserGroup


def ensure_dev_admin():
    """
    Garante que existe um usuário admin no ambiente de desenvolvimento.
    Cria automaticamente se não existir com senha '123'.
    """
    flask_env = os.getenv("FLASK_ENV", "DEV")
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    if flask_env != "DEV" and not debug:
        return False
    
    try:
        # Inicializar grupos padrão
        User.initialize_default_groups()
        
        # Verificar se já existe admin
        admin = User.query.filter_by(username="admin").first()
        
        if not admin:
            # Obter grupo Administrador
            admin_group = UserGroup.query.filter_by(name="Administrador").first()
            
            # Criar admin
            admin = User(
                username="admin",
                email="admin@devstation.com",
                is_admin=True,
                is_active=True,
                group_id=admin_group.id if admin_group else None
            )
            admin.set_password("123")
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Usuário admin criado automaticamente (usuário: admin, senha: 123)")
            return True
        else:
            # Admin já existe, garantir que está ativo
            if not admin.is_active:
                admin.is_active = True
                db.session.commit()
                print("✅ Usuário admin reativado")
            
            # Resetar senha para '123' em desenvolvimento
            admin.set_password("123")
            db.session.commit()
            print("✅ Senha do admin resetada para '123' (desenvolvimento)")
            
            return False
    except Exception as e:
        print(f"⚠️  Erro ao verificar/criar admin: {e}")
        db.session.rollback()
        return False
