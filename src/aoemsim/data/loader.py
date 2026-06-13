"""YAML loader with safe parsing and !include support."""

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]


class AoeSafeLoader(yaml.SafeLoader):  # type: ignore[misc]
    """Safe YAML loader with !include tag support."""

    def __init__(self, stream: Any) -> None:
        self._root = None
        if hasattr(stream, "name") and stream.name:
            self._root = Path(stream.name).parent
        super().__init__(stream)


def include_constructor(loader: AoeSafeLoader, node: yaml.Node) -> Any:
    """Constructor to resolve !include relative to the parent file."""
    filename = loader.construct_scalar(node)
    if not isinstance(filename, str):
        raise yaml.constructor.ConstructorError(
            None, None, f"Expected a string for !include tag, got {type(filename)}", node.start_mark
        )

    if loader._root:
        file_path = loader._root / filename
    else:
        file_path = Path(filename)

    return load_yaml_document(file_path)


AoeSafeLoader.add_constructor("!include", include_constructor)


def load_yaml_document(path: Path | str) -> Any:
    """Load and parse a YAML file using AoeSafeLoader."""
    file_path = Path(path)
    with open(file_path, encoding="utf-8") as f:
        return yaml.load(f, Loader=AoeSafeLoader)
