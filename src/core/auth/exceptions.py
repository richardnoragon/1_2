"""Custom exceptions for the authentication subsystem."""

from __future__ import annotations


class AuthenticationError(Exception):
    """Raised when credentials are invalid or authentication fails."""


class AccountBlockedError(AuthenticationError):
    """Raised when a blocked account attempts to authenticate."""
