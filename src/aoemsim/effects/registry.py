"""Registry for DSL effect handlers."""

from collections.abc import Callable

from aoemsim.engine.rng import RngService
from aoemsim.engine.state import TroopState
from aoemsim.models.skill import SkillEffect

# Handler type for effect registry
EffectHandler = Callable[[TroopState, TroopState, SkillEffect, RngService], None]


class EffectRegistry:
    """Central registry mapping effect kinds to their handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, EffectHandler] = {}

    def register(self, kind: str, handler: EffectHandler) -> None:
        """Register a handler for a specific effect kind."""
        self._handlers[kind] = handler

    def execute(
        self,
        attacker: TroopState,
        defender: TroopState,
        effect: SkillEffect,
        rng: RngService,
    ) -> None:
        """Execute a handler for the given effect."""
        handler = self._handlers.get(effect.kind)
        if not handler:
            raise ValueError(
                f"Unsupported skill effect kind: {effect.kind}. "
                f"Supported kinds: {list(self._handlers.keys())}"
            )
        handler(attacker, defender, effect, rng)


# Global registry instance
registry = EffectRegistry()
