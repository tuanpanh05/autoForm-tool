"""Shared test fixtures for AutoForm."""

from __future__ import annotations

import pytest

from autoform.domain.enums import FieldType, LabelSource
from autoform.domain.models import (
    FieldOption,
    FormField,
    FormSchema,
    FormSection,
    UserProfile,
)


@pytest.fixture
def sample_profile() -> UserProfile:
    """A sample user profile for testing."""
    return UserProfile(
        personal={
            "full_name": "Nguyen Van A",
            "first_name": "A",
            "last_name": "Nguyen",
            "date_of_birth": "2004-05-20",
            "gender": "Male",
        },
        contact={
            "email": "nguyenvana@example.com",
            "phone": "0123456789",
            "address": "123 Le Loi, District 1, HCMC",
        },
        education={
            "university": "FPT University",
            "major": "Software Engineering",
            "gpa": 3.5,
            "graduation_year": 2026,
        },
        work={
            "company": "Tech Corp",
            "position": "Junior Developer",
            "years_of_experience": 1,
        },
        skills={
            "programming_languages": ["Python", "Java", "C#"],
            "tools": ["Git", "Docker", "VS Code"],
        },
        preferences={
            "language": "Vietnamese",
        },
        custom={
            "github": "https://github.com/nguyenvana",
            "linkedin": "https://linkedin.com/in/nguyenvana",
        },
    )


@pytest.fixture
def sample_text_field() -> FormField:
    """A simple text form field."""
    return FormField(
        field_id="field_001",
        label="Full Name",
        label_source=LabelSource.LABEL_FOR,
        field_type=FieldType.TEXT,
        required=True,
        locator="#full-name",
    )


@pytest.fixture
def sample_email_field() -> FormField:
    """An email form field."""
    return FormField(
        field_id="field_002",
        label="Email Address",
        label_source=LabelSource.LABEL_FOR,
        field_type=FieldType.EMAIL,
        required=True,
        placeholder="you@example.com",
        locator="#email",
    )


@pytest.fixture
def sample_radio_field() -> FormField:
    """A radio button form field."""
    return FormField(
        field_id="field_003",
        label="Gender",
        label_source=LabelSource.LABEL_FOR,
        field_type=FieldType.RADIO,
        required=False,
        options=[
            FieldOption(value="male", text="Male", locator="input[name='gender'][value='male']"),
            FieldOption(
                value="female", text="Female", locator="input[name='gender'][value='female']"
            ),
            FieldOption(
                value="other", text="Other", locator="input[name='gender'][value='other']"
            ),
        ],
        locator="input[name='gender']",
    )


@pytest.fixture
def sample_form_fields(
    sample_text_field: FormField,
    sample_email_field: FormField,
    sample_radio_field: FormField,
) -> list[FormField]:
    """A list of sample form fields."""
    return [sample_text_field, sample_email_field, sample_radio_field]


@pytest.fixture
def sample_form_schema(sample_form_fields: list[FormField]) -> FormSchema:
    """A sample form schema."""
    return FormSchema(
        form_id="test_form_001",
        url="file:///test_forms/basic.html",
        title="Test Application Form",
        sections=[
            FormSection(
                section_id="section_0",
                title="Personal Information",
                fields=sample_form_fields,
                order=0,
            ),
        ],
    )
