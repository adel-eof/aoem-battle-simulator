"""Tests for the AOEM CLI entrypoint and validate command."""

from pathlib import Path

from typer.testing import CliRunner

from aoemsim.cli import app

runner = CliRunner()


def test_help_command_succeeds() -> None:
    """`aoemsim --help` should render help text and exit cleanly."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "AOEM battle simulator CLI." in result.stdout
    assert "Usage:" in result.stdout


def test_validate_help_shows_description() -> None:
    """`aoemsim validate --help` should show command description and path argument."""
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0
    assert "Validate" in result.stdout
    assert "PATH" in result.stdout


def test_validate_valid_hero(tmp_path: Path) -> None:
    """Validate a well-formed hero YAML file — exit code 0 and VALID status."""
    content = """\
schema_version: "1.0"
id: cyrus
name: Cyrus the Great
military: warrior
unit_types: [pikeman]
attributes:
  might: {base: 110.25, growth: 1.07}
  armor: {base: 85.69, growth: 0.86}
level: 1
skills: {}
"""
    hero_file = tmp_path / "hero.yaml"
    hero_file.write_text(content, encoding="utf-8")

    result = runner.invoke(app, ["validate", str(hero_file)])
    assert result.exit_code == 0
    assert "VALID" in result.stdout


def test_validate_valid_lineup(tmp_path: Path) -> None:
    """Validate a well-formed lineup YAML file — exit code 0 and VALID status."""
    content = """\
schema_version: "1.0"
name: Pike Stack
commander_id: cyrus
heroes: [cyrus, mansa, roland]
troop:
  unit_type: pikeman
  size: 130
"""
    lineup_file = tmp_path / "lineup.yaml"
    lineup_file.write_text(content, encoding="utf-8")

    result = runner.invoke(app, ["validate", str(lineup_file)])
    assert result.exit_code == 0
    assert "VALID" in result.stdout


def test_validate_invalid_schema_version(tmp_path: Path) -> None:
    """Validate a file with bad schema_version — exit code 1 and error message."""
    content = """\
schema_version: "9.0"
id: cyrus
name: Cyrus the Great
military: warrior
unit_types: [pikeman]
attributes: {}
"""
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text(content, encoding="utf-8")

    result = runner.invoke(app, ["validate", str(bad_file)])
    assert result.exit_code == 1
    assert "INVALID" in result.stdout
    assert "Unsupported schema_version" in result.stdout


def test_validate_missing_schema_version(tmp_path: Path) -> None:
    """Validate a file without schema_version — exit code 1 and helpful error."""
    content = """\
id: cyrus
name: Cyrus the Great
military: warrior
unit_types: [pikeman]
attributes: {}
"""
    bad_file = tmp_path / "no_version.yaml"
    bad_file.write_text(content, encoding="utf-8")

    result = runner.invoke(app, ["validate", str(bad_file)])
    assert result.exit_code == 1
    assert "INVALID" in result.stdout
    assert "schema_version" in result.stdout


def test_validate_nonexistent_file() -> None:
    """Validate a file path that does not exist — exit code non-zero."""
    result = runner.invoke(app, ["validate", "/tmp/does_not_exist_xyz.yaml"])
    assert result.exit_code != 0
