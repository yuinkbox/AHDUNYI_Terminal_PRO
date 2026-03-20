# -*- coding: utf-8 -*-
"""
AHDUNYI Server - FastAPI application entry point.

Deploy: uvicorn server.main:app --host 0.0.0.0 --port 8000
Author : AHDUNYI
Version: 9.0.0
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AHDUNYI Terminal API", version="9.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": "9.0.0"}
