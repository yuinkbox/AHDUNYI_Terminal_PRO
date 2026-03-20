# -*- coding: utf-8 -*-
"""
Task dispatch service — "Least Assigned First" algorithm.

Given a list of user_ids and required channels, assigns channels to users
such that each user's historical task count for that channel is minimised.
This guarantees fairness over time: no single auditor gets stuck with the
same channel every shift.

Author : AHDUNYI
Version: 9.0.0
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from server.db.models import ShiftTask, User
from server.schemas import (
    DispatchRequest,
    DispatchResponse,
    DispatchSummary,
    TaskAssignment,
)


def _get_weekly_channel_counts(
    db: Session,
    user_ids: List[int],
    channel: str,
) -> Dict[int, int]:
    """Return the number of times each user was assigned *channel* in the past 7 days."""
    from datetime import timedelta

    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    rows = (
        db.query(ShiftTask.user_id, func.count(ShiftTask.id))
        .filter(
            ShiftTask.user_id.in_(user_ids),
            ShiftTask.task_channel == channel,
            ShiftTask.shift_date >= cutoff,
        )
        .group_by(ShiftTask.user_id)
        .all()
    )
    counts: Dict[int, int] = defaultdict(int)
    for user_id, cnt in rows:
        counts[user_id] = cnt
    return counts


def dispatch_tasks(db: Session, request: DispatchRequest) -> DispatchResponse:
    """Assign channels to users using the least-assigned-first algorithm.

    Args:
        db:      Active SQLAlchemy session.
        request: Dispatch parameters (date, shift, user_ids, channels).

    Returns:
        :class:`DispatchResponse` with assignment list and summary.
    """
    # Load user info
    users: List[User] = (
        db.query(User)
        .filter(User.id.in_(request.user_ids), User.is_active.is_(True))
        .all()
    )
    user_map: Dict[int, User] = {u.id: u for u in users}

    assignments: List[TaskAssignment] = []
    channel_distribution: Dict[str, int] = defaultdict(int)

    # Round-robin over channels, picking the least-assigned user each time
    channels = list(request.required_channels)
    user_ids = [u.id for u in users]

    # Build historical counts per channel
    channel_counts: Dict[str, Dict[int, int]] = {}
    for ch in channels:
        channel_counts[ch] = _get_weekly_channel_counts(db, user_ids, ch)

    # Track how many channels we've already assigned to each user this round
    assigned_this_round: Dict[int, int] = defaultdict(int)

    for channel in channels:
        counts = channel_counts[channel]
        # Sort users by (historical_count ASC, assigned_this_round ASC, user_id ASC)
        eligible = sorted(
            user_ids,
            key=lambda uid: (counts.get(uid, 0), assigned_this_round[uid], uid),
        )
        chosen_id = eligible[0]
        chosen_user = user_map[chosen_id]
        historical = counts.get(chosen_id, 0)

        assignments.append(
            TaskAssignment(
                user_id=chosen_id,
                username=chosen_user.username,
                full_name=chosen_user.full_name,
                task_channel=channel,
                historical_count=historical,
            )
        )
        channel_distribution[channel] += 1
        assigned_this_round[chosen_id] += 1

    # Persist to DB
    for assignment in assignments:
        task = ShiftTask(
            user_id=assignment.user_id,
            shift_date=request.shift_date,
            shift_type=request.shift_type,
            task_channel=assignment.task_channel,
        )
        db.add(task)
    db.commit()

    return DispatchResponse(
        shift_date=request.shift_date,
        shift_type=request.shift_type,
        assignments=assignments,
        summary=DispatchSummary(
            total_assignments=len(assignments),
            channel_distribution=dict(channel_distribution),
            timestamp=datetime.now(timezone.utc).isoformat(),
        ),
    )
