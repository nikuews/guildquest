"""Quest event model with optional character participation metadata."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Quest:
    title: str
    completed: bool = False
    participating_character_ids: list[int] = field(default_factory=list)
