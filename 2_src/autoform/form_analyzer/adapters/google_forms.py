"""Google Forms adapter for platform-specific form handling."""

from __future__ import annotations

import re
from typing import Any

from autoform.browser.base import BrowserAdapter
from autoform.domain.enums import FieldType, LabelSource
from autoform.domain.models import FieldOption, FormField
from autoform.form_analyzer.adapters.base import FormAdapter
from autoform.infrastructure.logging import get_logger

logger = get_logger("form_analyzer.google_forms")


class GoogleFormsAdapter(FormAdapter):
    """
    Adapter for Google Forms.

    Google Forms uses a non-standard DOM structure:
    - No <form>, <input>, <select> elements in the traditional sense
    - Questions are rendered as div-based components
    - Radio/checkbox are custom div elements with role="radio"/"checkbox"
    - Dropdowns use custom listbox widgets
    - Text inputs use <input> inside question containers

    Selectors are based on Google Forms' data attributes and ARIA roles,
    which are more stable than CSS class names (which are obfuscated).
    """

    def can_handle(self, url: str) -> bool:
        """Check if URL is a Google Form."""
        url_lower = url.lower()
        return (
            "docs.google.com/forms" in url_lower
            or "forms.gle" in url_lower
        )

    async def detect_fields(self, browser: BrowserAdapter) -> list[FormField]:
        """Detect all form fields on a Google Form."""
        fields_data = await browser.evaluate("""
        () => {
            const fields = [];
            let fieldIndex = 0;

            // Google Forms question containers
            // Each question is wrapped in a div with data-params attribute
            // or has role="listitem" in the form items container
            const questionContainers = document.querySelectorAll(
                '[data-params], div[role="listitem"]'
            );

            // Fallback: try common Google Forms class patterns
            let containers = questionContainers;
            if (containers.length === 0) {
                // Try alternate selectors for newer Google Forms
                containers = document.querySelectorAll(
                    '.freebirdFormviewerComponentsQuestionBaseRoot, ' +
                    '.Qr7Oae, ' +  // Question root class (may change)
                    '[jscontroller] [data-item-id]'
                );
            }

            // If still nothing, try to find any visible input fields
            if (containers.length === 0) {
                containers = document.querySelectorAll('div:has(> [role="heading"])');
            }

            containers.forEach(container => {
                // Skip non-question elements
                if (container.querySelector('[role="heading"]') === null &&
                    container.querySelector('input') === null &&
                    container.querySelector('textarea') === null &&
                    container.querySelector('[role="radio"]') === null &&
                    container.querySelector('[role="checkbox"]') === null &&
                    container.querySelector('[role="listbox"]') === null) {
                    return;
                }

                // Extract question text
                let questionText = '';
                const heading = container.querySelector('[role="heading"]');
                if (heading) {
                    questionText = heading.textContent.trim();
                } else {
                    // Try other text elements
                    const titleEl = container.querySelector(
                        '.freebirdFormviewerComponentsQuestionBaseTitle, ' +
                        '.M7eMe, ' +  // Question title class
                        '[data-initial-value]'
                    );
                    if (titleEl) questionText = titleEl.textContent.trim();
                }

                if (!questionText) return;

                // Check if required
                const requiredMarker = container.querySelector(
                    '[aria-label="Required question"], ' +
                    '.freebirdFormviewerComponentsQuestionBaseRequiredAsterisk, ' +
                    'span[aria-label*="Required"]'
                );
                const isRequired = requiredMarker !== null ||
                    questionText.includes('*') ||
                    container.querySelector('[required]') !== null;

                // Clean question text (remove asterisk)
                questionText = questionText.replace(/\\s*\\*\\s*$/, '').trim();

                // Extract description/help text
                let description = '';
                const descEl = container.querySelector(
                    '.freebirdFormviewerComponentsQuestionBaseDescription, ' +
                    '.SL7Zdc'  // Description class
                );
                if (descEl) description = descEl.textContent.trim();

                // Detect field type
                let fieldType = 'unknown';
                let options = [];
                let locator = '';

                // Short answer (text input)
                const textInput = container.querySelector('input[type="text"], input:not([type])');
                if (textInput) {
                    fieldType = 'text';
                    // Check for email validation
                    const dataType = textInput.getAttribute('data-type') ||
                                    container.getAttribute('data-type') || '';
                    if (dataType.includes('email') || questionText.toLowerCase().includes('email')) {
                        fieldType = 'email';
                    }
                    locator = textInput.id ? '#' + CSS.escape(textInput.id) : '';
                    if (!locator) {
                        // Generate a locator based on aria-label
                        const ariaLabel = textInput.getAttribute('aria-label');
                        if (ariaLabel) locator = `input[aria-label="${ariaLabel}"]`;
                    }
                }

                // Paragraph (textarea)
                const textarea = container.querySelector('textarea');
                if (textarea) {
                    fieldType = 'textarea';
                    locator = textarea.id ? '#' + CSS.escape(textarea.id) : '';
                    if (!locator) {
                        const ariaLabel = textarea.getAttribute('aria-label');
                        if (ariaLabel) locator = `textarea[aria-label="${ariaLabel}"]`;
                    }
                }

                // Multiple choice (radio)
                const radioOptions = container.querySelectorAll('[role="radio"], [data-value]');
                if (radioOptions.length > 0 && fieldType === 'unknown') {
                    fieldType = 'radio';
                    radioOptions.forEach(opt => {
                        const text = opt.textContent.trim() ||
                                    opt.getAttribute('data-value') ||
                                    opt.getAttribute('aria-label') || '';
                        const value = opt.getAttribute('data-value') || text;
                        if (text) {
                            // Build locator for each option
                            let optLocator = '';
                            if (opt.getAttribute('data-value')) {
                                optLocator = `[data-value="${opt.getAttribute('data-value')}"]`;
                            } else {
                                optLocator = `[role="radio"][aria-label="${text}"]`;
                            }
                            options.push({ value, text, locator: optLocator, selected: opt.getAttribute('aria-checked') === 'true' });
                        }
                    });
                }

                // Checkboxes
                const checkboxOptions = container.querySelectorAll('[role="checkbox"]');
                if (checkboxOptions.length > 0 && fieldType === 'unknown') {
                    fieldType = 'checkbox';
                    checkboxOptions.forEach(opt => {
                        const text = opt.textContent.trim() ||
                                    opt.getAttribute('aria-label') || '';
                        const value = opt.getAttribute('data-value') || text;
                        if (text) {
                            let optLocator = '';
                            if (opt.getAttribute('data-value')) {
                                optLocator = `[data-value="${opt.getAttribute('data-value')}"]`;
                            } else {
                                optLocator = `[role="checkbox"][aria-label="${text}"]`;
                            }
                            options.push({ value, text, locator: optLocator, selected: opt.getAttribute('aria-checked') === 'true' });
                        }
                    });
                }

                // Dropdown (select/listbox)
                const listbox = container.querySelector('[role="listbox"]');
                if (listbox && fieldType === 'unknown') {
                    fieldType = 'select';
                    locator = listbox.id ? '#' + CSS.escape(listbox.id) : '[role="listbox"]';
                    // Options may need to be loaded by clicking the dropdown
                    const listOptions = listbox.querySelectorAll('[role="option"]');
                    listOptions.forEach(opt => {
                        const text = opt.textContent.trim();
                        const value = opt.getAttribute('data-value') || text;
                        if (text && text !== 'Choose') {
                            options.push({ value, text, locator: '', selected: opt.getAttribute('aria-selected') === 'true' });
                        }
                    });
                }

                // Date
                const dateInput = container.querySelector('input[type="date"]');
                if (dateInput) {
                    fieldType = 'date';
                    locator = dateInput.id ? '#' + CSS.escape(dateInput.id) : 'input[type="date"]';
                }

                // Number input
                const numberInput = container.querySelector('input[type="number"]');
                if (numberInput && fieldType === 'unknown') {
                    fieldType = 'number';
                    locator = numberInput.id ? '#' + CSS.escape(numberInput.id) : 'input[type="number"]';
                }

                if (fieldType === 'unknown') return;

                fields.push({
                    field_id: 'gf_' + String(fieldIndex++).padStart(3, '0'),
                    label: questionText,
                    label_source: 'question_text',
                    description: description,
                    field_type: fieldType,
                    required: isRequired,
                    options: options,
                    locator: locator,
                    visible: true,
                    enabled: true,
                });
            });

            return fields;
        }
        """)

        # Convert to FormField objects
        form_fields: list[FormField] = []
        type_map = {
            "text": FieldType.TEXT,
            "email": FieldType.EMAIL,
            "number": FieldType.NUMBER,
            "date": FieldType.DATE,
            "textarea": FieldType.TEXTAREA,
            "radio": FieldType.RADIO,
            "checkbox": FieldType.CHECKBOX,
            "select": FieldType.SELECT,
        }

        for data in fields_data:
            field_type = type_map.get(data["field_type"], FieldType.UNKNOWN)

            options = [
                FieldOption(
                    value=opt.get("value", ""),
                    text=opt.get("text", ""),
                    locator=opt.get("locator", ""),
                    selected=opt.get("selected", False),
                )
                for opt in data.get("options", [])
            ]

            form_field = FormField(
                field_id=data["field_id"],
                label=data["label"],
                label_source=LabelSource.QUESTION_TEXT,
                description=data.get("description", ""),
                field_type=field_type,
                required=data.get("required", False),
                options=options,
                locator=data.get("locator", ""),
                is_visible=True,
                is_disabled=False,
            )
            form_fields.append(form_field)

        logger.info("google_forms_fields_detected", count=len(form_fields))
        return form_fields

    async def get_form_title(self, browser: BrowserAdapter) -> str:
        """Extract Google Form title."""
        title = await browser.evaluate("""
        () => {
            // Google Forms title is usually in a heading element
            const titleEl = document.querySelector(
                '.freebirdFormviewerViewHeaderTitle, ' +
                '[role="heading"][aria-level="1"], ' +
                '.p6lMtc, ' +  // Newer title class
                'h1'
            );
            return titleEl ? titleEl.textContent.trim() : document.title || '';
        }
        """)
        # Clean up "- Google Forms" suffix
        if title:
            title = re.sub(r"\s*[-–]\s*Google Forms?\s*$", "", title, flags=re.IGNORECASE)
        return title or ""

    async def fill_field(
        self,
        browser: BrowserAdapter,
        field: FormField,
        value: Any,
    ) -> bool:
        """Fill a Google Forms field."""
        try:
            if field.field_type in (FieldType.TEXT, FieldType.EMAIL, FieldType.NUMBER):
                if field.locator:
                    await browser.fill(field.locator, str(value))
                    return True
                return False

            elif field.field_type == FieldType.TEXTAREA:
                if field.locator:
                    await browser.fill(field.locator, str(value))
                    return True
                return False

            elif field.field_type == FieldType.DATE:
                if field.locator:
                    await browser.fill(field.locator, str(value))
                    return True
                return False

            elif field.field_type == FieldType.RADIO:
                str_value = str(value).lower()
                for opt in field.options:
                    if opt.value.lower() == str_value or opt.text.lower() == str_value:
                        if opt.locator:
                            await browser.click(opt.locator)
                            return True
                return False

            elif field.field_type == FieldType.CHECKBOX:
                values = value if isinstance(value, list) else [value]
                checked = 0
                for val in values:
                    str_val = str(val).lower()
                    for opt in field.options:
                        if opt.value.lower() == str_val or opt.text.lower() == str_val:
                            if opt.locator:
                                await browser.click(opt.locator)
                                checked += 1
                                break
                return checked > 0

            elif field.field_type == FieldType.SELECT:
                # Google Forms dropdowns need to be clicked to open, then select option
                if field.locator:
                    await browser.click(field.locator)
                    import asyncio
                    await asyncio.sleep(0.5)  # Wait for dropdown to open

                    str_value = str(value).lower()
                    for opt in field.options:
                        if opt.value.lower() == str_value or opt.text.lower() == str_value:
                            # Click the option text
                            await browser.evaluate(f"""
                            () => {{
                                const options = document.querySelectorAll('[role="option"]');
                                for (const opt of options) {{
                                    if (opt.textContent.trim().toLowerCase() === '{str_value}') {{
                                        opt.click();
                                        return true;
                                    }}
                                }}
                                return false;
                            }}
                            """)
                            return True
                return False

            return False

        except Exception as e:
            logger.error(
                "google_forms_fill_error",
                field_id=field.field_id,
                field_type=field.field_type.value,
                error=str(e),
            )
            return False

    async def submit(self, browser: BrowserAdapter) -> bool:
        """Submit Google Form."""
        submit_locator = await self.detect_submit_button(browser)
        if submit_locator:
            await browser.click(submit_locator)
            # Wait for submission response
            import asyncio
            await asyncio.sleep(2)
            return True
        return False

    async def detect_captcha(self, browser: BrowserAdapter) -> bool:
        """Check for CAPTCHA on Google Form."""
        captcha_count = await browser.evaluate("""
        () => {
            // reCAPTCHA iframe
            const recaptcha = document.querySelector(
                'iframe[src*="recaptcha"], .g-recaptcha, [data-sitekey]'
            );
            return recaptcha ? 1 : 0;
        }
        """)
        has_captcha = int(captcha_count or 0) > 0
        if has_captcha:
            logger.warning("google_forms_captcha_detected")
        return has_captcha

    async def detect_submit_button(self, browser: BrowserAdapter) -> str | None:
        """Find Google Forms submit button."""
        # Google Forms submit button patterns
        submit_selectors = [
            '[role="button"][jsname="M2UYVd"]',      # Common jsname for submit
            'div[role="button"]:has-text("Submit")',
            'div[role="button"]:has-text("Gửi")',     # Vietnamese
            'div[role="button"]:has-text("送信")',     # Japanese
            'div[role="button"]:has-text("제출")',     # Korean
            '.freebirdFormviewerNavigationSubmitButton',
            '[data-action="submit"]',
        ]

        for selector in submit_selectors:
            try:
                count = await browser.count_elements(selector)
                if count > 0:
                    return selector
            except Exception:
                continue

        return None

    async def detect_next_button(self, browser: BrowserAdapter) -> str | None:
        """Find Google Forms 'Next' button for multi-page forms."""
        next_selectors = [
            'div[role="button"]:has-text("Next")',
            'div[role="button"]:has-text("Tiếp")',
            'div[role="button"]:has-text("次へ")',
            '[jsname="OCpkoe"]',
        ]

        for selector in next_selectors:
            try:
                count = await browser.count_elements(selector)
                if count > 0:
                    return selector
            except Exception:
                continue

        return None
