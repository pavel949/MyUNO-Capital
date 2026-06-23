"""Database engine, session factory, declarative Base, and FastAPI dependency."""

from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from app.config import settings


def _build_engine():
    """Create the SQLAlchemy engine, tuned for the target environment.

    - ``connect_args`` disables psycopg3 prepared statements so the engine is
      compatible with transaction-mode connection poolers (Supabase Supavisor /
      PgBouncer), and pins ``search_path`` via a libpq startup option when the
      app lives in a non-default schema (shared-instance isolation).
    - On serverless platforms (Vercel sets ``VERCEL=1``) we use ``NullPool`` so
      each invocation opens/closes its own connection through the pooler rather
      than holding idle connections across cold starts.
    """
    connect_args: dict = {"prepare_threshold": None}
    if settings.db_schema and settings.db_schema != "public":
        # Startup option survives transaction-pooled connections (unlike a
        # post-connect ``SET search_path`` which can be reset between txns).
        connect_args["options"] = f"-c search_path={settings.db_schema},extensions,public"

    kwargs: dict = {"pool_pre_ping": True, "future": True, "connect_args": connect_args}
    if os.getenv("VERCEL"):
        kwargs["poolclass"] = NullPool

    return create_engine(settings.database_url, **kwargs)


# Synchronous engine (SQLAlchemy 2.0 sync ORM, psycopg3 via postgresql+psycopg).
engine = _build_engine()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def get_db() -> Generator:
    """FastAPI dependency yielding a scoped session, committing on success."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
