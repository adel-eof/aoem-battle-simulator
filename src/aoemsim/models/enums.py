"""Domain enums for the AOEM Battle Simulator."""

from enum import StrEnum


class BuffStackPolicy(StrEnum):
    """Stacking policy for combat buffs and debuffs."""

    REPLACE = "replace"
    REPLACE_IF_STRONGER = "replace_if_stronger"
    REFRESH = "refresh"
    STACK = "stack"
    INDEPENDENT = "independent"


class Military(StrEnum):
    """Hero military specialty type."""

    WARRIOR = "warrior"
    MARSHAL = "marshal"
    TACTICIAN = "tactician"


class UnitType(StrEnum):
    """Troop and soldier unit classification."""

    SWORDSMAN = "swordsman"
    PIKEMAN = "pikeman"
    CAVALRY = "cavalry"
    ARCHER = "archer"


class SkillSlot(StrEnum):
    """Hero skill slot positions."""

    COMMANDER = "commander"
    SIGNATURE = "signature"
    CUSTOM_1 = "custom_1"
    CUSTOM_2 = "custom_2"


class TriggerType(StrEnum):
    """Conditions under which a skill is triggered."""

    ACTIVE = "active"
    TURN_BASED = "turn_based"
    SECONDARY_STRIKE = "secondary_strike"
    PASSIVE = "passive"


class StatKind(StrEnum):
    """Primary attributes and stats."""

    MIGHT = "might"
    ARMOR = "armor"
    STRATEGY = "strategy"
    SIEGE = "siege"
    MIGHT_DEFENSE = "might_defense"
    STRATEGY_DEFENSE = "strategy_defense"
    CRIT_CHANCE = "crit_chance"
    CRIT_DAMAGE = "crit_damage"
    MAX_RAGE = "max_rage"
    RAGE_REGEN = "rage_regen"


class CcType(StrEnum):
    """Types of Crowd Control."""

    SILENCE = "silence"
    DISARM = "disarm"
    INCAPACITATION = "incapacitation"
