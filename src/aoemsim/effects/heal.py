"""Heal effect handler."""

from aoemsim.engine.effects_lifecycle import apply_heal_with_cap
from aoemsim.engine.rng import RngService
from aoemsim.engine.state import TroopState
from aoemsim.models.skill import SkillEffect


def handle_heal(
    attacker: TroopState,
    defender: TroopState,
    effect: SkillEffect,
    rng: RngService,
) -> None:
    """Apply healing to the attacker (self-heal)."""
    # [TBD: Target resolution for ally vs self]
    # For now, handle as self-heal since context is simple
    rate = float(effect.params.get("rate", 0.0))
    # Formula: amount = rate * attacker.max_hp (example placeholder)
    amount = rate * attacker.max_hp * 0.1 
    apply_heal_with_cap(attacker, amount)
