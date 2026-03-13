"""Simple GuildQuest inventory model reused by adventures and profiles."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Inventory:
    items: list[str] = field(default_factory=list)

    def add(self, item: str) -> None:
        self.items.append(item)

    def remove(self, item: str) -> bool:
        if item not in self.items:
            return False
        self.items.remove(item)
        return True
