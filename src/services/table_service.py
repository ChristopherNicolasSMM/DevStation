"""
Serviço para criação e gerenciamento de tabelas dinâmicas.
"""

from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from db.database import db
from model.table_config import TableConfig
from model.field_config import FieldConfig
from utils.dynamic_model import create_dynamic_model, get_sqlalchemy_type


class TableService:
    """Serviço para operações com tabelas dinâmicas."""
    
    @staticmethod
    def create_table(table_config: TableConfig):
        """
        Cria uma tabela dinâmica no banco de dados baseada na configuração.
        
        Args:
            table_config: Instância de TableConfig com campos configurados
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Criar modelo dinâmico
            model_class = create_dynamic_model(table_config)
            
            # Criar tabela no banco
            model_class.__table__.create(db.engine, checkfirst=True)
            
            # Criar índices para chave única se especificada
            if table_config.unique_key:
                TableService._create_unique_index(table_config)
            
            # Criar índices para campos únicos
            for field in table_config.fields:
                if field.is_unique:
                    TableService._create_field_index(table_config.table_name, field.name, unique=True)
            
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Erro ao criar tabela: {str(e)}")
    
    @staticmethod
    def _create_unique_index(table_config: TableConfig):
        """Cria índice único composto para a chave única."""
        try:
            inspector = inspect(db.engine)
            index_name = f"idx_{table_config.table_name}_unique_key"
            
            # Verificar se índice já existe
            existing_indexes = [idx['name'] for idx in inspector.get_indexes(table_config.table_name)]
            if index_name in existing_indexes:
                return
            
            # Criar índice único
            columns = ', '.join(table_config.unique_key)
            sql = f"""
                CREATE UNIQUE INDEX IF NOT EXISTS {index_name}
                ON {table_config.table_name} ({columns})
            """
            db.session.execute(text(sql))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # Não falhar se não conseguir criar índice
            print(f"Aviso: Não foi possível criar índice único: {e}")
    
    @staticmethod
    def _create_field_index(table_name: str, field_name: str, unique: bool = False):
        """Cria índice para um campo."""
        try:
            inspector = inspect(db.engine)
            index_name = f"idx_{table_name}_{field_name}" + ("_unique" if unique else "")
            
            # Verificar se índice já existe
            existing_indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
            if index_name in existing_indexes:
                return
            
            unique_clause = "UNIQUE" if unique else ""
            sql = f"""
                CREATE {unique_clause} INDEX IF NOT EXISTS {index_name}
                ON {table_name} ({field_name})
            """
            db.session.execute(text(sql))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Aviso: Não foi possível criar índice: {e}")
    
    @staticmethod
    def drop_table(table_config: TableConfig):
        """
        Remove uma tabela dinâmica do banco de dados.
        
        Args:
            table_config: Instância de TableConfig
        """
        try:
            inspector = inspect(db.engine)
            if table_config.table_name in inspector.get_table_names():
                sql = f"DROP TABLE IF EXISTS {table_config.table_name}"
                db.session.execute(text(sql))
                db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Erro ao remover tabela: {str(e)}")
    
    @staticmethod
    def table_exists(table_name: str) -> bool:
        """
        Verifica se uma tabela existe no banco.
        
        Args:
            table_name: Nome da tabela
        
        Returns:
            True se existe, False caso contrário
        """
        try:
            inspector = inspect(db.engine)
            return table_name in inspector.get_table_names()
        except Exception:
            return False
    
    @staticmethod
    def add_field_to_table(table_config: TableConfig, field_config: FieldConfig):
        """
        Adiciona um campo a uma tabela existente.
        
        Args:
            table_config: Instância de TableConfig
            field_config: Instância de FieldConfig
        """
        try:
            sql_type = get_sqlalchemy_type(field_config.field_type, field_config.size)
            column_type = str(sql_type.compile(db.engine.dialect))
            
            nullable = "NULL" if not field_config.is_required else "NOT NULL"
            default = f"DEFAULT '{field_config.default_value}'" if field_config.default_value else ""
            
            sql = f"""
                ALTER TABLE {table_config.table_name}
                ADD COLUMN {field_config.name} {column_type} {nullable} {default}
            """
            db.session.execute(text(sql))
            db.session.commit()
            
            # Criar índice se necessário
            if field_config.is_unique:
                TableService._create_field_index(table_config.table_name, field_config.name, unique=True)
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Erro ao adicionar campo: {str(e)}")
    
    @staticmethod
    def get_table_model(table_config: TableConfig):
        """
        Obtém a classe do modelo para uma tabela configurada.
        
        Args:
            table_config: Instância de TableConfig
        
        Returns:
            Classe do modelo SQLAlchemy
        """
        if not TableService.table_exists(table_config.table_name):
            return None
        
        return create_dynamic_model(table_config)
