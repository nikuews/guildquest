"""Relic Hunt entities used by renderer-friendly state output."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BoardEntity:
    token: str
    row: int
    col: int
