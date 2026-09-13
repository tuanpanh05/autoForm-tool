"""Domain enumerations for AutoForm."""

from enum import Enum


class FieldType(Enum):
    """Types of form fields that can be detected and filled."""

    TEXT = "text"
    EMAIL = "email"
    NUMBER = "number"
    TEL = "tel"
    URL = "url"
    DATE = "date"
    DATETIME = "datetime-local"
    TEXTAREA = "textarea"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    SELECT = "select"
    FILE = "file"
    PASSWORD = "password"
    HIDDEN = "hidden"
    UNKNOWN = "unknown"

    @property
    def is_text_like(self) -> bool:
        """Check if the field type accepts text input."""
        return self in (
            FieldType.TEXT,
            FieldType.EMAIL,
            FieldType.NUMBER,
            FieldType.TEL,
            FieldType.URL,
            FieldType.TEXTAREA,
        )

    @property
    def is_selectable(self) -> bool:
        """Check if the field type requires option selection."""
        return self in (FieldType.RADIO, FieldType.CHECKBOX, FieldType.SELECT)

    @property
    def is_sensitive(self) -> bool:
        """Check if the field type handles sensitive data."""
        return self in (FieldType.PASSWORD, FieldType.FILE)

    @property
    def is_skippable(self) -> bool:
        """Check if the field type should be skipped during automation."""
        return self in (FieldType.HIDDEN, FieldType.PASSWORD, FieldType.FILE)


class ConfidenceLevel(Enum):
    """Classification of mapping confidence scores."""

    HIGH = "high"          # >= 0.85 — Auto-fill
    MEDIUM = "medium"      # >= 0.60 — Suggest, ask user to confirm
    LOW = "low"            # >= 0.30 — Show but don't recommend
    NO_MATCH = "no_match"  # < 0.30 — No mapping found

    @property
    def symbol(self) -> str:
        """Get display symbol for confidence level."""
        symbols = {
            ConfidenceLevel.HIGH: "✓",
            ConfidenceLevel.MEDIUM: "⚠",
            ConfidenceLevel.LOW: "❓",
            ConfidenceLevel.NO_MATCH: "✗",
        }
        return symbols[self]

    @property
    def color(self) -> str:
        """Get Rich color name for display."""
        colors = {
            ConfidenceLevel.HIGH: "green",
            ConfidenceLevel.MEDIUM: "yellow",
            ConfidenceLevel.LOW: "red",
            ConfidenceLevel.NO_MATCH: "dim",
        }
        return colors[self]


class Platform(Enum):
    """Supported form platforms."""

    GENERIC_HTML = "generic_html"
    GOOGLE_FORMS = "google_forms"
    MICROSOFT_FORMS = "microsoft_forms"
    TYPEFORM = "typeform"
    UNKNOWN = "unknown"


class LabelSource(Enum):
    """Source from which a field label was extracted."""

    LABEL_FOR = "label_for"                  # <label for="...">
    ARIA_LABEL = "aria_label"                # aria-label attribute
    ARIA_LABELLEDBY = "aria_labelledby"      # aria-labelledby reference
    WRAPPING_LABEL = "wrapping_label"        # <label><input></label>
    PLACEHOLDER = "placeholder"              # placeholder attribute
    NEARBY_TEXT = "nearby_text"              # Text near the field
    NAME_ATTR = "name_attribute"             # name attribute (humanized)
    ID_ATTR = "id_attribute"                 # id attribute (humanized)
    TITLE_ATTR = "title_attribute"           # title attribute
    DATA_ATTR = "data_attribute"             # data-* attributes
    QUESTION_TEXT = "question_text"          # Platform-specific question text
    UNKNOWN = "unknown"


class FillStatus(Enum):
    """Status of filling a single field."""

    FILLED = "filled"
    SKIPPED = "skipped"
    FAILED = "failed"
    ERROR = "error"
    BLOCKED = "blocked"


class MatchMethod(Enum):
    """Method used to match a form field to a profile field."""

    RULE_EXACT = "rule_exact"
    RULE_CONTAINS = "rule_contains"
    RULE_REGEX = "rule_regex"
    FUZZY = "fuzzy"
    EMBEDDING = "embedding"
    LLM = "llm"
    MANUAL = "manual"
    NONE = "none"
