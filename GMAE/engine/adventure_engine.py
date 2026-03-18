"""Game loop orchestrator for a single selected mini-adventure."""

from __future__ import annotations

from GMAE.adventures.base_adventure import MiniAdventure
from GMAE.display.cli_renderer import CliRenderer
from GMAE.engine.event_system import EventBus
from GMAE.engine.adventure_facade import AdventureFacade
from GMAE.profiles.player_profile import PlayerProfile


class AdventureEngine:
    def __init__(self, renderer: CliRenderer) -> None:
        self._renderer = renderer
        self._event_bus = EventBus()

        self._event_bus.subscribe("relic_collected", self._renderer.on_game_event)
        self._event_bus.subscribe("hazard_triggered", self._renderer.on_game_event)
        self._event_bus.subscribe("hazard_blocked", self._renderer.on_game_event)
        self._event_bus.subscribe("objective_complete", self._renderer.on_game_event)
        self._event_bus.subscribe("raid_window_warning", self._renderer.on_game_event)
        self._event_bus.subscribe("item_used", self._renderer.on_game_event)
        self._event_bus.subscribe("adventure_started", self._renderer.on_game_event)
        self._event_bus.subscribe("adventure_ended", self._renderer.on_game_event)

    def run(
        self,
        adventure: MiniAdventure,
        player_names: list[str],
        profiles: dict[int, PlayerProfile] | None = None,
    ) -> dict:
        if profiles is None:
            profiles = {}
        facade = AdventureFacade(
            event_bus=self._event_bus,
            player_profiles=profiles,
        )

        if hasattr(adventure, "set_facade"):
            adventure.set_facade(facade)

        adventure.start(player_names)

        self._event_bus.publish("adventure_started", {
            "adventure": adventure.name,
            "players": player_names,
        })

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

        self._event_bus.publish("adventure_ended", {
            "adventure": adventure.name,
            "outcome": outcome.get("summary", ""),
        })

        self._renderer.show_outcome(outcome)
        return outcome