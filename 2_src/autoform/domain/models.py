"""Domain models for AutoForm."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


from autoform.domain.enums import (
    ConfidenceLevel,
    FieldType,
    FillStatus,
    LabelSource,
    MatchMethod,
    Platform,
)


# =============================================================================
# Form Schema Models
# =============================================================================


@dataclass
class FieldValidation:
    """Validation rules extracted from a form field."""

    min_length: int | None = None
    max_length: int | None = None
    min_value: float | None = None
    max_value: float | None = None
    pattern: str | None = None
    step: float | None = None
    accepted_types: list[str] = field(default_factory=list)
    custom_rules: dict[str, Any] = field(default_factory=dict)


@dataclass
class FieldOption:
    """An option for radio/checkbox/select fields."""

    value: str
    text: str
    locator: str
    selected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "text": self.text,
            "locator": self.locator,
            "selected": self.selected,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FieldOption:
        return cls(
            value=data["value"],
            text=data["text"],
            locator=data["locator"],
            selected=data.get("selected", False),
        )


@dataclass
class FormField:
    """Normalized representation of a single form field."""

    # Identity
    field_id: str

    # Content
    label: str
    label_source: LabelSource = LabelSource.UNKNOWN
    description: str = ""
    placeholder: str = ""

    # Type
    field_type: FieldType = FieldType.UNKNOWN
    input_mode: str = ""

    # Options (for radio/checkbox/select)
    options: list[FieldOption] = field(default_factory=list)

    # Constraints
    required: bool = False
    validation: FieldValidation = field(default_factory=FieldValidation)

    # Location
    locator: str = ""
    section_context: str = ""

    # Raw data
    raw_attributes: dict[str, str] = field(default_factory=dict)
    raw_html: str = ""

    # State
    current_value: str | None = None
    is_disabled: bool = False
    is_visible: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "field_id": self.field_id,
            "label": self.label,
            "label_source": self.label_source.value,
            "description": self.description,
            "placeholder": self.placeholder,
            "field_type": self.field_type.value,
            "input_mode": self.input_mode,
            "options": [opt.to_dict() for opt in self.options],
            "required": self.required,
            "locator": self.locator,
            "section_context": self.section_context,
            "current_value": self.current_value,
            "is_disabled": self.is_disabled,
            "is_visible": self.is_visible,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FormField:
        """Deserialize from dictionary."""
        return cls(
            field_id=data["field_id"],
            label=data["label"],
            label_source=LabelSource(data.get("label_source", "unknown")),
            description=data.get("description", ""),
            placeholder=data.get("placeholder", ""),
            field_type=FieldType(data.get("field_type", "unknown")),
            input_mode=data.get("input_mode", ""),
            options=[FieldOption.from_dict(o) for o in data.get("options", [])],
            required=data.get("required", False),
            locator=data.get("locator", ""),
            section_context=data.get("section_context", ""),
            current_value=data.get("current_value"),
            is_disabled=data.get("is_disabled", False),
            is_visible=data.get("is_visible", True),
        )


@dataclass
class FormSection:
    """A logical section/group within a form."""

    section_id: str
    title: str = ""
    description: str = ""
    fields: list[FormField] = field(default_factory=list)
    order: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "section_id": self.section_id,
            "title": self.title,
            "description": self.description,
            "fields": [f.to_dict() for f in self.fields],
            "order": self.order,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FormSection:
        return cls(
            section_id=data["section_id"],
            title=data.get("title", ""),
            description=data.get("description", ""),
            fields=[FormField.from_dict(f) for f in data.get("fields", [])],
            order=data.get("order", 0),
        )


@dataclass
class FormSchema:
    """Complete normalized representation of a web form."""

    form_id: str
    url: str
    title: str = ""
    description: str = ""
    platform: Platform = Platform.UNKNOWN
    sections: list[FormSection] = field(default_factory=list)
    submit_locator: str | None = None
    has_captcha: bool = False
    is_multi_step: bool = False
    total_steps: int = 1
    current_step: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)
    analyzed_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def all_fields(self) -> list[FormField]:
        """Get all fields from all sections, flattened."""
        fields: list[FormField] = []
        for section in self.sections:
            fields.extend(section.fields)
        return fields

    @property
    def field_count(self) -> int:
        """Total number of fields across all sections."""
        return sum(len(s.fields) for s in self.sections)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "form_id": self.form_id,
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "platform": self.platform.value,
            "sections": [s.to_dict() for s in self.sections],
            "submit_locator": self.submit_locator,
            "has_captcha": self.has_captcha,
            "is_multi_step": self.is_multi_step,
            "total_steps": self.total_steps,
            "current_step": self.current_step,
            "metadata": self.metadata,
            "analyzed_at": self.analyzed_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FormSchema:
        """Deserialize from dictionary."""
        return cls(
            form_id=data["form_id"],
            url=data["url"],
            title=data.get("title", ""),
            description=data.get("description", ""),
            platform=Platform(data.get("platform", "unknown")),
            sections=[FormSection.from_dict(s) for s in data.get("sections", [])],
            submit_locator=data.get("submit_locator"),
            has_captcha=data.get("has_captcha", False),
            is_multi_step=data.get("is_multi_step", False),
            total_steps=data.get("total_steps", 1),
            current_step=data.get("current_step", 1),
            metadata=data.get("metadata", {}),
            analyzed_at=data.get("analyzed_at", ""),
        )

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        import json

        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> FormSchema:
        """Deserialize from JSON string."""
        import json

        return cls.from_dict(json.loads(json_str))


# =============================================================================
# Mapping Models
# =============================================================================


@dataclass
class MatchCandidate:
    """A candidate mapping from a matcher."""

    profile_path: str
    confidence: float
    method: MatchMethod

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_path": self.profile_path,
            "confidence": self.confidence,
            "method": self.method.value,
        }


@dataclass
class FieldMapping:
    """Mapping between a form field and a user profile field."""

    form_field: FormField
    profile_path: str | None = None
    value: Any = None
    confidence: float = 0.0
    confidence_level: ConfidenceLevel = ConfidenceLevel.NO_MATCH
    matched_by: MatchMethod = MatchMethod.NONE
    approved: bool = False
    user_edited: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_id": self.form_field.field_id,
            "field_label": self.form_field.label,
            "field_type": self.form_field.field_type.value,
            "profile_path": self.profile_path,
            "confidence": self.confidence,
            "confidence_level": self.confidence_level.value,
            "matched_by": self.matched_by.value,
            "approved": self.approved,
            "user_edited": self.user_edited,
        }


# =============================================================================
# Fill Result Models
# =============================================================================


@dataclass
class FillFieldResult:
    """Result of filling a single field."""

    field: FormField
    status: FillStatus
    value: Any = None
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_id": self.field.field_id,
            "field_label": self.field.label,
            "status": self.status.value,
            "reason": self.reason,
        }


@dataclass
class FillResult:
    """Result of filling an entire form."""

    field_results: list[FillFieldResult] = field(default_factory=list)
    url: str = ""
    processing_time_ms: float = 0.0

    @property
    def total_fields(self) -> int:
        return len(self.field_results)

    @property
    def filled_count(self) -> int:
        return sum(1 for r in self.field_results if r.status == FillStatus.FILLED)

    @property
    def skipped_count(self) -> int:
        return sum(1 for r in self.field_results if r.status == FillStatus.SKIPPED)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.field_results if r.status == FillStatus.FAILED)

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.field_results if r.status == FillStatus.ERROR)

    @property
    def success_rate(self) -> float:
        if self.total_fields == 0:
            return 0.0
        return self.filled_count / self.total_fields


@dataclass
class SubmitResult:
    """Result of form submission."""

    success: bool
    reason: str = ""
    needs_human_action: bool = False
    screenshot_path: str = ""


# =============================================================================
# User Profile Model
# =============================================================================


@dataclass
class UserProfile:
    """User's personal information for form filling."""

    personal: dict[str, Any] = field(default_factory=dict)
    contact: dict[str, Any] = field(default_factory=dict)
    education: dict[str, Any] = field(default_factory=dict)
    work: dict[str, Any] = field(default_factory=dict)
    skills: dict[str, Any] = field(default_factory=dict)
    preferences: dict[str, Any] = field(default_factory=dict)
    custom: dict[str, Any] = field(default_factory=dict)

    def get_field(self, path: str) -> Any:
        """
        Get value by dot-path.

        Examples:
            profile.get_field("personal.full_name")  -> "Nguyen Van A"
            profile.get_field("contact.email")        -> "test@example.com"
            profile.get_field("nonexistent.field")    -> None
        """
        parts = path.split(".", 1)
        if len(parts) != 2:
            return None

        category, field_name = parts
        category_data = getattr(self, category, None)
        if category_data is None or not isinstance(category_data, dict):
            return None

        return category_data.get(field_name)

    def set_field(self, path: str, value: Any) -> None:
        """
        Set value by dot-path.

        Examples:
            profile.set_field("personal.full_name", "Nguyen Van A")
            profile.set_field("custom.github", "https://github.com/example")
        """
        parts = path.split(".", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid path format: '{path}'. Expected 'category.field_name'.")

        category, field_name = parts
        category_data = getattr(self, category, None)
        if category_data is None:
            raise ValueError(f"Unknown category: '{category}'.")
        if not isinstance(category_data, dict):
            raise ValueError(f"Category '{category}' is not a dict.")

        category_data[field_name] = value

    def get_all_fields(self) -> dict[str, Any]:
        """
        Flatten profile to {path: value} dict.

        Returns:
            {"personal.full_name": "Nguyen Van A", "contact.email": "test@example.com", ...}
        """
        result: dict[str, Any] = {}
        categories = ["personal", "contact", "education", "work", "skills", "preferences", "custom"]

        for category in categories:
            category_data = getattr(self, category, {})
            if isinstance(category_data, dict):
                for key, value in category_data.items():
                    result[f"{category}.{key}"] = value

        return result

    def get_categories(self) -> list[str]:
        """Get list of all category names."""
        return ["personal", "contact", "education", "work", "skills", "preferences", "custom"]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "personal": self.personal,
            "contact": self.contact,
            "education": self.education,
            "work": self.work,
            "skills": self.skills,
            "preferences": self.preferences,
            "custom": self.custom,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserProfile:
        """Deserialize from dictionary."""
        return cls(
            personal=data.get("personal", {}),
            contact=data.get("contact", {}),
            education=data.get("education", {}),
            work=data.get("work", {}),
            skills=data.get("skills", {}),
            preferences=data.get("preferences", {}),
            custom=data.get("custom", {}),
        )

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        import json

        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> UserProfile:
        """Deserialize from JSON string."""
        import json

        return cls.from_dict(json.loads(json_str))
