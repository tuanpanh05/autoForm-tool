"""Factory for creating the appropriate form adapter based on URL."""

from __future__ import annotations

from autoform.domain.enums import Platform
from autoform.form_analyzer.adapters.base import FormAdapter
from autoform.form_analyzer.adapters.generic_html import GenericHTMLFormAdapter
from autoform.infrastructure.logging import get_logger

logger = get_logger("form_analyzer.factory")


class FormAdapterFactory:
    """
    Factory that selects the correct FormAdapter based on the form URL.

    URL patterns:
    - docs.google.com/forms → GoogleFormsAdapter
    - forms.office.com → MicrosoftFormsAdapter (future)
    - *typeform.com → TypeformAdapter (future)
    - Everything else → GenericHTMLFormAdapter
    """

    @staticmethod
    def create(url: str) -> tuple[FormAdapter, Platform]:
        """
        Create the appropriate adapter for a URL.

        Args:
            url: The form URL.

        Returns:
            Tuple of (FormAdapter instance, detected Platform).
        """
        url_lower = url.lower()

        # Google Forms
        if "docs.google.com/forms" in url_lower or "forms.gle" in url_lower:
            # GoogleFormsAdapter not yet implemented, fall back to generic
            logger.info("platform_detected", platform="google_forms", note="using generic fallback")
            return GenericHTMLFormAdapter(), Platform.GOOGLE_FORMS

        # Microsoft Forms (future)
        if "forms.office.com" in url_lower or "forms.microsoft.com" in url_lower:
            logger.info("platform_detected", platform="microsoft_forms", note="using generic fallback")
            return GenericHTMLFormAdapter(), Platform.MICROSOFT_FORMS

        # Typeform (future)
        if "typeform.com" in url_lower:
            logger.info("platform_detected", platform="typeform", note="using generic fallback")
            return GenericHTMLFormAdapter(), Platform.TYPEFORM

        # Default: Generic HTML
        logger.info("platform_detected", platform="generic_html")
        return GenericHTMLFormAdapter(), Platform.GENERIC_HTML
