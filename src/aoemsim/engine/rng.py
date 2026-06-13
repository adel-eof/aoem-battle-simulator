"""RNG service for deterministic battle simulation."""

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class RngRollEvent:
    """Represents a single RNG roll event for traceability."""

    roll_index: int
    source: str
    result: float


class RngService:
    """Centralized RNG service with seeded generation and roll counter."""

    def __init__(self, seed: int):
        self._rng = random.Random(seed)
        self._roll_counter = 0
        self._history: list[RngRollEvent] = []

    def random(self, source: str) -> float:
        """Generate a random float between 0.0 and 1.0 and record the event."""
        self._roll_counter += 1
        result = self._rng.random()
        event = RngRollEvent(roll_index=self._roll_counter, source=source, result=result)
        self._history.append(event)
        return result

    def randint(self, a: int, b: int, source: str) -> int:
        """Generate a random integer between a and b (inclusive) and record the event."""
        self._roll_counter += 1
        result = self._rng.randint(a, b)
        event = RngRollEvent(roll_index=self._roll_counter, source=source, result=float(result))
        self._history.append(event)
        return result

    def uniform(self, a: float, b: float, source: str) -> float:
        """Generate a random float between a and b (inclusive) and record the event."""
        self._roll_counter += 1
        result = self._rng.uniform(a, b)
        event = RngRollEvent(roll_index=self._roll_counter, source=source, result=result)
        self._history.append(event)
        return result

    @property
    def history(self) -> list[RngRollEvent]:
        """Return the history of RNG roll events."""
        return list(self._history)

    @property
    def roll_counter(self) -> int:
        """Return the current roll count."""
        return self._roll_counter
