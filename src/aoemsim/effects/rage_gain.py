"""Rage gain effect handler."""

from aoemsim.engine.rng import RngService
from aoemsim.engine.state import TroopState
from aoemsim.models.enums import StatKind
from aoemsim.models.skill import SkillEffect


def handle_rage_gain(
    attacker: TroopState,
    defender: TroopState,
    effect: SkillEffect,
    rng: RngService,
) -> None:
    """Add rage to the attacker."""
    amount = float(effect.params.get("value", 0.0))
    max_rage = attacker.stats_cache.get(StatKind.MAX_RAGE, 1000.0)
    attacker.rage = min(attacker.rage + amount, max_rage)
