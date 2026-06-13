"""Domain stat model representing attributes with base and growth values."""

from pydantic import BaseModel, Field


class Stat(BaseModel):
    """Represents a hero attribute that scales with level."""

    base: float = Field(ge=0.0, description="Base attribute value at level 1")
    growth: float = Field(default=0.0, description="Attribute growth per level")

    def at(self, level: int) -> float:
        """Calculate the effective stat value at a specific level.

        Formula: Effective_Stat = Base + Growth * (Level - 1)
        """
        if level < 1:
            raise ValueError("Level must be greater than or equal to 1")
        return self.base + self.growth * (level - 1)
