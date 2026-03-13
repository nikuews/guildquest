"""CLI menu behavior for adventure selection."""

from __future__ import annotations

from collections.abc import Callable

from GMAE.engine.adventure_registry import AdventureInfo


class MenuSystem:
    def choose_adventure(self, options: list[AdventureInfo], ask: Callable[[list[AdventureInfo]], str]) -> int:
        while True:
            raw = ask(options)
            try:
                selected = int(raw.strip())
            except ValueError:
                print("Enter a number from the menu.")
                continue

            if any(option.index == selected for option in options):
                return selected
            print("Invalid choice. Try again.")
