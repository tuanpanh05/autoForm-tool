"""Field value validators for AutoForm."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from autoform.domain.enums import FieldType
from autoform.infrastructure.logging import get_logger

logger = get_logger("validation")


# =============================================================================
# Validation Result
# =============================================================================


class ValidationResult:
    """Result of validating a field value."""

    def __init__(self, valid: bool, message: str = "") -> None:
        self.valid = valid
        self.message = message

    def __bool__(self) -> bool:
        return self.valid

    @staticmethod
    def ok() -> ValidationResult:
        return ValidationResult(valid=True)

    @staticmethod
    def error(message: str) -> ValidationResult:
        return ValidationResult(valid=False, message=message)


# =============================================================================
# Individual Validators
# =============================================================================

_EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

_PHONE_REGEX = re.compile(
    r"^[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{6,15}$"
)

_URL_REGEX = re.compile(
    r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE
)

_DATE_FORMATS = [
    "%Y-%m-%d",      # ISO: 2004-05-20
    "%d/%m/%Y",      # European: 20/05/2004
    "%m/%d/%Y",      # US: 05/20/2004
    "%d-%m-%Y",      # 20-05-2004
    "%Y/%m/%d",      # 2004/05/20
]


def validate_email(value: Any) -> ValidationResult:
    """Validate an email address."""
    if not value:
        return ValidationResult.error("Email is empty")
    s = str(value).strip()
    if _EMAIL_REGEX.match(s):
        return ValidationResult.ok()
    return ValidationResult.error(f"Invalid email format: '{s}'")


def validate_phone(value: Any) -> ValidationResult:
    """Validate a phone number."""
    if not value:
        return ValidationResult.error("Phone is empty")
    s = str(value).strip()
    # Remove common formatting
    cleaned = re.sub(r"[\s\-\.\(\)]", "", s)
    if len(cleaned) < 7 or len(cleaned) > 15:
        return ValidationResult.error(f"Phone number length invalid: '{s}'")
    if not re.match(r"^\+?[0-9]+$", cleaned):
        return ValidationResult.error(f"Phone contains invalid characters: '{s}'")
    return ValidationResult.ok()


def validate_date(value: Any) -> ValidationResult:
    """Validate a date string."""
    if not value:
        return ValidationResult.error("Date is empty")
    s = str(value).strip()
    for fmt in _DATE_FORMATS:
        try:
            datetime.strptime(s, fmt)
            return ValidationResult.ok()
        except ValueError:
            continue
    return ValidationResult.error(f"Invalid date format: '{s}'. Expected YYYY-MM-DD or DD/MM/YYYY")


def validate_number(value: Any, min_val: float | None = None, max_val: float | None = None) -> ValidationResult:
    """Validate a numeric value."""
    if value is None or value == "":
        return ValidationResult.error("Number is empty")
    try:
        num = float(value)
    except (ValueError, TypeError):
        return ValidationResult.error(f"Not a valid number: '{value}'")

    if min_val is not None and num < min_val:
        return ValidationResult.error(f"Value {num} is below minimum {min_val}")
    if max_val is not None and num > max_val:
        return ValidationResult.error(f"Value {num} exceeds maximum {max_val}")
    return ValidationResult.ok()


def validate_url(value: Any) -> ValidationResult:
    """Validate a URL."""
    if not value:
        return ValidationResult.error("URL is empty")
    s = str(value).strip()
    if _URL_REGEX.match(s):
        return ValidationResult.ok()
    return ValidationResult.error(f"Invalid URL format: '{s}'")


def validate_required(value: Any) -> ValidationResult:
    """Validate that a required field has a value."""
    if value is None:
        return ValidationResult.error("Required field is empty")
    if isinstance(value, str) and not value.strip():
        return ValidationResult.error("Required field is empty")
    if isinstance(value, list) and len(value) == 0:
        return ValidationResult.error("Required field has no selections")
    return ValidationResult.ok()


def validate_max_length(value: Any, max_length: int) -> ValidationResult:
    """Validate string length constraint."""
    if value is None:
        return ValidationResult.ok()
    s = str(value)
    if len(s) > max_length:
        return ValidationResult.error(f"Value exceeds max length {max_length} (got {len(s)})")
    return ValidationResult.ok()


# =============================================================================
# Field Validator (combines all checks)
# =============================================================================


class FieldValidator:
    """
    Validates field values based on field type and constraints.

    Usage:
        validator = FieldValidator()
        result = validator.validate(field, value)
        if not result:
            print(f"Validation failed: {result.message}")
    """

    def validate(
        self,
        field_type: FieldType,
        value: Any,
        required: bool = False,
        min_length: int | None = None,
        max_length: int | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> ValidationResult:
        """
        Validate a value against field type and constraints.

        Args:
            field_type: The field's type.
            value: The value to validate.
            required: Whether the field is required.
            min_length: Minimum string length.
            max_length: Maximum string length.
            min_value: Minimum numeric value.
            max_value: Maximum numeric value.

        Returns:
            ValidationResult with valid flag and error message.
        """
        # Required check
        if required:
            result = validate_required(value)
            if not result:
                return result

        # If not required and empty, skip type validation
        if value is None or (isinstance(value, str) and not value.strip()):
            return ValidationResult.ok()

        # Type-specific validation
        match field_type:
            case FieldType.EMAIL:
                result = validate_email(value)
                if not result:
                    return result

            case FieldType.TEL:
                result = validate_phone(value)
                if not result:
                    return result

            case FieldType.DATE | FieldType.DATETIME:
                result = validate_date(value)
                if not result:
                    return result

            case FieldType.NUMBER:
                result = validate_number(value, min_value, max_value)
                if not result:
                    return result

            case FieldType.URL:
                result = validate_url(value)
                if not result:
                    return result

        # Length constraints
        if max_length is not None:
            result = validate_max_length(value, max_length)
            if not result:
                return result

        return ValidationResult.ok()
