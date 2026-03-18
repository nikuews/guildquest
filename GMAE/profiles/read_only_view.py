from __future__ import annotations

from typing import Any

from GMAE.profiles.player_profile import CharacterClass, PlayerProfile


class ReadOnlyProfileView:

    def __init__(self, profile: PlayerProfile) -> None:
        # Name-mangled so adventure code cannot easily reach the real profile
        object.__setattr__(self, "_ReadOnlyProfileView__profile", profile)

    # ── Read-only properties (delegated to real profile) ───────────

    @property
    def user_id(self) -> int:
        return self.__profile.user_id

    @property
    def username(self) -> str:
        return self.__profile.username

    @property
    def character_name(self) -> str:
        return self.__profile.character_name

    @property
    def character_class(self) -> CharacterClass:
        selected = self.__profile.selected_character
        if selected is None:
            return CharacterClass.WARRIOR
        return selected.character_class

    @property
    def character_level(self) -> int:
        selected = self.__profile.selected_character
        if selected is None:
            return 1
        return selected.level

    @property
    def preferred_realm(self) -> str:
        return self.__profile.preferred_realm

    @property
    def sessions_played(self) -> int:
        return self.__profile.sessions_played

    @property
    def achievement_count(self) -> int:
        return len(self.__profile.achievements)

    @property
    def quest_count(self) -> int:
        return len(self.__profile.quest_history)

    @property
    def inventory_snapshot(self) -> list[str]:
        """Copy of selected character's inventory (adventures cannot modify original)."""
        selected = self.__profile.selected_character
        if selected is None:
            return []
        return list(selected.inventory_item_names)

    # ── Blocked write operations ───────────────────────────────────

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError(
            f"Cannot modify '{name}' on a read-only profile view. "
            f"Adventures are not allowed to write to player profiles. "
            f"Profile updates are handled by the GMAE engine after the adventure ends."
        )

    def __delattr__(self, name: str) -> None:
        raise AttributeError(
            f"Cannot delete '{name}' on a read-only profile view."
        )

    # ── Display ────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"ReadOnlyProfileView(username={self.username!r}, "
            f"character={self.character_name!r}, "
            f"class={self.character_class.value}, "
            f"level={self.character_level})"
        )

    def __str__(self) -> str:
        return f"{self.character_name} ({self.character_class.value} Lv{self.character_level})"