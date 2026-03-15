"""Timed Raid adventure with a realm-local raid window."""

from __future__ import annotations

import random
from typing import Any

from GMAE.adventures.base_adventure import MiniAdventure
from GMAE.adventures.timed_raid.entities import (
    BOARD_COLS,
    BOARD_ROWS,
    HAZARD_COUNT,
    HAZARD_TIME_PENALTY_MINUTES,
    OBSTACLE_COUNT,
    OBJECTIVE_COUNT,
    RAID_WINDOW_MINUTES,
    TIMED_RAID_LEGEND,
    TURN_COST_MINUTES,
)
from GMAE.adventures.timed_raid.objectives import RaidObjective, build_default_objectives
from GMAE.display.world_clock import KeepTime, WorldClock


clock = WorldClock()


class TimedRaidAdventure(MiniAdventure):
    adventure_id = "timed_raid"
    name = "Timed Raid Window"
    mode = "Co-op"
    description = "Complete shared objectives before the realm-local raid window closes."

    def __init__(self) -> None:
        self.rows = BOARD_ROWS
        self.cols = BOARD_COLS
        self.reset()

    def start(self, player_names: list[str]) -> None:
        if len(player_names) != 2:
            raise ValueError("Timed Raid requires exactly two local players.")

        self._players = player_names
        self._turn = 1
        self._active_player = 0
        self._complete = False
        self._success = False
        self._failure_reason = ""

        used: set[tuple[int, int]] = set()
        p1 = self._random_empty_cell(used)
        used.add(p1)
        p2 = self._random_empty_cell(used)
        used.add(p2)
        self._player_positions = {0: p1, 1: p2}

        objective_nodes = []
        for _ in range(OBJECTIVE_COUNT):
            pos = self._random_empty_cell(used)
            used.add(pos)
            objective_nodes.append(pos)
        self._objectives = build_default_objectives(objective_nodes)

        self._hazards = set()
        for _ in range(HAZARD_COUNT):
            pos = self._random_empty_cell(used)
            used.add(pos)
            self._hazards.add(pos)

        self._obstacles = set()
        for _ in range(OBSTACLE_COUNT):
            pos = self._random_empty_cell(used)
            used.add(pos)
            self._obstacles.add(pos)

        self._window_start = clock.get_time()
        self._window_end = self._window_start.add_time(RAID_WINDOW_MINUTES)
        self._last_message = (
            f"Raid window opened at {self._format_time(self._window_start)} and closes at "
            f"{self._format_time(self._window_end)}."
        )

    def get_state(self) -> dict[str, Any]:
        objective_lines = []
        for objective in self._objectives:
            marker = "[x]" if objective.complete else "[ ]"
            row, col = objective.node
            objective_lines.append(f"{marker} {objective.name} @ ({row}, {col})")

        minutes_remaining = self._minutes_until_deadline()
        return {
            "adventure_title": self.name,
            "mode": self.mode,
            "turn": self._turn,
            "scoreboard": [
                {
                    "name": "Realm Time",
                    "value": self._format_time(clock.get_time()),
                },
                {
                    "name": "Window",
                    "value": f"closes {self._format_time(self._window_end)} ({max(minutes_remaining, 0)}m left)",
                },
                {
                    "name": "Progress",
                    "value": f"{sum(o.complete for o in self._objectives)}/{len(self._objectives)} objectives",
                },
            ],
            "board_lines": self._render_board(),
            "legend": TIMED_RAID_LEGEND,
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
        elapsed_minutes = TURN_COST_MINUTES

        if normalized == "quit":
            self._complete = True
            self._success = False
            self._failure_reason = "Raid was aborted."
            self._last_message = f"{actor} aborted the raid."
            return

        if normalized.startswith("move"):
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
                elapsed_minutes += HAZARD_TIME_PENALTY_MINUTES
                self._last_message += f" Hazard delay (+{HAZARD_TIME_PENALTY_MINUTES}m)."

        elif normalized == "complete objective":
            actor_pos = self._player_positions[player_index]
            objective = self._objective_at(actor_pos)
            if objective is None:
                self._last_message = f"No objective node here for {actor}."
            elif objective.complete:
                self._last_message = f"Objective already complete: {objective.name}."
            else:
                objective.complete = True
                self._last_message = f"{actor} completed objective: {objective.name}."

        elif normalized == "interact":
            actor_pos = self._player_positions[player_index]
            objective = self._objective_at(actor_pos)
            if objective is None:
                self._last_message = f"{actor} searched but found no objective node."
            elif objective.complete:
                self._last_message = f"{actor} verified objective node is already secured."
            else:
                self._last_message = f"{actor} prepared node for objective: {objective.name}."

        elif normalized == "use item":
            actor_pos = self._player_positions[player_index]
            if actor_pos in self._hazards:
                self._hazards.remove(actor_pos)
                self._last_message = f"{actor} cleared a hazard with an item."
            else:
                self._last_message = f"{actor} used an item, but no hazard was present."

        else:
            self._last_message = f"{actor} performed '{action}' (placeholder)."

        clock.increment_time(elapsed_minutes)
        if self._window_has_ended():
            self._complete = True
            self._success = False
            self._failure_reason = "Raid window expired."
            self._last_message += " The raid window closed."
            return

        if all(objective.complete for objective in self._objectives):
            self._complete = True
            self._success = True
            self._last_message += " All objectives are complete before window close."
            return

        self._active_player = 1 - self._active_player
        self._turn += 1

    def is_complete(self) -> bool:
        return self._complete

    def get_outcome(self) -> dict[str, Any]:
        if self._success:
            summary = "Raid succeeded. All objectives completed within the realm-local window."
        elif self._failure_reason:
            summary = f"Raid failed. {self._failure_reason}"
        else:
            summary = "Raid failed."

        return {
            "title": self.name,
            "summary": summary,
            "scores": {
                "Objectives": f"{sum(o.complete for o in self._objectives)}/{len(self._objectives)}",
                "Window Closed": self._format_time(self._window_end),
                "Realm Time": self._format_time(clock.get_time()),
                "Minutes Remaining": str(max(self._minutes_until_deadline(), 0)),
            },
        }

    def reset(self) -> None:
        self._players = ["Player 1", "Player 2"]
        self._turn = 1
        self._active_player = 0
        self._complete = False
        self._success = False
        self._failure_reason = ""
        self._last_message = "Ready."
        self._player_positions = {0: (0, 0), 1: (0, 1)}
        self._objectives = build_default_objectives([(1, 1), (2, 2), (3, 3)])
        self._hazards: set[tuple[int, int]] = set()
        self._obstacles: set[tuple[int, int]] = set()
        self._window_start = clock.get_time()
        self._window_end = self._window_start.add_time(RAID_WINDOW_MINUTES)

    def _objective_at(self, position: tuple[int, int]) -> RaidObjective | None:
        return next((objective for objective in self._objectives if objective.node == position), None)

    def _render_board(self) -> list[str]:
        grid = [["." for _ in range(self.cols)] for _ in range(self.rows)]

        for row, col in self._obstacles:
            grid[row][col] = "#"
        for row, col in self._hazards:
            grid[row][col] = "H"
        for objective in self._objectives:
            row, col = objective.node
            grid[row][col] = "o" if objective.complete else "O"

        p1_row, p1_col = self._player_positions[0]
        p2_row, p2_col = self._player_positions[1]
        grid[p1_row][p1_col] = "1"
        grid[p2_row][p2_col] = "2"
        return [" ".join(row) for row in grid]

    def _random_empty_cell(self, used: set[tuple[int, int]]) -> tuple[int, int]:
        while True:
            position = (random.randrange(self.rows), random.randrange(self.cols))
            if position not in used:
                return position

    def _direction_delta(self, direction: str) -> tuple[int, int]:
        deltas = {
            "n": (-1, 0),
            "s": (1, 0),
            "e": (0, 1),
            "w": (0, -1),
        }
        if direction not in deltas:
            raise ValueError(f"Invalid movement direction: {direction}")
        return deltas[direction]

    def _minutes_until_deadline(self) -> int:
        return self._as_total_minutes(self._window_end) - self._as_total_minutes(clock.get_time())

    def _window_has_ended(self) -> bool:
        return self._minutes_until_deadline() < 0

    def _format_time(self, value: KeepTime) -> str:
        return f"Day {value.days} {value.hours:02d}:{value.minutes:02d}"

    def _as_total_minutes(self, value: KeepTime) -> int:
        return value.days * 24 * 60 + value.hours * 60 + value.minutes
