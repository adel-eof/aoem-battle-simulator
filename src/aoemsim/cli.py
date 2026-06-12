"""Command-line interface for AOEM battle simulator."""

import typer

app = typer.Typer(
    name="aoemsim",
    help="AOEM battle simulator CLI.",
    no_args_is_help=True,
)


@app.callback()
def root() -> None:
    """Root command for AOEM simulator operations."""
    return None


def main() -> None:
    """Run the CLI app."""
    app()
