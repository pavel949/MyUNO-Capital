"""Vercel Python serverless entrypoint.

Vercel's ``@vercel/python`` runtime detects the module-level ``app`` ASGI
callable and serves it. The ``vercel.json`` catch-all route forwards every
request path to this function, so FastAPI receives the original URL (e.g.
``/api/v1/auth/login``) and routes it normally.
"""

from __future__ import annotations

import os
import sys

# Ensure the backend project root (which contains the ``app`` package) is on the
# import path regardless of the runtime's working directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: E402  (import after sys.path setup)

__all__ = ["app"]
