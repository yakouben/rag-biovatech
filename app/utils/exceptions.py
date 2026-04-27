"""
Custom exceptions for the ChronicCare service.
Provides structured error handling with proper HTTP status codes.
"""
from typing import Any, Optional


class ChronicCareException(Exception):
    """Base exception for all ChronicCare errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(ChronicCareException):
    """Database operation failed."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, "DATABASE_ERROR", details)


class ValidationError(ChronicCareException):
    """Input validation failed."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, "VALIDATION_ERROR", details)


class EmbeddingError(ChronicCareException):
    """Embedding generation failed."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, "EMBEDDING_ERROR", details)


class GeminiError(ChronicCareException):
    """Gemini API call failed."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, "GEMINI_ERROR", details)


class ModelError(ChronicCareException):
    """ML model operation failed."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, "MODEL_ERROR", details)


class NotFoundError(ChronicCareException):
    """Resource not found."""

    def __init__(
        self,
        message: str,
        resource_type: str = "resource",
        details: Optional[dict[str, Any]] = None,
    ):
        if not details:
            details = {"resource_type": resource_type}
        super().__init__(message, 404, "NOT_FOUND", details)
