"""User profile manager for AutoForm."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from autoform.domain.exceptions import ProfileNotFoundError, ProfileValidationError
from autoform.domain.models import UserProfile
from autoform.infrastructure.logging import get_logger
from autoform.profile.storage import ProfileStorage

logger = get_logger("profile.manager")


# Default profile schema with descriptions for interactive creation
PROFILE_SCHEMA: dict[str, dict[str, str]] = {
    "personal": {
        "full_name": "Full name",
        "first_name": "First name",
        "last_name": "Last name",
        "date_of_birth": "Date of birth (YYYY-MM-DD)",
        "gender": "Gender",
    },
    "contact": {
        "email": "Email address",
        "phone": "Phone number",
        "address": "Street address",
        "city": "City",
        "country": "Country",
    },
    "education": {
        "university": "University/College",
        "major": "Major/Field of study",
        "gpa": "GPA",
        "graduation_year": "Graduation year",
    },
    "work": {
        "company": "Company/Organization",
        "position": "Position/Job title",
        "years_of_experience": "Years of experience",
    },
    "skills": {
        "programming_languages": "Programming languages (comma-separated)",
        "tools": "Tools & Technologies (comma-separated)",
    },
}


class ProfileManager:
    """
    High-level manager for user profile operations.

    Handles profile creation, editing, validation, and storage.
    """

    def __init__(self, storage: ProfileStorage) -> None:
        self._storage = storage

    @property
    def storage(self) -> ProfileStorage:
        """Access the underlying storage."""
        return self._storage

    def create_profile(
        self,
        data: dict[str, Any],
        profile_name: str = "default",
    ) -> UserProfile:
        """
        Create a new profile from a data dictionary.

        Args:
            data: Profile data dict with categories as keys.
            profile_name: Name for the profile.

        Returns:
            The created UserProfile.
        """
        profile = UserProfile.from_dict(data)
        self._storage.save(profile, profile_name)
        logger.info("profile_created", profile_name=profile_name)
        return profile

    def get_profile(self, profile_name: str = "default") -> UserProfile:
        """
        Get a profile by name.

        Args:
            profile_name: Profile to load.

        Returns:
            The loaded UserProfile.

        Raises:
            ProfileNotFoundError: If profile doesn't exist.
        """
        return self._storage.load(profile_name)

    def update_field(
        self,
        profile_name: str,
        field_path: str,
        value: Any,
    ) -> UserProfile:
        """
        Update a single field in a profile.

        Args:
            profile_name: Profile to update.
            field_path: Dot-path to the field (e.g., 'personal.full_name').
            value: New value.

        Returns:
            The updated profile.
        """
        profile = self._storage.load(profile_name)
        profile.set_field(field_path, value)
        self._storage.save(profile, profile_name)
        logger.info("profile_field_updated", profile_name=profile_name, field=field_path)
        return profile

    def update_category(
        self,
        profile_name: str,
        category: str,
        data: dict[str, Any],
    ) -> UserProfile:
        """
        Update an entire category in a profile.

        Args:
            profile_name: Profile to update.
            category: Category name (e.g., 'personal', 'contact').
            data: New data for the category.

        Returns:
            The updated profile.
        """
        profile = self._storage.load(profile_name)

        if not hasattr(profile, category):
            raise ProfileValidationError(f"Unknown category: '{category}'")

        current_data = getattr(profile, category)
        if isinstance(current_data, dict):
            current_data.update(data)
        else:
            setattr(profile, category, data)

        self._storage.save(profile, profile_name)
        logger.info("profile_category_updated", profile_name=profile_name, category=category)
        return profile

    def delete_profile(self, profile_name: str) -> None:
        """Delete a profile."""
        self._storage.delete(profile_name)

    def list_profiles(self) -> list[str]:
        """List all available profiles."""
        return self._storage.list_profiles()

    def profile_exists(self, profile_name: str = "default") -> bool:
        """Check if a profile exists."""
        return self._storage.exists(profile_name)

    def get_profile_summary(self, profile_name: str = "default") -> dict[str, int]:
        """
        Get a summary of profile completeness.

        Returns a dict of {category: number_of_fields_filled}.
        """
        profile = self._storage.load(profile_name)
        summary: dict[str, int] = {}

        for category in profile.get_categories():
            category_data = getattr(profile, category, {})
            if isinstance(category_data, dict):
                filled = sum(1 for v in category_data.values() if v)
                summary[category] = filled

        return summary

    def create_empty_profile(self, profile_name: str = "default") -> UserProfile:
        """
        Create an empty profile with default structure.

        Args:
            profile_name: Name for the profile.

        Returns:
            The created empty UserProfile.
        """
        profile = UserProfile()
        self._storage.save(profile, profile_name)
        logger.info("empty_profile_created", profile_name=profile_name)
        return profile

    @staticmethod
    def get_schema() -> dict[str, dict[str, str]]:
        """Get the default profile schema with field descriptions."""
        return PROFILE_SCHEMA
