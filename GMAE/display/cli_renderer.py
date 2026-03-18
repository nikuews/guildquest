"""Terminal renderer for GMAE interface flows.

The renderer subscribes to the EventBus (Observer pattern) via its
on_game_event() method.  The engine wires up the subscription —
the renderer itself doesn't know about the bus, keeping display
logic decoupled from event infrastructure.
"""

from __future__ import annotations

from GMAE.engine.adventure_registry import AdventureInfo
from GMAE.display.world_clock import WorldClock

clock = WorldClock()


class CliRenderer:
    def __init__(self) -> None:
        self._event_log: list[str] = []

    def show_welcome(self) -> None:
        print("=" * 47)
        print("   Welcome to GuildQuest Adventures!")
        print("=" * 47)
        print()

    def ask_player_name(self, index: int) -> str:
        return input(f"Player {index}, enter your user name: ").strip()

    def show_adventure_menu(self, options: list[AdventureInfo]) -> str:
        print()
        print(clock)
        print("-- Select a Mini-Adventure --")
        for option in options:
            print(f"{option.index}. {option.title} ({option.mode})")
        return input("\nChoice: ").strip()

    def on_game_event(self, payload: dict) -> None:
        event_type = payload.get("event", "unknown")
        message = payload.get("message", "")

        if message:
            self._event_log.append(f"  >> {message}")

    def render_adventure_state(self, state: dict) -> None:
        print()
        print(f"-- {state['adventure_title']} ({state['mode']}) --")

        scoreboard = " | ".join(
            f"{part['name']}: {part['value']}"
            for part in state.get("scoreboard", [])
        )
        if scoreboard:
            print(f"Turn: {state.get('turn', '?')} | {scoreboard}")

        board_lines = state.get("board_lines", [])
        if board_lines:
            print()
            width = len(board_lines[0].split()) if board_lines else 0
            if width:
                print("  " + " ".join(str(i) for i in range(width)))
            for row_index, row in enumerate(board_lines):
                print(f"{row_index} {row}")

        legend = state.get("legend")
        if legend:
            print()
            print(legend)

        objective_lines = state.get("objective_lines", [])
        if objective_lines:
            print()
            print("Objectives:")
            for line in objective_lines:
                print(f"  {line}")

        inventory_lines = state.get("inventory_lines", [])
        if inventory_lines:
            print()
            print("Inventory:")
            for line in inventory_lines:
                print(f"  {line}")

        if self._event_log:
            print()
            print("Events:")
            for entry in self._event_log:
                print(entry)
            self._event_log.clear()

        status_line = state.get("status_line")
        if status_line:
            print(f"\n{status_line}")

    def prompt_action(self, player_name: str, actions: list[str]) -> str:
        print()
        print(f"{player_name}'s turn. Actions: [{'] ['.join(actions)}]")
        return input("> ").strip()

    def show_outcome(self, outcome: dict) -> None:
        print()
        print("-- Adventure Complete --")
        print(outcome.get("summary", "Adventure ended."))
        print(clock)

        scores = outcome.get("scores", {})
        if scores:
            print("Results:")
            for key, value in scores.items():
                print(f"  {key}: {value}")