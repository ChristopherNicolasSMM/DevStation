"""
KPI Collector - Coleta e armazenamento de métricas
Sprint 3 - Sistema de KPIs
"""

import threading
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict, deque

from core.models.base import db_manager
from core.models.audit import AuditLog


class KPICollector:
    """
    Coletor centralizado de métricas de performance e uso.
    Usa in-memory para velocidade + persiste via AuditLog existente.
    """

    _instance: Optional["KPICollector"] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Inicializa estruturas in-memory"""
        # Últimas N execuções por transação: {code: deque([ms, ...])}
        self._response_times: dict = defaultdict(lambda: deque(maxlen=500))
        # Contadores totais por transação: {code: int}
        self._tx_counts: dict = defaultdict(int)
        # Contadores de erro por transação: {code: int}
        self._tx_errors: dict = defaultdict(int)
        # Usuários ativos (set de user_ids nas últimas 24h)
        self._active_users_cache: set = set()
        self._cache_reset_time: datetime = datetime.utcnow() + timedelta(hours=24)

    # ──────────────────────────────────────────────
    # Registro
    # ──────────────────────────────────────────────

    def record_transaction(
        self,
        transaction_code: str,
        duration_ms: int,
        success: bool,
        user_id: int = 0,
    ):
        """Registra execução de transação."""
        with self._lock:
            self._tx_counts[transaction_code] += 1
            self._response_times[transaction_code].append(duration_ms)
            if not success:
                self._tx_errors[transaction_code] += 1

            # Reset cache diário
            if datetime.utcnow() > self._cache_reset_time:
                self._active_users_cache = set()
                self._cache_reset_time = datetime.utcnow() + timedelta(hours=24)

            if user_id:
                self._active_users_cache.add(user_id)

    # ──────────────────────────────────────────────
    # Dashboard
    # ──────────────────────────────────────────────

    def get_dashboard_data(self) -> dict:
        """Monta os dados completos para o DS_KPI_DASH."""
        # Dados do banco (período)
        db_stats = self._query_db_stats()

        # Dados in-memory
        top_tx = self._get_top_transactions(10)
        avg_rt = self._get_avg_response_time()
        error_rate = self._get_overall_error_rate()

        return {
            "total_transactions": db_stats["total"],
            "transactions_today": db_stats["today"],
            "active_users_session": len(self._active_users_cache),
            "avg_response_time_ms": avg_rt,
            "error_rate_pct": error_rate,
            "kpi_score": self._calculate_kpi_score(avg_rt, error_rate),
            "top_transactions": top_tx,
            "hourly_distribution": db_stats["hourly"],
            "action_distribution": db_stats["actions"],
            "success_vs_error": db_stats["success_vs_error"],
        }

    def _query_db_stats(self) -> dict:
        """Consulta estatísticas do banco de dados."""
        try:
            session = db_manager.get_session()

            total = session.query(AuditLog).count()
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today = session.query(AuditLog).filter(AuditLog.timestamp >= today_start).count()

            # Distribuição por hora (últimas 24h)
            since_24h = datetime.utcnow() - timedelta(hours=24)
            recent = (
                session.query(AuditLog)
                .filter(AuditLog.timestamp >= since_24h)
                .all()
            )

            hourly: dict = defaultdict(int)
            actions: dict = defaultdict(int)
            success_count = 0
            error_count = 0

            for row in recent:
                if row.timestamp:
                    hourly[row.timestamp.hour] += 1
                if row.action_type:
                    actions[row.action_type] += 1
                if row.success:
                    success_count += 1
                else:
                    error_count += 1

            session.close()

            return {
                "total": total,
                "today": today,
                "hourly": [{"hour": h, "count": hourly[h]} for h in sorted(hourly)],
                "actions": [{"action": k, "count": v} for k, v in actions.items()],
                "success_vs_error": {
                    "success": success_count,
                    "error": error_count,
                },
            }
        except Exception as exc:
            print(f"[KPICollector] Erro DB: {exc}")
            return {"total": 0, "today": 0, "hourly": [], "actions": [], "success_vs_error": {"success": 0, "error": 0}}

    def _get_top_transactions(self, n: int = 10) -> list:
        with self._lock:
            sorted_tx = sorted(
                self._tx_counts.items(), key=lambda x: x[1], reverse=True
            )[:n]
            result = []
            for code, count in sorted_tx:
                times = list(self._response_times[code])
                avg = int(sum(times) / len(times)) if times else 0
                errors = self._tx_errors[code]
                result.append(
                    {
                        "code": code,
                        "count": count,
                        "avg_ms": avg,
                        "errors": errors,
                        "error_rate": round(errors / count * 100, 1) if count > 0 else 0,
                    }
                )
            return result

    def _get_avg_response_time(self) -> float:
        with self._lock:
            all_times = []
            for times in self._response_times.values():
                all_times.extend(times)
            if not all_times:
                return 0.0
            return round(sum(all_times) / len(all_times), 1)

    def _get_overall_error_rate(self) -> float:
        with self._lock:
            total = sum(self._tx_counts.values())
            errors = sum(self._tx_errors.values())
            if total == 0:
                return 0.0
            return round(errors / total * 100, 2)

    def _calculate_kpi_score(self, avg_rt: float, error_rate: float) -> int:
        """
        Score de 0-100 baseado em:
        - Tempo de resposta (ideal < 200ms)
        - Taxa de erro (ideal 0%)
        """
        rt_score = max(0, 100 - int(avg_rt / 10))  # -1 pt por 10ms
        err_score = max(0, 100 - int(error_rate * 10))  # -10 pts por 1% de erro
        return min(100, (rt_score + err_score) // 2)

    def get_transaction_detail(self, code: str) -> dict:
        """Retorna detalhes de uma transação específica."""
        with self._lock:
            times = list(self._response_times[code])
            count = self._tx_counts[code]
            errors = self._tx_errors[code]

            if not times:
                return {"code": code, "no_data": True}

            return {
                "code": code,
                "total_executions": count,
                "total_errors": errors,
                "avg_ms": round(sum(times) / len(times), 1),
                "min_ms": min(times),
                "max_ms": max(times),
                "p95_ms": sorted(times)[int(len(times) * 0.95)] if times else 0,
                "error_rate": round(errors / count * 100, 2) if count > 0 else 0,
            }


# Instância global
kpi_collector = KPICollector()
