"""Setup file ingestion for ChirpStack provisioning.

This module handles parsing and extracting data from setup files that define
the hierarchical structure of tenants, applications, gateways, device profiles, etc.
"""

import json
from pathlib import Path

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


def decompose_gateways(tenants: list[dict]) -> list[dict]:
    """Decompose gateways from tenants into individual gateway objects.

    Each gateway is extracted from its parent tenant and the tenant_id
    is added to the gateway object for reference.

    Args:
        tenants: List of tenant objects

    Returns:
        List of gateway objects with tenant_id added
    """
    gateways = []
    for tenant in tenants:
        tenant_id = tenant.get("id")
        tenant_gateways = tenant.get("gateways", [])
        for gateway in tenant_gateways:
            gateway_copy = gateway.copy()
            gateway_copy["tenant_id"] = tenant_id
            gateways.append(gateway_copy)
    return gateways


def decompose_applications(tenants: list[dict]) -> list[dict]:
    """Decompose applications from tenants into individual application objects.

    Each application is extracted from its parent tenant and the tenant_id
    is added to the application object for reference.

    Args:
        tenants: List of tenant objects

    Returns:
        List of application objects with tenant_id added
    """
    applications = []
    for tenant in tenants:
        tenant_id = tenant.get("id")
        tenant_apps = tenant.get("applications", [])
        for app in tenant_apps:
            app_copy = app.copy()
            app_copy["tenant_id"] = tenant_id
            applications.append(app_copy)
    return applications


def decompose_device_profiles(tenants: list[dict]) -> list[dict]:
    """Decompose device profiles from tenants into individual profile objects.

    Each device profile is extracted from its parent tenant and the tenant_id
    is added to the profile object for reference.

    Args:
        tenants: List of tenant objects

    Returns:
        List of device profile objects with tenant_id added
    """
    profiles = []
    for tenant in tenants:
        tenant_id = tenant.get("id")
        tenant_profiles = tenant.get("device_profiles", [])
        for profile in tenant_profiles:
            profile_copy = profile.copy()
            profile_copy["tenant_id"] = tenant_id
            profiles.append(profile_copy)
    return profiles
