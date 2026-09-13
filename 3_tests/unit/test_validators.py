"""Unit tests for field validators."""

from __future__ import annotations

import pytest
from autoform.domain.enums import FieldType
from autoform.validation.validators import (
    FieldValidator,
    ValidationResult,
    validate_date,
    validate_email,
    validate_number,
    validate_phone,
    validate_required,
    validate_url,
)


class TestValidators:
    """Test suite for individual validation functions."""

    def test_validate_email(self) -> None:
        assert validate_email("user@example.com").valid is True
        assert validate_email("john.doe@sub.domain.org").valid is True
        assert validate_email("invalid-email").valid is False
        assert validate_email("").valid is False
        assert validate_email("@no-user.com").valid is False

    def test_validate_phone(self) -> None:
        assert validate_phone("0987654321").valid is True
        assert validate_phone("+84 987 654 321").valid is True
        assert validate_phone("123").valid is False  # Too short
        assert validate_phone("abc-def-ghij").valid is False

    def test_validate_date(self) -> None:
        assert validate_date("2024-05-20").valid is True
        assert validate_date("20/05/2024").valid is True
        assert validate_date("05/20/2024").valid is True
        assert validate_date("invalid-date").valid is False

    def test_validate_number(self) -> None:
        assert validate_number("123").valid is True
        assert validate_number(45.67).valid is True
        assert validate_number("10", min_val=0, max_val=20).valid is True
        assert validate_number("-5", min_val=0).valid is False
        assert validate_number("100", max_val=50).valid is False
        assert validate_number("abc").valid is False

    def test_validate_url(self) -> None:
        assert validate_url("https://example.com").valid is True
        assert validate_url("http://sub.domain.org/path?q=1").valid is True
        assert validate_url("ftp://invalid-scheme.com").valid is False
        assert validate_url("not-a-url").valid is False

    def test_validate_required(self) -> None:
        assert validate_required("some text").valid is True
        assert validate_required(["option1"]).valid is True
        assert validate_required("").valid is False
        assert validate_required(None).valid is False
        assert validate_required([]).valid is False


class TestFieldValidator:
    """Test suite for FieldValidator class."""

    def setup_method(self) -> None:
        self.validator = FieldValidator()

    def test_field_validator_email(self) -> None:
        res = self.validator.validate(FieldType.EMAIL, "test@test.com", required=True)
        assert res.valid is True

        res_invalid = self.validator.validate(FieldType.EMAIL, "invalid", required=True)
        assert res_invalid.valid is False

    def test_field_validator_optional_empty(self) -> None:
        res = self.validator.validate(FieldType.EMAIL, "", required=False)
        assert res.valid is True

    def test_field_validator_required_empty(self) -> None:
        res = self.validator.validate(FieldType.TEXT, "", required=True)
        assert res.valid is False

    def test_field_validator_max_length(self) -> None:
        res = self.validator.validate(FieldType.TEXT, "12345", max_length=3)
        assert res.valid is False
