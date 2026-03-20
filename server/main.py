# -*- coding: utf-8 -*-
"""
AHDUNYI Server — FastAPI application entry point.

Startup
-------
    uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload

All routers are registered here.  A global exception handler ensures that
any unhandled exception returns a well-formed JSON body instead of a 500
HTML page.

Author : AHDUNYI
Version: 9.0.0
"""
from __future__ import annotations

import logging
import traceback

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from server.api.auth        import router as auth_router
from server.api.permissions import router as permissions_router
from server.api.users       import router as users_router
from server.api.tasks       import router as tasks_router
from server.api.team        import router as team_router
from server.api.logs        import router as logs_router

logger = logging.getLogger("ahdunyi")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AHDUNYI Terminal API",
    version="9.0.0",
    description="风控巡查终端后端服务",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Global exception handler — never return raw 500 HTML
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def _global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method,
        request.url.path,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "detail": "Internal server error. Please contact the system administrator.",
        },
    )

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth_router)        # /api/auth/login, /api/auth/change-password
app.include_router(permissions_router) # /api/auth/permissions, /api/auth/roles
app.include_router(users_router)       # /api/users/active, /api/users/{id}/role
app.include_router(tasks_router)       # /api/task/my, /api/task/{id}/*, /api/dispatch/auto
app.include_router(team_router)        # /api/team/insight, /api/team/user/{id}/stats
app.include_router(logs_router)        # /api/log/action, /api/log/list

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["system"])
def health() -> dict:
    """Liveness probe — returns immediately without hitting the DB."""
    return {"status": "ok", "version": "9.0.0"}


@app.get("/", tags=["system"])
def root() -> dict:
    return {"message": "AHDUNYI Terminal API is running.", "docs": "/docs"}
