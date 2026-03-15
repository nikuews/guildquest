"""Facade for running one full GMAE session from the CLI."""

from __future__ import annotations

from GMAE.display.cli_renderer import CliRenderer
from GMAE.engine.adventure_engine import AdventureEngine
from GMAE.engine.adventure_registry import AdventureRegistry
from GMAE.engine.menu_system import MenuSystem
from GMAE.profiles.player_profile import PlayerProfile
from GMAE.profiles.profile_manager import ProfileManager
from GMAE.profiles.profile_proxy import ProfileProxy


class GmaeFacade:
    def __init__(self) -> None:
        self._renderer = CliRenderer()
        self._registry = AdventureRegistry()
        self._menu = MenuSystem()
        self._engine = AdventureEngine(self._renderer)
        self._profiles = ProfileProxy(ProfileManager(persist_to_disk=False))

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

        self._configure_selected_character(profile_one, player_index=1)
        self._configure_selected_character(profile_two, player_index=2)

        options = self._registry.list_adventures()
        selected = self._menu.choose_adventure(
            options,
            ask=lambda items: self._renderer.show_adventure_menu(items),
        )
        adventure = self._registry.create_by_index(selected)

        player_labels = [self._player_label(profile_one), self._player_label(profile_two)]
        self._engine.run(adventure, player_labels)

        profile_one.sessions_played += 1
        profile_two.sessions_played += 1
        self._profiles.save_profiles([profile_one, profile_two])

    def _configure_selected_character(self, profile: PlayerProfile, player_index: int) -> None:
        while True:
            print()
            print(f"-- Player {player_index} Character Setup ({profile.username}) --")
            if not profile.characters:
                print("No characters found. Create one to continue.")
            else:
                self._print_character_table(profile)

            print()
            print("Enter character id to select, N to create new, or press Enter to keep current.")
            raw = input("Choice: ").strip()

            if raw == "":
                if profile.selected_character is None:
                    print("No selected character yet. Choose one id or create a new character.")
                    continue
                return

            if raw.lower() == "n":
                print()
                self._create_character(profile, player_index)
                continue

            try:
                choice_id = int(raw)
            except ValueError:
                print("Invalid input. Enter a numeric id, N, or Enter.")
                continue

            try:
                self._profiles.select_character(profile, choice_id)
                chosen = profile.selected_character
                if chosen is not None:
                    print(
                        f"Selected: {chosen.name} "
                        f"({chosen.character_class.value}, Lv {chosen.level})"
                    )
                return
            except ValueError as error:
                print(error)

    def _create_character(self, profile: PlayerProfile, player_index: int) -> None:
        while True:
            name = input(f"Player {player_index}, new character name: ").strip()
            class_raw = input(
                "Class [WARRIOR/ASSASSIN/MAGE]: "
            ).strip()
            level_raw = input("Starting level (default 1): ").strip()

            if not class_raw:
                print("Choose a class to continue.")
                continue
            class_name = class_raw
            try:
                level = int(level_raw) if level_raw else 1
            except ValueError:
                print("Level must be a number.")
                continue

            try:
                created = self._profiles.add_character(
                    profile=profile,
                    name=name,
                    class_name=class_name,
                    level=level,
                )
                self._profiles.select_character(profile, created.character_id)
                print(
                    f"Created and selected: {created.name} "
                    f"({created.character_class.value}, Lv {created.level})"
                )
                return
            except ValueError as error:
                print(error)

    @staticmethod
    def _player_label(profile: PlayerProfile) -> str:
        selected = profile.selected_character
        if selected is None:
            return profile.username
        class_label = selected.character_class.value.title()
        return f"{selected.name} ({class_label} Lv{selected.level})"

    @staticmethod
    def _print_character_table(profile: PlayerProfile) -> None:
        characters = profile.characters
        id_col = "Player ID"
        name_col = "Name"
        class_col = "Class"
        level_col = "Level"
        status_col = "Status"

        id_width = max(len(id_col), max(len(str(item.character_id)) for item in characters))
        name_width = max(len(name_col), max(len(item.name) for item in characters))
        class_width = max(len(class_col), max(len(item.character_class.value) for item in characters))
        level_values = [f"Lv {item.level}" for item in characters]
        level_width = max(len(level_col), max(len(level) for level in level_values))
        status_values = [
            "selected" if item.character_id == profile.selected_character_id else ""
            for item in characters
        ]
        status_width = max(len(status_col), max(len(status) for status in status_values))

        header = (
            f"{id_col:^{id_width}} | "
            f"{name_col:<{name_width}} | "
            f"{class_col:<{class_width}} | "
            f"{level_col:<{level_width}} | "
            f"{status_col:<{status_width}}"
        )
        print(header)
        print("-" * len(header))

        for character, level_text, status_text in zip(characters, level_values, status_values):
            print(
                f"{character.character_id:^{id_width}} | "
                f"{character.name:<{name_width}} | "
                f"{character.character_class.value:<{class_width}} | "
                f"{level_text:<{level_width}} | "
                f"{status_text:<{status_width}}"
            )
