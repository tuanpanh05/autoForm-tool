"""Confidence scoring and classification for field mappings."""

from __future__ import annotations

from autoform.domain.enums import ConfidenceLevel, FieldType


# Field type compatibility matrix — which FieldTypes match which profile data types
_TYPE_COMPATIBILITY: dict[str, set[FieldType]] = {
    "contact.email": {FieldType.EMAIL, FieldType.TEXT},
    "contact.phone": {FieldType.TEL, FieldType.TEXT, FieldType.NUMBER},
    "personal.date_of_birth": {FieldType.DATE, FieldType.DATETIME, FieldType.TEXT},
    "personal.gender": {FieldType.RADIO, FieldType.SELECT, FieldType.TEXT},
    "education.gpa": {FieldType.NUMBER, FieldType.TEXT},
    "education.graduation_year": {FieldType.NUMBER, FieldType.TEXT, FieldType.DATE},
    "work.years_of_experience": {FieldType.NUMBER, FieldType.TEXT},
    "skills.programming_languages": {FieldType.CHECKBOX, FieldType.TEXT, FieldType.TEXTAREA},
    "skills.tools": {FieldType.CHECKBOX, FieldType.TEXT, FieldType.TEXTAREA},
}

# Context keywords that boost confidence when they match the profile category
_CONTEXT_KEYWORDS: dict[str, list[str]] = {
    "personal": ["personal", "about you", "basic info", "thông tin cá nhân"],
    "contact": ["contact", "reach you", "liên hệ", "thông tin liên lạc"],
    "education": ["education", "academic", "school", "học vấn", "giáo dục"],
    "work": ["work", "employment", "professional", "career", "công việc", "nghề nghiệp"],
    "skills": ["skills", "abilities", "competencies", "kỹ năng"],
}


class ConfidenceScorer:
    """
    Calculates and classifies confidence scores for field mappings.

    Score adjustments:
    - Field type compatibility: +0.05 bonus / -0.15 penalty
    - Context match: +0.05 bonus
    - Final score clamped to [0.0, 1.0]
    """

    def __init__(
        self,
        high_threshold: float = 0.85,
        medium_threshold: float = 0.60,
        low_threshold: float = 0.30,
    ) -> None:
        self._high = high_threshold
        self._medium = medium_threshold
        self._low = low_threshold

    def calculate(
        self,
        method_score: float,
        field_type: FieldType = FieldType.UNKNOWN,
        profile_path: str = "",
        context: str = "",
    ) -> float:
        """
        Calculate final confidence score with adjustments.

        Args:
            method_score: Raw confidence from the matcher (0.0-1.0).
            field_type: The form field's type.
            profile_path: The matched profile field path.
            context: Section/group context of the form field.

        Returns:
            Adjusted confidence score (0.0-1.0).
        """
        score = method_score

        # Type compatibility adjustment
        if profile_path and field_type != FieldType.UNKNOWN:
            compatible_types = _TYPE_COMPATIBILITY.get(profile_path)
            if compatible_types is not None:
                if field_type in compatible_types:
                    score = min(1.0, score + 0.05)  # Bonus
                else:
                    score = max(0.0, score - 0.15)  # Penalty

        # Context bonus
        if context and profile_path:
            category = profile_path.split(".")[0] if "." in profile_path else ""
            context_lower = context.lower()
            keywords = _CONTEXT_KEYWORDS.get(category, [])
            if any(kw in context_lower for kw in keywords):
                score = min(1.0, score + 0.05)

        return round(score, 3)

    def classify(self, score: float) -> ConfidenceLevel:
        """
        Classify a confidence score into a ConfidenceLevel.

        Args:
            score: Confidence score (0.0-1.0).

        Returns:
            ConfidenceLevel (HIGH, MEDIUM, LOW, NO_MATCH).
        """
        if score >= self._high:
            return ConfidenceLevel.HIGH
        elif score >= self._medium:
            return ConfidenceLevel.MEDIUM
        elif score >= self._low:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.NO_MATCH
