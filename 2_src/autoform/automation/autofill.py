"""Autofill engine — fills form fields based on approved mappings."""

from __future__ import annotations

import asyncio
import random
from typing import Any

from autoform.browser.base import BrowserAdapter
from autoform.domain.enums import FieldType, FillStatus
from autoform.domain.models import FieldMapping, FillFieldResult, FillResult, SubmitResult
from autoform.form_analyzer.adapters.base import FormAdapter
from autoform.infrastructure.logging import get_logger

logger = get_logger("automation.autofill")


class AutofillEngine:
    """
    Fills form fields based on approved mappings.

    Safety rules:
    - Only fills approved mappings
    - Skips sensitive fields (password, file)
    - Requires confirmation before submit
    - Detects CAPTCHA and pauses
    - Adds human-like delays between fields
    """

    def __init__(
        self,
        browser: BrowserAdapter,
        form_adapter: FormAdapter,
        min_delay_ms: int = 100,
        max_delay_ms: int = 300,
        max_retries: int = 2,
    ) -> None:
        self._browser = browser
        self._form_adapter = form_adapter
        self._min_delay_ms = min_delay_ms
        self._max_delay_ms = max_delay_ms
        self._max_retries = max_retries

    async def fill_form(self, mappings: list[FieldMapping]) -> FillResult:
        """
        Fill all approved mappings in the form.

        Args:
            mappings: List of field mappings (only approved ones will be filled).

        Returns:
            FillResult with status for each field.
        """
        import time

        start = time.perf_counter()
        results: list[FillFieldResult] = []

        for mapping in mappings:
            # Skip unapproved mappings
            if not mapping.approved:
                results.append(FillFieldResult(
                    field=mapping.form_field,
                    status=FillStatus.SKIPPED,
                    reason="not approved",
                ))
                continue

            # Skip if no value
            if mapping.value is None:
                results.append(FillFieldResult(
                    field=mapping.form_field,
                    status=FillStatus.SKIPPED,
                    reason="no value",
                ))
                continue

            # Skip sensitive fields
            if mapping.form_field.field_type.is_sensitive:
                results.append(FillFieldResult(
                    field=mapping.form_field,
                    status=FillStatus.BLOCKED,
                    reason="sensitive field type",
                ))
                continue

            # Fill with retry
            result = await self._fill_with_retry(mapping)
            results.append(result)

            # Human-like delay between fields
            await self._field_delay()

        elapsed_ms = (time.perf_counter() - start) * 1000
        fill_result = FillResult(field_results=results, processing_time_ms=elapsed_ms)

        logger.info(
            "form_filled",
            total=fill_result.total_fields,
            filled=fill_result.filled_count,
            skipped=fill_result.skipped_count,
            failed=fill_result.failed_count,
            errors=fill_result.error_count,
            time_ms=round(elapsed_ms),
        )

        return fill_result

    async def _fill_with_retry(self, mapping: FieldMapping) -> FillFieldResult:
        """Fill a field with retry logic."""
        for attempt in range(self._max_retries + 1):
            try:
                success = await self._form_adapter.fill_field(
                    self._browser,
                    mapping.form_field,
                    mapping.value,
                )

                if success:
                    logger.info(
                        "field_filled",
                        field_id=mapping.form_field.field_id,
                        field_label=mapping.form_field.label,
                        status="filled",
                    )
                    return FillFieldResult(
                        field=mapping.form_field,
                        status=FillStatus.FILLED,
                        value=mapping.value,
                    )
                else:
                    if attempt < self._max_retries:
                        await asyncio.sleep(0.5)
                        continue
                    return FillFieldResult(
                        field=mapping.form_field,
                        status=FillStatus.FAILED,
                        reason="fill returned false",
                    )

            except Exception as e:
                if attempt < self._max_retries:
                    logger.debug(
                        "field_fill_retry",
                        field_id=mapping.form_field.field_id,
                        attempt=attempt + 1,
                        error=str(e),
                    )
                    await asyncio.sleep(0.5)
                    continue

                logger.error(
                    "field_fill_error",
                    field_id=mapping.form_field.field_id,
                    error=str(e),
                )
                return FillFieldResult(
                    field=mapping.form_field,
                    status=FillStatus.ERROR,
                    reason=str(e),
                )

        return FillFieldResult(
            field=mapping.form_field,
            status=FillStatus.FAILED,
            reason="max retries exceeded",
        )

    async def submit_form(self, confirmed: bool = False) -> SubmitResult:
        """
        Submit the form after all checks pass.

        Args:
            confirmed: Must be True to proceed (user confirmation required).

        Returns:
            SubmitResult with success status.
        """
        if not confirmed:
            return SubmitResult(success=False, reason="User confirmation required")

        # Check for CAPTCHA
        has_captcha = await self._form_adapter.detect_captcha(self._browser)
        if has_captcha:
            return SubmitResult(
                success=False,
                reason="CAPTCHA detected. Please solve it manually.",
                needs_human_action=True,
            )

        # Submit
        try:
            success = await self._form_adapter.submit(self._browser)

            if success:
                # Wait for response
                await asyncio.sleep(2)
                logger.info("form_submitted")

            return SubmitResult(success=success)

        except Exception as e:
            logger.error("submit_error", error=str(e))
            return SubmitResult(success=False, reason=str(e))

    async def _field_delay(self) -> None:
        """Add human-like delay between field fills."""
        delay = random.uniform(self._min_delay_ms / 1000, self._max_delay_ms / 1000)
        await asyncio.sleep(delay)
