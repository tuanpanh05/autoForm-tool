"""Rule-based matcher using keywords and regex patterns."""

from __future__ import annotations

import re
from typing import Any

from autoform.domain.enums import MatchMethod
from autoform.domain.models import MatchCandidate
from autoform.mapping.matchers.base import Matcher

# =============================================================================
# Keyword Rules — exact and contains matching
# =============================================================================

KEYWORD_RULES: dict[str, list[str]] = {
    # Personal
    "personal.full_name": [
        "full name", "full_name", "fullname", "your name", "applicant name",
        "legal name", "complete name", "name", "họ và tên", "họ tên",
    ],
    "personal.first_name": [
        "first name", "first_name", "firstname", "given name", "tên",
    ],
    "personal.last_name": [
        "last name", "last_name", "lastname", "family name", "surname", "họ",
    ],
    "personal.date_of_birth": [
        "date of birth", "dob", "birthday", "birth date", "birthdate",
        "ngày sinh", "sinh nhật",
    ],
    "personal.gender": [
        "gender", "sex", "giới tính",
    ],
    # Contact
    "contact.email": [
        "email", "e-mail", "email address", "e-mail address", "your email",
        "mail", "địa chỉ email",
    ],
    "contact.phone": [
        "phone", "phone number", "mobile", "mobile number", "cell",
        "cell phone", "telephone", "contact number", "tel",
        "số điện thoại", "điện thoại",
    ],
    "contact.address": [
        "address", "street address", "mailing address", "home address",
        "địa chỉ",
    ],
    "contact.city": [
        "city", "town", "thành phố",
    ],
    "contact.country": [
        "country", "nation", "quốc gia", "quốc tịch",
    ],
    # Education
    "education.university": [
        "university", "school", "college", "institution", "alma mater",
        "trường đại học", "trường", "đại học",
    ],
    "education.major": [
        "major", "field of study", "specialization", "concentration",
        "department", "chuyên ngành", "ngành học", "ngành",
    ],
    "education.gpa": [
        "gpa", "grade point average", "grades", "điểm trung bình",
    ],
    "education.graduation_year": [
        "graduation year", "year of graduation", "grad year",
        "expected graduation", "năm tốt nghiệp",
    ],
    # Work
    "work.company": [
        "company", "employer", "organization", "organisation", "workplace",
        "công ty", "tổ chức",
    ],
    "work.position": [
        "position", "job title", "role", "title", "designation",
        "vị trí", "chức vụ", "chức danh",
    ],
    "work.years_of_experience": [
        "years of experience", "experience years", "work experience",
        "professional experience", "kinh nghiệm", "năm kinh nghiệm",
    ],
    # Custom / Social
    "custom.github": [
        "github", "github url", "github profile", "github link",
        "github username",
    ],
    "custom.linkedin": [
        "linkedin", "linkedin url", "linkedin profile", "linkedin link",
    ],
    "custom.website": [
        "website", "personal website", "portfolio", "blog",
        "trang web", "trang cá nhân",
    ],
}

# =============================================================================
# Regex Rules — more flexible pattern matching
# =============================================================================

REGEX_RULES: list[tuple[str, str, float]] = [
    # (pattern, profile_path, confidence)
    (r"(?:full\s+)?name(?:\s+of\s+(?:applicant|candidate|student))?", "personal.full_name", 0.92),
    (r"(?:first|given)\s+name", "personal.first_name", 0.95),
    (r"(?:last|family|sur)\s*name", "personal.last_name", 0.95),
    (r"e-?mail\s*(?:address)?", "contact.email", 0.95),
    (r"(?:phone|mobile|cell|tel)(?:ephone)?\s*(?:number|no\.?)?", "contact.phone", 0.93),
    (r"(?:date\s+of\s+birth|d\.?o\.?b\.?|birth\s*(?:date|day))", "personal.date_of_birth", 0.95),
    (r"(?:university|college|school|institution)\s*(?:name)?", "education.university", 0.90),
    (r"(?:major|field\s+of\s+study|specializ(?:ation|e))", "education.major", 0.90),
    (r"(?:years?\s+of\s+)?(?:work\s+|professional\s+)?experience", "work.years_of_experience", 0.88),
    (r"(?:company|employer|organi[sz]ation)\s*(?:name)?", "work.company", 0.90),
    (r"(?:job\s+)?(?:title|position|role)", "work.position", 0.88),
    (r"g(?:rade\s+)?p(?:oint\s+)?a(?:verage)?", "education.gpa", 0.95),
    (r"graduat(?:ion|e|ing)\s*(?:year|date)?", "education.graduation_year", 0.90),
    (r"(?:programming\s+)?languages?", "skills.programming_languages", 0.80),
    (r"git\s*hub", "custom.github", 0.95),
    (r"linked\s*in", "custom.linkedin", 0.95),
]


class RuleMatcher(Matcher):
    """
    Rule-based matcher using keyword dictionaries and regex patterns.

    This is the fastest and most deterministic matcher.
    It handles common form fields (name, email, phone, etc.) with
    high confidence and zero cost.

    Matching priority:
    1. Exact keyword match (confidence: 0.98)
    2. Keyword contains match (confidence: 0.90)
    3. Regex pattern match (confidence: varies, typically 0.88-0.95)
    """

    def match(
        self,
        field_label: str,
        profile_fields: dict[str, Any],
    ) -> list[MatchCandidate]:
        label_lower = field_label.lower().strip()
        # Remove common prefixes like "Enter your", "Please provide", etc.
        label_clean = re.sub(
            r"^(?:please\s+)?(?:enter|provide|type|input|specify|write)\s+(?:your\s+)?",
            "",
            label_lower,
            flags=re.IGNORECASE,
        ).strip()

        candidates: list[MatchCandidate] = []
        seen_paths: set[str] = set()

        # Step 1: Exact keyword match
        for profile_path, keywords in KEYWORD_RULES.items():
            if profile_path not in profile_fields:
                continue
            for keyword in keywords:
                if keyword == label_lower or keyword == label_clean:
                    if profile_path not in seen_paths:
                        candidates.append(MatchCandidate(
                            profile_path=profile_path,
                            confidence=0.98,
                            method=MatchMethod.RULE_EXACT,
                        ))
                        seen_paths.add(profile_path)
                    break

        # Step 2: Keyword contains match
        if not candidates:
            for profile_path, keywords in KEYWORD_RULES.items():
                if profile_path not in profile_fields:
                    continue
                if profile_path in seen_paths:
                    continue
                for keyword in keywords:
                    if len(keyword) >= 3 and keyword in label_lower:
                        candidates.append(MatchCandidate(
                            profile_path=profile_path,
                            confidence=0.90,
                            method=MatchMethod.RULE_CONTAINS,
                        ))
                        seen_paths.add(profile_path)
                        break

        # Step 3: Regex pattern match
        if not candidates:
            for pattern, profile_path, confidence in REGEX_RULES:
                if profile_path not in profile_fields:
                    continue
                if profile_path in seen_paths:
                    continue
                if re.search(pattern, label_lower, re.IGNORECASE):
                    candidates.append(MatchCandidate(
                        profile_path=profile_path,
                        confidence=confidence,
                        method=MatchMethod.RULE_REGEX,
                    ))
                    seen_paths.add(profile_path)

        # Sort by confidence descending
        return sorted(candidates, key=lambda c: c.confidence, reverse=True)
