"""
Modelo de auditoria e histórico de alterações.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from db.database import db


class AuditAction(enum.Enum):
    """Ações auditadas."""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    IMPORT = "IMPORT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"


class AuditLog(db.Model):
    """Log de auditoria de alterações."""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_config_id = Column(Integer, ForeignKey('table_configs.id', ondelete='CASCADE'), nullable=False)
    record_id = Column(Integer, nullable=False)  # ID do registro na tabela dinâmica
    
    # Ação realizada
    action = Column(Enum(AuditAction), nullable=False)
    
    # Usuário que realizou a ação
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Dados antes e depois (para UPDATE)
    data_before = Column(JSON, nullable=True)  # Dados antes da alteração
    data_after = Column(JSON, nullable=True)  # Dados depois da alteração
    
    # Campos alterados (para UPDATE)
    changed_fields = Column(JSON, nullable=True)  # Lista de campos que foram alterados
    
    # Informações adicionais
    import_log_id = Column(Integer, ForeignKey('import_logs.id', ondelete='SET NULL'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=func.now())
    
    # Relacionamentos
    table_config = relationship('TableConfig')
    user = relationship('User')
    import_log = relationship('ImportLog')
    
    def to_dict(self):
        return {
            'id': self.id,
            'table_config_id': self.table_config_id,
            'record_id': self.record_id,
            'action': self.action.value if self.action else None,
            'user_id': self.user_id,
            'data_before': self.data_before,
            'data_after': self.data_after,
            'changed_fields': self.changed_fields,
            'import_log_id': self.import_log_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<AuditLog {self.action.value} record:{self.record_id} table:{self.table_config_id}>'
