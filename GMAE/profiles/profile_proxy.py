"""Proxy around profile operations with simple local validation rules."""

from __future__ import annotations

from GMAE.profiles.player_profile import CharacterClass, CharacterProfile, PlayerProfile
from GMAE.profiles.profile_manager import ProfileManager


class ProfileProxy:
    def __init__(self, manager: ProfileManager) -> None:
        self._manager = manager

    def get_two_distinct_profiles(self, name_one: str, name_two: str) -> tuple[PlayerProfile, PlayerProfile]:
        left = self._normalize_name(name_one)
        right = self._normalize_name(name_two)
        if left == right:
            raise ValueError("Player names must be different for two local players.")

        return self._manager.get_or_create(left), self._manager.get_or_create(right)

    def save_profiles(self, profiles: list[PlayerProfile]) -> None:
        for profile in profiles:
            self._manager.save(profile)

    def add_character(
        self,
        profile: PlayerProfile,
        name: str,
        class_name: str,
        level: int = 1,
    ) -> CharacterProfile:
        normalized_name = self._normalize_name(name)
        character_class = CharacterClass.parse(class_name)
        if level < 1:
            raise ValueError("Character level must be at least 1.")
        created = profile.create_character(
            name=normalized_name,
            character_class=character_class,
            level=level,
        )
        self._manager.save(profile)
        return created

    def select_character(self, profile: PlayerProfile, character_id: int) -> None:
        if not profile.select_character(character_id):
            raise ValueError("Character id was not found in this profile.")
        self._manager.save(profile)

    @staticmethod
    def _normalize_name(raw: str) -> str:
        cleaned = " ".join(raw.strip().split())
        if not cleaned:
            raise ValueError("Player name cannot be blank.")
        return cleaned[:24]
