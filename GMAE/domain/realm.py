"""Realm/map model used by mini-adventure UI state."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Realm:
    name: str
    width: int
    height: int
