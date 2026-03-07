"""Facade for running one full GMAE session from the CLI."""

from __future__ import annotations

from GMAE.display.cli_renderer import CliRenderer
from GMAE.engine.adventure_engine import AdventureEngine
from GMAE.engine.adventure_registry import AdventureRegistry
from GMAE.engine.menu_system import MenuSystem
from GMAE.profiles.profile_manager import ProfileManager
from GMAE.profiles.profile_proxy import ProfileProxy


class GmaeFacade:
    def __init__(self) -> None:
        self._renderer = CliRenderer()
        self._registry = AdventureRegistry()
        self._menu = MenuSystem()
        self._engine = AdventureEngine(self._renderer)
        self._profiles = ProfileProxy(ProfileManager())

    def run(self) -> None:
        self._renderer.show_welcome()

        while True:
            first = self._renderer.ask_player_name(1)
            second = self._renderer.ask_player_name(2)
            try:
                profile_one, profile_two = self._profiles.get_two_distinct_profiles(first, second)
                break
            except ValueError as error:
                print(error)
                print("Please try entering names again.\n")

        options = self._registry.list_adventures()
        selected = self._menu.choose_adventure(
            options,
            ask=lambda items: self._renderer.show_adventure_menu(items),
        )
        adventure = self._registry.create_by_index(selected)

        self._engine.run(adventure, [profile_one.character_name, profile_two.character_name])

        profile_one.sessions_played += 1
        profile_two.sessions_played += 1
        self._profiles.save_profiles([profile_one, profile_two])
