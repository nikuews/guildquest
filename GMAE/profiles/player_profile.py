"""Player profile and character models.

This module adapts the core behavior from the original Java domain model:
- user profile owns multiple characters
- each character has name, class, level
- selected character can be switched
- quest records may include participating characters
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class CharacterClass(str, Enum):
    WARRIOR = "WARRIOR"
    ASSASSIN = "ASSASSIN"
    MAGE = "MAGE"

    @classmethod
    def parse(cls, raw: str | None) -> "CharacterClass":
        if raw is None:
            return cls.WARRIOR
        token = raw.strip().upper()
        # Accept common misspelling and safely downgrade removed legacy classes.
        if token == "ASSASIN":
            token = "ASSASSIN"
        if token in {"RANGER", "PRIEST"}:
            token = "WARRIOR"
        if token not in cls.__members__:
            raise ValueError("Unsupported character class. Use WARRIOR, ASSASSIN, or MAGE.")
        return cls[token]


@dataclass
class CharacterProfile:
    character_id: int
    name: str
    character_class: CharacterClass = CharacterClass.WARRIOR
    level: int = 1
    inventory_item_names: list[str] = field(default_factory=list)

    def add_item(self, item_name: str) -> None:
        self.inventory_item_names.append(item_name)

    def remove_item(self, item_name: str) -> bool:
        if item_name not in self.inventory_item_names:
            return False
        self.inventory_item_names.remove(item_name)
        return True

    def update_item(self, old_name: str, new_name: str) -> bool:
        try:
            index = self.inventory_item_names.index(old_name)
        except ValueError:
            return False
        self.inventory_item_names[index] = new_name
        return True

    def to_dict(self) -> dict:
        return {
            "character_id": self.character_id,
            "name": self.name,
            "character_class": self.character_class.value,
            "level": self.level,
            "inventory_item_names": list(self.inventory_item_names),
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "CharacterProfile":
        return cls(
            character_id=int(payload.get("character_id", 0)),
            name=str(payload.get("name", "Adventurer")),
            character_class=CharacterClass.parse(payload.get("character_class")),
            level=max(1, int(payload.get("level", 1))),
            inventory_item_names=list(payload.get("inventory_item_names", [])),
        )


@dataclass
class PlayerProfile:
    user_id: int
    username: str
    preferred_realm: str = "Starter Plains"
    characters: list[CharacterProfile] = field(default_factory=list)
    selected_character_id: int | None = None
    quest_history: list[str] = field(default_factory=list)
    achievements: list[str] = field(default_factory=list)
    sessions_played: int = 0
    _next_character_id: int = 1

    @property
    def selected_character(self) -> CharacterProfile | None:
        if self.selected_character_id is None:
            return None
        return self.find_character(self.selected_character_id)

    @property
    def character_name(self) -> str:
        selected = self.selected_character
        return selected.name if selected is not None else self.username

    def create_character(
        self,
        name: str,
        character_class: CharacterClass = CharacterClass.WARRIOR,
        level: int = 1,
    ) -> CharacterProfile:
        created = CharacterProfile(
            character_id=self._next_character_id,
            name=name,
            character_class=character_class,
            level=max(1, level),
        )
        self._next_character_id += 1
        self.characters.append(created)
        if self.selected_character_id is None:
            self.selected_character_id = created.character_id
        return created

    def remove_character(self, character_id: int) -> bool:
        character = self.find_character(character_id)
        if character is None:
            return False
        self.characters = [item for item in self.characters if item.character_id != character_id]
        if self.selected_character_id == character_id:
            self.selected_character_id = self.characters[0].character_id if self.characters else None
        return True

    def select_character(self, character_id: int) -> bool:
        if self.find_character(character_id) is None:
            return False
        self.selected_character_id = character_id
        return True

    def find_character(self, character_id: int) -> CharacterProfile | None:
        for character in self.characters:
            if character.character_id == character_id:
                return character
        return None

    def record_quest_event(
        self,
        title: str,
        participating_character_ids: Iterable[int] | None = None,
        granted_items_by_character: dict[int, list[str]] | None = None,
        removed_items_by_character: dict[int, list[str]] | None = None,
    ) -> None:
        participant_ids = sorted(set(participating_character_ids or []))
        if participant_ids:
            participant_names = []
            for char_id in participant_ids:
                character = self.find_character(char_id)
                if character is not None:
                    participant_names.append(character.name)
            participants_label = ", ".join(participant_names) if participant_names else "unknown"
            self.quest_history.append(f"{title} (participants: {participants_label})")
        else:
            self.quest_history.append(title)

        for char_id, item_names in (granted_items_by_character or {}).items():
            character = self.find_character(char_id)
            if character is None:
                continue
            for item_name in item_names:
                character.add_item(item_name)

        for char_id, item_names in (removed_items_by_character or {}).items():
            character = self.find_character(char_id)
            if character is None:
                continue
            for item_name in item_names:
                character.remove_item(item_name)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "preferred_realm": self.preferred_realm,
            "characters": [character.to_dict() for character in self.characters],
            "selected_character_id": self.selected_character_id,
            "quest_history": list(self.quest_history),
            "achievements": list(self.achievements),
            "sessions_played": self.sessions_played,
            "_next_character_id": self._next_character_id,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "PlayerProfile":
        characters_payload = payload.get("characters")
        # Backward compatibility for the original simple profile format.
        if characters_payload is None:
            legacy_name = str(payload.get("character_name", payload.get("username", "Adventurer")))
            legacy_inventory = list(payload.get("inventory_snapshot", []))
            legacy_character = CharacterProfile(
                character_id=1,
                name=legacy_name,
                character_class=CharacterClass.WARRIOR,
                level=1,
                inventory_item_names=legacy_inventory,
            )
            characters = [legacy_character]
            selected_character_id = 1
            next_character_id = 2
        else:
            characters = [CharacterProfile.from_dict(item) for item in characters_payload]
            selected_character_id = payload.get("selected_character_id")
            if selected_character_id is not None:
                selected_character_id = int(selected_character_id)
            default_next = max((character.character_id for character in characters), default=0) + 1
            next_character_id = int(payload.get("_next_character_id", default_next))

        profile = cls(
            user_id=int(payload.get("user_id", 0)),
            username=str(payload.get("username", payload.get("character_name", "Adventurer"))),
            preferred_realm=str(payload.get("preferred_realm", "Starter Plains")),
            characters=characters,
            selected_character_id=selected_character_id,
            quest_history=list(payload.get("quest_history", [])),
            achievements=list(payload.get("achievements", [])),
            sessions_played=int(payload.get("sessions_played", 0)),
            _next_character_id=max(1, next_character_id),
        )

        if profile.characters and profile.selected_character_id is None:
            profile.selected_character_id = profile.characters[0].character_id
        return profile
