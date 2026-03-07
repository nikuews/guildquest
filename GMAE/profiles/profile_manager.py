"""Profile CRUD for local JSON persistence."""

from __future__ import annotations

import json
from pathlib import Path

from GMAE.profiles.player_profile import PlayerProfile


class ProfileManager:
    def __init__(self, storage_path: Path | None = None) -> None:
        default_path = Path(__file__).resolve().parent / "profiles.json"
        self._storage_path = storage_path or default_path

    def _load_raw(self) -> dict[str, dict]:
        if not self._storage_path.exists():
            return {}
        return json.loads(self._storage_path.read_text(encoding="utf-8"))

    def _save_raw(self, data: dict[str, dict]) -> None:
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(
            json.dumps(data, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def get_or_create(self, character_name: str) -> PlayerProfile:
        data = self._load_raw()
        existing = data.get(character_name)
        if existing is not None:
            return PlayerProfile.from_dict(existing)

        created = PlayerProfile(character_name=character_name)
        data[character_name] = created.to_dict()
        self._save_raw(data)
        return created

    def save(self, profile: PlayerProfile) -> None:
        data = self._load_raw()
        data[profile.character_name] = profile.to_dict()
        self._save_raw(data)
