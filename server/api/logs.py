# -*- coding: utf-8 -*-
"""
Action log API router.

Endpoints
---------
POST /api/log/action  -- Write one action log entry (called per key-press)
GET  /api/log/list    -- Paginated log list for shadow-audit dashboard

Author : AHDUNYI
Version: 9.0.0
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from server.core.database import get_db
from server.db.models import ActionLog, User
from server.schemas import ActionLogCreate, ActionLogListResponse, ActionLogOut, OkResponse
from server.api.permissions import _get_current_user
from server.constants.permissions import Permission, get_permissions_for_role

router = APIRouter(prefix="/api/log", tags=["logs"])


@router.post("/action", response_model=OkResponse)
def write_action_log(
    body: ActionLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
) -> OkResponse:
    """Persist a single auditor action to the log table.

    Called silently from the frontend on every key-press / workflow event.
    Failures are tolerated — the client swallows them.

    Args:
        body:         Log entry payload.
        db:           Injected DB session.
        current_user: Resolved from JWT.

    Returns:
        :class:`OkResponse`
    """
    try:
        ts: datetime
        if body.timestamp:
            try:
                ts = datetime.fromisoformat(body.timestamp.replace("Z", "+00:00"))
            except ValueError:
                ts = datetime.now(timezone.utc)
        else:
            ts = datetime.now(timezone.utc)

        entry = ActionLog(
            user_id=current_user.id,
            username=current_user.username,
            action=body.action,
            details=body.details,
            task_id=body.task_id,
            duration=body.duration,
            timestamp=ts,
        )
        db.add(entry)
        db.commit()
        return OkResponse(message="Log written.")
    except Exception as exc:
        db.rollback()
        # Do NOT raise 500 — the frontend ignores log failures by design.
        return OkResponse(success=False, message=f"Log write failed silently: {exc}")


@router.get("/list", response_model=ActionLogListResponse)
def list_action_logs(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
) -> ActionLogListResponse:
    """Return a paginated list of action logs for the shadow-audit dashboard.

    Requires ``view:shadow_audit`` permission.

    Args:
        user_id:      Filter by specific user.
        action:       Filter by action name (partial match).
        start_time:   ISO datetime lower bound.
        end_time:     ISO datetime upper bound.
        page:         1-based page number.
        page_size:    Number of items per page (max 200).
        db:           Injected DB session.
        current_user: Resolved from JWT.

    Returns:
        :class:`ActionLogListResponse`
    """
    perms = get_permissions_for_role(current_user.role.value)
    if Permission.VIEW_SHADOW_AUDIT not in perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view audit logs.",
        )

    try:
        q = db.query(ActionLog).order_by(ActionLog.timestamp.desc())

        if user_id is not None:
            q = q.filter(ActionLog.user_id == user_id)
        if action:
            q = q.filter(ActionLog.action.contains(action))
        if start_time:
            try:
                st = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                q = q.filter(ActionLog.timestamp >= st)
            except ValueError:
                pass
        if end_time:
            try:
                et = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                q = q.filter(ActionLog.timestamp <= et)
            except ValueError:
                pass

        total = q.count()
        items = q.offset((page - 1) * page_size).limit(page_size).all()

        return ActionLogListResponse(
            items=[ActionLogOut.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Log query failed: {exc}",
        ) from exc
