from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes_findings import router as findings_router
from src.api.routes_health import router as health_router
from src.api.routes_review import router as review_router
from src.api.routes_runs import router as runs_router

app = FastAPI(
    title="Payer Policy Drift Sentinel",
    description="Healthcare payer AI prototype for detecting policy drift",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(runs_router)
app.include_router(findings_router)
app.include_router(review_router)
