"""Command-line interface for AOEM battle simulator."""

from pathlib import Path
from typing import Annotated

import typer

from aoemsim.data.loader import load_yaml_document
from aoemsim.data.validators import check_unknown_fields, validate_schema_version

app = typer.Typer(
    name="aoemsim",
    help="AOEM battle simulator CLI.",
    no_args_is_help=True,
)


@app.callback()
def root() -> None:
    """Root command for AOEM simulator operations."""
    return None


def _print_validation_result(path: Path, *, success: bool, message: str) -> None:
    """Print a human-readable validation result to the console."""
    status = "✔ VALID" if success else "✘ INVALID"
    typer.echo(f"[{status}] {path}")
    if message:
        typer.echo(f"  {message}")


@app.command()
def validate(
    path: Annotated[
        Path,
        typer.Argument(
            help="Path to a YAML data file (hero or lineup) to validate.",
            exists=True,
            readable=True,
            resolve_path=True,
        ),
    ],
) -> None:
    """Validate a YAML data file (hero or lineup).

    Loads and validates schema_version, checks for unknown fields,
    and parses the document against the domain model.
    """
    try:
        data = load_yaml_document(path)

        if not isinstance(data, dict):
            _print_validation_result(
                path,
                success=False,
                message=f"Expected YAML root to be a mapping, got {type(data).__name__}.",
            )
            raise typer.Exit(code=1)

        validate_schema_version(data)
        check_unknown_fields(_detect_model(data), data)
        _parse_model(data)

    except typer.Exit:
        raise
    except ValueError as exc:
        _print_validation_result(path, success=False, message=str(exc))
        raise typer.Exit(code=1) from None
    except Exception as exc:  # noqa: BLE001
        _print_validation_result(path, success=False, message=str(exc))
        raise typer.Exit(code=1) from None

    _print_validation_result(path, success=True, message="Document is valid.")


def _detect_model(data: dict[str, object]) -> type:
    """Detect the target Pydantic model based on document fields."""
    from aoemsim.models import Hero, Lineup

    if "commander_id" in data or "troop" in data:
        return Lineup
    return Hero


def _parse_model(data: dict[str, object]) -> None:
    """Parse a raw dict into the appropriate domain model."""
    model_cls = _detect_model(data)
    model_cls(**data)


def main() -> None:
    """Run the CLI app."""
    app()
