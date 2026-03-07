"""Observer-style event bus used for lightweight UI notifications."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable


EventHandler = Callable[[dict], None]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._subscribers[event_name].append(handler)

    def publish(self, event_name: str, payload: dict) -> None:
        for handler in self._subscribers.get(event_name, []):
            handler(payload)
