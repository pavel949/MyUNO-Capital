"""Celery application and tasks.

Exposes a Celery app named `app` so `celery -A app.worker worker` works
(i.e. `app.worker.app`). Wired to CELERY_BROKER_URL / CELERY_RESULT_BACKEND.
"""

from __future__ import annotations

import uuid

from celery import Celery

from app.config import settings
from app.db import SessionLocal

app = Celery(
    "myuno",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@app.task(name="app.worker.run_agent_run")
def run_agent_run(run_id: str) -> dict:
    """Load an agent_run, execute the agent via the orchestrator, persist results.

    Imported lazily so importing this module never requires the full ORM/agent
    graph (keeps worker startup and `py_compile` robust).
    """
    from app.agents.orchestrator import execute_run

    db = SessionLocal()
    try:
        run = execute_run(db, uuid.UUID(str(run_id)))
        db.commit()
        return {"run_id": str(run.id), "status": run.status}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@app.task(name="app.worker.ping")
def ping() -> str:
    """Trivial liveness task."""
    return "pong"
