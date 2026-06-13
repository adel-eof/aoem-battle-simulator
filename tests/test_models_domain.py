"""Unit tests for AOEM Battle Simulator domain models."""

import pytest
from pydantic import ValidationError

from aoemsim.models import (
    Hero,
    Lineup,
    Military,
    Skill,
    SkillEffect,
    SkillSlot,
    SkillTrigger,
    Stat,
    StatKind,
    TriggerType,
    Troop,
    UnitType,
)


def test_valid_parsing_all_models() -> None:
    """Test parsing of valid dictionaries for all domain models."""
    # Test Stat
    stat = Stat(base=100.0, growth=1.5)
    assert stat.base == 100.0
    assert stat.growth == 1.5

    # Test SkillTrigger & Effect
    trigger = SkillTrigger(
        type=TriggerType.ACTIVE,
        activation_chance=0.65,
        cooldown_sec=5.0,
    )
    effect = SkillEffect(kind="damage", params={"rate": 1.1026})
    skill = Skill(
        id="cyrus_cmd",
        name="Isolated Green Vine",
        slot=SkillSlot.COMMANDER,
        trigger=trigger,
        rage_cost=250,
        effects=[effect],
    )
    assert skill.id == "cyrus_cmd"

    # Test Hero
    hero_data = {
        "schema_version": "1.0",
        "id": "cyrus",
        "name": "Cyrus the Great",
        "military": "warrior",
        "unit_types": ["pikeman"],
        "level": 1,
        "attributes": {
            "might": {"base": 110.25, "growth": 1.07},
            "armor": {"base": 85.69, "growth": 0.86},
        },
        "skills": {
            "commander": {
                "id": "cyrus_cmd",
                "name": "Isolated Green Vine",
                "slot": "commander",
                "trigger": {
                    "type": "active",
                    "activation_chance": 1.0,
                },
                "effects": [
                    {
                        "kind": "damage",
                        "params": {"rate": 1.1026},
                    }
                ],
            }
        },
    }
    hero = Hero(**hero_data)
    assert hero.id == "cyrus"
    assert hero.stat(StatKind.MIGHT) == 110.25

    # Test Troop
    troop = Troop(unit_type=UnitType.PIKEMAN, size=130)
    assert troop.total_hp == 130000.0

    # Test Lineup
    lineup = Lineup(
        schema_version="2.0",
        name="Cyrus Pike Stack",
        commander_id="cyrus",
        heroes=["cyrus", "mansa", "roland"],
        troop=troop,
    )
    assert lineup.name == "Cyrus Pike Stack"


def test_invalid_types_and_missing_fields() -> None:
    """Test validation errors for invalid types and missing required fields."""
    # Missing required field id in Hero
    with pytest.raises(ValidationError) as exc_info:
        Hero(
            name="Cyrus the Great",
            military=Military.WARRIOR,
            unit_types=[UnitType.PIKEMAN],
            attributes={},
        )
    assert "id" in str(exc_info.value)
    assert "Field required" in str(exc_info.value)

    # Invalid type for military specialty
    with pytest.raises(ValidationError) as exc_info:
        Hero(
            id="cyrus",
            name="Cyrus the Great",
            military="invalid_specialty",  # type: ignore[arg-type]
            unit_types=[UnitType.PIKEMAN],
            attributes={},
        )
    assert "military" in str(exc_info.value)

    # Invalid boundary: negative base stat
    with pytest.raises(ValidationError) as exc_info:
        Stat(base=-10.0, growth=1.0)
    assert "base" in str(exc_info.value)

    # Invalid boundary: activation chance out of range
    with pytest.raises(ValidationError) as exc_info:
        SkillTrigger(type=TriggerType.ACTIVE, activation_chance=1.5)
    assert "activation_chance" in str(exc_info.value)

    # Invalid boundary: negative hero level
    with pytest.raises(ValidationError) as exc_info:
        Hero(
            id="cyrus",
            name="Cyrus the Great",
            military=Military.WARRIOR,
            unit_types=[UnitType.PIKEMAN],
            attributes={},
            level=0,
        )
    assert "level" in str(exc_info.value)


def test_stat_formula_calculation() -> None:
    """Test the effective stat calculation formula: Base + Growth * (Level - 1)."""
    # 1. Direct Stat model check
    stat = Stat(base=110.25, growth=1.07)
    # level = 10 -> 110.25 + 1.07 * 9 = 110.25 + 9.63 = 119.88
    assert pytest.approx(stat.at(10)) == 119.88

    # Check level < 1 raises ValueError
    with pytest.raises(ValueError, match="Level must be greater than or equal to 1"):
        stat.at(0)

    # 2. Hero helper method check
    hero = Hero(
        id="cyrus",
        name="Cyrus the Great",
        military=Military.WARRIOR,
        unit_types=[UnitType.PIKEMAN],
        attributes={
            StatKind.MIGHT: Stat(base=110.25, growth=1.07),
        },
        level=10,
    )
    assert pytest.approx(hero.stat(StatKind.MIGHT)) == 119.88

    # Querying missing stat kind
    with pytest.raises(ValueError, match="Attribute 'armor' is missing for hero 'cyrus'"):
        hero.stat(StatKind.ARMOR)


def test_schema_version_validation() -> None:
    """Verify that schema_version validates correctly (1.x - 2.x allowed)."""
    # Valid versions (1.x and 2.x)
    hero_1 = Hero(
        schema_version="1.0",
        id="cyrus",
        name="Cyrus the Great",
        military=Military.WARRIOR,
        unit_types=[UnitType.PIKEMAN],
        attributes={},
    )
    assert hero_1.schema_version == "1.0"

    hero_2 = Hero(
        schema_version="2.15",
        id="cyrus",
        name="Cyrus the Great",
        military=Military.WARRIOR,
        unit_types=[UnitType.PIKEMAN],
        attributes={},
    )
    assert hero_2.schema_version == "2.15"

    # Invalid version (e.g. 3.0 or non-numeric)
    with pytest.raises(ValidationError) as exc_info:
        Hero(
            schema_version="3.0",
            id="cyrus",
            name="Cyrus the Great",
            military=Military.WARRIOR,
            unit_types=[UnitType.PIKEMAN],
            attributes={},
        )
    assert "Unsupported schema_version: 3.0. Supported range: 1.x - 2.x." in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        Hero(
            schema_version="abc",
            id="cyrus",
            name="Cyrus the Great",
            military=Military.WARRIOR,
            unit_types=[UnitType.PIKEMAN],
            attributes={},
        )
    assert "Unsupported schema_version: abc. Supported range: 1.x - 2.x." in str(exc_info.value)
