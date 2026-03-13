"""Game loop orchestrator for a single selected mini-adventure."""

from __future__ import annotations

from GMAE.adventures.base_adventure import MiniAdventure
from GMAE.display.cli_renderer import CliRenderer


class AdventureEngine:
    def __init__(self, renderer: CliRenderer) -> None:
        self._renderer = renderer

    def run(self, adventure: MiniAdventure, player_names: list[str]) -> dict:
        adventure.start(player_names)

        while not adventure.is_complete():
            state = adventure.get_state()
            self._renderer.render_adventure_state(state)

            active_index = int(state["active_player_index"])
            actions = adventure.get_actions_for_player(active_index)
            player_name = player_names[active_index]
            action = self._renderer.prompt_action(player_name, actions)

            if action not in actions:
                print("Invalid action. Choose one listed action exactly.")
                continue

            adventure.submit_action(active_index, action)

        outcome = adventure.get_outcome()
        self._renderer.show_outcome(outcome)
        return outcome
