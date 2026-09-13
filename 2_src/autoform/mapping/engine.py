"""Mapping engine — orchestrates the matching pipeline."""

from __future__ import annotations

from typing import Any

from autoform.domain.enums import ConfidenceLevel, FieldType, MatchMethod
from autoform.domain.models import (
    FieldMapping,
    FormField,
    FormSchema,
    MatchCandidate,
    UserProfile,
)
from autoform.infrastructure.logging import get_logger
from autoform.mapping.confidence import ConfidenceScorer
from autoform.mapping.matchers.base import Matcher

logger = get_logger("mapping.engine")


class MappingEngine:
    """
    Orchestrates the field-to-profile mapping pipeline.

    Pipeline: RuleMatcher → FuzzyMatcher → (EmbeddingMatcher → LLMMatcher)

    Short-circuit: If a matcher returns confidence above its threshold,
    subsequent matchers are skipped for that field.
    """

    # Short-circuit thresholds per matcher
    _SHORT_CIRCUIT_THRESHOLDS: dict[str, float] = {
        "RuleMatcher": 0.95,
        "FuzzyMatcher": 0.85,
        "EmbeddingMatcher": 0.85,
        "LLMMatcher": 0.0,  # Always use LLM result
    }

    def __init__(
        self,
        matchers: list[Matcher],
        scorer: ConfidenceScorer | None = None,
    ) -> None:
        """
        Args:
            matchers: Ordered list of matchers (first = highest priority).
            scorer: Confidence scorer. Uses default if None.
        """
        self._matchers = matchers
        self._scorer = scorer or ConfidenceScorer()

    def map_field(
        self,
        field: FormField,
        profile: UserProfile,
    ) -> FieldMapping:
        """
        Map a single form field to the best matching profile field.

        Args:
            field: The form field to map.
            profile: The user's profile.

        Returns:
            FieldMapping with the best match (or NO_MATCH).
        """
        profile_fields = profile.get_all_fields()
        best_candidate: MatchCandidate | None = None

        for matcher in self._matchers:
            candidates = matcher.match(field.label, profile_fields)

            if candidates:
                top = candidates[0]
                if best_candidate is None or top.confidence > best_candidate.confidence:
                    best_candidate = top

                # Short-circuit if confidence is high enough
                matcher_name = type(matcher).__name__
                threshold = self._SHORT_CIRCUIT_THRESHOLDS.get(matcher_name, 0.85)
                if top.confidence >= threshold:
                    logger.debug(
                        "mapping_short_circuit",
                        field_label=field.label,
                        matcher=matcher_name,
                        confidence=top.confidence,
                    )
                    break

        if best_candidate and best_candidate.confidence >= 0.30:
            # Calculate adjusted confidence
            confidence = self._scorer.calculate(
                method_score=best_candidate.confidence,
                field_type=field.field_type,
                profile_path=best_candidate.profile_path,
                context=field.section_context,
            )
            confidence_level = self._scorer.classify(confidence)

            value = profile.get_field(best_candidate.profile_path)

            logger.info(
                "field_mapped",
                field_label=field.label,
                profile_path=best_candidate.profile_path,
                confidence=confidence,
                level=confidence_level.value,
                method=best_candidate.method.value,
            )

            return FieldMapping(
                form_field=field,
                profile_path=best_candidate.profile_path,
                value=value,
                confidence=confidence,
                confidence_level=confidence_level,
                matched_by=best_candidate.method,
                approved=False,
                user_edited=False,
            )

        logger.info("field_no_match", field_label=field.label)
        return FieldMapping(
            form_field=field,
            profile_path=None,
            value=None,
            confidence=0.0,
            confidence_level=ConfidenceLevel.NO_MATCH,
            matched_by=MatchMethod.NONE,
            approved=False,
            user_edited=False,
        )

    def map_form(
        self,
        schema: FormSchema,
        profile: UserProfile,
    ) -> list[FieldMapping]:
        """
        Map all fields in a form schema to profile fields.

        Args:
            schema: The normalized form schema.
            profile: The user's profile.

        Returns:
            List of FieldMapping for all non-skippable fields.
        """
        mappings: list[FieldMapping] = []

        for section in schema.sections:
            for field in section.fields:
                # Skip hidden, password, file fields
                if field.field_type.is_skippable:
                    continue
                if field.is_disabled or not field.is_visible:
                    continue

                mapping = self.map_field(field, profile)
                mappings.append(mapping)

        # Summary
        mapped = sum(1 for m in mappings if m.profile_path is not None)
        high = sum(1 for m in mappings if m.confidence_level == ConfidenceLevel.HIGH)
        medium = sum(1 for m in mappings if m.confidence_level == ConfidenceLevel.MEDIUM)
        low = sum(1 for m in mappings if m.confidence_level == ConfidenceLevel.LOW)
        no_match = sum(1 for m in mappings if m.confidence_level == ConfidenceLevel.NO_MATCH)

        logger.info(
            "form_mapped",
            total_fields=len(mappings),
            mapped=mapped,
            high=high,
            medium=medium,
            low=low,
            no_match=no_match,
        )

        return mappings
