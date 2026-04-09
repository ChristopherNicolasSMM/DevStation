"""
AuditLogger - Serviço centralizado de auditoria
Sprint 2 - Rastreabilidade Total
"""

import threading
from datetime import datetime
from typing import Optional, Any
from contextlib import contextmanager

from core.models.base import db_manager
from core.models.audit import AuditLog, ChangeLog


class AuditLogger:
    """
    Serviço singleton para registro de auditoria.
    Toda ação no sistema passa por aqui.
    """

    _instance: Optional["AuditLogger"] = None
    _lock = threading.Lock()
    _chg_counter: int = 0

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Inicializa o contador de CHG a partir do banco"""
        try:
            session = db_manager.get_session()
            count = session.query(ChangeLog).count()
            self._chg_counter = count
            session.close()
        except Exception:
            self._chg_counter = 0

    # ──────────────────────────────────────────────
    # Audit Log
    # ──────────────────────────────────────────────

    def log(
        self,
        *,
        user_id: int,
        user_name: str,
        user_profiles: str,
        transaction_code: str,
        action_type: str,
        object_type: str,
        object_id: str = "",
        object_name: str = "",
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
        diff_summary: str = "",
        execution_time_ms: int = 0,
        success: bool = True,
        error_message: str = "",
        session_id: str = "",
        ip_address: str = "127.0.0.1",
        kpi_tags: list = None,
    ) -> Optional[AuditLog]:
        """Registra uma ação de auditoria no banco."""
        try:
            session = db_manager.get_session()
            entry = AuditLog(
                timestamp=datetime.utcnow(),
                user_id=user_id,
                user_name=user_name,
                user_profile_codes=user_profiles,
                session_id=session_id,
                ip_address=ip_address,
                transaction_code=transaction_code,
                action_type=action_type,
                object_type=object_type,
                object_id=str(object_id),
                object_name=object_name,
                old_value=old_value,
                new_value=new_value,
                diff_summary=diff_summary,
                execution_time_ms=execution_time_ms,
                success=success,
                error_message=error_message,
                kpi_tags=kpi_tags or [],
            )
            session.add(entry)
            session.commit()
            session.refresh(entry)
            result_id = entry.id
            session.close()
            return result_id
        except Exception as exc:
            print(f"[AuditLogger] Erro ao salvar log: {exc}")
            return None

    @contextmanager
    def track(
        self,
        *,
        user_id: int,
        user_name: str,
        user_profiles: str,
        transaction_code: str,
        action_type: str,
        object_type: str,
        object_id: str = "",
        object_name: str = "",
        kpi_tags: list = None,
    ):
        """
        Context manager que mede tempo e captura erros automaticamente.

        Uso:
            with audit_logger.track(...) as ctx:
                ctx["old"] = data_before
                do_something()
                ctx["new"] = data_after
        """
        ctx: dict = {"old": None, "new": None, "error": None}
        start = datetime.utcnow()
        try:
            yield ctx
            elapsed = int((datetime.utcnow() - start).total_seconds() * 1000)
            self.log(
                user_id=user_id,
                user_name=user_name,
                user_profiles=user_profiles,
                transaction_code=transaction_code,
                action_type=action_type,
                object_type=object_type,
                object_id=object_id,
                object_name=object_name,
                old_value=ctx.get("old"),
                new_value=ctx.get("new"),
                execution_time_ms=elapsed,
                success=True,
                kpi_tags=kpi_tags or [],
            )
        except Exception as exc:
            elapsed = int((datetime.utcnow() - start).total_seconds() * 1000)
            self.log(
                user_id=user_id,
                user_name=user_name,
                user_profiles=user_profiles,
                transaction_code=transaction_code,
                action_type=action_type,
                object_type=object_type,
                object_id=object_id,
                object_name=object_name,
                execution_time_ms=elapsed,
                success=False,
                error_message=str(exc),
                kpi_tags=kpi_tags or [],
            )
            raise

    # ──────────────────────────────────────────────
    # Change Log
    # ──────────────────────────────────────────────

    def _next_chg_id(self) -> str:
        with self._lock:
            self._chg_counter += 1
            year = datetime.utcnow().year
            return f"CHG-{year}-{self._chg_counter:04d}"

    def log_change(
        self,
        *,
        author_id: int,
        author_name: str,
        author_profile: str,
        object_type: str,
        object_path: str = "",
        object_code: str = "",
        change_type: str,
        change_summary: str,
        change_description: str = "",
        version_before: str = "",
        version_after: str = "",
        git_commit_hash: str = "",
        ticket_id: str = "",
        branch_name: str = "",
        affected_objects: list = None,
        kpi_impact: str = "NEUTRAL",
    ) -> str:
        """Registra uma mudança estrutural no ChangeLog. Retorna o change_id."""
        change_id = self._next_chg_id()
        try:
            session = db_manager.get_session()
            entry = ChangeLog(
                change_id=change_id,
                timestamp=datetime.utcnow(),
                author_id=author_id,
                author_name=author_name,
                author_profile=author_profile,
                object_type=object_type,
                object_path=object_path,
                object_code=object_code,
                change_type=change_type,
                change_summary=change_summary,
                change_description=change_description,
                version_before=version_before,
                version_after=version_after,
                git_commit_hash=git_commit_hash,
                ticket_id=ticket_id,
                branch_name=branch_name,
                affected_objects=affected_objects or [],
                kpi_impact=kpi_impact,
            )
            session.add(entry)
            session.commit()
            session.close()
        except Exception as exc:
            print(f"[AuditLogger] Erro ao salvar ChangeLog: {exc}")
        return change_id

    # ──────────────────────────────────────────────
    # Consultas rápidas
    # ──────────────────────────────────────────────

    def get_recent_audit(self, limit: int = 100) -> list:
        """Retorna os logs de auditoria mais recentes."""
        session = db_manager.get_session()
        rows = (
            session.query(AuditLog)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )
        result = [r.to_dict() for r in rows]
        session.close()
        return result

    def get_recent_changes(self, limit: int = 100) -> list:
        """Retorna os changelogs mais recentes."""
        session = db_manager.get_session()
        rows = (
            session.query(ChangeLog)
            .order_by(ChangeLog.timestamp.desc())
            .limit(limit)
            .all()
        )
        result = [r.to_dict() for r in rows]
        session.close()
        return result

    def get_audit_stats(self) -> dict:
        """Retorna estatísticas de auditoria para o dashboard."""
        session = db_manager.get_session()
        total = session.query(AuditLog).count()
        errors = session.query(AuditLog).filter(AuditLog.success == False).count()
        changes = session.query(ChangeLog).count()
        session.close()
        return {
            "total_actions": total,
            "total_errors": errors,
            "total_changes": changes,
            "success_rate": round((total - errors) / total * 100, 1) if total > 0 else 100.0,
        }


# Instância global
audit_logger = AuditLogger()
