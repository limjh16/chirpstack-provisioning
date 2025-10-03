"""Setup file ingestion for ChirpStack provisioning.

This module handles reading and parsing the setup.json file that defines
the hierarchical structure of tenants, applications, gateways, device profiles, etc.
"""

import json
from pathlib import Path

import jsonschema

from .schema import load_schema


def load_setup_file(file_path: str | Path) -> dict:
    """Load and parse a setup file.

    Args:
        file_path: Path to the setup.json file

    Returns:
        Parsed setup data as a dictionary

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_setup_data(setup_data: dict, schema_path: str | Path) -> None:
    """Validate setup data against the setup schema.

    Args:
        setup_data: The setup data to validate
        schema_path: Path to the setup.schema.json file

    Raises:
        jsonschema.ValidationError: If the data doesn't match the schema
    """
    schema_path = Path(schema_path).resolve()
    schema = load_schema(schema_path)

    # Create a resolver to handle $ref references relative to the schema file
    resolver = jsonschema.RefResolver(
        base_uri=schema_path.as_uri(),
        referrer=schema,
    )

    validator = jsonschema.Draft202012Validator(schema, resolver=resolver)
    validator.validate(setup_data)


def extract_tenants(setup_data: dict) -> list[dict]:
    """Extract tenant information from setup data.

    Args:
        setup_data: The setup data dictionary

    Returns:
        List of tenant objects
    """
    return setup_data.get("tenants", [])


def extract_global_users(setup_data: dict) -> list[dict]:
    """Extract global user information from setup data.

    Args:
        setup_data: The setup data dictionary

    Returns:
        List of global user objects
    """
    return setup_data.get("users", [])


def extract_device_profile_templates(setup_data: dict) -> list[dict]:
    """Extract device profile templates from setup data.

    Args:
        setup_data: The setup data dictionary

    Returns:
        List of device profile template objects
    """
    return setup_data.get("device_profile_templates", [])
