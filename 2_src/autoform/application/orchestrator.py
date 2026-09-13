"""Orchestrator — main pipeline controller connecting all modules."""

from __future__ import annotations

import time
from typing import Any

from autoform.automation.autofill import AutofillEngine
from autoform.browser.playwright_adapter import PlaywrightAdapter
from autoform.domain.enums import ConfidenceLevel, Platform
from autoform.domain.models import (
    FieldMapping,
    FillResult,
    FormSchema,
    FormSection,
    SubmitResult,
    UserProfile,
)
from autoform.form_analyzer.adapters.factory import FormAdapterFactory
from autoform.infrastructure.config import Config
from autoform.infrastructure.logging import get_logger
from autoform.mapping.confidence import ConfidenceScorer
from autoform.mapping.engine import MappingEngine
from autoform.mapping.matchers.base import Matcher
from autoform.mapping.matchers.fuzzy_matcher import FuzzyMatcher
from autoform.mapping.matchers.rule_matcher import RuleMatcher

logger = get_logger("application.orchestrator")


class Orchestrator:
    """
    Main pipeline controller.

    Orchestrates the complete form-filling workflow:
    1. Launch browser → Navigate to form URL
    2. Detect platform → Select adapter
    3. Analyze form → Extract fields
    4. Map fields → Match to profile
    5. Human review → Approve/reject mappings
    6. Autofill → Fill approved fields
    7. Confirm → Submit (optional)
    """

    def __init__(self, config: Config | None = None) -> None:
        self._config = config or Config()
        self._browser: PlaywrightAdapter | None = None
        self._mapping_engine = self._create_mapping_engine()

    def _create_mapping_engine(self) -> MappingEngine:
        """Create the mapping engine with configured matchers."""
        matchers: list[Matcher] = []

        if self._config.get("mapping", "enable_rules", True):
            matchers.append(RuleMatcher())

        if self._config.get("mapping", "enable_fuzzy", True):
            min_score = self._config.get("mapping", "fuzzy_min_score", 60)
            matchers.append(FuzzyMatcher(min_score=min_score))

        scorer = ConfidenceScorer(
            high_threshold=self._config.high_confidence_threshold,
            medium_threshold=self._config.medium_confidence_threshold,
            low_threshold=self._config.low_confidence_threshold,
        )

        return MappingEngine(matchers=matchers, scorer=scorer)

    async def analyze_form(self, url: str) -> tuple[FormSchema, list[FieldMapping], UserProfile]:
        """
        Analyze a form URL and map fields to a profile.

        This is the first half of the pipeline (steps 1-4).

        Args:
            url: The form URL to analyze.

        Returns:
            Tuple of (FormSchema, list of FieldMappings, UserProfile).
        """
        from autoform.profile.manager import ProfileManager
        from autoform.profile.storage import ProfileStorage

        start = time.perf_counter()

        # Step 1: Launch browser
        self._browser = PlaywrightAdapter(
            browser_type=self._config.browser_type,
            timeout_ms=self._config.browser_timeout,
        )
        await self._browser.launch(headless=self._config.browser_headless)

        # Step 2: Navigate to form
        await self._browser.open(url)
        logger.info("form_opened", url=url)

        # Step 3: Detect platform and select adapter
        adapter, platform = FormAdapterFactory.create(url)
        logger.info("adapter_selected", platform=platform.value)

        # Step 4: Analyze form
        fields = await adapter.detect_fields(self._browser)
        title = await adapter.get_form_title(self._browser)
        submit_locator = await adapter.detect_submit_button(self._browser)
        has_captcha = await adapter.detect_captcha(self._browser)

        schema = FormSchema(
            form_id=f"form_{int(time.time())}",
            url=url,
            title=title,
            platform=platform,
            sections=[
                FormSection(
                    section_id="section_0",
                    title="Form Fields",
                    fields=fields,
                    order=0,
                )
            ],
            submit_locator=submit_locator,
            has_captcha=has_captcha,
        )

        logger.info(
            "form_analyzed",
            title=title,
            fields=len(fields),
            platform=platform.value,
            has_captcha=has_captcha,
        )

        # Step 5: Load profile
        storage = ProfileStorage(self._config.profile_dir)
        manager = ProfileManager(storage)

        default_profile_name = self._config.get("profile", "default_profile", "default")
        if manager.profile_exists(default_profile_name):
            profile = manager.get_profile(default_profile_name)
        else:
            profile = manager.create_empty_profile(default_profile_name)
            logger.warning("no_profile_found", using="empty")

        # Step 6: Map fields to profile
        mappings = self._mapping_engine.map_form(schema, profile)

        elapsed = time.perf_counter() - start
        logger.info("analysis_complete", time_s=round(elapsed, 2))

        return schema, mappings, profile

    async def fill_form(
        self,
        mappings: list[FieldMapping],
    ) -> FillResult:
        """
        Fill the form with approved mappings.

        This is the second half of the pipeline (steps 5-6).
        Must be called after analyze_form().

        Args:
            mappings: List of mappings (should have approved=True on desired fields).

        Returns:
            FillResult with status for each field.
        """
        if self._browser is None:
            raise RuntimeError("Browser not launched. Call analyze_form() first.")

        # Select adapter based on current URL
        url = await self._browser.get_url()
        adapter, _ = FormAdapterFactory.create(url)

        engine = AutofillEngine(
            browser=self._browser,
            form_adapter=adapter,
            min_delay_ms=self._config.get("automation", "min_field_delay_ms", 100),
            max_delay_ms=self._config.get("automation", "max_field_delay_ms", 300),
            max_retries=self._config.get("automation", "max_retries", 2),
        )

        return await engine.fill_form(mappings)

    async def submit_form(self, confirmed: bool = False) -> SubmitResult:
        """
        Submit the form.

        Args:
            confirmed: Must be True to proceed.

        Returns:
            SubmitResult.
        """
        if self._browser is None:
            raise RuntimeError("Browser not launched.")

        url = await self._browser.get_url()
        adapter, _ = FormAdapterFactory.create(url)

        engine = AutofillEngine(
            browser=self._browser,
            form_adapter=adapter,
        )

        return await engine.submit_form(confirmed=confirmed)

    async def close(self) -> None:
        """Close the browser and clean up."""
        if self._browser:
            await self._browser.close()
            self._browser = None

    @staticmethod
    def auto_approve_high_confidence(
        mappings: list[FieldMapping],
        threshold: float = 0.85,
    ) -> list[FieldMapping]:
        """
        Auto-approve mappings with HIGH confidence.

        Args:
            mappings: List of field mappings.
            threshold: Minimum confidence for auto-approval.

        Returns:
            The same list with high-confidence mappings approved.
        """
        for mapping in mappings:
            if mapping.confidence >= threshold:
                mapping.approved = True
        return mappings
