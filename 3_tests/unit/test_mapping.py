"""Unit tests for the mapping engine, matchers, and confidence scorer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from autoform.domain.enums import ConfidenceLevel, FieldType, MatchMethod
from autoform.domain.exceptions import ProfileNotFoundError
from autoform.domain.models import FormField, FormSchema, FormSection, UserProfile
from autoform.mapping.confidence import ConfidenceScorer
from autoform.mapping.engine import MappingEngine
from autoform.mapping.matchers.fuzzy_matcher import FuzzyMatcher
from autoform.mapping.matchers.rule_matcher import RuleMatcher
from autoform.profile.manager import ProfileManager
from autoform.profile.storage import ProfileStorage


# =============================================================================
# Rule Matcher Tests
# =============================================================================


class TestRuleMatcher:
    """Tests for the rule-based matcher."""

    @pytest.fixture
    def matcher(self) -> RuleMatcher:
        return RuleMatcher()

    @pytest.fixture
    def profile_fields(self, sample_profile: UserProfile) -> dict[str, Any]:
        return sample_profile.get_all_fields()

    def test_exact_match_full_name(self, matcher: RuleMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("Full Name", profile_fields)
        assert len(results) > 0
        assert results[0].profile_path == "personal.full_name"
        assert results[0].confidence >= 0.95
        assert results[0].method == MatchMethod.RULE_EXACT

    def test_exact_match_email(self, matcher: RuleMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("Email", profile_fields)
        assert results[0].profile_path == "contact.email"

    def test_contains_match(self, matcher: RuleMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("Your Email Address", profile_fields)
        assert len(results) > 0
        assert results[0].profile_path == "contact.email"

    def test_case_insensitive(self, matcher: RuleMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("EMAIL", profile_fields)
        assert results[0].profile_path == "contact.email"

    def test_vietnamese_label(self, matcher: RuleMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("Họ và tên", profile_fields)
        assert results[0].profile_path == "personal.full_name"

    def test_vietnamese_phone(self, matcher: RuleMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("Số điện thoại", profile_fields)
        assert results[0].profile_path == "contact.phone"

    def test_university(self, matcher: RuleMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("University", profile_fields)
        assert results[0].profile_path == "education.university"

    def test_date_of_birth(self, matcher: RuleMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("Date of Birth", profile_fields)
        assert results[0].profile_path == "personal.date_of_birth"

    def test_regex_match(self, matcher: RuleMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("What is your phone number?", profile_fields)
        assert len(results) > 0
        assert results[0].profile_path == "contact.phone"

    def test_no_match_random(self, matcher: RuleMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("Favorite dinosaur species", profile_fields)
        assert len(results) == 0

    def test_no_match_for_missing_profile_field(self, matcher: RuleMatcher) -> None:
        # Profile with only email
        profile_fields = {"contact.email": "test@test.com"}
        results = matcher.match("Full Name", profile_fields)
        assert len(results) == 0  # personal.full_name not in profile

    def test_github_match(self, matcher: RuleMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("GitHub Profile", profile_fields)
        assert results[0].profile_path == "custom.github"

    def test_prefix_removal(self, matcher: RuleMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("Enter your email", profile_fields)
        assert results[0].profile_path == "contact.email"

    def test_gender(self, matcher: RuleMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("Gender", profile_fields)
        assert results[0].profile_path == "personal.gender"


# =============================================================================
# Fuzzy Matcher Tests
# =============================================================================


class TestFuzzyMatcher:
    """Tests for the fuzzy string matcher."""

    @pytest.fixture
    def matcher(self) -> FuzzyMatcher:
        return FuzzyMatcher(min_score=60)

    @pytest.fixture
    def profile_fields(self, sample_profile: UserProfile) -> dict[str, Any]:
        return sample_profile.get_all_fields()

    def test_close_match_email(self, matcher: FuzzyMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("Your Email", profile_fields)
        assert len(results) > 0
        # Should find email-related match
        paths = [r.profile_path for r in results]
        assert "contact.email" in paths

    def test_close_match_name(self, matcher: FuzzyMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("Applicant Name", profile_fields)
        assert len(results) > 0

    def test_question_format(self, matcher: FuzzyMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("What university are you studying at?", profile_fields)
        assert len(results) > 0
        paths = [r.profile_path for r in results]
        assert "education.university" in paths

    def test_very_different_text(self, matcher: FuzzyMatcher, profile_fields: dict[str, Any]) -> None:
        # With min_score=60, very short descriptions (like 'gpa') can still
        # partially match long strings via token_set_ratio, so we use a stricter threshold
        strict_matcher = FuzzyMatcher(min_score=75)
        results = strict_matcher.match("xyzzy plugh twisty little passages", profile_fields)
        assert len(results) == 0

    def test_returns_top_5(self, matcher: FuzzyMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("name", profile_fields)
        assert len(results) <= 5

    def test_all_fuzzy_method(self, matcher: FuzzyMatcher, profile_fields: dict[str, Any]) -> None:
        results = matcher.match("Email Address", profile_fields)
        for r in results:
            assert r.method == MatchMethod.FUZZY


# =============================================================================
# Confidence Scorer Tests
# =============================================================================


class TestConfidenceScorer:
    """Tests for confidence scoring and classification."""

    @pytest.fixture
    def scorer(self) -> ConfidenceScorer:
        return ConfidenceScorer()

    def test_high_classification(self, scorer: ConfidenceScorer) -> None:
        assert scorer.classify(0.95) == ConfidenceLevel.HIGH
        assert scorer.classify(0.85) == ConfidenceLevel.HIGH

    def test_medium_classification(self, scorer: ConfidenceScorer) -> None:
        assert scorer.classify(0.72) == ConfidenceLevel.MEDIUM
        assert scorer.classify(0.60) == ConfidenceLevel.MEDIUM

    def test_low_classification(self, scorer: ConfidenceScorer) -> None:
        assert scorer.classify(0.45) == ConfidenceLevel.LOW
        assert scorer.classify(0.30) == ConfidenceLevel.LOW

    def test_no_match_classification(self, scorer: ConfidenceScorer) -> None:
        assert scorer.classify(0.15) == ConfidenceLevel.NO_MATCH
        assert scorer.classify(0.0) == ConfidenceLevel.NO_MATCH

    def test_type_compatibility_bonus(self, scorer: ConfidenceScorer) -> None:
        # Email field type + email profile path → bonus
        score = scorer.calculate(
            method_score=0.90,
            field_type=FieldType.EMAIL,
            profile_path="contact.email",
        )
        assert score > 0.90

    def test_type_incompatibility_penalty(self, scorer: ConfidenceScorer) -> None:
        # Radio field type + email profile path → penalty
        score = scorer.calculate(
            method_score=0.90,
            field_type=FieldType.RADIO,
            profile_path="contact.email",
        )
        assert score < 0.90

    def test_context_bonus(self, scorer: ConfidenceScorer) -> None:
        # "Personal Information" section + personal field → bonus
        score = scorer.calculate(
            method_score=0.80,
            profile_path="personal.full_name",
            context="Personal Information",
        )
        assert score > 0.80

    def test_score_clamped(self, scorer: ConfidenceScorer) -> None:
        score = scorer.calculate(method_score=0.99, field_type=FieldType.EMAIL, profile_path="contact.email")
        assert score <= 1.0

    def test_no_adjustments(self, scorer: ConfidenceScorer) -> None:
        score = scorer.calculate(method_score=0.75)
        assert score == 0.75


# =============================================================================
# Mapping Engine Tests
# =============================================================================


class TestMappingEngine:
    """Tests for the mapping engine pipeline."""

    @pytest.fixture
    def engine(self) -> MappingEngine:
        return MappingEngine(
            matchers=[RuleMatcher(), FuzzyMatcher()],
            scorer=ConfidenceScorer(),
        )

    def test_map_simple_field(self, engine: MappingEngine, sample_profile: UserProfile) -> None:
        field = FormField(field_id="f1", label="Full Name", field_type=FieldType.TEXT)
        mapping = engine.map_field(field, sample_profile)
        assert mapping.profile_path == "personal.full_name"
        assert mapping.confidence >= 0.90
        assert mapping.confidence_level == ConfidenceLevel.HIGH

    def test_map_email_with_type_bonus(
        self, engine: MappingEngine, sample_profile: UserProfile
    ) -> None:
        field = FormField(field_id="f2", label="Email", field_type=FieldType.EMAIL)
        mapping = engine.map_field(field, sample_profile)
        assert mapping.profile_path == "contact.email"
        assert mapping.confidence_level == ConfidenceLevel.HIGH

    def test_map_unknown_field(self, engine: MappingEngine, sample_profile: UserProfile) -> None:
        field = FormField(field_id="f3", label="What is your favorite dinosaur species?", field_type=FieldType.TEXT)
        mapping = engine.map_field(field, sample_profile)
        # May still get a low fuzzy match but should NOT be HIGH
        assert mapping.confidence_level != ConfidenceLevel.HIGH

    def test_map_form_skips_hidden(
        self,
        engine: MappingEngine,
        sample_profile: UserProfile,
        sample_form_schema: FormSchema,
    ) -> None:
        hidden_field = FormField(
            field_id="f_hidden", label="csrf_token", field_type=FieldType.HIDDEN
        )
        sample_form_schema.sections[0].fields.append(hidden_field)
        mappings = engine.map_form(sample_form_schema, sample_profile)
        # Hidden field should be skipped
        mapped_ids = [m.form_field.field_id for m in mappings]
        assert "f_hidden" not in mapped_ids

    def test_map_form_returns_all(
        self,
        engine: MappingEngine,
        sample_profile: UserProfile,
        sample_form_schema: FormSchema,
    ) -> None:
        mappings = engine.map_form(sample_form_schema, sample_profile)
        # Should have mappings for all visible, non-skippable fields
        assert len(mappings) == 3  # name, email, gender

    def test_value_populated(self, engine: MappingEngine, sample_profile: UserProfile) -> None:
        field = FormField(field_id="f1", label="Email", field_type=FieldType.EMAIL)
        mapping = engine.map_field(field, sample_profile)
        assert mapping.value == "nguyenvana@example.com"

    def test_not_approved_by_default(
        self, engine: MappingEngine, sample_profile: UserProfile
    ) -> None:
        field = FormField(field_id="f1", label="Full Name", field_type=FieldType.TEXT)
        mapping = engine.map_field(field, sample_profile)
        assert mapping.approved is False


# =============================================================================
# Profile Storage Tests
# =============================================================================


class TestProfileStorage:
    """Tests for JSON profile storage."""

    def test_save_and_load(self, tmp_path: Path, sample_profile: UserProfile) -> None:
        storage = ProfileStorage(tmp_path)
        storage.save(sample_profile, "test")
        loaded = storage.load("test")
        assert loaded.get_field("personal.full_name") == "Nguyen Van A"
        assert loaded.get_field("contact.email") == "nguyenvana@example.com"

    def test_list_profiles(self, tmp_path: Path, sample_profile: UserProfile) -> None:
        storage = ProfileStorage(tmp_path)
        storage.save(sample_profile, "profile_a")
        storage.save(sample_profile, "profile_b")
        profiles = storage.list_profiles()
        assert "profile_a" in profiles
        assert "profile_b" in profiles

    def test_delete_profile(self, tmp_path: Path, sample_profile: UserProfile) -> None:
        storage = ProfileStorage(tmp_path)
        storage.save(sample_profile, "to_delete")
        assert storage.exists("to_delete")
        storage.delete("to_delete")
        assert not storage.exists("to_delete")

    def test_load_nonexistent(self, tmp_path: Path) -> None:
        storage = ProfileStorage(tmp_path)
        with pytest.raises(ProfileNotFoundError):
            storage.load("nonexistent")

    def test_profile_manager_create(self, tmp_path: Path) -> None:
        storage = ProfileStorage(tmp_path)
        manager = ProfileManager(storage)

        profile = manager.create_profile(
            {"personal": {"full_name": "Test User"}, "contact": {"email": "test@test.com"}},
            "mgr_test",
        )
        assert profile.get_field("personal.full_name") == "Test User"
        assert manager.profile_exists("mgr_test")

    def test_profile_manager_update_field(self, tmp_path: Path, sample_profile: UserProfile) -> None:
        storage = ProfileStorage(tmp_path)
        manager = ProfileManager(storage)
        storage.save(sample_profile, "update_test")

        updated = manager.update_field("update_test", "personal.full_name", "New Name")
        assert updated.get_field("personal.full_name") == "New Name"

    def test_profile_summary(self, tmp_path: Path, sample_profile: UserProfile) -> None:
        storage = ProfileStorage(tmp_path)
        manager = ProfileManager(storage)
        storage.save(sample_profile, "summary_test")

        summary = manager.get_profile_summary("summary_test")
        assert summary["personal"] >= 3
        assert summary["contact"] >= 2
