"""Relic Hunt adventure (interface-first placeholder behavior)."""

from __future__ import annotations

from typing import Any
import random

from GMAE.adventures.base_adventure import MiniAdventure
from GMAE.adventures.relic_hunt.maps import RELIC_HUNT_LEGEND
from GMAE.display.world_clock import WorldClock

from GMAE.domain.inventory import (
    Inventory,
    shield_amulet,
    relic_shard,
)


clock = WorldClock()

class RelicHuntAdventure(MiniAdventure):
    adventure_id = "relic_hunt"
    name = "Relic Hunt"
    mode = "Competitive"
    description = "Collect relics before your opponent."

    def __init__(self) -> None:
        clock.increment_time(30)
        self.rows = 6
        self.cols = 8
        self.reset()

    def start(self, player_names: list[str]) -> None:
        if len(player_names) != 2:
            raise ValueError("Relic Hunt requires exactly two local players.")

        self._players = player_names
        self._scores = {player_names[0]: 0, player_names[1]: 0}
        self._turn = 1
        self._active_player = 0
        self._complete = False
        self._winner = None
        self._last_message = "Adventure started."
        self._inventories = {
            0: Inventory(max_slots=5, max_weight=10.0),
            1: Inventory(max_slots=5, max_weight=10.0),
        }

        # Give each player a starting shield amulet
        self._inventories[0].add(shield_amulet(), 1)
        self._inventories[1].add(shield_amulet(), 1)

        used = set()

        p1 = self._random_empty_cell(used)
        used.add(p1)

        p2 = self._random_empty_cell(used)
        used.add(p2)

        self._player_positions = {0: p1, 1: p2}

        self._relics = set()
        for _ in range(4):
            pos = self._random_empty_cell(used)
            used.add(pos)
            self._relics.add(pos)

        self._hazards = set()
        for _ in range(2):
            pos = self._random_empty_cell(used)
            used.add(pos)
            self._hazards.add(pos)

        self._obstacles = set()
        for _ in range(4):
            pos = self._random_empty_cell(used)
            used.add(pos)
            self._obstacles.add(pos)

    def get_state(self) -> dict[str, Any]:
        active_inv = self._inventories[self._active_player]
        inv_lines = active_inv.summary_lines()
        return {
            "adventure_title": self.name,
            "mode": self.mode,
            "turn": self._turn,
            "scoreboard": [
                {"name": self._players[0], "value": f"{self._scores[self._players[0]]} relics"},
                {"name": self._players[1], "value": f"{self._scores[self._players[1]]} relics"},
            ],
            "board_lines": self._render_board(),
            "legend": RELIC_HUNT_LEGEND,
            "active_player_index": self._active_player,
            "status_line": self._last_message,
            "inventory_lines": inv_lines,
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
            pos = self._player_positions[player_index]
            if pos in self._relics:
                self._relics.remove(pos)
                self._scores[actor] += 1
                self._inventories[player_index].add(relic_shard(), 1)
                self._last_message = f"{actor} picked up a relic!"
            else:
                self._last_message = f"No relic here for {actor}."
        elif normalized.startswith("move"):
            direction = normalized.split()[-1].lower()
            dr, dc = self._direction_delta(direction)

            row, col = self._player_positions[player_index]
            new_row, new_col = row + dr, col + dc

            if not (0 <= new_row < self.rows and 0 <= new_col < self.cols):
                self._last_message = f"{actor} hit the edge of the map."
                return

            if (new_row, new_col) in self._obstacles:
                self._last_message = f"{actor} hit an obstacle."
                return

            if (new_row, new_col) == self._player_positions[1 - player_index]:
                self._last_message = f"{actor} cannot move onto the other player."
                return

            self._player_positions[player_index] = (new_row, new_col)
            self._last_message = f"{actor} moved {direction.upper()}."

            if (new_row, new_col) in self._hazards:
                inv = self._inventories[player_index]
                if inv.has("shield_amulet"):
                    result = inv.use_item("shield_amulet")
                    self._last_message += " Hazard blocked by Shield Amulet!"
                else:
                    self._last_message += " A hazard was triggered! (-1 relic)"
                    if self._scores[actor] > 0:
                        self._scores[actor] -= 1
                        inv.remove("relic_shard", 1)
        elif normalized == "use item":
            inv = self._inventories[player_index]
            if inv.has("shield_amulet"):
                self._last_message = f"{actor} has a Shield Amulet — it will block the next hazard automatically."
            else:
                self._last_message = f"{actor} has no usable items."
        else:
            self._last_message = f"{actor} performed '{action}' (placeholder)."

        if self._scores[actor] >= 3:
            self._complete = True
            self._winner = actor
            return

        if not self._relics:
            self._complete = True
            p1, p2 = self._players
            if self._scores[p1] == self._scores[p2]:
                self._winner = None
            else:
                self._winner = p1 if self._scores[p1] > self._scores[p2] else p2
            return

        self._active_player = 1 - self._active_player
        self._turn += 1

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
        self._player_positions = {0: (0, 0), 1: (0, 1)}
        self._relics = set()
        self._hazards = set()
        self._obstacles = set()
        self._inventories = {0: Inventory(), 1: Inventory()}

    def _random_empty_cell(self, used: set[tuple[int, int]]) -> tuple[int, int]:
        while True:
            pos = (random.randrange(self.rows), random.randrange(self.cols))
            if pos not in used:
                return pos

    def _direction_delta(self, direction: str) -> tuple[int, int]:
        return {
            "n": (-1, 0),
            "s": (1, 0),
            "e": (0, 1),
            "w": (0, -1),
        }[direction]

    def _render_board(self) -> list[str]:
        grid = [["." for _ in range(self.cols)] for _ in range(self.rows)]

        for r, c in self._obstacles:
            grid[r][c] = "#"

        for r, c in self._hazards:
            grid[r][c] = "H"

        for r, c in self._relics:
            grid[r][c] = "R"

        p1r, p1c = self._player_positions[0]
        p2r, p2c = self._player_positions[1]
        grid[p1r][p1c] = "1"
        grid[p2r][p2c] = "2"

        return [" ".join(row) for row in grid]