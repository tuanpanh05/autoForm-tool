"""Configuration manager for AutoForm."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


# =============================================================================
# Default Configuration
# =============================================================================

_DEFAULTS: dict[str, Any] = {
    "general": {
        "app_name": "AutoForm",
        "data_dir": "~/.autoform",
    },
    "browser": {
        "type": "chromium",
        "headless": False,
        "timeout_ms": 30000,
        "viewport_width": 1280,
        "viewport_height": 720,
    },
    "automation": {
        "min_field_delay_ms": 100,
        "max_field_delay_ms": 300,
        "min_click_delay_ms": 200,
        "max_click_delay_ms": 500,
        "submit_delay_ms": 1000,
        "max_retries": 2,
        "retry_delay_ms": 500,
    },
    "confidence": {
        "high_threshold": 0.85,
        "medium_threshold": 0.60,
        "low_threshold": 0.30,
    },
    "mapping": {
        "enable_rules": True,
        "enable_fuzzy": True,
        "enable_embedding": False,
        "enable_llm": False,
        "fuzzy_min_score": 60,
    },
    "profile": {
        "storage_format": "json",
        "default_profile": "default",
    },
    "logging": {
        "level": "INFO",
        "format": "console",
        "log_dir": "~/.autoform/logs",
        "redact_pii": True,
        "max_log_files": 7,
    },
    "cache": {
        "enabled": True,
        "cache_dir": "~/.autoform/cache",
        "ttl_hours": 24,
    },
    "ai": {
        "enabled": False,
        "provider": "local",
        "send_labels": True,
        "send_field_types": True,
        "send_profile_paths": True,
        "send_values": False,
        "send_url": False,
    },
}


class Config:
    """
    Application configuration manager.

    Loads configuration from TOML file and environment variables.
    Environment variables override TOML values.
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
        """
        Initialize configuration.

        Args:
            config_path: Path to TOML config file. If None, uses defaults only.
        """
        # Load .env file
        load_dotenv()

        # Start with defaults
        self._config: dict[str, Any] = _DEFAULTS.copy()

        # Load TOML config if provided
        if config_path:
            self._load_toml(Path(config_path))

        # Apply environment variable overrides
        self._apply_env_overrides()

    def _load_toml(self, path: Path) -> None:
        """Load configuration from TOML file."""
        if not path.exists():
            return

        try:
            import tomllib
        except ImportError:
            import tomli as tomllib  # type: ignore[import-not-found,no-redef]

        with open(path, "rb") as f:
            toml_config = tomllib.load(f)

        # Deep merge TOML config into defaults
        self._deep_merge(self._config, toml_config)

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        env_mappings = {
            "LOG_LEVEL": ("logging", "level"),
            "BROWSER_HEADLESS": ("browser", "headless"),
            "BROWSER_TYPE": ("browser", "type"),
        }

        for env_var, (section, key) in env_mappings.items():
            env_val = os.getenv(env_var)
            if env_val is not None:
                parsed_val: Any = env_val
                # Type conversion
                if env_val.lower() in ("true", "false"):
                    parsed_val = env_val.lower() == "true"
                if section in self._config:
                    self._config[section][key] = parsed_val

    @staticmethod
    def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deep merge override dict into base dict."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                Config._deep_merge(base[key], value)
            else:
                base[key] = value
        return base

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            section: Config section (e.g., 'browser', 'mapping').
            key: Config key within section.
            default: Default value if not found.

        Returns:
            The configuration value.
        """
        return self._config.get(section, {}).get(key, default)

    def get_section(self, section: str) -> dict[str, Any]:
        """Get an entire configuration section."""
        sec = self._config.get(section, {})
        return dict(sec) if isinstance(sec, dict) else {}

    # =========================================================================
    # Convenience Properties
    # =========================================================================

    @property
    def data_dir(self) -> Path:
        """Application data directory (expanded)."""
        return Path(str(self.get("general", "data_dir", "~/.autoform"))).expanduser()

    @property
    def profile_dir(self) -> Path:
        """Profile storage directory."""
        return self.data_dir / "profiles"

    @property
    def cache_dir(self) -> Path:
        """Cache directory."""
        return Path(str(self.get("cache", "cache_dir", "~/.autoform/cache"))).expanduser()

    @property
    def log_dir(self) -> Path:
        """Log directory."""
        return Path(str(self.get("logging", "log_dir", "~/.autoform/logs"))).expanduser()

    @property
    def browser_type(self) -> str:
        """Browser type (chromium, firefox, webkit)."""
        return str(self.get("browser", "type", "chromium"))

    @property
    def browser_headless(self) -> bool:
        """Whether to run browser in headless mode."""
        return bool(self.get("browser", "headless", False))

    @property
    def browser_timeout(self) -> int:
        """Browser default timeout in milliseconds."""
        return int(self.get("browser", "timeout_ms", 30000))

    @property
    def high_confidence_threshold(self) -> float:
        """Confidence threshold for HIGH classification."""
        return float(self.get("confidence", "high_threshold", 0.85))

    @property
    def medium_confidence_threshold(self) -> float:
        """Confidence threshold for MEDIUM classification."""
        return float(self.get("confidence", "medium_threshold", 0.60))

    @property
    def low_confidence_threshold(self) -> float:
        """Confidence threshold for LOW classification."""
        return float(self.get("confidence", "low_threshold", 0.30))

    @property
    def openai_api_key(self) -> str | None:
        """OpenAI API key from environment."""
        return os.getenv("OPENAI_API_KEY") or None

    @property
    def anthropic_api_key(self) -> str | None:
        """Anthropic API key from environment."""
        return os.getenv("ANTHROPIC_API_KEY") or None

    @property
    def log_level(self) -> str:
        """Logging level."""
        return str(self.get("logging", "level", "INFO"))

    @property
    def log_format(self) -> str:
        """Logging format (console or json)."""
        return str(self.get("logging", "format", "console"))

    @property
    def redact_pii(self) -> bool:
        """Whether to redact PII from logs."""
        return bool(self.get("logging", "redact_pii", True))

