"""Crowd Control management logic."""

from typing import TYPE_CHECKING

from aoemsim.models.enums import CcType

if TYPE_CHECKING:
    from aoemsim.engine.state import TroopState


def apply_cc(troop: "TroopState", cc_type: CcType, duration_ticks: int) -> bool:
    """
    Apply a CC effect if the troop is not immune.
    Returns True if applied, False if rejected due to immunity.
    """
    if troop.cc_immunity_timers.get(cc_type, 0) > 0:
        return False

    current_timer = troop.cc_timers.get(cc_type, 0)
    troop.cc_timers[cc_type] = max(current_timer, duration_ticks)
    return True


def is_silenced(troop: "TroopState") -> bool:
    """Check if the troop is currently silenced."""
    return troop.cc_timers.get(CcType.SILENCE, 0) > 0


def is_disarmed(troop: "TroopState") -> bool:
    """Check if the troop is currently disarmed."""
    return troop.cc_timers.get(CcType.DISARM, 0) > 0


def is_incapacitated(troop: "TroopState") -> bool:
    """Check if the troop is currently incapacitated."""
    return troop.cc_timers.get(CcType.INCAPACITATION, 0) > 0


def update_cc_timers(troop: "TroopState", immunity_duration_ticks: int) -> None:
    """Update CC and immunity timers for a single tick."""
    # We iterate over CcType to ensure all types are checked
    for cc_type in list(CcType):
        # 1. Update active CC timers
        if troop.cc_timers.get(cc_type, 0) > 0:
            troop.cc_timers[cc_type] -= 1
            if troop.cc_timers[cc_type] <= 0:
                # CC just ended, trigger immunity
                del troop.cc_timers[cc_type]
                troop.cc_immunity_timers[cc_type] = immunity_duration_ticks
        # 2. Update immunity timers
        elif troop.cc_immunity_timers.get(cc_type, 0) > 0:
            troop.cc_immunity_timers[cc_type] -= 1
            if troop.cc_immunity_timers[cc_type] <= 0:
                del troop.cc_immunity_timers[cc_type]
