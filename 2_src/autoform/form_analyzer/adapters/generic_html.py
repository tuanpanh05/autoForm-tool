"""Generic HTML form adapter for standard HTML forms."""

from __future__ import annotations

import re
from typing import Any

from autoform.browser.base import BrowserAdapter
from autoform.domain.enums import FieldType, LabelSource
from autoform.domain.models import FieldOption, FieldValidation, FormField
from autoform.form_analyzer.adapters.base import FormAdapter
from autoform.infrastructure.logging import get_logger

logger = get_logger("form_analyzer.generic_html")

# Map HTML input types to FieldType
_INPUT_TYPE_MAP: dict[str, FieldType] = {
    "text": FieldType.TEXT,
    "email": FieldType.EMAIL,
    "number": FieldType.NUMBER,
    "tel": FieldType.TEL,
    "url": FieldType.URL,
    "date": FieldType.DATE,
    "datetime-local": FieldType.DATETIME,
    "password": FieldType.PASSWORD,
    "radio": FieldType.RADIO,
    "checkbox": FieldType.CHECKBOX,
    "file": FieldType.FILE,
    "hidden": FieldType.HIDDEN,
}


def _humanize(text: str) -> str:
    """Convert a technical name/id to human-readable label."""
    # Replace underscores, hyphens, camelCase
    text = re.sub(r"[_\-]", " ", text)
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    # Remove common prefixes
    text = re.sub(r"^(field|input|txt|sel|chk|rb|frm|form)[_\s]*", "", text, flags=re.IGNORECASE)
    return text.strip().title()


