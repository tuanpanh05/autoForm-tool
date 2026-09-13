"""Abstract form adapter interface for platform-specific form handling."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from autoform.browser.base import BrowserAdapter
from autoform.domain.models import FormField, FormSchema


class FormAdapter(ABC):
    """
    Abstract interface for platform-specific form handling.

    Each form platform (Google Forms, HTML forms, Typeform, etc.)
    has its own DOM structure. FormAdapter encapsulates the
    platform-specific logic for detecting fields, extracting labels,
    filling values, and submitting forms.
    """

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """
        Check if this adapter can handle the given URL.

        Args:
            url: The form URL.

        Returns:
            True if this adapter supports the URL.
        """
        ...

    @abstractmethod
    async def detect_fields(self, browser: BrowserAdapter) -> list[FormField]:
        """
        Detect all form fields on the current page.

        Args:
            browser: The browser adapter with the form loaded.

        Returns:
            List of detected FormField objects.
        """
        ...

    @abstractmethod
    async def get_form_title(self, browser: BrowserAdapter) -> str:
        """Extract the form title from the page."""
        ...

    @abstractmethod
    async def fill_field(
        self,
        browser: BrowserAdapter,
        field: FormField,
        value: Any,
    ) -> bool:
        """
        Fill a specific field with a value.

        Args:
            browser: The browser adapter.
            field: The form field to fill.
            value: The value to fill.

        Returns:
            True if the field was filled successfully.
        """
        ...

    @abstractmethod
    async def submit(self, browser: BrowserAdapter) -> bool:
        """
        Submit the form.

        Args:
            browser: The browser adapter.

        Returns:
            True if submit was triggered successfully.
        """
        ...

    @abstractmethod
    async def detect_captcha(self, browser: BrowserAdapter) -> bool:
        """
        Check if a CAPTCHA is present on the page.

        Args:
            browser: The browser adapter.

        Returns:
            True if CAPTCHA is detected.
        """
        ...

    @abstractmethod
    async def detect_submit_button(self, browser: BrowserAdapter) -> str | None:
        """
        Find the submit button locator.

        Args:
            browser: The browser adapter.

        Returns:
            Locator string for the submit button, or None.
        """
        ...
