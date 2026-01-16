"""
Modelo de layouts salvos para listagens.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import db


class Layout(db.Model):
    """Layout salvo para uma tabela."""
    __tablename__ = 'layouts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_config_id = Column(Integer, ForeignKey('table_configs.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)  # None = layout padrão
    group_id = Column(Integer, ForeignKey('user_groups.id', ondelete='CASCADE'), nullable=True)  # None = layout pessoal ou padrão
    
    # Nome e descrição
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)  # Layout padrão da tabela
    
    # Configuração do layout
    visible_fields = Column(JSON, nullable=True)  # Lista de campos visíveis
    filters = Column(JSON, nullable=True)  # Filtros aplicados {field: value}
    order_by = Column(String(100), nullable=True)  # Campo de ordenação
    order_dir = Column(String(10), default='asc')  # Direção da ordenação
    per_page = Column(Integer, default=20)  # Registros por página
    
    # Agrupamento e sumarização
    group_by = Column(JSON, nullable=True)  # Campos para agrupar
    summarize_fields = Column(JSON, nullable=True)  # Campos para sumarizar {field: function}
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    table_config = relationship('TableConfig')
    user = relationship('User')
    group = relationship('UserGroup')
    
    def to_dict(self):
        return {
            'id': self.id,
            'table_config_id': self.table_config_id,
            'user_id': self.user_id,
            'group_id': self.group_id,
            'name': self.name,
            'description': self.description,
            'is_default': self.is_default,
            'visible_fields': self.visible_fields,
            'filters': self.filters,
            'order_by': self.order_by,
            'order_dir': self.order_dir,
            'per_page': self.per_page,
            'group_by': self.group_by,
            'summarize_fields': self.summarize_fields,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        scope = 'padrão' if self.is_default else ('grupo' if self.group_id else ('pessoal' if self.user_id else 'padrão'))
        return f'<Layout {self.name} ({scope})>'
