"""Event Bus for battle engine lifecycle events according to Section 5.3."""

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aoemsim.engine.state import TroopState


class EventType(StrEnum):
    """Lifecycle event types in the battle engine."""

    BATTLE_START = "on_battle_start"
    TICK = "on_tick"
    NORMAL_ATTACK = "on_normal_attack"
    HIT = "on_hit"
    SKILL_CAST = "on_skill_cast"
    DAMAGE_TAKEN = "on_damage_taken"
    HEAL = "on_heal"
    ALLY_DEATH = "on_ally_death"
    BATTLE_END = "on_battle_end"


@dataclass(frozen=True)
class EventPayload:
    """Explicit container for event data."""

    tick: int
    attacker: "TroopState | None" = None
    defender: "TroopState | None" = None
    data: dict[str, Any] = field(default_factory=dict)


# Type alias for event subscriber callback
Subscriber = Callable[[EventPayload], None]


class EventBus:
    """
    Deterministic event bus for battle lifecycle.
    Section 5.3: Dispatch events through a registry.
    """

    def __init__(self) -> None:
        # Using a list to maintain registration order for determinism
        self._subscribers: dict[EventType, list[Subscriber]] = defaultdict(list)

    def subscribe(self, event_type: EventType, callback: Subscriber) -> None:
        """Register a subscriber callback for a specific event type."""
        self._subscribers[event_type].append(callback)

    def publish(self, event_type: EventType, payload: EventPayload) -> None:
        """Publishes an event to all registered subscribers in order."""
        for callback in self._subscribers[event_type]:
            callback(payload)
