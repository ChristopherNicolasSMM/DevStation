"""
Modelo de logs de importação de arquivos Excel.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import db


class ImportLog(db.Model):
    """Log de uma importação de arquivo Excel."""
    __tablename__ = 'import_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_config_id = Column(Integer, ForeignKey('table_configs.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Informações do arquivo
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)  # Caminho do arquivo salvo
    file_size = Column(Integer, nullable=True)  # Tamanho em bytes
    
    # Estatísticas
    total_rows = Column(Integer, default=0)
    new_records = Column(Integer, default=0)
    updated_records = Column(Integer, default=0)
    unchanged_records = Column(Integer, default=0)
    error_records = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default='pending')  # pending, processing, completed, failed, approved, rejected
    error_message = Column(Text, nullable=True)
    
    # Dados processados (para auditoria)
    processed_data = Column(JSON, nullable=True)  # Dados parseados do Excel
    divergences = Column(JSON, nullable=True)  # Divergências detectadas
    
    # Timestamps
    uploaded_at = Column(DateTime, default=func.now())
    processed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Relacionamentos
    table_config = relationship('TableConfig')
    user = relationship('User', foreign_keys=[user_id])
    approved_by = relationship('User', foreign_keys=[approved_by_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'table_config_id': self.table_config_id,
            'user_id': self.user_id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'total_rows': self.total_rows,
            'new_records': self.new_records,
            'updated_records': self.updated_records,
            'unchanged_records': self.unchanged_records,
            'error_records': self.error_records,
            'status': self.status,
            'error_message': self.error_message,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approved_by_id': self.approved_by_id,
        }
    
    def __repr__(self):
        return f'<ImportLog {self.filename} ({self.status})>'
