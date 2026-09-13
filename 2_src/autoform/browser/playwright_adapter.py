"""Playwright-based browser adapter implementation."""

from __future__ import annotations

from typing import Any

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from autoform.browser.base import BrowserAdapter
from autoform.domain.exceptions import (
    BrowserLaunchError,
    BrowserNavigationError,
    BrowserTimeoutError,
    ElementNotFoundError,
    ElementNotInteractableError,
)
from autoform.infrastructure.logging import get_logger

logger = get_logger("browser.playwright")


class PlaywrightAdapter(BrowserAdapter):
    """
    Browser adapter implementation using Microsoft Playwright.

    Features:
    - Auto-wait for elements before interaction
    - Shadow DOM piercing
    - iframe support via frame_locator
    - Isolated browser contexts
    - Network interception capability
    - Trace recording for debugging
    """

    def __init__(
        self,
        browser_type: str = "chromium",
        timeout_ms: int = 30000,
        viewport_width: int = 1280,
        viewport_height: int = 720,
    ) -> None:
        self._browser_type_name = browser_type
        self._timeout_ms = timeout_ms
        self._viewport_width = viewport_width
        self._viewport_height = viewport_height

        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    @property
    def page(self) -> Page:
        """Get the active page, raising if not initialized."""
        if self._page is None:
            raise BrowserLaunchError("Browser not launched. Call launch() first.")
        return self._page

    @property
    def is_launched(self) -> bool:
        """Check if the browser is currently launched."""
        return self._browser is not None and self._browser.is_connected()

    async def launch(self, headless: bool = False) -> None:
        """Launch browser with an isolated context."""
        try:
            self._playwright = await async_playwright().start()

            # Select browser type
            browser_type = getattr(self._playwright, self._browser_type_name, None)
            if browser_type is None:
                raise BrowserLaunchError(
                    f"Unknown browser type: {self._browser_type_name}. "
                    "Use 'chromium', 'firefox', or 'webkit'."
                )

            self._browser = await browser_type.launch(headless=headless)

            # Create isolated context (no shared cookies/storage)
            self._context = await self._browser.new_context(
                viewport={"width": self._viewport_width, "height": self._viewport_height},
                ignore_https_errors=False,
            )
            self._context.set_default_timeout(self._timeout_ms)

            self._page = await self._context.new_page()

            logger.info(
                "browser_launched",
                browser_type=self._browser_type_name,
                headless=headless,
                viewport=f"{self._viewport_width}x{self._viewport_height}",
            )
        except Exception as e:
            if "Executable doesn't exist" in str(e):
                raise BrowserLaunchError(
                    f"Browser '{self._browser_type_name}' not installed. "
                    f"Run: playwright install {self._browser_type_name}"
                ) from e
            raise BrowserLaunchError(f"Failed to launch browser: {e}") from e

    async def close(self) -> None:
        """Close browser and clean up all resources."""
        try:
            if self._context:
                await self._context.clear_cookies()
                await self._context.close()
                self._context = None

            if self._browser:
                await self._browser.close()
                self._browser = None

            if self._playwright:
                await self._playwright.stop()
                self._playwright = None

            self._page = None
            logger.info("browser_closed")
        except Exception as e:
            logger.warning("browser_close_error", error=str(e))

    async def open(self, url: str) -> None:
        """Navigate to a URL and wait for load."""
        try:
            response = await self.page.goto(url, wait_until="domcontentloaded")
            if response and response.status >= 400:
                logger.warning("navigation_http_error", url=url, status=response.status)
            logger.info("page_opened", url=url)
        except Exception as e:
            raise BrowserNavigationError(f"Failed to navigate to {url}: {e}") from e

    async def get_url(self) -> str:
        return self.page.url

    async def get_title(self) -> str:
        return await self.page.title()

    async def get_page_content(self) -> str:
        return await self.page.content()

    async def find_elements(self, selector: str) -> list[dict[str, Any]]:
        """Find elements and return their properties as dicts."""
        elements = []
        locator = self.page.locator(selector)
        count = await locator.count()

        for i in range(count):
            el = locator.nth(i)
            try:
                element_info: dict[str, Any] = {
                    "tag_name": await el.evaluate("el => el.tagName.toLowerCase()"),
                    "text_content": (await el.text_content() or "").strip(),
                    "inner_html": await el.inner_html(),
                    "outer_html": await el.evaluate("el => el.outerHTML"),
                    "visible": await el.is_visible(),
                    "enabled": await el.is_enabled(),
                    "attributes": await el.evaluate(
                        """el => {
                            const attrs = {};
                            for (const attr of el.attributes) {
                                attrs[attr.name] = attr.value;
                            }
                            return attrs;
                        }"""
                    ),
                }
                elements.append(element_info)
            except Exception:
                # Element may have been detached from DOM
                continue

        return elements

    async def get_element_attribute(self, selector: str, attribute: str) -> str | None:
        try:
            return await self.page.locator(selector).first.get_attribute(attribute)
        except Exception:
            return None

    async def get_text(self, selector: str) -> str:
        try:
            text = await self.page.locator(selector).first.text_content()
            return (text or "").strip()
        except Exception as e:
            raise ElementNotFoundError(selector, str(e)) from e

    async def get_value(self, selector: str) -> str:
        try:
            return await self.page.locator(selector).first.input_value()
        except Exception as e:
            raise ElementNotFoundError(selector, str(e)) from e

    async def fill(self, selector: str, value: str) -> None:
        try:
            await self.page.locator(selector).first.fill(value)
            logger.debug("field_filled", selector=selector)
        except Exception as e:
            if "not visible" in str(e).lower() or "not enabled" in str(e).lower():
                raise ElementNotInteractableError(selector, str(e)) from e
            raise ElementNotFoundError(selector, str(e)) from e

    async def click(self, selector: str) -> None:
        try:
            await self.page.locator(selector).first.click()
            logger.debug("element_clicked", selector=selector)
        except Exception as e:
            if "not visible" in str(e).lower():
                raise ElementNotInteractableError(selector, str(e)) from e
            raise ElementNotFoundError(selector, str(e)) from e

    async def check(self, selector: str) -> None:
        try:
            await self.page.locator(selector).first.check()
        except Exception as e:
            raise ElementNotInteractableError(selector, str(e)) from e

    async def uncheck(self, selector: str) -> None:
        try:
            await self.page.locator(selector).first.uncheck()
        except Exception as e:
            raise ElementNotInteractableError(selector, str(e)) from e

    async def select_option(
        self,
        selector: str,
        value: str | None = None,
        label: str | None = None,
    ) -> None:
        try:
            if value is not None:
                await self.page.locator(selector).first.select_option(value=value)
            elif label is not None:
                await self.page.locator(selector).first.select_option(label=label)
            logger.debug("option_selected", selector=selector, value=value, label=label)
        except Exception as e:
            raise ElementNotInteractableError(selector, str(e)) from e

    async def is_visible(self, selector: str) -> bool:
        try:
            return await self.page.locator(selector).first.is_visible()
        except Exception:
            return False

    async def is_enabled(self, selector: str) -> bool:
        try:
            return await self.page.locator(selector).first.is_enabled()
        except Exception:
            return False

    async def is_checked(self, selector: str) -> bool:
        try:
            return await self.page.locator(selector).first.is_checked()
        except Exception:
            return False

    async def wait_for(
        self,
        selector: str,
        timeout_ms: int = 5000,
        state: str = "visible",
    ) -> None:
        try:
            await self.page.locator(selector).first.wait_for(
                timeout=timeout_ms,
                state=state,  # type: ignore[arg-type]
            )
        except Exception as e:
            raise BrowserTimeoutError(
                f"Timed out waiting for '{selector}' to be {state} "
                f"after {timeout_ms}ms: {e}"
            ) from e

    async def wait_for_navigation(self, timeout_ms: int = 10000) -> None:
        try:
            await self.page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        except Exception as e:
            raise BrowserTimeoutError(f"Navigation timeout after {timeout_ms}ms: {e}") from e

    async def screenshot(self, path: str, full_page: bool = False) -> None:
        await self.page.screenshot(path=path, full_page=full_page)
        logger.info("screenshot_taken", path=path)

    async def evaluate(self, js_expression: str) -> Any:
        return await self.page.evaluate(js_expression)

    async def scroll_to(self, selector: str) -> None:
        await self.page.locator(selector).first.scroll_into_view_if_needed()

    async def count_elements(self, selector: str) -> int:
        return await self.page.locator(selector).count()
