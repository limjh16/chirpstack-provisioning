"""Schema validation utilities for ChirpStack provisioning data."""

import json
from pathlib import Path


def load_schema(schema_path: str | Path) -> object:
    """Load a JSON schema from file.

    Args:
        schema_path: Path to the JSON schema file

    Returns:
        The loaded schema object
    """
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)
