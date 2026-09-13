"""Structured logging setup with PII redaction for AutoForm."""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path
from typing import Any

import structlog


# =============================================================================
# PII Redaction Patterns
# =============================================================================

_REDACT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL_REDACTED]"),
    (re.compile(r"\b\d{10,11}\b"), "[PHONE_REDACTED]"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "[API_KEY_REDACTED]"),
    (re.compile(r"sk-ant-[a-zA-Z0-9-]{20,}"), "[API_KEY_REDACTED]"),
    (re.compile(r"Bearer\s+[a-zA-Z0-9._-]+"), "[BEARER_TOKEN_REDACTED]"),
]

_SENSITIVE_KEYS: set[str] = {
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "session_id",
    "profile_value",
    "field_value",
    "fill_value",
}


def _redact_pii(
    logger: structlog.types.WrappedLogger,
    method_name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    """structlog processor to redact sensitive data from log events."""
    for key in list(event_dict.keys()):
        value = event_dict[key]

        # Redact known sensitive keys
        if key.lower() in _SENSITIVE_KEYS:
            event_dict[key] = "[REDACTED]"
            continue

        # Redact patterns in string values
        if isinstance(value, str):
            for pattern, replacement in _REDACT_PATTERNS:
                value = pattern.sub(replacement, value)
            event_dict[key] = value

    return event_dict


# =============================================================================
# Logging Setup
# =============================================================================


def setup_logging(
    level: str = "INFO",
    log_format: str = "console",
    log_dir: str | None = None,
    redact_pii: bool = True,
) -> None:
    """
    Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR).
        log_format: Output format ('console' for human-readable, 'json' for machine-readable).
        log_dir: Directory for log files. If None, logs only to stderr.
        redact_pii: Whether to enable PII redaction in logs.
    """
    # Build processor chain
    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    # Add PII redaction if enabled
    if redact_pii:
        processors.append(_redact_pii)

    # Add format-specific processor
    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=sys.stderr.isatty(),
                pad_event=35,
            )
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )

    # Setup log file if directory specified
    if log_dir:
        log_path = Path(log_dir).expanduser()
        log_path.mkdir(parents=True, exist_ok=True)


def get_logger(name: str | None = None, **initial_context: Any) -> Any:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically module name).
        **initial_context: Initial context values to bind.

    Returns:
        A bound structured logger.

    Example:
        logger = get_logger("form_analyzer", session_id="abc123")
        logger.info("field_detected", field_id="f1", field_type="text")
    """
    log = structlog.get_logger(name)
    if initial_context:
        log = log.bind(**initial_context)
    return log

