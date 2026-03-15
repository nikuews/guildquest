"""Profile CRUD for local JSON persistence."""

from __future__ import annotations

import json
from pathlib import Path

from GMAE.profiles.player_profile import PlayerProfile


class ProfileManager:
    def __init__(self, storage_path: Path | None = None, persist_to_disk: bool = False) -> None:
        default_path = Path(__file__).resolve().parent / "profiles.json"
        self._storage_path = storage_path or default_path
        self._persist_to_disk = persist_to_disk
        self._memory_store: dict[str, dict] = {}
        if self._persist_to_disk and self._storage_path.exists():
            self._memory_store = json.loads(self._storage_path.read_text(encoding="utf-8"))

    def _load_raw(self) -> dict[str, dict]:
        return self._memory_store

    def _save_raw(self, data: dict[str, dict]) -> None:
        self._memory_store = data
        if not self._persist_to_disk:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(
            json.dumps(data, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _next_user_id(self, data: dict[str, dict]) -> int:
        max_user_id = 0
        for payload in data.values():
            try:
                max_user_id = max(max_user_id, int(payload.get("user_id", 0)))
            except (TypeError, ValueError):
                continue
        return max_user_id + 1

    def get_or_create(self, username: str) -> PlayerProfile:
        data = self._load_raw()
        existing = data.get(username)
        if existing is not None:
            return PlayerProfile.from_dict(existing)

        created = PlayerProfile(
            user_id=self._next_user_id(data),
            username=username,
        )
        data[username] = created.to_dict()
        self._save_raw(data)
        return created

    def save(self, profile: PlayerProfile) -> None:
        data = self._load_raw()
        data[profile.username] = profile.to_dict()
        self._save_raw(data)

    def list_profiles(self) -> list[PlayerProfile]:
        return [PlayerProfile.from_dict(payload) for payload in self._load_raw().values()]
