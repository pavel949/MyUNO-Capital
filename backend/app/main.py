"""FastAPI application entrypoint (app.main:app)."""

from __future__ import annotations

import uuid

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1 import api_router
from app.config import settings
from app.db import engine

app = FastAPI(
    title="MyUNO Capital API",
    version="0.1.0",
    description="Autonomous AI Operating System for solo entrepreneurs.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Error envelope handlers (api-reference §Conventions) ------------------
_CODE_BY_STATUS = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
    429: "rate_limited",
    500: "internal_error",
}


def _error_response(status_code: int, message: str, details=None) -> JSONResponse:
    code = _CODE_BY_STATUS.get(status_code, "error")
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or [],
                "request_id": f"req_{uuid.uuid4().hex[:12]}",
            }
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    return _error_response(exc.status_code, str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {"field": ".".join(str(p) for p in err.get("loc", [])), "issue": err.get("msg", "")}
        for err in exc.errors()
    ]
    return _error_response(
        status.HTTP_422_UNPROCESSABLE_ENTITY, "Request validation failed.", details
    )


# --- Health endpoints ------------------------------------------------------
@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
def readyz() -> JSONResponse:
    """Readiness check: verifies a DB round-trip."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return JSONResponse(status_code=200, content={"status": "ready", "database": "ok"})
    except Exception as exc:  # pragma: no cover - depends on live DB
        return JSONResponse(
            status_code=503, content={"status": "not_ready", "database": str(exc)}
        )


app.include_router(api_router, prefix="/api/v1")
