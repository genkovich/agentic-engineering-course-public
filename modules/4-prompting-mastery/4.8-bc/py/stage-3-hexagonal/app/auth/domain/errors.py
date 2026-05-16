"""Auth domain — sentinel errors. ``infra/http/errors.py`` maps them to AppError."""
from __future__ import annotations


class AuthDomainError(Exception):
    """Base for auth domain errors."""


class InvalidCredentialsError(AuthDomainError):
    """auth.invalid_credentials"""


class EmailAlreadyExistsError(AuthDomainError):
    """auth.email_already_exists"""


class UserNotFoundError(AuthDomainError):
    """auth.user_not_found"""
