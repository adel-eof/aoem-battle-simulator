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
