"""
Modelo de mapeamento Excel para campos de tabelas.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from db.database import db


class ExcelMapping(db.Model):
    """Mapeamento de colunas Excel para campos de tabela."""
    __tablename__ = 'excel_mappings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_config_id = Column(Integer, ForeignKey('table_configs.id', ondelete='CASCADE'), nullable=False)
    
    # Configuração do arquivo
    has_header = Column(Boolean, default=True)  # Primeira linha é cabeçalho
    start_row = Column(Integer, default=1)  # Linha inicial dos dados (1-indexed)
    
    # Mapeamento de colunas: {coluna_excel: campo_tabela}
    column_mapping = Column(JSON, nullable=False)  # {"A": "nome", "B": "preco", ...}
    
    # Relacionamentos
    table_config = relationship('TableConfig')
    
    def to_dict(self):
        return {
            'id': self.id,
            'table_config_id': self.table_config_id,
            'has_header': self.has_header,
            'start_row': self.start_row,
            'column_mapping': self.column_mapping,
        }
    
    def __repr__(self):
        return f'<ExcelMapping table:{self.table_config_id}>'
