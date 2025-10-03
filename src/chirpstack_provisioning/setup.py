"""Setup file ingestion for ChirpStack provisioning.

This module handles parsing and extracting data from setup files that define
the hierarchical structure of tenants, applications, gateways, device profiles, etc.
"""

import json
from pathlib import Path
from typing import Any

import jsonschema


def validate_setup_data(setup_data: dict, schema_path: str | Path) -> None:
    """Validate setup data against the setup schema.

    Args:
        setup_data: The setup data to validate
        schema_path: Path to the setup.schema.json file

    Raises:
        jsonschema.ValidationError: If the data doesn't match the schema
    """
    schema_path = Path(schema_path).resolve()
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

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


def decompose_tenants(
    tenants: list[dict],
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """Decompose tenants into clean tenant objects and child entities.

    This function performs a single pass through the tenants list to extract
    all child entities (gateways, applications, device_profiles) and create
    clean tenant objects without nested children.

    Args:
        tenants: List of tenant objects

    Returns:
        Tuple containing:
        - List of clean tenant objects (without nested children)
        - List of gateway objects with tenant_id added
        - List of application objects with tenant_id added
        - List of device profile objects with tenant_id added
    """
    clean_tenants = []
    gateways = []
    applications = []
    device_profiles = []

    for tenant in tenants:
        tenant_id = tenant.get("id")

        # Extract and decompose gateways
        for gateway in tenant.get("gateways", []):
            gateway_copy = gateway.copy()
            gateway_copy["tenant_id"] = tenant_id
            gateways.append(gateway_copy)

        # Extract and decompose applications
        for app in tenant.get("applications", []):
            app_copy = app.copy()
            app_copy["tenant_id"] = tenant_id
            applications.append(app_copy)

        # Extract and decompose device profiles
        for profile in tenant.get("device_profiles", []):
            profile_copy = profile.copy()
            profile_copy["tenant_id"] = tenant_id
            device_profiles.append(profile_copy)

        # Create clean tenant without nested children
        tenant_copy = tenant.copy()
        tenant_copy.pop("gateways", None)
        tenant_copy.pop("applications", None)
        tenant_copy.pop("device_profiles", None)
        clean_tenants.append(tenant_copy)

    return clean_tenants, gateways, applications, device_profiles


def load_setup_file(file_path: str | Path) -> dict[str, Any]:
    """Load a setup file from disk.

    Args:
        file_path: Path to the setup JSON file

    Returns:
        Dictionary containing the setup data

    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    file_path = Path(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def ingest_setup_file(
    file_path: str | Path, schema_path: str | Path
) -> dict[str, list[dict]]:
    """Ingest a setup file and decompose it into individual messages.

    This function:
    1. Loads the setup file
    2. Validates it against the schema
    3. Extracts top-level entities (tenants, users, templates)
    4. Decomposes nested entities (gateways, applications, device_profiles)

    Args:
        file_path: Path to the setup JSON file
        schema_path: Path to the setup.schema.json file

    Returns:
        Dictionary containing decomposed entities:
        - 'tenants': List of tenant objects (without nested children)
        - 'users': List of global user objects
        - 'device_profile_templates': List of device profile template objects
        - 'gateways': List of gateway objects with tenant_id
        - 'applications': List of application objects with tenant_id
        - 'device_profiles': List of device profile objects with tenant_id

    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file is not valid JSON
        jsonschema.ValidationError: If the data doesn't match the schema
    """
    setup_data = load_setup_file(file_path)
    validate_setup_data(setup_data, schema_path)

    tenants = extract_tenants(setup_data)
    users = extract_global_users(setup_data)
    templates = extract_device_profile_templates(setup_data)

    # Decompose tenants in a single pass for efficiency
    clean_tenants, gateways, applications, device_profiles = decompose_tenants(tenants)

    return {
        "tenants": clean_tenants,
        "users": users,
        "device_profile_templates": templates,
        "gateways": gateways,
        "applications": applications,
        "device_profiles": device_profiles,
    }
