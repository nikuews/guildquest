"""Common mini-adventure interface for all GMAE adventures."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MiniAdventure(ABC):
    """Defined interface required by all mini-adventures."""

    adventure_id: str = "base"
    name: str = "Base Adventure"
    mode: str = "Unknown"
    description: str = ""

    @abstractmethod
    def start(self, player_names: list[str]) -> None:
        """Initialize an adventure session for exactly two local players."""

    @abstractmethod
    def get_state(self) -> dict[str, Any]:
        """Return serializable state for rendering."""

    @abstractmethod
    def get_actions_for_player(self, player_index: int) -> list[str]:
        """Return allowed action labels for the active player."""

    @abstractmethod
    def submit_action(self, player_index: int, action: str) -> None:
        """Accept one action from the active player and advance the session."""

    @abstractmethod
    def is_complete(self) -> bool:
        """Return whether adventure has reached a terminal condition."""

    @abstractmethod
    def get_outcome(self) -> dict[str, Any]:
        """Return completion result for summary output."""

    @abstractmethod
    def reset(self) -> None:
        """Reset internal state so the adventure can be replayed."""
