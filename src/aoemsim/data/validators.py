"""Validators for schema version and unrecognized fields."""

import logging
import warnings
from typing import Any, get_args, get_origin

from pydantic import BaseModel

logger = logging.getLogger("aoemsim.data")


def validate_schema_version(data: dict[str, Any]) -> None:
    """Validate that the root schema_version is within the supported range (1.x - 2.x)."""
    schema_version = data.get("schema_version")
    if schema_version is None:
        raise ValueError("Unsupported schema_version: None. Supported range: 1.x - 2.x.")

    parts = str(schema_version).split(".")
    try:
        major = int(parts[0])
    except (ValueError, IndexError) as err:
        raise ValueError(
            f"Unsupported schema_version: {schema_version}. Supported range: 1.x - 2.x."
        ) from err

    if major not in (1, 2):
        raise ValueError(
            f"Unsupported schema_version: {schema_version}. Supported range: 1.x - 2.x."
        )


def _get_base_model_classes(annotation: Any) -> list[type[BaseModel]]:
    """Extract Pydantic BaseModel classes from a type annotation."""
    if annotation is None:
        return []

    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return [annotation]

    origin = get_origin(annotation)
    if origin is not None:
        classes = []
        for arg in get_args(annotation):
            classes.extend(_get_base_model_classes(arg))
        return classes

    return []


def check_unknown_fields(model_cls: type[BaseModel], data: Any) -> None:
    """Recursively check for unknown fields in the input data relative to a BaseModel."""
    if not isinstance(data, dict):
        return

    allowed_fields = set(model_cls.model_fields.keys())
    for key, val in data.items():
        if key not in allowed_fields:
            msg = f"Unknown field {key} ignored."
            warnings.warn(msg, UserWarning, stacklevel=2)
            logger.warning(msg)
            continue

        field_info = model_cls.model_fields[key]
        annotation = field_info.annotation
        if annotation is None:
            continue

        sub_models = _get_base_model_classes(annotation)
        if not sub_models:
            continue

        sub_model = sub_models[0]

        if isinstance(val, dict):
            origin = get_origin(annotation)
            # Check if annotation is a dict/mapping (e.g. dict[StatKind, Stat])
            if origin is dict or origin is dict:
                for sub_val in val.values():
                    check_unknown_fields(sub_model, sub_val)
            else:
                check_unknown_fields(sub_model, val)
        elif isinstance(val, list):
            for sub_val in val:
                check_unknown_fields(sub_model, sub_val)
