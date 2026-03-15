"""Timed Raid objective models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RaidObjective:
    name: str
    node: tuple[int, int]
    complete: bool = False


def build_default_objectives(nodes: list[tuple[int, int]]) -> list[RaidObjective]:
    objective_names = [
        "Breach the gate",
        "Disable the alarm runes",
        "Secure the relic vault",
    ]
    if len(nodes) < len(objective_names):
        raise ValueError("Not enough objective nodes provided.")

    return [
        RaidObjective(name=objective_names[index], node=nodes[index])
        for index in range(len(objective_names))
    ]
