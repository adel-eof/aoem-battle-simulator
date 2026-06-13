"""Synergy resolver for hero and lineup bonuses."""

from collections import Counter
from collections.abc import Sequence

from aoemsim.config import (
    MILITARY_SYNERGY_2_SAME,
    MILITARY_SYNERGY_3_SAME,
    UNIT_TYPE_SYNERGY_1_MATCH,
    UNIT_TYPE_SYNERGY_2_MATCH,
    UNIT_TYPE_SYNERGY_3_MATCH,
)
from aoemsim.models.enums import UnitType
from aoemsim.models.hero import Hero


def resolve_military_bonus(heroes: Sequence[Hero]) -> float:
    """Calculate the military specialty bonus multiplier.

    Returns the bonus value (e.g., 0.20 for 20%) if 2 or 3 heroes
    share the same military specialty.
    """
    if not heroes:
        return 0.0

    counts = Counter(hero.military for hero in heroes)
    max_count = max(counts.values()) if counts else 0

    if max_count >= 3:
        return MILITARY_SYNERGY_3_SAME
    if max_count == 2:
        return MILITARY_SYNERGY_2_SAME

    return 0.0


def resolve_unit_type_bonus(heroes: Sequence[Hero], troop_unit_type: UnitType) -> float:
    """Calculate the unit type specialty bonus multiplier.

    Returns the bonus value based on how many heroes have a specialty
    matching the troop's unit type (1: 5%, 2: 10%, 3: 15%).
    """
    match_count = sum(1 for hero in heroes if troop_unit_type in hero.unit_types)

    if match_count >= 3:
        return UNIT_TYPE_SYNERGY_3_MATCH
    if match_count == 2:
        return UNIT_TYPE_SYNERGY_2_MATCH
    if match_count == 1:
        return UNIT_TYPE_SYNERGY_1_MATCH

    return 0.0


def apply_synergy_to_stats(heroes: Sequence[Hero], troop_unit_type: UnitType) -> float:
    """Calculate the total synergy bonus applicable to hero attributes.

    The total bonus is the sum of military bonus and unit type bonus.
    Example: 20% military + 5% unit type = 25% (0.25).
    """
    mil_bonus = resolve_military_bonus(heroes)
    unit_bonus = resolve_unit_type_bonus(heroes, troop_unit_type)
    return mil_bonus + unit_bonus
