"""
Serviço de auditoria e histórico de alterações.
"""

from sqlalchemy import desc
from db.database import db
from model.audit import AuditLog, AuditAction
from flask_login import current_user


class AuditService:
    """Serviço para operações de auditoria."""
    
    @staticmethod
    def log_action(table_config_id: int, record_id: int, action: AuditAction, 
                   data_before: dict = None, data_after: dict = None,
                   changed_fields: list = None, import_log_id: int = None,
                   notes: str = None):
        """
        Registra uma ação no log de auditoria.
        
        Args:
            table_config_id: ID da configuração da tabela
            record_id: ID do registro
            action: Ação realizada
            data_before: Dados antes da alteração
            data_after: Dados depois da alteração
            changed_fields: Lista de campos alterados
            import_log_id: ID do log de importação (se aplicável)
            notes: Notas adicionais
        """
        audit_log = AuditLog(
            table_config_id=table_config_id,
            record_id=record_id,
            action=action,
            user_id=current_user.id if current_user.is_authenticated else None,
            data_before=data_before,
            data_after=data_after,
            changed_fields=changed_fields,
            import_log_id=import_log_id,
            notes=notes
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return audit_log
    
    @staticmethod
    def get_audit_history(table_config_id: int, record_id: int = None, limit: int = 100):
        """
        Obtém histórico de auditoria.
        
        Args:
            table_config_id: ID da configuração da tabela
            record_id: ID do registro (opcional, para filtrar)
            limit: Limite de registros
        
        Returns:
            Lista de logs de auditoria
        """
        query = AuditLog.query.filter_by(table_config_id=table_config_id)
        
        if record_id:
            query = query.filter_by(record_id=record_id)
        
        logs = query.order_by(desc(AuditLog.created_at)).limit(limit).all()
        
        return [log.to_dict() for log in logs]
    
    @staticmethod
    def get_recent_activity(table_config_id: int = None, limit: int = 50):
        """
        Obtém atividade recente.
        
        Args:
            table_config_id: ID da configuração da tabela (opcional)
            limit: Limite de registros
        
        Returns:
            Lista de logs de auditoria
        """
        query = AuditLog.query
        
        if table_config_id:
            query = query.filter_by(table_config_id=table_config_id)
        
        logs = query.order_by(desc(AuditLog.created_at)).limit(limit).all()
        
        return [log.to_dict() for log in logs]
