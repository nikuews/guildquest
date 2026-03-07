"""Player profile data model."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class PlayerProfile:
    character_name: str
    preferred_realm: str = "Starter Plains"
    inventory_snapshot: list[str] = field(default_factory=list)
    quest_history: list[str] = field(default_factory=list)
    achievements: list[str] = field(default_factory=list)
    sessions_played: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict) -> "PlayerProfile":
        return cls(
            character_name=payload.get("character_name", "Adventurer"),
            preferred_realm=payload.get("preferred_realm", "Starter Plains"),
            inventory_snapshot=list(payload.get("inventory_snapshot", [])),
            quest_history=list(payload.get("quest_history", [])),
            achievements=list(payload.get("achievements", [])),
            sessions_played=int(payload.get("sessions_played", 0)),
        )
