"""Rage accumulation and commander skill interrupt logic."""

from aoemsim.engine.rng import RngService
from aoemsim.engine.state import TroopState
from aoemsim.models.enums import StatKind
from aoemsim.models.skill import Skill


def update_rage(state: TroopState, tick_sec: float) -> None:
    """Update rage for a troop based on its RAGE_REGEN stat."""
    regen = state.stats_cache.get(StatKind.RAGE_REGEN, 0.0)
    max_rage = state.stats_cache.get(StatKind.MAX_RAGE, 1000.0)

    if regen > 0:
        gain = regen * tick_sec
        # Accumulate rage without exceeding max_rage
        state.rage = min(state.rage + gain, max_rage)


def should_interrupt_cast(state: TroopState) -> Skill | None:
    """Check if the commander skill should be cast as an interrupt."""
    skill = state.commander_skill
    if not skill or skill.rage_cost is None:
        return None

    if state.rage >= skill.rage_cost:
        return skill

    return None


def cast_commander_interrupt(
    attacker: TroopState, defender: TroopState, skill: Skill, rng: RngService
) -> None:
    """Cast the commander skill and reset rage."""
    # Record the cast event for determinism
    rng.random(source=f"cast_skill_{skill.id}")

    # Logic for effects would go here in M3-002+ (Out of scope for M3-001)
    # For M3-001, we just need to ensure the cast happens and rage is reset.

    # Reset rage without overflow: attacker.rage -= skill.rage_cost
    # Acceptance Criteria says: "rage di-reset sesuai aturan tanpa overflow"
    # Usually in AOEM, it resets to 0 or subtracts the cost.
    # The requirement says "reset rage" and "tanpa overflow".
    # I'll subtract the cost to be safe, but "reset" often means to 0.
    # Re-reading: "reset rage sesuai aturan tanpa overflow"
    # I'll set it to (current_rage - cost) but ensure it doesn't go below 0.
    if skill.rage_cost is not None:
        state_rage_before = attacker.rage
        attacker.rage = max(0.0, state_rage_before - skill.rage_cost)
