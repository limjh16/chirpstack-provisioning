"""
Tests for JSON schema definitions and validation.
"""

import pytest
from chirpstack_provisioning.schemas import (
    get_device_schema,
    get_gateway_schema,
    get_tenant_schema,
    get_application_schema,
    get_device_profile_schema,
)
from chirpstack_provisioning.validation import (
    validate_device,
    validate_gateway,
    validate_tenant,
    validate_application,
    validate_device_profile,
    detect_entity_type,
    validate_batch,
)


class TestDeviceSchema:
    """Tests for device schema validation."""
    
    def test_valid_device_minimal(self):
        """Test validation of minimal valid device."""
        device = {
            "dev_eui": "0123456789ABCDEF",
            "device_name": "Test Device",
            "app_key": "0123456789ABCDEF0123456789ABCDEF",
            "tenant_name": "test-tenant",
            "application_name": "test-app",
            "device_profile_name": "test-profile"
        }
        result = validate_device(device)
        assert result.is_valid, f"Validation failed: {result.errors}"
    
    def test_valid_device_with_ids(self):
        """Test validation of device with UUIDs instead of names."""
        device = {
            "dev_eui": "0123456789ABCDEF",
            "device_name": "Test Device",
            "app_key": "0123456789ABCDEF0123456789ABCDEF",
            "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
            "application_id": "550e8400-e29b-41d4-a716-446655440001",
            "device_profile_id": "550e8400-e29b-41d4-a716-446655440002"
        }
        result = validate_device(device)
        assert result.is_valid, f"Validation failed: {result.errors}"
    
    def test_valid_device_full(self):
        """Test validation of device with all optional fields."""
        device = {
            "dev_eui": "0123456789ABCDEF",
            "device_name": "Test Device",
            "description": "A test device for validation",
            "app_key": "0123456789ABCDEF0123456789ABCDEF",
            "app_eui": "FEDCBA9876543210",
            "tenant_name": "test-tenant",
            "application_name": "test-app",
            "device_profile_name": "test-profile",
            "variables": {"var1": "value1", "var2": "value2"},
            "tags": {"environment": "test", "version": "1.0"},
            "is_disabled": False,
            "skip_fcnt_check": True
        }
        result = validate_device(device)
        assert result.is_valid, f"Validation failed: {result.errors}"
    
    def test_invalid_device_missing_dev_eui(self):
        """Test validation fails when dev_eui is missing."""
        device = {
            "device_name": "Test Device",
            "app_key": "0123456789ABCDEF0123456789ABCDEF",
            "tenant_name": "test-tenant",
            "application_name": "test-app",
            "device_profile_name": "test-profile"
        }
        result = validate_device(device)
        assert not result.is_valid
        assert any("dev_eui" in error for error in result.errors)
    
    def test_invalid_device_bad_dev_eui_format(self):
        """Test validation fails with invalid dev_eui format."""
        device = {
            "dev_eui": "invalid_eui",
            "device_name": "Test Device",
            "app_key": "0123456789ABCDEF0123456789ABCDEF",
            "tenant_name": "test-tenant",
            "application_name": "test-app",
            "device_profile_name": "test-profile"
        }
        result = validate_device(device)
        assert not result.is_valid
    
    def test_invalid_device_bad_app_key_format(self):
        """Test validation fails with invalid app_key format."""
        device = {
            "dev_eui": "0123456789ABCDEF",
            "device_name": "Test Device",
            "app_key": "invalid_key",
            "tenant_name": "test-tenant",
            "application_name": "test-app",
            "device_profile_name": "test-profile"
        }
        result = validate_device(device)
        assert not result.is_valid
    
    def test_invalid_device_missing_tenant_info(self):
        """Test validation fails when both tenant_id and tenant_name are missing."""
        device = {
            "dev_eui": "0123456789ABCDEF",
            "device_name": "Test Device",
            "app_key": "0123456789ABCDEF0123456789ABCDEF",
            "application_name": "test-app",
            "device_profile_name": "test-profile"
        }
        result = validate_device(device)
        assert not result.is_valid


