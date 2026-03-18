from __future__ import annotations

from typing import Any

from GMAE.display.world_clock import WorldClock
from GMAE.engine.event_system import EventBus
from GMAE.profiles.player_profile import PlayerProfile
from GMAE.profiles.read_only_view import ReadOnlyProfileView


class AdventureFacade:
    def __init__(
        self,
        event_bus: EventBus,
        player_profiles: dict[int, PlayerProfile],
    ) -> None:
        # Private — adventures cannot access these directly
        object.__setattr__(self, "_AdventureFacade__event_bus", event_bus)
        object.__setattr__(self, "_AdventureFacade__profile_views", {
            idx: ReadOnlyProfileView(profile)
            for idx, profile in player_profiles.items()
        })
        object.__setattr__(self, "_AdventureFacade__clock", WorldClock())

    # ── Player profile access (read-only via Proxy) ────────────────

    def get_player_view(self, player_index: int) -> ReadOnlyProfileView:
        view = self.__profile_views.get(player_index)
        if view is None:
            raise KeyError(f"No player profile for index {player_index}.")
        return view

    def get_player_name(self, player_index: int) -> str:
        """Convenience: get the display name for a player."""
        return self.get_player_view(player_index).character_name

    def get_player_level(self, player_index: int) -> int:
        """Convenience: get the character level for a player."""
        return self.get_player_view(player_index).character_level

    def get_player_class(self, player_index: int) -> str:
        """Convenience: get the character class name for a player."""
        return self.get_player_view(player_index).character_class.value

    # ── Event publishing (publish-only access to event bus) ────────

    def publish_event(self, event_name: str, payload: dict[str, Any]) -> None:
        self.__event_bus.publish(event_name, payload)

    # ── Realm time queries (read-only) ─────────────────────────────

    def get_current_time(self) -> tuple[int, int, int]:
        time = self.__clock.get_time()
        return (time.days, time.hours, time.minutes)

    def get_current_time_str(self) -> str:
        """Return a formatted time string for display."""
        time = self.__clock.get_time()
        return f"Day {time.days}, {time.hours:02d}:{time.minutes:02d}"

    # ── Blocked write operations ───────────────────────────────────

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError(
            f"Cannot set '{name}' on AdventureFacade. "
            f"Adventures are not allowed to modify framework internals."
        )

    def __delattr__(self, name: str) -> None:
        raise AttributeError(
            f"Cannot delete '{name}' on AdventureFacade. "
            f"Adventures are not allowed to modify framework internals."
        )

    def __repr__(self) -> str:
        return f"AdventureFacade(players={len(self.__profile_views)})"