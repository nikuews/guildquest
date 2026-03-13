"""Minimal quest model reused for objective presentation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Quest:
    title: str
    completed: bool = False
