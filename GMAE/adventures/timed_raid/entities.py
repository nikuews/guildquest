"""Timed Raid constants and lightweight entities."""

from __future__ import annotations

from dataclasses import dataclass


BOARD_ROWS = 6
BOARD_COLS = 8
OBJECTIVE_COUNT = 3
HAZARD_COUNT = 3
OBSTACLE_COUNT = 5
RAID_WINDOW_MINUTES = 90
TURN_COST_MINUTES = 10
HAZARD_TIME_PENALTY_MINUTES = 5
TIMED_RAID_LEGEND = (
    "1=Player 1  2=Player 2  O=Objective Node  o=Completed Node  H=Hazard  #=Obstacle"
)


@dataclass
class RaidTeam:
    players: tuple[str, str]
