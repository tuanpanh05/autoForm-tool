"""Abstract matcher interface for field-to-profile matching."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from autoform.domain.models import MatchCandidate


class Matcher(ABC):
    """
    Abstract interface for field-to-profile matching.

    Each matcher implementation uses a different strategy
    (rules, fuzzy, embedding, LLM) to find matching profile
    fields for a given form field label.
    """

    @abstractmethod
    def match(
        self,
        field_label: str,
        profile_fields: dict[str, Any],
    ) -> list[MatchCandidate]:
        """
        Find matching profile fields for a form field label.

        Args:
            field_label: The label text from the form field.
            profile_fields: Flattened profile dict {path: value}.

        Returns:
            List of MatchCandidate sorted by confidence (descending).
        """
        ...
