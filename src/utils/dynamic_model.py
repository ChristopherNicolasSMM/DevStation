"""
Utilitário para criação dinâmica de modelos SQLAlchemy.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, Date, JSON
from sqlalchemy.ext.declarative import declarative_base
from db.database import db
from model.field_config import FieldConfig


def get_sqlalchemy_type(field_type: str, size: int = None):
    """
    Converte o tipo de campo configurado para tipo SQLAlchemy.
    
    Args:
        field_type: Tipo do campo (text, number, date, boolean, list)
        size: Tamanho máximo (para texto)
    
    Returns:
        Tipo SQLAlchemy correspondente
    """
    type_mapping = {
        'text': String(size) if size else Text,
        'number': Float,
        'integer': Integer,
        'date': Date,
        'datetime': DateTime,
        'boolean': Boolean,
        'list': String(255),  # Armazena como string JSON
        'json': JSON,
    }
    
    return type_mapping.get(field_type, Text)


def create_dynamic_model(table_config):
    """
    Cria um modelo SQLAlchemy dinamicamente baseado na configuração.
    
    Args:
        table_config: Instância de TableConfig
    
    Returns:
        Classe do modelo SQLAlchemy
    """
    # Criar dicionário de atributos
    attrs = {
        '__tablename__': table_config.table_name,
        'id': Column(Integer, primary_key=True, autoincrement=True),
    }
    
    # Adicionar campos baseados na configuração
    for field_config in table_config.fields:
        sql_type = get_sqlalchemy_type(field_config.field_type, field_config.size)
        
        # Configurar coluna
        column_args = []
        column_kwargs = {
            'nullable': not field_config.is_required,
        }
        
        if field_config.is_unique:
            column_kwargs['unique'] = True
        
        if field_config.default_value is not None:
            column_kwargs['default'] = field_config.default_value
        
        attrs[field_config.name] = Column(sql_type, *column_args, **column_kwargs)
    
    # Adicionar timestamps
    attrs['created_at'] = Column(DateTime, default=db.func.now())
    attrs['updated_at'] = Column(DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # Criar classe dinamicamente
    model_class = type(
        f'DynamicTable_{table_config.table_name}',
        (db.Model,),
        attrs
    )
    
    return model_class


def get_dynamic_table_class(table_name: str):
    """
    Obtém a classe do modelo dinâmico pelo nome da tabela.
    
    Args:
        table_name: Nome da tabela no banco
    
    Returns:
        Classe do modelo ou None se não encontrado
    """
    from sqlalchemy import inspect
    from db.database import db
    
    # Verificar se a tabela existe
    inspector = inspect(db.engine)
    if table_name not in inspector.get_table_names():
        return None
    
    # Criar classe dinâmica baseada na estrutura da tabela
    # Isso é uma abordagem simplificada - em produção, seria melhor
    # manter um registro de modelos criados
    attrs = {
        '__tablename__': table_name,
    }
    
    # Obter colunas da tabela
    columns = inspector.get_columns(table_name)
    for col in columns:
        col_name = col['name']
        if col_name == 'id':
            attrs[col_name] = Column(Integer, primary_key=True, autoincrement=True)
        elif col_name in ['created_at', 'updated_at']:
            attrs[col_name] = Column(DateTime)
        else:
            # Tipo genérico - em produção, mapear corretamente
            attrs[col_name] = Column(Text)
    
    model_class = type(
        f'DynamicTable_{table_name}',
        (db.Model,),
        attrs
    )
    
    return model_class
