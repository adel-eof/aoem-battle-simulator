# aoem-battle-simulator

Project skeleton for an AOEM battle simulator, including a Typer-based CLI,
baseline QA tooling, and policy documentation for future milestones.

## Requirements

- Python 3.12+
- `uv` package manager

## Setup

```bash
uv sync --extra dev
```

## Run CLI

```bash
uv run aoemsim --help
```

## Quality Checks

```bash
uv run ruff check .
uv run mypy src
uv run pytest
```

## Project Structure

```text
src/
	aoemsim/
		__init__.py
		cli.py
tests/
docs/
```
