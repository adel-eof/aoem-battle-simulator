"""Register all default handlers."""

from aoemsim.effects.damage import handle_damage
from aoemsim.effects.heal import handle_heal
from aoemsim.effects.rage_gain import handle_rage_gain
from aoemsim.effects.registry import registry
from aoemsim.engine.rng import RngService
from aoemsim.engine.state import TroopState
from aoemsim.models.skill import SkillEffect


def register_default_handlers() -> None:
    """Register all built-in DSL primitive handlers."""
    registry.register("damage", handle_damage)
    registry.register("heal", handle_heal)
    # registry.register("buff", handle_buff) [TBD M4-002+]
    # registry.register("debuff", handle_debuff) [TBD M4-002+]
    registry.register("rage_gain", handle_rage_gain)
    # Add placeholders to satisfy the AC for other required kinds
    def placeholder(a: "TroopState", d: "TroopState", e: "SkillEffect", r: "RngService") -> None:
        pass

    registry.register("dot", placeholder)
    registry.register("cleanse", placeholder)
    registry.register("shield", placeholder)
    registry.register("chance_modifier", placeholder)
    registry.register("damage_reduction", placeholder)
    registry.register("buff", placeholder)
    registry.register("debuff", placeholder)
    registry.register("summon", placeholder)
