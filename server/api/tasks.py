# -*- coding: utf-8 -*-
"""
Tasks API router.

Endpoints
---------
GET   /api/task/my                  -- Current user's today + historical tasks
PATCH /api/task/{task_id}/progress  -- Update task progress metrics
POST  /api/task/{task_id}/complete  -- Mark task as completed
POST  /api/dispatch/auto            -- Auto-dispatch tasks for a shift

Author : AHDUNYI
Version: 9.0.0
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.api.permissions import _get_current_user
from server.constants.permissions import Permission, get_permissions_for_role
from server.core.database import get_db
from server.db.models import ShiftTask, User
from server.schemas import (
    DispatchRequest,
    DispatchResponse,
    OkResponse,
    TaskOut,
    TaskProgressUpdate,
    UserTaskResponse,
    WeeklyStats,
)
from server.services.dispatch import dispatch_tasks

# 统一使用北京时间 (UTC+8) 避免跨日期 Bug
CST = timezone(timedelta(hours=8))


def _cst_today() -> str:
    """Return today's date string in CST (UTC+8)."""
    return datetime.now(CST).strftime("%Y-%m-%d")


def _cst_now() -> datetime:
    """Return current datetime in CST."""
    return datetime.now(CST)


router = APIRouter(tags=["tasks"])


@router.get("/api/task/my/live-patrol", response_model=TaskOut)
def get_or_create_live_patrol_task(
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
) -> TaskOut:
    """Get or auto-create today's live patrol task for the calling auditor.

    This endpoint is idempotent: calling it multiple times on the same day
    always returns the same task row. No dispatcher required.

    Args:
        db:           Injected DB session.
        current_user: Resolved from JWT.

    Returns:
        :class:`TaskOut` — the auditor's live patrol task for today.
    """
    today = _cst_today()

    # 幂等查询：先找今日已有的直播巡查任务
    task = (
        db.query(ShiftTask)
        .filter(
            ShiftTask.user_id == current_user.id,
            ShiftTask.shift_date == today,
            ShiftTask.task_channel == "live",
        )
        .first()
    )

    if task is None:
        # 自动推断班次
        hour = _cst_now().hour
        if hour < 12:
            shift_type = "morning"
        elif hour < 18:
            shift_type = "afternoon"
        else:
            shift_type = "night"

        task = ShiftTask(
            user_id=current_user.id,
            shift_date=today,
            shift_type=shift_type,
            task_channel="live",
            is_completed=False,
            reviewed_count=0,
            violation_count=0,
            work_duration=0,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

    out = TaskOut.model_validate(task)
    out.user_info = {
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
    }
    return out


@router.get("/api/task/my", response_model=UserTaskResponse)
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
) -> UserTaskResponse:
    """Return today's tasks and historical tasks for the calling user.

    Args:
        db:           Injected DB session.
        current_user: Resolved from JWT.

    Returns:
        :class:`UserTaskResponse`
    """
    try:
        today = _cst_today()

        today_tasks = (
            db.query(ShiftTask)
            .filter(
                ShiftTask.user_id == current_user.id,
                ShiftTask.shift_date == today,
            )
            # 进行中（is_completed=False）排在前面，已完成排在后面
            .order_by(ShiftTask.is_completed.asc(), ShiftTask.id.desc())
            .all()
        )

        historical = (
            db.query(ShiftTask)
            .filter(
                ShiftTask.user_id == current_user.id,
                ShiftTask.shift_date < today,
            )
            .order_by(ShiftTask.shift_date.desc())
            .limit(30)
            .all()
        )

        now = _cst_now()
        week_start = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
        week_tasks = (
            db.query(ShiftTask)
            .filter(
                ShiftTask.user_id == current_user.id,
                ShiftTask.shift_date >= week_start,
            )
            .all()
        )
        weekly = WeeklyStats(
            total_reviewed=sum(t.reviewed_count for t in week_tasks),
            total_violations=sum(t.violation_count for t in week_tasks),
            total_duration=sum(t.work_duration for t in week_tasks),
            task_count=len(week_tasks),
            week=now.isocalendar()[1],
            year=now.year,
        )

        def _enrich(task: ShiftTask) -> TaskOut:
            out = TaskOut.model_validate(task)
            out.user_info = {
                "username": current_user.username,
                "full_name": current_user.full_name,
                "role": current_user.role.value,
            }
            return out

        return UserTaskResponse(
            today_tasks=[_enrich(t) for t in today_tasks],
            historical_tasks=[_enrich(t) for t in historical],
            weekly_stats=weekly,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load tasks: {exc}",
        ) from exc


@router.patch("/api/task/{task_id}/progress", response_model=OkResponse)
def update_task_progress(
    task_id: int,
    body: TaskProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
) -> OkResponse:
    """Incrementally update a task's progress metrics."""
    try:
        task = (
            db.query(ShiftTask)
            .filter(
                ShiftTask.id == task_id,
                ShiftTask.user_id == current_user.id,
            )
            .first()
        )
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )

        if body.reviewed_count is not None:
            task.reviewed_count = body.reviewed_count
        if body.violation_count is not None:
            task.violation_count = body.violation_count
        if body.work_duration is not None:
            task.work_duration = body.work_duration
        if body.is_completed is not None:
            task.is_completed = body.is_completed

        db.commit()
        return OkResponse(message="Progress updated.")
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update progress: {exc}",
        ) from exc


@router.post("/api/task/{task_id}/complete", response_model=OkResponse)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
) -> OkResponse:
    """Mark a task as completed."""
    try:
        task = (
            db.query(ShiftTask)
            .filter(
                ShiftTask.id == task_id,
                ShiftTask.user_id == current_user.id,
            )
            .first()
        )
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        task.is_completed = True
        db.commit()
        return OkResponse(message="Task completed.")
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete task: {exc}",
        ) from exc


@router.post("/api/dispatch/auto", response_model=DispatchResponse)
def auto_dispatch(
    body: DispatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
) -> DispatchResponse:
    """Auto-dispatch shift tasks using the least-assigned-first algorithm.

    Requires ``action:dispatch_task`` permission.
    """
    perms = get_permissions_for_role(current_user.role.value)
    if Permission.ACTION_DISPATCH_TASK not in perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to dispatch tasks.",
        )
    try:
        return dispatch_tasks(db, body)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dispatch failed: {exc}",
        ) from exc
