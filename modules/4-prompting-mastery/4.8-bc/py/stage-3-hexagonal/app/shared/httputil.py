"""Shared HTTP helpers — error mapping AppError -> HTTPException.

Cross-cutting utilities only. No business logic, no BC-specific imports.
"""
from __future__ import annotations

from fastapi import HTTPException

from app.shared.apperr import AppError


def to_http_exception(err: Exception) -> HTTPException:
    if isinstance(err, AppError):
        return HTTPException(
            status_code=err.status_code,
            detail={"error": err.code, "message": err.message},
        )
    return HTTPException(
        status_code=500,
        detail={"error": "internal", "message": "unexpected error"},
    )
