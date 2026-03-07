"""Terminal renderer for GMAE interface flows."""

from __future__ import annotations

from GMAE.engine.adventure_registry import AdventureInfo


class CliRenderer:
    def show_welcome(self) -> None:
        print("=" * 47)
        print("   Welcome to GuildQuest Adventures!")
        print("=" * 47)
        print()

    def ask_player_name(self, index: int) -> str:
        return input(f"Player {index}, enter your character name: ").strip()

    def show_adventure_menu(self, options: list[AdventureInfo]) -> str:
        print()
        print("-- Select a Mini-Adventure --")
        for option in options:
            print(f"{option.index}. {option.title} ({option.mode})")
        return input("\nChoice: ").strip()

    def render_adventure_state(self, state: dict) -> None:
        print()
        print(f"-- {state['adventure_title']} ({state['mode']}) --")

        scoreboard = " | ".join(f"{part['name']}: {part['value']}" for part in state.get("scoreboard", []))
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
                print(f"- {line}")

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

        scores = outcome.get("scores", {})
        if scores:
            print("Results:")
            for key, value in scores.items():
                print(f"- {key}: {value}")
