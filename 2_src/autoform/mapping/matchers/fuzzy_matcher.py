"""Fuzzy string matching for field-to-profile mapping."""

from __future__ import annotations

from typing import Any

from rapidfuzz import fuzz

from autoform.domain.enums import MatchMethod
from autoform.domain.models import MatchCandidate
from autoform.mapping.matchers.base import Matcher

# Field descriptions for fuzzy matching — multiple phrasings per field
FIELD_DESCRIPTIONS: dict[str, list[str]] = {
    "personal.full_name": ["full name", "name", "applicant name", "your name", "complete name"],
    "personal.first_name": ["first name", "given name", "forename"],
    "personal.last_name": ["last name", "family name", "surname"],
    "personal.date_of_birth": ["date of birth", "birthday", "birth date", "dob"],
    "personal.gender": ["gender", "sex"],
    "contact.email": ["email address", "email", "e-mail", "mail"],
    "contact.phone": ["phone number", "mobile number", "telephone", "contact number", "cell phone"],
    "contact.address": ["address", "street address", "home address", "mailing address"],
    "contact.city": ["city", "town", "municipality"],
    "contact.country": ["country", "nation", "nationality"],
    "education.university": ["university", "college", "school", "institution", "alma mater"],
    "education.major": ["major", "field of study", "specialization", "department", "concentration"],
    "education.gpa": ["gpa", "grade point average", "grades", "academic score"],
    "education.graduation_year": ["graduation year", "year of graduation", "expected graduation"],
    "work.company": ["company", "employer", "organization", "workplace"],
    "work.position": ["position", "job title", "role", "designation"],
    "work.years_of_experience": [
        "years of experience", "work experience", "professional experience",
        "how many years", "experience level",
    ],
    "skills.programming_languages": [
        "programming languages", "coding languages", "languages you know",
        "technical skills", "programming skills",
    ],
    "skills.tools": ["tools", "technologies", "software", "frameworks"],
    "custom.github": ["github", "github profile", "github url", "github account"],
    "custom.linkedin": ["linkedin", "linkedin profile", "linkedin url"],
    "custom.website": ["website", "personal website", "portfolio", "blog", "homepage"],
}


class FuzzyMatcher(Matcher):
    """
    Fuzzy string matching for field-to-profile mapping.

    Uses rapidfuzz library (C++ backend) for fast string similarity.
    Applies multiple fuzzy algorithms and takes the best score.

    Algorithms used:
    - ratio: Overall string similarity
    - partial_ratio: Best partial string match
    - token_sort_ratio: Word order independent matching
    - token_set_ratio: Extra words tolerance
    """

    def __init__(self, min_score: int = 60) -> None:
        """
        Args:
            min_score: Minimum fuzzy score (0-100) to consider a match.
        """
        self._min_score = min_score

    def match(
        self,
        field_label: str,
        profile_fields: dict[str, Any],
    ) -> list[MatchCandidate]:
        label_lower = field_label.lower().strip()
        candidates: list[MatchCandidate] = []

        for profile_path, descriptions in FIELD_DESCRIPTIONS.items():
            # Only match fields that exist in user's profile
            if profile_path not in profile_fields:
                continue

            best_score = 0.0
            for desc in descriptions:
                # Run multiple fuzzy algorithms
                scores = [
                    fuzz.ratio(label_lower, desc) / 100,
                    fuzz.partial_ratio(label_lower, desc) / 100,
                    fuzz.token_sort_ratio(label_lower, desc) / 100,
                    fuzz.token_set_ratio(label_lower, desc) / 100,
                ]
                score = max(scores)
                if score > best_score:
                    best_score = score

            if best_score >= (self._min_score / 100):
                candidates.append(MatchCandidate(
                    profile_path=profile_path,
                    confidence=round(best_score, 3),
                    method=MatchMethod.FUZZY,
                ))

        # Sort by confidence descending, take top 5
        return sorted(candidates, key=lambda c: c.confidence, reverse=True)[:5]
