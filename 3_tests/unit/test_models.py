"""Unit tests for domain models."""

from __future__ import annotations

import pytest

from autoform.domain.enums import ConfidenceLevel, FieldType, LabelSource, Platform
from autoform.domain.models import (
    FieldMapping,
    FieldOption,
    FormField,
    FormSchema,
    FormSection,
    MatchCandidate,
    UserProfile,
)


class TestUserProfile:
    """Tests for UserProfile model."""

    def test_get_field_valid_path(self, sample_profile: UserProfile) -> None:
        assert sample_profile.get_field("personal.full_name") == "Nguyen Van A"

    def test_get_field_contact(self, sample_profile: UserProfile) -> None:
        assert sample_profile.get_field("contact.email") == "nguyenvana@example.com"

    def test_get_field_nonexistent(self, sample_profile: UserProfile) -> None:
        assert sample_profile.get_field("personal.nonexistent") is None

    def test_get_field_nonexistent_category(self, sample_profile: UserProfile) -> None:
        assert sample_profile.get_field("nonexistent.field") is None

    def test_get_field_invalid_path(self, sample_profile: UserProfile) -> None:
        assert sample_profile.get_field("invalid_no_dot") is None

    def test_set_field(self, sample_profile: UserProfile) -> None:
        sample_profile.set_field("personal.full_name", "Tran Van B")
        assert sample_profile.get_field("personal.full_name") == "Tran Van B"

    def test_set_field_custom(self, sample_profile: UserProfile) -> None:
        sample_profile.set_field("custom.website", "https://example.com")
        assert sample_profile.get_field("custom.website") == "https://example.com"

    def test_set_field_invalid_path(self, sample_profile: UserProfile) -> None:
        with pytest.raises(ValueError, match="Invalid path format"):
            sample_profile.set_field("nodot", "value")

    def test_set_field_invalid_category(self, sample_profile: UserProfile) -> None:
        with pytest.raises(ValueError, match="Unknown category"):
            sample_profile.set_field("nonexistent.field", "value")

    def test_get_all_fields(self, sample_profile: UserProfile) -> None:
        all_fields = sample_profile.get_all_fields()
        assert "personal.full_name" in all_fields
        assert "contact.email" in all_fields
        assert "education.university" in all_fields
        assert all_fields["personal.full_name"] == "Nguyen Van A"

    def test_serialization_roundtrip(self, sample_profile: UserProfile) -> None:
        data = sample_profile.to_dict()
        restored = UserProfile.from_dict(data)
        assert restored.get_field("personal.full_name") == "Nguyen Van A"
        assert restored.get_field("contact.email") == "nguyenvana@example.com"

    def test_json_roundtrip(self, sample_profile: UserProfile) -> None:
        json_str = sample_profile.to_json()
        restored = UserProfile.from_json(json_str)
        assert restored.get_field("personal.full_name") == "Nguyen Van A"

    def test_empty_profile(self) -> None:
        profile = UserProfile()
        assert profile.get_all_fields() == {}
        assert profile.get_field("personal.name") is None

    def test_list_field(self, sample_profile: UserProfile) -> None:
        langs = sample_profile.get_field("skills.programming_languages")
        assert isinstance(langs, list)
        assert "Python" in langs


class TestFormField:
    """Tests for FormField model."""

    def test_basic_creation(self, sample_text_field: FormField) -> None:
        assert sample_text_field.field_id == "field_001"
        assert sample_text_field.label == "Full Name"
        assert sample_text_field.field_type == FieldType.TEXT
        assert sample_text_field.required is True

    def test_serialization_roundtrip(self, sample_text_field: FormField) -> None:
        data = sample_text_field.to_dict()
        restored = FormField.from_dict(data)
        assert restored.field_id == sample_text_field.field_id
        assert restored.label == sample_text_field.label
        assert restored.field_type == sample_text_field.field_type

    def test_radio_field_options(self, sample_radio_field: FormField) -> None:
        assert len(sample_radio_field.options) == 3
        assert sample_radio_field.options[0].text == "Male"
        assert sample_radio_field.options[1].value == "female"


class TestFormSchema:
    """Tests for FormSchema model."""

    def test_all_fields(self, sample_form_schema: FormSchema) -> None:
        all_fields = sample_form_schema.all_fields
        assert len(all_fields) == 3

    def test_field_count(self, sample_form_schema: FormSchema) -> None:
        assert sample_form_schema.field_count == 3

    def test_json_roundtrip(self, sample_form_schema: FormSchema) -> None:
        json_str = sample_form_schema.to_json()
        restored = FormSchema.from_json(json_str)
        assert restored.form_id == sample_form_schema.form_id
        assert restored.field_count == sample_form_schema.field_count
        assert restored.all_fields[0].label == "Full Name"


class TestFieldType:
    """Tests for FieldType enum."""

    def test_text_is_text_like(self) -> None:
        assert FieldType.TEXT.is_text_like is True

    def test_email_is_text_like(self) -> None:
        assert FieldType.EMAIL.is_text_like is True

    def test_radio_is_not_text_like(self) -> None:
        assert FieldType.RADIO.is_text_like is False

    def test_radio_is_selectable(self) -> None:
        assert FieldType.RADIO.is_selectable is True

    def test_text_is_not_selectable(self) -> None:
        assert FieldType.TEXT.is_selectable is False

    def test_password_is_sensitive(self) -> None:
        assert FieldType.PASSWORD.is_sensitive is True

    def test_hidden_is_skippable(self) -> None:
        assert FieldType.HIDDEN.is_skippable is True

    def test_text_is_not_skippable(self) -> None:
        assert FieldType.TEXT.is_skippable is False


class TestConfidenceLevel:
    """Tests for ConfidenceLevel enum."""

    def test_high_symbol(self) -> None:
        assert ConfidenceLevel.HIGH.symbol == "✓"

    def test_medium_color(self) -> None:
        assert ConfidenceLevel.MEDIUM.color == "yellow"

    def test_no_match_symbol(self) -> None:
        assert ConfidenceLevel.NO_MATCH.symbol == "✗"
