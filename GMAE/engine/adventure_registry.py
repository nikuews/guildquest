"""Adventure registration and lookup."""

from __future__ import annotations

from dataclasses import dataclass

from GMAE.adventures.base_adventure import MiniAdventure
from GMAE.adventures.relic_hunt.relic_hunt import RelicHuntAdventure
from GMAE.adventures.timed_raid.timed_raid import TimedRaidAdventure


@dataclass(frozen=True)
class AdventureInfo:
    index: int
    title: str
    mode: str
    description: str


class AdventureRegistry:
    def __init__(self) -> None:
        self._adventure_types: list[type[MiniAdventure]] = [
            RelicHuntAdventure,
            TimedRaidAdventure,
        ]

    def list_adventures(self) -> list[AdventureInfo]:
        items: list[AdventureInfo] = []
        for idx, adventure_type in enumerate(self._adventure_types, start=1):
            items.append(
                AdventureInfo(
                    index=idx,
                    title=adventure_type.name,
                    mode=adventure_type.mode,
                    description=adventure_type.description,
                )
            )
        return items

    def create_by_index(self, index: int) -> MiniAdventure:
        if index < 1 or index > len(self._adventure_types):
            raise ValueError("Invalid adventure choice.")
        return self._adventure_types[index - 1]()
