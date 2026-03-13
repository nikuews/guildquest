"""Timed Raid adventure (interface-first placeholder behavior)."""

from __future__ import annotations

from typing import Any

from GMAE.adventures.base_adventure import MiniAdventure
from GMAE.adventures.timed_raid.objectives import RaidObjective, build_default_objectives
from GMAE.display.world_clock import WorldClock


clock = WorldClock()

class TimedRaidAdventure(MiniAdventure):
    adventure_id = "timed_raid"
    name = "Timed Raid Window"
    mode = "Co-op"
    description = "Complete shared objectives before time expires."

    def __init__(self) -> None:
        clock.increment_time(30)
        self.reset()

    def start(self, player_names: list[str]) -> None:
        if len(player_names) != 2:
            raise ValueError("Timed Raid requires exactly two local players.")

        self._players = player_names
        self._turn = 1
        self._active_player = 0
        self._time_remaining = 8
        self._objectives: list[RaidObjective] = build_default_objectives()
        self._complete = False
        self._success = False
        self._last_message = "Raid window opened."

    def get_state(self) -> dict[str, Any]:
        objective_lines = []
        for objective in self._objectives:
            marker = "[x]" if objective.complete else "[ ]"
            objective_lines.append(f"{marker} {objective.name}")

        return {
            "adventure_title": self.name,
            "mode": self.mode,
            "turn": self._turn,
            "scoreboard": [
                {"name": "Window", "value": f"{self._time_remaining} turns left"},
                {
                    "name": "Progress",
                    "value": f"{sum(o.complete for o in self._objectives)}/{len(self._objectives)} objectives",
                },
            ],
            "board_lines": [
                ". . . # . .",
                ". P . . H .",
                ". . . . . .",
                "# . O . . .",
                ". . . . E .",
            ],
            "legend": "P=Player 1  E=Player 2  O=Objective Node  H=Hazard  #=Obstacle",
            "objective_lines": objective_lines,
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
            "interact",
            "complete objective",
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
            self._success = False
            self._last_message = f"{actor} aborted the raid."
            return

        if normalized == "complete objective":
            next_open = next((obj for obj in self._objectives if not obj.complete), None)
            if next_open is not None:
                next_open.complete = True
                self._last_message = f"{actor} completed objective: {next_open.name}."
            else:
                self._last_message = "All objectives already complete."
        elif normalized == "interact":
            self._last_message = f"{actor} interacted with the environment."
        elif normalized.startswith("move"):
            self._last_message = f"{actor} moved ({normalized.split()[-1].upper()})."
        elif normalized == "use item":
            self._last_message = f"{actor} used an item (placeholder effect)."
        else:
            self._last_message = f"{actor} performed '{action}' (placeholder)."

        all_done = all(objective.complete for objective in self._objectives)
        if all_done:
            self._complete = True
            self._success = True
            return

        self._time_remaining -= 1
        self._active_player = 1 - self._active_player
        self._turn += 1
        if self._time_remaining <= 0:
            self._complete = True
            self._success = False

    def is_complete(self) -> bool:
        return self._complete

    def get_outcome(self) -> dict[str, Any]:
        summary = "Raid succeeded." if self._success else "Raid failed."
        return {
            "title": self.name,
            "summary": summary,
            "scores": {
                "Objectives": f"{sum(o.complete for o in self._objectives)}/{len(self._objectives)}",
                "Time Left": str(self._time_remaining),
            },
        }

    def reset(self) -> None:
        self._players = ["Player 1", "Player 2"]
        self._turn = 1
        self._active_player = 0
        self._time_remaining = 8
        self._objectives = build_default_objectives()
        self._complete = False
        self._success = False
        self._last_message = "Ready."
