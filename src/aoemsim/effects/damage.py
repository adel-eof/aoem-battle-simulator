"""Damage effect handler."""

from aoemsim.engine.damage import resolve_damage
from aoemsim.engine.rng import RngService
from aoemsim.engine.state import TroopState
from aoemsim.models.skill import SkillEffect


def handle_damage(
    attacker: TroopState,
    defender: TroopState,
    effect: SkillEffect,
    rng: RngService,
) -> None:
    """Resolve damage and apply to defender HP."""
    troop_loss = resolve_damage(attacker, defender, effect, rng)
    # Convert troop loss back to HP for internal state update
    hp_loss = troop_loss * defender.lineup.troop.unit_base_hp
    defender.hp = max(0.0, defender.hp - hp_loss)
