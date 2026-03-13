"""CLI menu behavior for adventure selection."""

from __future__ import annotations

from collections.abc import Callable

from GMAE.engine.adventure_registry import AdventureInfo
from GMAE.display.world_clock import WorldClock

clock = WorldClock()

class MenuSystem:
    def choose_adventure(self, options: list[AdventureInfo], ask: Callable[[list[AdventureInfo]], str]) -> int:
        while True:
            raw = ask(options)
            try:
                selected = int(raw.strip())
                clock.increment_time(1)
            except ValueError:
                print("Enter a number from the menu.")
                clock.increment_time(1)
                continue

            if any(option.index == selected for option in options):
                clock.increment_time(1)
                return selected
            print("Invalid choice. Try again.")
