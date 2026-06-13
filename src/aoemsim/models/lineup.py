"""Domain lineup model for AOEM Battle Simulator."""

from pydantic import BaseModel, Field, field_validator

from aoemsim.models.troop import Troop


class Lineup(BaseModel):
    """Represents a battle lineup containing heroes and a troop."""

    schema_version: str = Field(default="1.0", description="Schema version of the lineup document")
    name: str = Field(..., description="Name of the lineup configuration")
    commander_id: str = Field(..., description="ID of the hero acting as the commander")
    heroes: list[str] = Field(..., description="IDs of all heroes in the lineup")
    troop: Troop = Field(..., description="Pasukan/Troop assigned to the lineup")

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
