"""
JSON schema definitions for ChirpStack provisioning data.

This module defines the JSON schemas used to validate input data for provisioning
ChirpStack devices, gateways, and related entities.
"""

from pathlib import Path
import json

# Get the directory where this module is located
_SCHEMA_DIR = Path(__file__).parent / "schemas"

def load_schema(schema_name: str) -> dict:
    """Load a JSON schema from the schemas directory.
    
    Args:
        schema_name: Name of the schema file (without .json extension)
        
    Returns:
        The loaded JSON schema as a dictionary
        
    Raises:
        FileNotFoundError: If the schema file doesn't exist
        json.JSONDecodeError: If the schema file is not valid JSON
    """
    schema_path = _SCHEMA_DIR / f"{schema_name}.json"
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_device_schema() -> dict:
    """Get the JSON schema for device provisioning data."""
    return load_schema("device")

def get_gateway_schema() -> dict:
    """Get the JSON schema for gateway provisioning data."""
    return load_schema("gateway")

def get_tenant_schema() -> dict:
    """Get the JSON schema for tenant data."""
    return load_schema("tenant")

def get_application_schema() -> dict:
    """Get the JSON schema for application data."""
    return load_schema("application")

def get_device_profile_schema() -> dict:
    """Get the JSON schema for device profile data."""
    return load_schema("device_profile")