"""Domain hero model for AOEM Battle Simulator."""

from pydantic import BaseModel, Field, field_validator

from aoemsim.models.enums import Military, SkillSlot, StatKind, UnitType
from aoemsim.models.skill import Skill
from aoemsim.models.stat import Stat


class Hero(BaseModel):
    """Represents a Hero character with attributes and skills."""

    schema_version: str = Field(default="1.0", description="Schema version of the hero document")
    id: str = Field(..., description="Unique identifier for the hero")
    name: str = Field(..., description="Display name of the hero")
    military: Military = Field(..., description="Military specialty type")
    unit_types: list[UnitType] = Field(..., description="Supported unit type specialties")
    attributes: dict[StatKind, Stat] = Field(..., description="Hero base stats and scaling")
    level: int = Field(default=1, ge=1, description="Current hero level")
    skills: dict[SkillSlot, Skill] = Field(default_factory=dict, description="Equipped skills")

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, v: str) -> str:
        """Validate that the schema version is within the supported range (1.x - 2.x)."""
        parts = v.split(".")
        try:
            major = int(parts[0])
        except ValueError as err:
            raise ValueError(
                f"Unsupported schema_version: {v}. Supported range: 1.x - 2.x. "
                f"Please check and upgrade or migrate the schema."
            ) from err
        if major not in (1, 2):
            raise ValueError(
                f"Unsupported schema_version: {v}. Supported range: 1.x - 2.x. "
                f"Please check and upgrade or migrate the schema."
            )
        return v

    def stat(self, k: StatKind) -> float:
        """Calculate the effective stat value of a given StatKind at current hero level."""
        if k not in self.attributes:
            raise ValueError(f"Attribute '{k}' is missing for hero '{self.id}'")
        return self.attributes[k].at(self.level)
