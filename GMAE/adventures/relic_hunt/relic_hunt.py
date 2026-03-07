"""Relic Hunt adventure (interface-first placeholder behavior)."""

from __future__ import annotations

from typing import Any

from GMAE.adventures.base_adventure import MiniAdventure
from GMAE.adventures.relic_hunt.maps import RELIC_HUNT_BOARD, RELIC_HUNT_LEGEND


class RelicHuntAdventure(MiniAdventure):
    adventure_id = "relic_hunt"
    name = "Relic Hunt"
    mode = "Competitive"
    description = "Collect relics before your opponent."

    def __init__(self) -> None:
        self.reset()

    def start(self, player_names: list[str]) -> None:
        if len(player_names) != 2:
            raise ValueError("Relic Hunt requires exactly two local players.")

        self._players = player_names
        self._scores = {player_names[0]: 0, player_names[1]: 0}
        self._turn = 1
        self._active_player = 0
        self._complete = False
        self._winner: str | None = None
        self._last_message = "Adventure started."

    def get_state(self) -> dict[str, Any]:
        return {
            "adventure_title": self.name,
            "mode": self.mode,
            "turn": self._turn,
            "scoreboard": [
                {"name": self._players[0], "value": f"{self._scores[self._players[0]]} relics"},
                {"name": self._players[1], "value": f"{self._scores[self._players[1]]} relics"},
            ],
            "board_lines": RELIC_HUNT_BOARD,
            "legend": RELIC_HUNT_LEGEND,
            "active_player_index": self._active_player,
            "status_line": self._last_message,
        }

    def get_actions_for_player(self, player_index: int) -> list[str]:
        if player_index != self._active_player:
            return []
        return [
            "move N",
            "move S",
            "move E",
            "move W",
            "pickup",
            "use item",
            "quit",
        ]

    def submit_action(self, player_index: int, action: str) -> None:
        if self._complete:
            return
        if player_index != self._active_player:
            self._last_message = "Not your turn."
            return

        actor = self._players[player_index]
        normalized = action.strip().lower()

        if normalized == "quit":
            self._complete = True
            self._winner = self._players[1 - player_index]
            self._last_message = f"{actor} quit the run."
            return

        if normalized == "pickup":
            self._scores[actor] += 1
            self._last_message = f"{actor} picked up a relic."
        elif normalized.startswith("move"):
            self._last_message = f"{actor} moved ({normalized.split()[-1].upper()})."
        elif normalized == "use item":
            self._last_message = f"{actor} used an item (placeholder effect)."
        else:
            self._last_message = f"{actor} performed '{action}' (placeholder)."

        if self._scores[actor] >= 3:
            self._complete = True
            self._winner = actor
            return

        self._active_player = 1 - self._active_player
        self._turn += 1
        if self._turn > 12:
            self._complete = True
            p1, p2 = self._players
            if self._scores[p1] == self._scores[p2]:
                self._winner = None
            else:
                self._winner = p1 if self._scores[p1] > self._scores[p2] else p2

    def is_complete(self) -> bool:
        return self._complete

    def get_outcome(self) -> dict[str, Any]:
        if self._winner is None:
            summary = "Relic Hunt ended in a draw."
        else:
            summary = f"{self._winner} wins Relic Hunt."

        return {
            "title": self.name,
            "summary": summary,
            "scores": self._scores.copy(),
        }

    def reset(self) -> None:
        self._players = ["Player 1", "Player 2"]
        self._scores = {"Player 1": 0, "Player 2": 0}
        self._turn = 1
        self._active_player = 0
        self._complete = False
        self._winner = None
        self._last_message = "Ready."
