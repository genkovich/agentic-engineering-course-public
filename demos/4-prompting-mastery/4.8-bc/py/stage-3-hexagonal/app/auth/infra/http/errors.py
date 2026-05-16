"""Auth HTTP error mapping — domain sentinels -> AppError -> HTTPException."""
from __future__ import annotations

from app.auth.domain.errors import (
    AuthDomainError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from app.shared.apperr import AppError


def to_app_error(err: AuthDomainError) -> AppError:
    if isinstance(err, InvalidCredentialsError):
        return AppError(
            code="auth.invalid_credentials",
            message="invalid email or password",
            status_code=401,
        )
    if isinstance(err, EmailAlreadyExistsError):
        return AppError(
            code="auth.email_already_exists",
            message="email is already registered",
            status_code=409,
        )
    if isinstance(err, UserNotFoundError):
        return AppError(
            code="auth.user_not_found",
            message="user not found",
            status_code=404,
        )
    return AppError(code="auth.unknown", message=str(err), status_code=500)