class GenericHTMLFormAdapter(FormAdapter):
    """
    Adapter for standard HTML forms.

    Handles forms built with standard HTML elements:
    <form>, <input>, <textarea>, <select>, <label>

    This is the baseline adapter. Other platform-specific adapters
    (GoogleFormsAdapter, etc.) extend or override this behavior.
    """

    def can_handle(self, url: str) -> bool:
        """GenericHTML handles any URL as a fallback."""
        return True

    async def detect_fields(self, browser: BrowserAdapter) -> list[FormField]:
        """Detect all form fields using JavaScript DOM traversal."""
        # Use JS to extract all field information in one call for performance
        fields_data = await browser.evaluate("""
        () => {
            const fields = [];
            let fieldIndex = 0;

            // Collect all form-interactive elements
            const elements = document.querySelectorAll(
                'input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="reset"]):not([type="image"]), ' +
                'textarea, select'
            );

            // Helper: find label for an element
            function findLabel(el) {
                // 1. <label for="id">
                if (el.id) {
                    const label = document.querySelector(`label[for="${el.id}"]`);
                    if (label) return { text: label.textContent.trim(), source: 'label_for' };
                }

                // 2. aria-label
                const ariaLabel = el.getAttribute('aria-label');
                if (ariaLabel) return { text: ariaLabel, source: 'aria_label' };

                // 3. aria-labelledby
                const ariaLabelledBy = el.getAttribute('aria-labelledby');
                if (ariaLabelledBy) {
                    const ref = document.getElementById(ariaLabelledBy);
                    if (ref) return { text: ref.textContent.trim(), source: 'aria_labelledby' };
                }

                // 4. Wrapping <label>
                const parentLabel = el.closest('label');
                if (parentLabel) {
                    // Get label text excluding the input's own text
                    const clone = parentLabel.cloneNode(true);
                    const inputs = clone.querySelectorAll('input, select, textarea');
                    inputs.forEach(i => i.remove());
                    const text = clone.textContent.trim();
                    if (text) return { text, source: 'wrapping_label' };
                }

                // 5. Placeholder
                const placeholder = el.getAttribute('placeholder');
                if (placeholder) return { text: placeholder, source: 'placeholder' };

                // 6. title attribute
                const title = el.getAttribute('title');
                if (title) return { text: title, source: 'title_attribute' };

                // 7. Nearest preceding text (sibling or parent)
                let prev = el.previousElementSibling;
                if (prev && (prev.tagName === 'LABEL' || prev.tagName === 'SPAN' || prev.tagName === 'P' || prev.tagName === 'DIV')) {
                    const text = prev.textContent.trim();
                    if (text && text.length < 200) return { text, source: 'nearby_text' };
                }

                // 8. name attribute (humanized)
                const name = el.getAttribute('name');
                if (name) return { text: name, source: 'name_attribute' };

                // 9. id attribute (humanized)
                if (el.id) return { text: el.id, source: 'id_attribute' };

                return { text: 'Unknown Field', source: 'unknown' };
            }

            // Helper: get options for select/radio/checkbox
            function getOptions(el, type) {
                const options = [];

                if (type === 'select') {
                    el.querySelectorAll('option').forEach(opt => {
                        if (opt.value || opt.textContent.trim()) {
                            options.push({
                                value: opt.value,
                                text: opt.textContent.trim(),
                                selected: opt.selected
                            });
                        }
                    });
                }

                return options;
            }

            // Track processed radio/checkbox groups
            const processedGroups = new Set();

            elements.forEach(el => {
                const tagName = el.tagName.toLowerCase();
                let type = el.getAttribute('type') || (tagName === 'textarea' ? 'textarea' : tagName === 'select' ? 'select' : 'text');
                type = type.toLowerCase();

                // Skip if hidden
                if (el.offsetParent === null && type !== 'hidden') return;

                // Group radio/checkbox by name
                if ((type === 'radio' || type === 'checkbox') && el.name) {
                    if (processedGroups.has(type + ':' + el.name)) return;
                    processedGroups.add(type + ':' + el.name);

                    // Collect all options in the group
                    const groupEls = document.querySelectorAll(`input[type="${type}"][name="${el.name}"]`);
                    const options = [];
                    groupEls.forEach(ge => {
                        const optLabel = findLabel(ge);
                        options.push({
                            value: ge.value,
                            text: optLabel.text || ge.value,
                            selected: ge.checked
                        });
                    });

                    // Find the group label (usually a parent element or preceding text)
                    let groupLabel = findLabel(el);
                    // Try fieldset legend
                    const fieldset = el.closest('fieldset');
                    if (fieldset) {
                        const legend = fieldset.querySelector('legend');
                        if (legend) groupLabel = { text: legend.textContent.trim(), source: 'nearby_text' };
                    }

                    const attrs = {};
                    for (const attr of el.attributes) attrs[attr.name] = attr.value;

                    fields.push({
                        field_id: 'field_' + String(fieldIndex++).padStart(3, '0'),
                        label: groupLabel.text,
                        label_source: groupLabel.source,
                        field_type: type,
                        placeholder: '',
                        required: el.required || el.getAttribute('aria-required') === 'true',
                        options: options,
                        locator_css: el.name ? `input[type="${type}"][name="${el.name}"]` : '',
                        visible: true,
                        enabled: !el.disabled,
                        current_value: null,
                        attributes: attrs,
                        validation: {
                            min_length: el.minLength > 0 ? el.minLength : null,
                            max_length: el.maxLength > 0 ? el.maxLength : null,
                            pattern: el.pattern || null,
                        }
                    });
                    return;
                }

                const label = findLabel(el);
                const attrs = {};
                for (const attr of el.attributes) attrs[attr.name] = attr.value;

                const options = getOptions(el, type);

                // Build CSS selector
                let locator = '';
                if (el.id) locator = '#' + CSS.escape(el.id);
                else if (el.name) locator = `${tagName}[name="${el.name}"]`;
                else locator = `${tagName}:nth-of-type(${fieldIndex + 1})`;

                fields.push({
                    field_id: 'field_' + String(fieldIndex++).padStart(3, '0'),
                    label: label.text,
                    label_source: label.source,
                    field_type: type === 'select' ? 'select' : type,
                    placeholder: el.placeholder || '',
                    required: el.required || el.getAttribute('aria-required') === 'true',
                    options: options,
                    locator_css: locator,
                    visible: el.offsetParent !== null,
                    enabled: !el.disabled,
                    current_value: el.value || null,
                    attributes: attrs,
                    validation: {
                        min_length: el.minLength > 0 ? el.minLength : null,
                        max_length: el.maxLength > 0 && el.maxLength < 524288 ? el.maxLength : null,
                        min_value: el.min ? parseFloat(el.min) : null,
                        max_value: el.max ? parseFloat(el.max) : null,
                        pattern: el.pattern || null,
                        step: el.step ? parseFloat(el.step) : null,
                    }
                });
            });

            return fields;
        }
        """)

        # Convert JS data to FormField objects
        form_fields: list[FormField] = []
        for data in fields_data:
            field_type = _INPUT_TYPE_MAP.get(data["field_type"], FieldType.UNKNOWN)
            if field_type == FieldType.UNKNOWN and data["field_type"] == "textarea":
                field_type = FieldType.TEXTAREA
            elif field_type == FieldType.UNKNOWN and data["field_type"] == "select":
                field_type = FieldType.SELECT

            label_text = data["label"]
            label_source_str = data.get("label_source", "unknown")

            # Humanize label if it came from name/id attributes
            if label_source_str in ("name_attribute", "id_attribute"):
                label_text = _humanize(label_text)

            try:
                label_source = LabelSource(label_source_str)
            except ValueError:
                label_source = LabelSource.UNKNOWN

            options = [
                FieldOption(
                    value=opt["value"],
                    text=opt["text"],
                    locator="",  # Will be set below
                    selected=opt.get("selected", False),
                )
                for opt in data.get("options", [])
            ]

            # Build option locators
            if field_type == FieldType.RADIO:
                name = data.get("attributes", {}).get("name", "")
                for opt in options:
                    opt.locator = f'input[type="radio"][name="{name}"][value="{opt.value}"]'
            elif field_type == FieldType.CHECKBOX:
                name = data.get("attributes", {}).get("name", "")
                for opt in options:
                    opt.locator = f'input[type="checkbox"][name="{name}"][value="{opt.value}"]'
            elif field_type == FieldType.SELECT:
                # Select options are selected via the <select> element itself
                for opt in options:
                    opt.locator = data["locator_css"]

            validation_data = data.get("validation", {})
            validation = FieldValidation(
                min_length=validation_data.get("min_length"),
                max_length=validation_data.get("max_length"),
                min_value=validation_data.get("min_value"),
                max_value=validation_data.get("max_value"),
                pattern=validation_data.get("pattern"),
                step=validation_data.get("step"),
            )

            form_field = FormField(
                field_id=data["field_id"],
                label=label_text,
                label_source=label_source,
                field_type=field_type,
                placeholder=data.get("placeholder", ""),
                required=data.get("required", False),
                options=options,
                validation=validation,
                locator=data["locator_css"],
                raw_attributes=data.get("attributes", {}),
                current_value=data.get("current_value"),
                is_disabled=not data.get("enabled", True),
                is_visible=data.get("visible", True),
            )
            form_fields.append(form_field)

        logger.info("fields_detected", count=len(form_fields))
        return form_fields

    async def get_form_title(self, browser: BrowserAdapter) -> str:
        """Extract form title from page title or h1."""
        title = await browser.evaluate("""
        () => {
            const h1 = document.querySelector('h1');
            if (h1) return h1.textContent.trim();
            const title = document.querySelector('title');
            if (title) return title.textContent.trim();
            return '';
        }
        """)
        return title or ""

    async def fill_field(
        self,
        browser: BrowserAdapter,
        field: FormField,
        value: Any,
    ) -> bool:
        """Fill a field using the appropriate method for its type."""
        try:
            if field.field_type.is_text_like or field.field_type == FieldType.DATE:
                await browser.fill(field.locator, str(value))
                return True

            elif field.field_type == FieldType.RADIO:
                # Find matching option and click it
                str_value = str(value).lower()
                for opt in field.options:
                    if opt.value.lower() == str_value or opt.text.lower() == str_value:
                        await browser.click(opt.locator)
                        return True
                return False

            elif field.field_type == FieldType.CHECKBOX:
                # Check matching options
                values = value if isinstance(value, list) else [value]
                checked = 0
                for val in values:
                    str_val = str(val).lower()
                    for opt in field.options:
                        if opt.value.lower() == str_val or opt.text.lower() == str_val:
                            await browser.check(opt.locator)
                            checked += 1
                            break
                return checked > 0

            elif field.field_type == FieldType.SELECT:
                await browser.select_option(field.locator, value=str(value))
                return True

            else:
                logger.warning("unsupported_field_type", field_type=field.field_type.value)
                return False

        except Exception as e:
            logger.error(
                "fill_field_error",
                field_id=field.field_id,
                field_type=field.field_type.value,
                error=str(e),
            )
            return False

    async def submit(self, browser: BrowserAdapter) -> bool:
        """Find and click the submit button."""
        submit_locator = await self.detect_submit_button(browser)
        if submit_locator:
            await browser.click(submit_locator)
            return True
        return False

    async def detect_captcha(self, browser: BrowserAdapter) -> bool:
        """Check for common CAPTCHA patterns."""
        captcha_selectors = [
            "iframe[src*='recaptcha']",
            "iframe[src*='captcha']",
            ".g-recaptcha",
            "#captcha",
            "[data-sitekey]",
            "iframe[src*='hcaptcha']",
            ".h-captcha",
        ]

        for selector in captcha_selectors:
            count = await browser.count_elements(selector)
            if count > 0:
                logger.warning("captcha_detected", selector=selector)
                return True

        return False

    async def detect_submit_button(self, browser: BrowserAdapter) -> str | None:
        """Find the submit button locator."""
        # Try various submit button patterns
        submit_selectors = [
            'input[type="submit"]',
            'button[type="submit"]',
            'button:has-text("Submit")',
            'button:has-text("Send")',
            'button:has-text("Gửi")',
            'input[type="button"][value="Submit"]',
        ]

        for selector in submit_selectors:
            count = await browser.count_elements(selector)
            if count > 0:
                return selector

        return None
