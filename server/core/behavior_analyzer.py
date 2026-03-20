# -*- coding: utf-8 -*-
"""
Contextual Audit Engine - multi-dimensional behaviour analysis.

Replaces single-dimension dwell-time judgement with a context-aware
exemption chain.  All heavy I/O (DB queries) are delegated to an
injectable :class:`RiskDataProvider` interface so the engine itself
remains stateless and unit-testable.

Author : AHDUNYI
Version: 9.0.0
"""

import time
import threading
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import logging

try:
    from cachetools import TTLCache  # type: ignore
    _CACHETOOLS_OK: bool = True
except ImportError:
    TTLCache = None  # type: ignore
    _CACHETOOLS_OK = False

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------

class AuditStatus(Enum):
    """Possible outcomes of a single behaviour-analysis call."""

    NORMAL = "normal"
    SUSPICIOUS = "suspicious"
    SUDDEN_ISSUE = "sudden_issue"
    RISK_TRACKING = "risk_tracking"
    EXEMPTED = "exempted"


class AuditResult:
    """Encapsulates the outcome of one :meth:`ContextualAuditEngine.analyze_behavior` call.

    Args:
        status: Final verdict.
        reason: Human-readable explanation.
        checks: Ordered list of intermediate check results.
    """

    def __init__(
        self,
        status: AuditStatus,
        reason: str,
        checks: List[Dict[str, Any]],
    ) -> None:
        self.status = status
        self.reason = reason
        self.checks = checks

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dictionary (JSON-safe)."""
        return {
            "status": self.status.value,
            "reason": self.reason,
            "checks": self.checks,
        }


# ---------------------------------------------------------------------------
# Risk-data provider interface
# ---------------------------------------------------------------------------

class RiskDataProvider:
    """Abstract interface for external risk data.

    Subclass and override both methods to connect a real data source
    (database, Redis, remote API, etc.).
    """

    def get_risk_user_ids(self) -> List[int]:
        """Return the current list of high-risk user IDs."""
        return []

    def get_report_count(self, room_id: str, window_seconds: int) -> int:
        """Return the number of reports for *room_id* in the last *window_seconds*."""
        return 0


# ---------------------------------------------------------------------------
# In-memory cache
# ---------------------------------------------------------------------------

class MemoryCache:
    """Thread-safe in-memory cache with optional TTL support via *cachetools*.

    Falls back to plain ``dict`` with manual timestamp expiry when
    *cachetools* is not installed.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        if _CACHETOOLS_OK:
            self._risk: Any = TTLCache(maxsize=1000, ttl=300)
            self._reports: Any = TTLCache(maxsize=5000, ttl=60)
        else:
            self._risk: Dict[str, Any] = {}
            self._reports: Dict[str, Any] = {}
            self._ts: Dict[str, float] = {}

    # -- risk list -----------------------------------------------------------

    def get_risk_list(self) -> List[int]:
        """Return the cached high-risk user ID list."""
        with self._lock:
            if _CACHETOOLS_OK:
                return self._risk.get("risk_list", [])
            if time.time() - self._ts.get("risk_list", 0) > 300:
                return []
            return self._risk.get("risk_list", [])

    def set_risk_list(self, risk_list: List[int]) -> None:
        """Update the cached high-risk user ID list."""
        with self._lock:
            self._risk["risk_list"] = risk_list
            if not _CACHETOOLS_OK:
                self._ts["risk_list"] = time.time()

    # -- report counts -------------------------------------------------------

    def get_report_count(self, room_id: str, window: int) -> int:
        """Return the cached report count for *room_id*."""
        key = f"r_{room_id}_{window}"
        with self._lock:
            if _CACHETOOLS_OK:
                return self._reports.get(key, 0)
            if time.time() - self._ts.get(key, 0) > 60:
                return 0
            return self._reports.get(key, 0)

    def 
