"""Unit tests for GoogleFormsAdapter."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from autoform.form_analyzer.adapters.google_forms import GoogleFormsAdapter


class TestGoogleFormsAdapter:
    """Test suite for GoogleFormsAdapter."""

    def setup_method(self) -> None:
        self.adapter = GoogleFormsAdapter()

    def test_can_handle_google_forms(self) -> None:
        assert self.adapter.can_handle("https://docs.google.com/forms/d/e/1FAIpQLSc.../viewform") is True
        assert self.adapter.can_handle("https://forms.gle/xyz123") is True
        assert self.adapter.can_handle("https://example.com/form") is False

    @pytest.mark.asyncio
    async def test_get_form_title(self) -> None:
        mock_browser = AsyncMock()
        mock_browser.evaluate.return_value = "Registration Form - Google Forms"
        title = await self.adapter.get_form_title(mock_browser)
        assert title == "Registration Form"

    @pytest.mark.asyncio
    async def test_detect_captcha(self) -> None:
        mock_browser = AsyncMock()
        mock_browser.evaluate.return_value = 1
        has_captcha = await self.adapter.detect_captcha(mock_browser)
        assert has_captcha is True

        mock_browser.evaluate.return_value = 0
        has_captcha_false = await self.adapter.detect_captcha(mock_browser)
        assert has_captcha_false is False
