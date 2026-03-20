# -*- coding: utf-8 -*-
"""
Team insight API router.

Endpoints
---------
GET /api/team/insight            -- Aggregated team performance stats
GET /api/team/user/{user_id}/stats -- Detailed stats for a single user

Author : AHDUNYI
Version: 9.0.0
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from server.core.database import get_db
from server.db.models import ShiftTask, User
from server.schemas import (
    ChannelStats,
    OverallStats,
    TeamInsightResponse,
    UserDetailedStats,
    UserOut,
    UserStats,
    TaskOut,
)
from server.api.permissions import _get_current_user
from server.constants.permissions import Permission, get_permissions_for_role

router = APIRouter(prefix="/api/team", tags=["team"])


def _require_insight_permission(current_user: User) -> None:
    perms = get_permissions_for_role(current_user.role.value)
    if Permission.VIEW_TEAM_INSIGHT not in perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view team insights.",
        )


@router.get("/insight", response_model=TeamInsightResponse)
def get_team_insight(
    start_date: str,
    end_date: str,
    user_ids: Optional[str] = None,
    channels: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
) -> TeamInsightResponse:
    """Return aggregated team performance data for the given date range.

    Args:
        start_date:   ISO date string YYYY-MM-DD.
        end_date:     ISO date string YYYY-MM-DD.
        user_ids:     Optional comma-separated user IDs filter.
        channels:     Optional comma-separated channel filter.
        db:           Injected DB session.
        current_user: Resolved from JWT.

    Returns:
        :class:`TeamInsightResponse`
    """
    _require_insight_permission(current_user)

    try:
        uid_filter: Optional[List[int]] = None
        if user_ids:
            uid_filter = [int(x.strip()) for x in user_ids.split(",") if x.strip().isdigit()]

        ch_filter: Optional[List[str]] = None
        if channels:
            ch_filter = [c.strip() for c in channels.split(",") if c.strip()]

        q = db.query(ShiftTask).filter(
            ShiftTask.shift_date >= start_date,
            ShiftTask.shift_date <= end_date,
        )
        if uid_filter:
            q = q.filter(ShiftTask.user_id.in_(uid_filter))
        if ch_filter:
            q = q.filter(ShiftTask.task_channel.in_(ch_filter))

        tasks: List[ShiftTask] = q.all()

        # Load user info map
        user_ids_in_tasks = list({t.user_id for t in tasks})
        users = db.query(User).filter(User.id.in_(user_ids_in_tasks)).all()
        user_map: Dict[int, User] = {u.id: u for u in users}

        # --- Per-user aggregation ---
        user_agg: Dict[int, Dict[str, Any]] = defaultdict(lambda: {
            "total_tasks": 0, "total_reviewed": 0,
            "total_violations": 0, "total_duration": 0,
            "channels": defaultdict(lambda: {"count": 0, "reviewed": 0, "violations": 0}),
        })
        for t in tasks:
            agg = user_agg[t.user_id]
            agg["total_tasks"]      += 1
            agg["total_reviewed"]   += t.reviewed_count
            agg["total_violations"] += t.violation_count
            agg["total_duration"]   += t.work_duration
            ch = agg["channels"][t.task_channel]
            ch["count"]      += 1
            ch["reviewed"]   += t.reviewed_count
            ch["violations"] += t.violation_count

        user_stats: List[UserStats] = []
        for uid, agg in user_agg.items():
            u = user_map.get(uid)
            vr = (agg["total_violations"] / agg["total_reviewed"]) if agg["total_reviewed"] else 0.0
            user_stats.append(UserStats(
                user_id=uid,
                username=u.username if u else str(uid),
                full_name=u.full_name if u else "",
                total_tasks=agg["total_tasks"],
                total_reviewed=agg["total_reviewed"],
                total_violations=agg["total_violations"],
                total_duration=agg["total_duration"],
                violation_rate=round(vr, 4),
                channels=dict(agg["channels"]),
            ))

        # --- Per-channel aggregation ---
        ch_agg: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total_tasks": 0, "total_reviewed": 0,
            "total_violations": 0, "unique_users": set(),
        })
        for t in tasks:
            ca = ch_agg[t.task_channel]
            ca["total_tasks"]      += 1
            ca["total_reviewed"]   += t.reviewed_count
            ca["total_violations"] += t.violation_count
            ca["unique_users"].add(t.user_id)

        channel_stats: List[ChannelStats] = []
        for ch, ca in ch_agg.items():
            avg = (ca["total_reviewed"] / ca["total_tasks"]) if ca["total_tasks"] else 0.0
            channel_stats.append(ChannelStats(
                channel=ch,
                total_tasks=ca["total_tasks"],
                total_reviewed=ca["total_reviewed"],
                total_violations=ca["total_violations"],
                avg_reviewed_per_task=round(avg, 2),
                unique_users=len(ca["unique_users"]),
            ))

        # --- Overall ---
        total_reviewed = sum(t.total_reviewed for t in user_stats)
        n_users = len(user_stats)
        overall = OverallStats(
            period_start=start_date,
            period_end=end_date,
            total_tasks=len(tasks),
            total_users=n_users,
            total_reviewed=total_reviewed,
            total_violations=sum(t.total_violations for t in user_stats),
            total_duration=sum(t.total_duration for t in user_stats),
            avg_reviewed_per_user=round(total_reviewed / n_users, 2) if n_users else 0.0,
            channels_covered=len(ch_agg),
        )

        return TeamInsightResponse(
            period={"start": start_date, "end": end_date},
            user_stats=user_stats,
            channel_stats=channel_stats,
            overall_stats=overall,
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Team insight query failed: {exc}",
        ) from exc


@router.get("/user/{user_id}/stats", response_model=UserDetailedStats)
def get_user_detailed_stats(
    user_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
) -> UserDetailedStats:
    """Return detailed performance stats for a specific user."""
    _require_insight_permission(current_user)

    try:
        target = db.query(User).filter(User.id == user_id).first()
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        sd = start_date or "2024-01-01"
        ed = end_date or today

        tasks: List[ShiftTask] = (
            db.query(ShiftTask)
            .filter(
                ShiftTask.user_id == user_id,
                ShiftTask.shift_date >= sd,
                ShiftTask.shift_date <= ed,
            )
            .order_by(ShiftTask.shift_date.desc())
            .all()
        )

        ch_agg: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "task_count": 0, "total_reviewed": 0, "total_violations": 0, "total_duration": 0,
        })
        for t in tasks:
            ca = ch_agg[t.task_channel]
            ca["task_count"]      += 1
            ca["total_reviewed"]  += t.reviewed_count
            ca["total_violations"] += t.violation_count
            ca["total_duration"]  += t.work_duration

        total_reviewed   = sum(t.reviewed_count for t in tasks)
        total_violations = sum(t.violation_count for t in tasks)

        return UserDetailedStats(
            user=UserOut.model_validate(target),
            period={"start": sd, "end": ed},
            summary={
                "total_tasks":      len(tasks),
                "total_reviewed":   total_reviewed,
                "total_violations": total_violations,
                "total_duration":   sum(t.work_duration for t in tasks),
                "violation_rate":   round(total_violations / total_reviewed, 4) if total_reviewed else 0.0,
            },
            channel_stats=[
                {"channel": ch, **ca} for ch, ca in ch_agg.items()
            ],
            recent_shifts=[TaskOut.model_validate(t) for t in tasks[:10]],
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User stats query failed: {exc}",
        ) from exc
