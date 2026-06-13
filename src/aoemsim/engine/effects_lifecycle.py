"""Runtime state for active effects and lifecycle management."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from aoemsim.models.buff import BuffEffect
from aoemsim.models.enums import BuffStackPolicy

if TYPE_CHECKING:
    from aoemsim.engine.state import TroopState


@dataclass
class ActiveEffect:
    """An instance of an effect currently active on a troop."""

    config: BuffEffect
    remaining_ticks: int
    stacks: int = 1

    @property
    def id(self) -> str:
        return self.config.id


def apply_heal_with_cap(troop: "TroopState", amount: float) -> float:
    """Apply healing to a troop, ensuring it doesn't exceed max_hp."""
    actual_heal = min(amount, troop.max_hp - troop.hp)
    if actual_heal > 0:
        troop.hp += actual_heal
    return actual_heal


def apply_effect(troop: "TroopState", effect_config: BuffEffect) -> None:
    """Apply a buff/debuff effect to a troop based on its stacking policy."""

    existing = next((e for e in troop.active_effects if e.id == effect_config.id), None)

    if not existing or effect_config.stack_policy == BuffStackPolicy.INDEPENDENT:
        troop.active_effects.append(
            ActiveEffect(
                config=effect_config, remaining_ticks=effect_config.duration_ticks, stacks=1
            )
        )
        return

    match effect_config.stack_policy:
        case BuffStackPolicy.REFRESH:
            existing.remaining_ticks = effect_config.duration_ticks
            existing.config = effect_config  # Update with potentially new values
        case BuffStackPolicy.STACK:
            if existing.stacks < effect_config.max_stacks:
                existing.stacks += 1
            existing.remaining_ticks = effect_config.duration_ticks
            existing.config = effect_config
        case BuffStackPolicy.REPLACE:
            existing.remaining_ticks = effect_config.duration_ticks
            existing.config = effect_config
            existing.stacks = 1
        case BuffStackPolicy.REPLACE_IF_STRONGER:
            if effect_config.value > existing.config.value:
                existing.config = effect_config
                existing.remaining_ticks = effect_config.duration_ticks


def prune_expired_effects(troop: "TroopState") -> None:
    """Updates remaining ticks and removes expired effects."""
    for effect in troop.active_effects:
        effect.remaining_ticks -= 1

    troop.active_effects = [e for e in troop.active_effects if e.remaining_ticks > 0]
