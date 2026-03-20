# -*- coding: utf-8 -*-
"""
Pydantic schemas for all API request/response models.

Naming convention:
  *Create  — request body for creation
  *Update  — request body for partial update
  *Out     — response model (never exposes hashed_password)
  *Response — top-level response envelope

Author : AHDUNYI
Version: 9.0.0
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Shared / base
# ---------------------------------------------------------------------------
class OkResponse(BaseModel):
    """Generic success envelope."""
    success: bool = True
    message: str = "ok"


# ---------------------------------------------------------------------------
# User schemas
# ---------------------------------------------------------------------------
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    email: Optional[str] = ""
    role: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserRoleUpdate(BaseModel):
    role: str = Field(..., description="New role value, must match server/constants/roles.py")


class ActiveUsersResponse(BaseModel):
    users: List[UserOut]
    count: int
    filter_role: str = ""


# ---------------------------------------------------------------------------
# ShiftTask schemas
# ---------------------------------------------------------------------------
class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    shift_date: str
    shift_type: str
    task_channel: str
    is_completed: bool
    reviewed_count: int
    violation_count: int
    work_duration: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_info: Optional[Dict[str, Any]] = None


class TaskProgressUpdate(BaseModel):
    reviewed_count: Optional[int] = None
    violation_count: Optional[int] = None
    work_duration: Optional[int] = None
    is_completed: Optional[bool] = None


class WeeklyStats(BaseModel):
    total_reviewed: int = 0
    total_violations: int = 0
    total_duration: int = 0
    task_count: int = 0
    week: int
    year: int


class UserTaskResponse(BaseModel):
    today_tasks: List[TaskOut] = []
    historical_tasks: List[TaskOut] = []
    weekly_stats: WeeklyStats


# ---------------------------------------------------------------------------
# Dispatch schemas
# ---------------------------------------------------------------------------
class DispatchRequest(BaseModel):
    shift_date: str = Field(..., description="ISO date YYYY-MM-DD")
    shift_type: str = Field(..., description="morning | afternoon | night")
    user_ids: List[int]
    required_channels: List[str]


class TaskAssignment(BaseModel):
    user_id: int
    username: str
    full_name: str
    task_channel: str
    historical_count: int = 0


class DispatchSummary(BaseModel):
    total_assignments: int
    channel_distribution: Dict[str, int]
    algorithm: str = "least-assigned-first"
    timestamp: str


class DispatchResponse(BaseModel):
    shift_date: str
    shift_type: str
    assignments: List[TaskAssignment]
    summary: DispatchSummary


# ---------------------------------------------------------------------------
# Team insight schemas
# ---------------------------------------------------------------------------
class ChannelStats(BaseModel):
    channel: str
    total_tasks: int = 0
    total_reviewed: int = 0
    total_violations: int = 0
    avg_reviewed_per_task: float = 0.0
    unique_users: int = 0


class UserStats(BaseModel):
    user_id: int
    username: str
    full_name: str
    total_tasks: int = 0
    total_reviewed: int = 0
    total_violations: int = 0
    total_duration: int = 0
    violation_rate: float = 0.0
    channels: Dict[str, Any] = {}


class OverallStats(BaseModel):
    period_start: str
    period_end: str
    total_tasks: int = 0
    total_users: int = 0
    total_reviewed: int = 0
    total_violations: int = 0
    total_duration: int = 0
    avg_reviewed_per_user: float = 0.0
    channels_covered: int = 0


class TeamInsightResponse(BaseModel):
    period: Dict[str, str]
    user_stats: List[UserStats]
    channel_stats: List[ChannelStats]
    overall_stats: OverallStats


class UserDetailedStats(BaseModel):
    user: UserOut
    period: Dict[str, str]
    summary: Dict[str, Any]
    channel_stats: List[Dict[str, Any]]
    recent_shifts: List[TaskOut]


# ---------------------------------------------------------------------------
# ActionLog schemas
# ---------------------------------------------------------------------------
class ActionLogCreate(BaseModel):
    action: str
    details: str = ""
    task_id: Optional[int] = None
    duration: Optional[int] = None
    timestamp: Optional[str] = None


class ActionLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    username: str
    action: str
    details: str
    task_id: Optional[int] = None
    duration: Optional[int] = None
    timestamp: datetime


class ActionLogListResponse(BaseModel):
    items: List[ActionLogOut]
    total: int
    page: int
    page_size: int
