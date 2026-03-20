# -*- coding: utf-8 -*-
"""
Users API router.

Endpoints
---------
GET  /api/users/active         -- List active users (optional role filter)
PUT  /api/users/{user_id}/role -- Update a user's role (manager only)

Author : AHDUNYI
Version: 9.0.0
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.core.database import get_db
from server.db.models import User
from server.schemas import ActiveUsersResponse, OkResponse, UserOut, UserRoleUpdate
from server.api.permissions import _get_current_user
from server.constants.permissions import Permission, get_permissions_for_role

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/active", response_model=ActiveUsersResponse)
def list_active_users(
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
) -> ActiveUsersResponse:
    """Return all active users, optionally filtered by role.

    Any authenticated user may call this endpoint so that team-leaders
    can build their dispatch list.

    Args:
        role:         Optional role filter string.
        db:           Injected DB session.
        current_user: Resolved from JWT.

    Returns:
        :class:`ActiveUsersResponse`
    """
    try:
        q = db.query(User).filter(User.is_active.is_(True))
        if role:
            q = q.filter(User.role == role)
        users = q.order_by(User.id).all()
        return ActiveUsersResponse(
            users=[UserOut.model_validate(u) for u in users],
            count=len(users),
            filter_role=role or "",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query users: {exc}",
        ) from exc


@router.put("/{user_id}/role", response_model=OkResponse)
def update_user_role(
    user_id: int,
    body: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
) -> OkResponse:
    """Update a user's role.  Requires ``action:update_role`` permission.

    Args:
        user_id:      Target user primary key.
        body:         JSON body with ``role`` field.
        db:           Injected DB session.
        current_user: Resolved from JWT.

    Returns:
        :class:`OkResponse`

    Raises:
        HTTPException 403: Caller lacks ``action:update_role`` permission.
        HTTPException 404: Target user not found.
        HTTPException 400: Invalid role value.
    """
    # Permission check
    caller_perms = get_permissions_for_role(current_user.role.value)
    if Permission.ACTION_UPDATE_ROLE not in caller_perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update user roles.",
        )

    try:
        target = db.query(User).filter(User.id == user_id).first()
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        # Validate role value against known roles
        from server.constants.roles import UserRole
        valid_roles = {r.value for r in UserRole}
        if body.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role '{body.role}'. Valid: {sorted(valid_roles)}",
            )

        target.role = body.role  # type: ignore[assignment]
        db.commit()
        db.refresh(target)
        return OkResponse(message=f"User {target.username} role updated to '{body.role}'.")

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update role: {exc}",
        ) from exc
