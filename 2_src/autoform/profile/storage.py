"""User profile storage for AutoForm."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from autoform.domain.exceptions import ProfileNotFoundError, ProfileValidationError
from autoform.domain.models import UserProfile
from autoform.infrastructure.logging import get_logger

logger = get_logger("profile.storage")


class ProfileStorage:
    """
    JSON file-based profile storage.

    Stores user profiles as JSON files in the profile directory.
    Each profile is a separate file: {profile_name}.json

    MVP: Plain JSON files.
    v1.1: Encrypted JSON using Fernet + OS keyring.
    """

    def __init__(self, profile_dir: Path | str) -> None:
        self._profile_dir = Path(profile_dir).expanduser()
        self._profile_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, profile_name: str) -> Path:
        """Get the file path for a profile."""
        # Sanitize profile name
        safe_name = "".join(c for c in profile_name if c.isalnum() or c in ("_", "-"))
        if not safe_name:
            raise ProfileValidationError(f"Invalid profile name: '{profile_name}'")
        return self._profile_dir / f"{safe_name}.json"

    def save(self, profile: UserProfile, profile_name: str = "default") -> Path:
        """
        Save a profile to a JSON file.

        Args:
            profile: The user profile to save.
            profile_name: Name for the profile file.

        Returns:
            Path to the saved file.
        """
        path = self._get_path(profile_name)
        data = profile.to_dict()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info("profile_saved", profile_name=profile_name, path=str(path))
        return path

    def load(self, profile_name: str = "default") -> UserProfile:
        """
        Load a profile from a JSON file.

        Args:
            profile_name: Name of the profile to load.

        Returns:
            The loaded user profile.

        Raises:
            ProfileNotFoundError: If the profile file doesn't exist.
        """
        path = self._get_path(profile_name)

        if not path.exists():
            raise ProfileNotFoundError(profile_name)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info("profile_loaded", profile_name=profile_name)
        return UserProfile.from_dict(data)

    def delete(self, profile_name: str) -> None:
        """
        Delete a profile file.

        Args:
            profile_name: Name of the profile to delete.

        Raises:
            ProfileNotFoundError: If the profile doesn't exist.
        """
        path = self._get_path(profile_name)

        if not path.exists():
            raise ProfileNotFoundError(profile_name)

        path.unlink()
        logger.info("profile_deleted", profile_name=profile_name)

    def exists(self, profile_name: str = "default") -> bool:
        """Check if a profile exists."""
        return self._get_path(profile_name).exists()

    def list_profiles(self) -> list[str]:
        """List all available profile names."""
        profiles = []
        for path in self._profile_dir.glob("*.json"):
            profiles.append(path.stem)
        return sorted(profiles)

    def export_profile(self, profile_name: str, export_path: Path | str) -> Path:
        """Export a profile to a specific path."""
        profile = self.load(profile_name)
        export_path = Path(export_path)

        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info("profile_exported", profile_name=profile_name, path=str(export_path))
        return export_path

    def import_profile(self, import_path: Path | str, profile_name: str = "imported") -> UserProfile:
        """Import a profile from a JSON file."""
        import_path = Path(import_path)

        if not import_path.exists():
            raise FileNotFoundError(f"Import file not found: {import_path}")

        with open(import_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        profile = UserProfile.from_dict(data)
        self.save(profile, profile_name)
        logger.info("profile_imported", profile_name=profile_name, source=str(import_path))
        return profile
