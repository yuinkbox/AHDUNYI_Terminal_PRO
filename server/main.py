# -*- coding: utf-8 -*-
"""
AHDUNYI Server — FastAPI application entry point.

Startup
-------
    uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload

Author : AHDUNYI
Version: 9.0.0
"""
from __future__ import annotations

import logging
import traceback

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from server.api.auth import router as auth_router
from server.api.logs import router as logs_router
from server.api.permissions import router as permissions_router
from server.api.tasks import router as tasks_router
from server.api.team import router as team_router
from server.api.users import router as users_router
from server.api.violation import router as violation_router

logger = logging.getLogger("ahdunyi")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

app = FastAPI(
    title="AHDUNYI Terminal API",
    version="9.0.0",
    description="风控巡查终端后端服务",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def _global_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
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
            "detail": "Internal server error.",
        },
    )


app.include_router(auth_router)
app.include_router(permissions_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(team_router)
app.include_router(logs_router)
app.include_router(violation_router)


@app.get("/health", tags=["system"])
def health() -> dict:
    """Liveness probe."""
    return {"status": "ok", "version": "9.0.0"}


@app.get("/", tags=["system"])
def root() -> dict:
    """Root endpoint."""
    return {"message": "AHDUNYI Terminal API is running.", "docs": "/docs"}
