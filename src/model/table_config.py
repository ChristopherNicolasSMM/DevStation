"""
Modelo de configuração de tabelas dinâmicas.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import db


class TableConfig(db.Model):
    """Configuração de uma tabela dinâmica."""
    __tablename__ = 'table_configs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    table_name = Column(String(100), unique=True, nullable=False)  # Nome da tabela no banco
    unique_key = Column(JSON, nullable=True)  # Lista de campos que compõem a chave única
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    fields = relationship('FieldConfig', back_populates='table_config', cascade='all, delete-orphan', order_by='FieldConfig.order')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'table_name': self.table_name,
            'unique_key': self.unique_key,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'fields': [f.to_dict() for f in self.fields] if self.fields else []
        }
    
    def __repr__(self):
        return f'<TableConfig {self.name}>'
