"""
Modelo de configuração de campos de tabelas dinâmicas.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import db


class FieldConfig(db.Model):
    """Configuração de um campo de uma tabela dinâmica."""
    __tablename__ = 'field_configs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_config_id = Column(Integer, ForeignKey('table_configs.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)  # Nome do campo no banco
    label = Column(String(100), nullable=False)  # Label para exibição
    field_type = Column(String(50), nullable=False)  # text, number, date, boolean, list
    size = Column(Integer, nullable=True)  # Tamanho máximo (para texto)
    is_required = Column(Boolean, default=False)
    is_unique = Column(Boolean, default=False)
    default_value = Column(Text, nullable=True)  # Valor padrão
    validations = Column(JSON, nullable=True)  # Regras de validação (regex, min, max, etc.)
    options = Column(JSON, nullable=True)  # Opções para campos do tipo list
    order = Column(Integer, default=0)  # Ordem de exibição
    is_filterable = Column(Boolean, default=True)  # Se pode ser usado em filtros
    is_visible = Column(Boolean, default=True)  # Se é visível por padrão
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    table_config = relationship('TableConfig', back_populates='fields')
    
    def to_dict(self):
        return {
            'id': self.id,
            'table_config_id': self.table_config_id,
            'name': self.name,
            'label': self.label,
            'field_type': self.field_type,
            'size': self.size,
            'is_required': self.is_required,
            'is_unique': self.is_unique,
            'default_value': self.default_value,
            'validations': self.validations,
            'options': self.options,
            'order': self.order,
            'is_filterable': self.is_filterable,
            'is_visible': self.is_visible,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<FieldConfig {self.name} (table: {self.table_config_id})>'
