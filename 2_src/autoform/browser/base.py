"""Abstract browser adapter interface for AutoForm."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BrowserAdapter(ABC):
    """
    Abstract interface for browser automation.

    All browser interactions go through this interface,
    allowing the automation engine to be framework-agnostic.

    Currently implemented by PlaywrightAdapter.
    Designed to be replaceable with SeleniumAdapter or others in the future.
    """

    @abstractmethod
    async def launch(self, headless: bool = False) -> None:
        """
        Launch the browser.

        Args:
            headless: If True, run without visible UI.
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close the browser and clean up resources."""
        ...

    @abstractmethod
    async def open(self, url: str) -> None:
        """
        Navigate to a URL.

        Args:
            url: The URL to navigate to.
        """
        ...

    @abstractmethod
    async def get_url(self) -> str:
        """Get the current page URL."""
        ...

    @abstractmethod
    async def get_title(self) -> str:
        """Get the current page title."""
        ...

    @abstractmethod
    async def get_page_content(self) -> str:
        """Get the full HTML content of the current page."""
        ...

    @abstractmethod
    async def find_elements(self, selector: str) -> list[dict[str, Any]]:
        """
        Find elements matching a CSS selector.

        Returns a list of element info dicts with keys:
          - tag_name, text_content, inner_html, outer_html, attributes, visible, enabled
        """
        ...

    @abstractmethod
    async def get_element_attribute(self, selector: str, attribute: str) -> str | None:
        """Get an attribute value from the first matching element."""
        ...

    @abstractmethod
    async def get_text(self, selector: str) -> str:
        """Get text content of the first matching element."""
        ...

    @abstractmethod
    async def get_value(self, selector: str) -> str:
        """Get the input value of the first matching element."""
        ...

    @abstractmethod
    async def fill(self, selector: str, value: str) -> None:
        """
        Clear and fill an input/textarea element.

        Args:
            selector: CSS selector or Playwright locator string.
            value: Text value to fill.
        """
        ...

    @abstractmethod
    async def click(self, selector: str) -> None:
        """
        Click an element.

        Args:
            selector: CSS selector or Playwright locator string.
        """
        ...

    @abstractmethod
    async def check(self, selector: str) -> None:
        """
        Check a checkbox (make it checked).

        Args:
            selector: CSS selector for the checkbox.
        """
        ...

    @abstractmethod
    async def uncheck(self, selector: str) -> None:
        """
        Uncheck a checkbox (make it unchecked).

        Args:
            selector: CSS selector for the checkbox.
        """
        ...

    @abstractmethod
    async def select_option(self, selector: str, value: str | None = None, label: str | None = None) -> None:
        """
        Select an option from a <select> element.

        Args:
            selector: CSS selector for the <select>.
            value: Option value to select.
            label: Option label text to select.
        """
        ...

    @abstractmethod
    async def is_visible(self, selector: str) -> bool:
        """Check if an element is visible on the page."""
        ...

    @abstractmethod
    async def is_enabled(self, selector: str) -> bool:
        """Check if an element is enabled (not disabled)."""
        ...

    @abstractmethod
    async def is_checked(self, selector: str) -> bool:
        """Check if a checkbox/radio is checked."""
        ...

    @abstractmethod
    async def wait_for(self, selector: str, timeout_ms: int = 5000, state: str = "visible") -> None:
        """
        Wait for an element to reach a specific state.

        Args:
            selector: CSS selector.
            timeout_ms: Maximum wait time in milliseconds.
            state: Target state ('visible', 'hidden', 'attached', 'detached').
        """
        ...

    @abstractmethod
    async def wait_for_navigation(self, timeout_ms: int = 10000) -> None:
        """Wait for a page navigation to complete."""
        ...

    @abstractmethod
    async def screenshot(self, path: str, full_page: bool = False) -> None:
        """
        Take a screenshot.

        Args:
            path: File path to save the screenshot.
            full_page: If True, capture the entire page.
        """
        ...

    @abstractmethod
    async def evaluate(self, js_expression: str) -> Any:
        """
        Execute JavaScript in the page context and return the result.

        Args:
            js_expression: JavaScript code to execute.
        """
        ...

    @abstractmethod
    async def scroll_to(self, selector: str) -> None:
        """Scroll to make an element visible."""
        ...

    @abstractmethod
    async def count_elements(self, selector: str) -> int:
        """Count the number of elements matching the selector."""
        ...
