"""Domain models for buffs and debuffs."""

from typing import Any

from pydantic import BaseModel, Field

from aoemsim.models.enums import BuffStackPolicy, StatKind


class BuffEffect(BaseModel):
    """Configuration for a buff or debuff effect."""

    id: str  # Unique identifier for the effect type (e.g., 'might_boost')
    name: str
    stat_kind: StatKind | None = None
    value: float = 0.0
    duration_ticks: int = 0
    stack_policy: BuffStackPolicy = BuffStackPolicy.REFRESH
    max_stacks: int = 1

    # Optional fields for more complex effects
    params: dict[str, Any] = Field(default_factory=dict)
