from enum import Enum
from typing import Any, Dict, List


class AuditStatus(Enum):
    NORMAL = "normal"
    SUSPICIOUS = "suspicious"
    SUDDEN_ISSUE = "sudden_issue"
    RISK_TRACKING = "risk_tracking"
    EXEMPTED = "exempted"


class AuditResult:
    def __init__(self, status: AuditStatus, reason: str, checks: List[Dict[str, Any]]) -> None:
        self.status = status
        self.reason = reason
        self.checks = checks

    def to_dict(self) -> Dict[str, Any]:
        return {"status": self.status.value, "reason": self.reason, "checks": self.checks}
