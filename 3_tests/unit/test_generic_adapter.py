"""Unit tests for GenericHTMLFormAdapter and utility functions."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from autoform.form_analyzer.adapters.generic_html import GenericHTMLFormAdapter, _humanize


class TestGenericHTMLFormAdapter:
    """Test suite for GenericHTMLFormAdapter."""

    def setup_method(self) -> None:
        self.adapter = GenericHTMLFormAdapter()

    def test_humanize(self) -> None:
        assert _humanize("first_name") == "First Name"
        assert _humanize("txtEmailAddress") == "Email Address"
        assert _humanize("user-phone-number") == "User Phone Number"

    def test_can_handle_all_urls(self) -> None:
        assert self.adapter.can_handle("https://example.com/form.html") is True
        assert self.adapter.can_handle("http://localhost:8080") is True

    @pytest.mark.asyncio
    async def test_get_form_title(self) -> None:
        mock_browser = AsyncMock()
        mock_browser.evaluate.return_value = "Contact Us Form"
        title = await self.adapter.get_form_title(mock_browser)
        assert title == "Contact Us Form"

    @pytest.mark.asyncio
    async def test_detect_captcha_none(self) -> None:
        mock_browser = AsyncMock()
        mock_browser.count_elements.return_value = 0
        has_captcha = await self.adapter.detect_captcha(mock_browser)
        assert has_captcha is False

    @pytest.mark.asyncio
    async def test_detect_captcha_found(self) -> None:
        mock_browser = AsyncMock()

        def side_effect(sel: str) -> int:
            return 1 if "recaptcha" in sel else 0

        mock_browser.count_elements.side_effect = side_effect
        has_captcha = await self.adapter.detect_captcha(mock_browser)
        assert has_captcha is True

    @pytest.mark.asyncio
    async def test_detect_submit_button(self) -> None:
        mock_browser = AsyncMock()

        def side_effect(sel: str) -> int:
            return 1 if sel == 'button[type="submit"]' else 0

        mock_browser.count_elements.side_effect = side_effect
        submit_btn = await self.adapter.detect_submit_button(mock_browser)
        assert submit_btn == 'button[type="submit"]'
