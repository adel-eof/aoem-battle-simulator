"""Configuration and balance constants for the AOEM Battle Simulator engine."""

# Military Specialty Synergy Bonuses (Section 2.5)
# Applied when 2 or 3 heroes in a lineup share the same Military specialty.
MILITARY_SYNERGY_2_SAME = 0.20
MILITARY_SYNERGY_3_SAME = 0.30

# Unit Type Specialty Synergy Bonuses (Section 2.5)
# Applied based on how many heroes have a specialty matching the troop's unit type.
UNIT_TYPE_SYNERGY_1_MATCH = 0.05
UNIT_TYPE_SYNERGY_2_MATCH = 0.10
UNIT_TYPE_SYNERGY_3_MATCH = 0.15

# Stat conversion constants (Section 2.4)
STAT_TO_MODIFIER_RATE = 0.0015  # 0.15% per stat point
SKILL_STAT_TO_EFFECT_RATE = 0.0030  # 0.3% per stat point

# Counter and Damage Multipliers (Section 2.2, Section 7.1)
COUNTER_BONUS_RATE = 0.30
DAMAGE_VARIANCE_RANGE = (0.95, 1.05)

# Critical Hit Defaults (Section 7.1)
CRIT_CHANCE_DEFAULT = 0.0
CRIT_DAMAGE_DEFAULT = 1.50
CRIT_CHANCE_CAP = 0.75
