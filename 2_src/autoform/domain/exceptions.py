"""Domain exceptions for AutoForm."""


class AutoFormError(Exception):
    """Base exception for all AutoForm errors."""

    pass


# =============================================================================
# Browser Errors
# =============================================================================


class BrowserError(AutoFormError):
    """Base error for browser-related issues."""

    pass


class BrowserLaunchError(BrowserError):
    """Failed to launch browser."""

    pass


class BrowserNavigationError(BrowserError):
    """Failed to navigate to URL."""

    pass


class BrowserTimeoutError(BrowserError):
    """Browser operation timed out."""

    pass


class ElementNotFoundError(BrowserError):
    """Element not found on the page."""

    def __init__(self, locator: str, message: str = ""):
        self.locator = locator
        super().__init__(message or f"Element not found: {locator}")


class ElementNotInteractableError(BrowserError):
    """Element found but not interactable (hidden, disabled, covered)."""

    def __init__(self, locator: str, message: str = ""):
        self.locator = locator
        super().__init__(message or f"Element not interactable: {locator}")


# =============================================================================
# Form Analysis Errors
# =============================================================================


class FormAnalysisError(AutoFormError):
    """Base error for form analysis issues."""

    pass


class NoFieldsDetectedError(FormAnalysisError):
    """No form fields were detected on the page."""

    pass


class UnsupportedPlatformError(FormAnalysisError):
    """The form platform is not supported."""

    def __init__(self, url: str, message: str = ""):
        self.url = url
        super().__init__(message or f"Unsupported form platform for URL: {url}")


# =============================================================================
# Mapping Errors
# =============================================================================


class MappingError(AutoFormError):
    """Base error for field mapping issues."""

    pass


class NoMappingFoundError(MappingError):
    """No mapping could be found for a field."""

    def __init__(self, field_label: str, message: str = ""):
        self.field_label = field_label
        super().__init__(message or f"No mapping found for: {field_label}")


# =============================================================================
# Autofill Errors
# =============================================================================


class FillError(AutoFormError):
    """Base error for autofill issues."""

    pass


class FillVerificationError(FillError):
    """Filled value doesn't match the expected value."""

    def __init__(self, field_id: str, expected: str, actual: str):
        self.field_id = field_id
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"Fill verification failed for {field_id}: expected '{expected}', got '{actual}'"
        )


class SafetyCheckError(FillError):
    """A safety check prevented the fill operation."""

    pass


class CaptchaDetectedError(FillError):
    """CAPTCHA was detected on the form."""

    def __init__(self, message: str = ""):
        super().__init__(message or "CAPTCHA detected. Please solve it manually.")


# =============================================================================
# Profile Errors
# =============================================================================


class ProfileError(AutoFormError):
    """Base error for profile-related issues."""

    pass


class ProfileNotFoundError(ProfileError):
    """Profile file not found."""

    def __init__(self, profile_name: str, message: str = ""):
        self.profile_name = profile_name
        super().__init__(message or f"Profile not found: {profile_name}")


class ProfileValidationError(ProfileError):
    """Profile data validation failed."""

    pass


# =============================================================================
# Configuration Errors
# =============================================================================


class ConfigError(AutoFormError):
    """Configuration-related error."""

    pass
