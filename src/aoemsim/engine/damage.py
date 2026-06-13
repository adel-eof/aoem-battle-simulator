"""Damage resolver and formula implementations for AOEM Battle Simulator."""

import math

from aoemsim.config import (
    COUNTER_BONUS_RATE,
    CRIT_CHANCE_CAP,
    CRIT_CHANCE_DEFAULT,
    CRIT_DAMAGE_DEFAULT,
    DAMAGE_VARIANCE_RANGE,
    SKILL_STAT_TO_EFFECT_RATE,
    STAT_TO_MODIFIER_RATE,
)
from aoemsim.engine.rng import RngService
from aoemsim.engine.state import TroopState
from aoemsim.models.enums import StatKind, UnitType
from aoemsim.models.skill import SkillEffect


def compute_counter_multiplier(attacker_type: UnitType, defender_type: UnitType) -> float:
    """Calculate counter bonus based on UnitType matchup (Section 2.2).

    Archer -> Swordsman -> Pikeman -> Cavalry -> Archer.
    Returns 1.30 if matchup matches, else 1.00.
    """
    matchups = {
        UnitType.ARCHER: UnitType.SWORDSMAN,
        UnitType.SWORDSMAN: UnitType.PIKEMAN,
        UnitType.PIKEMAN: UnitType.CAVALRY,
        UnitType.CAVALRY: UnitType.ARCHER,
    }
    if matchups.get(attacker_type) == defender_type:
        return 1.0 + COUNTER_BONUS_RATE
    return 1.0


def compute_attack_stat(troop_base_attack: float, effective_might_or_strat: float) -> float:
    """Calculate effective attack stat (Section 2.7).

    Formula: attack_stat = unit_base_attack * (1 + 0.0015 * effective_might)
    """
    return troop_base_attack * (1.0 + STAT_TO_MODIFIER_RATE * effective_might_or_strat)


def compute_defense_multiplier(effective_armor_or_strat_def: float) -> float:
    """Calculate defense impact as a multiplier (Section 2.7).

    Formula: defense_mult = 1 / (1 + 0.0015 * effective_armor_of_target)
    """
    return 1.0 / (1.0 + STAT_TO_MODIFIER_RATE * effective_armor_or_strat_def)


def compute_crit(
    base_damage: float,
    attacker: TroopState,
    rng: RngService,
    is_normal_attack: bool,
    can_crit_skill: bool,
) -> float:
    """Apply critical hit multiplier if applicable (Section 2.7.1)."""
    if not (is_normal_attack or can_crit_skill):
        return base_damage

    crit_chance = min(
        attacker.stats_cache.get(StatKind.CRIT_CHANCE, CRIT_CHANCE_DEFAULT),
        CRIT_CHANCE_CAP,
    )

    if rng.random(source="damage_crit") < crit_chance:
        crit_damage = attacker.stats_cache.get(StatKind.CRIT_DAMAGE, CRIT_DAMAGE_DEFAULT)
        return base_damage * crit_damage

    return base_damage


def compute_troop_loss(damage_float: float, unit_base_hp: float) -> int:
    """Convert float damage to integer troop loss (Section 2.7).

    Formula: final_troop_loss = floor(final_damage_float / unit_base_health)
    """
    return math.floor(damage_float / unit_base_hp)


def resolve_damage(
    attacker: TroopState,
    defender: TroopState,
    effect: SkillEffect,
    rng: RngService,
    is_normal_attack: bool = False,
) -> int:
    """Calculate and resolve damage between attacker and defender (Section 2.7).

    Integrates armor, counter, variance, and troop scaling.
    Returns the integer troop loss.
    """
    params = effect.params
    base_rate = float(params.get("rate", 0.0))

    # 1. Determine attack and bonus stat kinds
    attack_kind_str = params.get("attack_stat", "might")
    attack_kind = StatKind.MIGHT if attack_kind_str == "might" else StatKind.STRATEGY

    bonus_kind_str = params.get("bonus", "none")

    # 2. Effective Attack Stat
    eff_atk_stat_val = attacker.stats_cache.get(attack_kind, 0.0)
    attack_stat = compute_attack_stat(
        attacker.lineup.troop.unit_base_attack, eff_atk_stat_val
    )

    # 3. Apply Skill Rate Bonus (Section 2.4)
    skill_rate = base_rate
    if bonus_kind_str != "none":
        bonus_kind = StatKind.MIGHT if bonus_kind_str == "might" else StatKind.STRATEGY
        eff_bonus_val = attacker.stats_cache.get(bonus_kind, 0.0)
        skill_rate *= 1.0 + (SKILL_STAT_TO_EFFECT_RATE * eff_bonus_val)

    # 4. Initial Raw Damage
    damage = skill_rate * attack_stat

    # 5. Defense Multiplier
    target_def_kind = StatKind.ARMOR
    if attack_kind == StatKind.STRATEGY:
        if StatKind.STRATEGY_DEFENSE in defender.stats_cache:
            target_def_kind = StatKind.STRATEGY_DEFENSE
    eff_def_val = defender.stats_cache.get(target_def_kind, 0.0)
    damage *= compute_defense_multiplier(eff_def_val)

    # 6. Counter Multiplier
    damage *= compute_counter_multiplier(attacker.unit_type, defender.unit_type)

    # 7. Critical Hit
    damage = compute_crit(
        damage, attacker, rng, is_normal_attack, params.get("can_crit", False)
    )

    # 8. Troop Scaling
    # damage menurun seiring hilangnya jumlah pasukan (current / max)
    troop_scaling_mult = attacker.hp / attacker.max_hp
    damage *= troop_scaling_mult

    # 9. Random Variance
    var_min, var_max = DAMAGE_VARIANCE_RANGE
    random_mult = rng.uniform(var_min, var_max, source="damage_variance")
    damage *= random_mult

    # 10. Convert to Troop Loss (Final step)
    return compute_troop_loss(damage, defender.lineup.troop.unit_base_hp)
