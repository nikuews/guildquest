"""Timed Raid entities for interface output."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RaidTeam:
    players: tuple[str, str]
