"""Domain skill models for AOEM Battle Simulator."""

from typing import Any, Literal

from pydantic import BaseModel, Field

from aoemsim.models.enums import SkillSlot, TriggerType


class SkillEffect(BaseModel):
    """Represents a discrete effect applied by a skill."""

    kind: Literal[
        "damage",
        "heal",
        "buff",
        "debuff",
        "rage_gain",
        "cleanse",
        "summon",
        "dot",
        "shield",
        "chance_modifier",
        "damage_reduction",
    ]
    params: dict[str, Any] = Field(default_factory=dict)


class SkillTrigger(BaseModel):
    """Defines the triggering condition and timing for a skill."""

    type: TriggerType
    activation_chance: float = Field(default=1.0, ge=0.0, le=1.0)
    interval_sec: float | None = Field(default=None, ge=0.0)
    cooldown_sec: float | None = Field(default=None, ge=0.0)
    conditions: list[str] = Field(default_factory=list)


class Skill(BaseModel):
    """Represents a hero skill configuration."""

    id: str
    name: str
    slot: SkillSlot
    trigger: SkillTrigger
    rage_cost: int | None = Field(default=None, ge=0)
    target: Literal["self", "ally", "enemy", "front_3", "aoe", "random"] = "enemy"
    effects: list[SkillEffect] = Field(default_factory=list)
    description: str = ""
