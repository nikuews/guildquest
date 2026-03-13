"""Timed Raid objective models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RaidObjective:
    name: str
    complete: bool = False


def build_default_objectives() -> list[RaidObjective]:
    return [
        RaidObjective("Breach the gate"),
        RaidObjective("Disable the alarm runes"),
        RaidObjective("Secure the relic vault"),
    ]
