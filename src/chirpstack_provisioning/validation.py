"""
Data validation utilities for ChirpStack provisioning.

This module provides utilities for validating input data against JSON schemas.
"""

from typing import Any, Dict, List, Union
import jsonschema
from jsonschema import ValidationError

from .schemas import (
    get_device_schema,
    get_gateway_schema,
    get_tenant_schema,
    get_application_schema,
    get_device_profile_schema,
)


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def __bool__(self) -> bool:
        return self.is_valid
    
    def __str__(self) -> str:
        if self.is_valid:
            return "Valid"
        return f"Invalid: {'; '.join(self.errors)}"


def validate_data(data: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
    """Validate data against a JSON schema.
    
    Args:
        data: The data to validate
        schema: The JSON schema to validate against
        
    Returns:
        ValidationResult indicating if the data is valid and any errors
    """
    try:
        jsonschema.validate(data, schema)
        return ValidationResult(True)
    except ValidationError as e:
        errors = [str(e.message)]
        
        # Collect additional validation errors if there are multiple
        for error in e.context:
            errors.append(str(error.message))
            
        return ValidationResult(False, errors)
    except jsonschema.SchemaError as e:
        return ValidationResult(False, [f"Schema error: {e.message}"])


def validate_device(data: Dict[str, Any]) -> ValidationResult:
    """Validate device data against the device schema.
    
    Args:
        data: Device data to validate
        
    Returns:
        ValidationResult indicating if the data is valid
    """
    schema = get_device_schema()
    return validate_data(data, schema)


def validate_gateway(data: Dict[str, Any]) -> ValidationResult:
    """Validate gateway data against the gateway schema.
    
    Args:
        data: Gateway data to validate
        
    Returns:
        ValidationResult indicating if the data is valid
    """
    schema = get_gateway_schema()
    return validate_data(data, schema)


def validate_tenant(data: Dict[str, Any]) -> ValidationResult:
    """Validate tenant data against the tenant schema.
    
    Args:
        data: Tenant data to validate
        
    Returns:
        ValidationResult indicating if the data is valid
    """
    schema = get_tenant_schema()
    return validate_data(data, schema)


def validate_application(data: Dict[str, Any]) -> ValidationResult:
    """Validate application data against the application schema.
    
    Args:
        data: Application data to validate
        
    Returns:
        ValidationResult indicating if the data is valid
    """
    schema = get_application_schema()
    return validate_data(data, schema)


def validate_device_profile(data: Dict[str, Any]) -> ValidationResult:
    """Validate device profile data against the device profile schema.
    
    Args:
        data: Device profile data to validate
        
    Returns:
        ValidationResult indicating if the data is valid
    """
    schema = get_device_profile_schema()
    return validate_data(data, schema)


def validate_batch(
    data_list: List[Dict[str, Any]], 
    entity_type: str
) -> List[ValidationResult]:
    """Validate a batch of data items.
    
    Args:
        data_list: List of data items to validate
        entity_type: Type of entity ('device', 'gateway', 'tenant', 'application', 'device_profile')
        
    Returns:
        List of ValidationResult objects, one for each data item
        
    Raises:
        ValueError: If entity_type is not supported
    """
    validators = {
        'device': validate_device,
        'gateway': validate_gateway,
        'tenant': validate_tenant,
        'application': validate_application,
        'device_profile': validate_device_profile,
    }
    
    if entity_type not in validators:
        raise ValueError(f"Unsupported entity type: {entity_type}")
    
    validator = validators[entity_type]
    return [validator(data) for data in data_list]


def detect_entity_type(data: Dict[str, Any]) -> Union[str, None]:
    """Attempt to detect the entity type based on the data structure.
    
    Args:
        data: Data dictionary to analyze
        
    Returns:
        The detected entity type or None if unable to determine
    """
    # Check for unique identifiers
    if 'dev_eui' in data:
        return 'device'
    elif 'gateway_id' in data:
        return 'gateway'
    elif 'name' in data:
        # Check for entity-specific fields to disambiguate
        if 'region' in data or 'mac_version' in data:
            return 'device_profile'
        elif 'can_have_gateways' in data or 'max_device_count' in data:
            return 'tenant'
        elif 'tenant_id' in data or 'tenant_name' in data:
            return 'application'
        # Default to tenant if just has a name
        return 'tenant'
    
    return None