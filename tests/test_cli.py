"""Tests for the AOEM CLI entrypoint."""

from typer.testing import CliRunner

from aoemsim.cli import app

runner = CliRunner()


def test_help_command_succeeds() -> None:
    """`aoemsim --help` should render help text and exit cleanly."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "AOEM battle simulator CLI." in result.stdout
    assert "Usage:" in result.stdout
