"""Data repositories for loading domain models from files."""

from pathlib import Path

from aoemsim.data.loader import load_yaml_document
from aoemsim.data.validators import check_unknown_fields, validate_schema_version
from aoemsim.models import Hero, Lineup


def load_hero(path: Path | str) -> Hero:
    """Load, validate, and parse a Hero domain model from a YAML file."""
    data = load_yaml_document(path)
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML root to be a dictionary, got {type(data)}")

    validate_schema_version(data)
    check_unknown_fields(Hero, data)
    return Hero(**data)


def load_lineup(path: Path | str) -> Lineup:
    """Load, validate, and parse a Lineup domain model from a YAML file."""
    data = load_yaml_document(path)
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML root to be a dictionary, got {type(data)}")

    validate_schema_version(data)
    check_unknown_fields(Lineup, data)
    return Lineup(**data)
