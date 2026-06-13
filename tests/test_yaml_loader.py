"""Unit tests for YAML loader, schema validator, and unknown fields warning."""

from pathlib import Path

import pytest

from aoemsim.data.repositories import load_hero


def test_yaml_include_resolved(tmp_path: Path) -> None:
    """Test that !include references resolve correctly relative to the parent file."""
    # Create child file
    child_content = """
    id: child_skill
    name: Child Skill
    slot: commander
    trigger:
      type: active
      activation_chance: 0.65
    effects:
      - kind: damage
        params: {rate: 1.1}
    """
    child_file = tmp_path / "child.yaml"
    child_file.write_text(child_content, encoding="utf-8")

    # Create parent file referencing the child
    parent_content = f"""
    schema_version: "1.0"
    id: cyrus
    name: Cyrus the Great
    military: warrior
    unit_types: [pikeman]
    attributes:
      might: {{base: 110.25, growth: 1.07}}
      armor: {{base: 85.69, growth: 0.86}}
    level: 1
    skills:
      commander: !include {child_file.name}
    """
    parent_file = tmp_path / "parent.yaml"
    parent_file.write_text(parent_content, encoding="utf-8")

    # Load hero using parent_file
    hero = load_hero(parent_file)
    assert hero.id == "cyrus"
    assert hero.skills["commander"].id == "child_skill"
    assert hero.skills["commander"].trigger.activation_chance == 0.65


def test_schema_version_validation(tmp_path: Path) -> None:
    """Test that invalid or missing schema versions fail fast with expected message."""
    # Missing schema_version
    file_missing = tmp_path / "missing.yaml"
    file_missing.write_text(
        """
    id: cyrus
    name: Cyrus the Great
    """,
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as exc_info:
        load_hero(file_missing)
    assert "Unsupported schema_version: None. Supported range: 1.x - 2.x." in str(exc_info.value)

    # Incompatible schema_version 3.0
    file_v3 = tmp_path / "v3.yaml"
    file_v3.write_text(
        """
    schema_version: "3.0"
    id: cyrus
    name: Cyrus the Great
    """,
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as exc_info:
        load_hero(file_v3)
    assert "Unsupported schema_version: 3.0. Supported range: 1.x - 2.x." in str(exc_info.value)

    # Non-numeric schema_version
    file_invalid = tmp_path / "invalid.yaml"
    file_invalid.write_text(
        """
    schema_version: "abc"
    id: cyrus
    name: Cyrus the Great
    """,
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as exc_info:
        load_hero(file_invalid)
    assert "Unsupported schema_version: abc. Supported range: 1.x - 2.x." in str(exc_info.value)


def test_unknown_fields_warning(tmp_path: Path) -> None:
    """Test that unknown fields trigger a warning but are otherwise ignored."""
    content = """
    schema_version: "1.0"
    id: cyrus
    name: Cyrus the Great
    military: warrior
    unit_types: [pikeman]
    attributes:
      might: {base: 110.25, growth: 1.07}
    level: 1
    gear: "shield"  # Unknown field
    skills:
      commander:
        id: cyrus_cmd
        name: Isolated Green Vine
        slot: commander
        trigger:
          type: active
          activation_chance: 1.0
        effects:
          - kind: damage
            params: {rate: 1.1026}
            extra_param: 123  # Unknown field in SkillEffect
    """
    file_path = tmp_path / "hero.yaml"
    file_path.write_text(content, encoding="utf-8")

    # Load hero and verify warnings are emitted
    with pytest.warns(UserWarning) as record:
        hero = load_hero(file_path)

    # Check that the hero parsed successfully
    assert hero.id == "cyrus"

    # Verify the warning messages
    warnings_list = [str(w.message) for w in record]
    assert any("Unknown field gear ignored." in w for w in warnings_list)
    assert any("Unknown field extra_param ignored." in w for w in warnings_list)
