"""
Audit logging models for traceability
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from datetime import datetime

from core.models.base import Base


class AuditLog(Base):
    """Audit log for all system actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Who
    user_id = Column(Integer, index=True)
    user_name = Column(String(100))
    user_profile_codes = Column(String(500))  # Comma-separated profile codes
    session_id = Column(String(128))
    ip_address = Column(String(45))
    
    # What
    transaction_code = Column(String(20), index=True)
    action_type = Column(String(50))  # CREATE, READ, UPDATE, DELETE, EXECUTE, EXPORT
    object_type = Column(String(100))
    object_id = Column(String(200))
    object_name = Column(String(200))
    
    # Before/After (for changes)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    diff_summary = Column(String(500))
    
    # Context
    execution_time_ms = Column(Integer)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    # KPI Tags
    kpi_tags = Column(JSON, default=list)
    
    def to_dict(self) -> dict:
        """Convert audit log to dictionary"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_name": self.user_name,
            "transaction_code": self.transaction_code,
            "action_type": self.action_type,
            "object_type": self.object_type,
            "object_name": self.object_name,
            "success": self.success,
            "execution_time_ms": self.execution_time_ms
        }


class ChangeLog(Base):
    """Log of system modifications for version tracking"""
    __tablename__ = "changelog"
    
    id = Column(Integer, primary_key=True)
    change_id = Column(String(20), unique=True, index=True)  # CHG-2024-001
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Author
    author_id = Column(Integer)
    author_name = Column(String(100))
    author_profile = Column(String(50))
    
    # Object modified
    object_type = Column(String(50))  # FILE, TRANSACTION, PLUGIN, WORKFLOW, API
    object_path = Column(String(500))
    object_code = Column(String(50))
    
    # Change details
    change_type = Column(String(30))  # CREATE, MODIFY, DELETE, RENAME, MOVE
    change_summary = Column(String(200))
    change_description = Column(Text)
    
    # Versioning
    version_before = Column(String(20))
    version_after = Column(String(20))
    git_commit_hash = Column(String(40))
    
    # Traceability
    ticket_id = Column(String(50))
    branch_name = Column(String(100))
    
    # Impact
    affected_objects = Column(JSON, default=list)
    kpi_impact = Column(String(100))
    
    def to_dict(self) -> dict:
        """Convert change log to dictionary"""
        return {
            "change_id": self.change_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "author_name": self.author_name,
            "object_type": self.object_type,
            "object_code": self.object_code,
            "change_type": self.change_type,
            "change_summary": self.change_summary,
            "version_after": self.version_after
        }