class TestGatewaySchema:
    """Tests for gateway schema validation."""
    
    def test_valid_gateway_minimal(self):
        """Test validation of minimal valid gateway."""
        gateway = {
            "gateway_id": "0123456789ABCDEF",
            "gateway_name": "Test Gateway",
            "tenant_name": "test-tenant"
        }
        result = validate_gateway(gateway)
        assert result.is_valid, f"Validation failed: {result.errors}"
    
    def test_valid_gateway_full(self):
        """Test validation of gateway with all fields."""
        gateway = {
            "gateway_id": "0123456789ABCDEF",
            "gateway_name": "Test Gateway",
            "description": "A test gateway",
            "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
            "latitude": 52.520008,
            "longitude": 13.404954,
            "altitude": 100.0,
            "stats_interval": 30,
            "tags": {"location": "Berlin", "owner": "test"},
            "metadata": {"version": "1.0", "model": "test-model"}
        }
        result = validate_gateway(gateway)
        assert result.is_valid, f"Validation failed: {result.errors}"
    
    def test_invalid_gateway_bad_coordinates(self):
        """Test validation fails with invalid coordinates."""
        gateway = {
            "gateway_id": "0123456789ABCDEF",
            "gateway_name": "Test Gateway",
            "tenant_name": "test-tenant",
            "latitude": 100.0,  # Invalid: > 90
            "longitude": 200.0  # Invalid: > 180
        }
        result = validate_gateway(gateway)
        assert not result.is_valid


class TestTenantSchema:
    """Tests for tenant schema validation."""
    
    def test_valid_tenant_minimal(self):
        """Test validation of minimal valid tenant."""
        tenant = {
            "name": "test-tenant"
        }
        result = validate_tenant(tenant)
        assert result.is_valid, f"Validation failed: {result.errors}"
    
    def test_valid_tenant_full(self):
        """Test validation of tenant with all fields."""
        tenant = {
            "name": "test-tenant",
            "description": "A test tenant",
            "can_have_gateways": True,
            "max_device_count": 1000,
            "max_gateway_count": 10,
            "tags": {"environment": "test"}
        }
        result = validate_tenant(tenant)
        assert result.is_valid, f"Validation failed: {result.errors}"


class TestApplicationSchema:
    """Tests for application schema validation."""
    
    def test_valid_application(self):
        """Test validation of valid application."""
        application = {
            "name": "test-app",
            "tenant_name": "test-tenant"
        }
        result = validate_application(application)
        assert result.is_valid, f"Validation failed: {result.errors}"


class TestDeviceProfileSchema:
    """Tests for device profile schema validation."""
    
    def test_valid_device_profile(self):
        """Test validation of valid device profile."""
        profile = {
            "name": "test-profile",
            "region": "EU868",
            "tenant_name": "test-tenant"
        }
        result = validate_device_profile(profile)
        assert result.is_valid, f"Validation failed: {result.errors}"
    
    def test_invalid_device_profile_bad_region(self):
        """Test validation fails with invalid region."""
        profile = {
            "name": "test-profile",
            "region": "INVALID",
            "tenant_name": "test-tenant"
        }
        result = validate_device_profile(profile)
        assert not result.is_valid


class TestEntityDetection:
    """Tests for entity type detection."""
    
    def test_detect_device(self):
        """Test detection of device entity."""
        data = {"dev_eui": "0123456789ABCDEF", "device_name": "Test"}
        assert detect_entity_type(data) == "device"
    
    def test_detect_gateway(self):
        """Test detection of gateway entity."""
        data = {"gateway_id": "0123456789ABCDEF", "gateway_name": "Test"}
        assert detect_entity_type(data) == "gateway"
    
    def test_detect_device_profile(self):
        """Test detection of device profile entity."""
        data = {"name": "test-profile", "region": "EU868"}
        assert detect_entity_type(data) == "device_profile"
    
    def test_detect_tenant(self):
        """Test detection of tenant entity."""
        data = {"name": "test-tenant", "can_have_gateways": True}
        assert detect_entity_type(data) == "tenant"
    
    def test_detect_application(self):
        """Test detection of application entity."""
        data = {"name": "test-app", "tenant_name": "test-tenant"}
        assert detect_entity_type(data) == "application"


class TestBatchValidation:
    """Tests for batch validation."""
    
    def test_validate_batch_devices(self):
        """Test batch validation of devices."""
        devices = [
            {
                "dev_eui": "0123456789ABCDEF",
                "device_name": "Device 1",
                "app_key": "0123456789ABCDEF0123456789ABCDEF",
                "tenant_name": "test-tenant",
                "application_name": "test-app",
                "device_profile_name": "test-profile"
            },
            {
                "dev_eui": "FEDCBA9876543210",
                "device_name": "Device 2",
                "app_key": "FEDCBA9876543210FEDCBA9876543210",
                "tenant_name": "test-tenant",
                "application_name": "test-app",
                "device_profile_name": "test-profile"
            }
        ]
        results = validate_batch(devices, "device")
        assert len(results) == 2
        assert all(result.is_valid for result in results)
    
    def test_validate_batch_invalid_type(self):
        """Test batch validation with invalid entity type."""
        with pytest.raises(ValueError, match="Unsupported entity type"):
            validate_batch([], "invalid_type")