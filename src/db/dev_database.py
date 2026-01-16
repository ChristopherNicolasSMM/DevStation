"""
Configuração de banco de dados SQLite para desenvolvimento.
"""

from flask_sqlalchemy import SQLAlchemy
import os
from pathlib import Path
from sqlalchemy import text

db = SQLAlchemy()

def init_db(app):
    """Inicializa o banco de dados SQLite."""
    try:
        # Garantir que o diretório existe
        current_dir = Path.cwd()
        if current_dir.name == 'src':
            db_path = Path('instance')
        else:
            db_path = Path('src/instance')
        
        db_path.mkdir(parents=True, exist_ok=True)
        
        # Configurar SQLite com caminho absoluto
        database_uri = f"sqlite:///{db_path.absolute()}/devstation.db"
        app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        print(f"Database path: {database_uri}")
        
        # Inicializar db com app
        db.init_app(app)
        
        # Importar modelos DEPOIS de inicializar o db
        with app.app_context():
            # Importar modelos core
            import model.user
            import model.table_config
            import model.field_config
            import model.permission
            import model.excel_mapping
            import model.import_log
            import model.audit
            import model.layout
            #import model.table_config
            #import model.field_config
            #import model.permission
            
            # Criar tabelas core
            db.create_all()
            print("✅ Tabelas core criadas com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        raise

def get_db():
    """Retorna a instância do banco de dados."""
    return db

def test_connection():
    """Testa a conexão com o banco de dados."""
    from flask import current_app
    try:
        with current_app.app_context():
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            
            print("✅ Conexão com o banco de dados estabelecida com sucesso!")
            return True
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro na conexão com o banco: {e}")
        return False
