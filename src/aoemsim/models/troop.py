"""Domain troop model for AOEM Battle Simulator."""

from pydantic import BaseModel, Field

from aoemsim.models.enums import UnitType


class Troop(BaseModel):
    """Represents a military troop configuration led by a commander."""

    unit_type: UnitType = Field(..., description="Type of unit in this troop")
    size: int = Field(default=130, ge=0, description="Number of troops/units")
    unit_base_attack: float = Field(
        default=100.0, ge=0.0, description="Base attack of a single unit"
    )
    unit_base_defense: float = Field(
        default=100.0, ge=0.0, description="Base defense of a single unit"
    )
    unit_base_hp: float = Field(default=1000.0, ge=0.0, description="Base HP of a single unit")
    speed: float = Field(default=100.0, ge=0.0, description="Movement/attack speed value")

    @property
    def total_hp(self) -> float:
        """Calculate total HP from size and base unit HP."""
        return self.size * self.unit_base_hp
