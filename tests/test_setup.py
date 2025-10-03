"""Tests for setup file ingestion."""

import json
from pathlib import Path

import pytest

from chirpstack_provisioning.setup import (
    extract_device_profile_templates,
    extract_global_users,
    extract_tenants,
    load_setup_file,
    validate_setup_data,
)


@pytest.fixture
def temp_setup_file(tmp_path):
    """Create a temporary setup file for testing."""
    setup_data = {
        "tenants": [
            {
                "id": "00000000-0000-0000-0000-000000000001",
                "name": "Test Tenant",
                "description": "A test tenant",
                "canHaveGateways": True,
                "maxGatewayCount": 10,
                "maxDeviceCount": 100,
                "privateGatewaysUp": False,
                "privateGatewaysDown": False,
                "gateways": [],
                "applications": [],
                "device_profiles": [],
            }
        ],
        "users": [
            {
                "id": "00000000-0000-0000-0000-000000000010",
                "email": "test@example.com",
                "isAdmin": True,
                "isActive": True,
                "note": "Test user",
            }
        ],
    }
    file_path = tmp_path / "setup.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(setup_data, f)
    return file_path


@pytest.fixture
def invalid_json_file(tmp_path):
    """Create a file with invalid JSON."""
    file_path = tmp_path / "invalid.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("{ invalid json }")
    return file_path


@pytest.fixture
def setup_schema_path():
    """Get the path to the setup schema."""
    return Path(__file__).parent.parent / "setup.schema.json"


class TestLoadSetupFile:
    """Tests for load_setup_file function."""

    def test_load_valid_setup_file(self, temp_setup_file):
        """Test loading a valid setup file."""
        data = load_setup_file(temp_setup_file)
        assert isinstance(data, dict)
        assert "tenants" in data
        assert "users" in data

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_setup_file("/nonexistent/path/setup.json")

    def test_load_invalid_json(self, invalid_json_file):
        """Test loading a file with invalid JSON."""
        with pytest.raises(json.JSONDecodeError):
            load_setup_file(invalid_json_file)


class TestValidateSetupData:
    """Tests for validate_setup_data function."""

    def test_validate_schema_function_exists(self, setup_schema_path):
        """Test that validate_setup_data function exists and can be called."""
        # This is a basic test to verify the function exists
        # Full schema validation with $ref resolution will be tested separately
        # when the schema infrastructure is fully set up
        empty_data = {}
        # Should not raise an exception for empty data
        validate_setup_data(empty_data, setup_schema_path)


class TestExtractTenants:
    """Tests for extract_tenants function."""

    def test_extract_tenants_with_data(self, temp_setup_file):
        """Test extracting tenants from setup data."""
        data = load_setup_file(temp_setup_file)
        tenants = extract_tenants(data)
        assert isinstance(tenants, list)
        assert len(tenants) == 1
        assert tenants[0]["name"] == "Test Tenant"

    def test_extract_tenants_without_tenants_key(self):
        """Test extracting tenants when tenants key is missing."""
        data = {"users": []}
        tenants = extract_tenants(data)
        assert isinstance(tenants, list)
        assert len(tenants) == 0

    def test_extract_tenants_empty_list(self):
        """Test extracting tenants when tenants list is empty."""
        data = {"tenants": []}
        tenants = extract_tenants(data)
        assert isinstance(tenants, list)
        assert len(tenants) == 0


class TestExtractGlobalUsers:
    """Tests for extract_global_users function."""

    def test_extract_users_with_data(self, temp_setup_file):
        """Test extracting global users from setup data."""
        data = load_setup_file(temp_setup_file)
        users = extract_global_users(data)
        assert isinstance(users, list)
        assert len(users) == 1
        assert users[0]["email"] == "test@example.com"

    def test_extract_users_without_users_key(self):
        """Test extracting users when users key is missing."""
        data = {"tenants": []}
        users = extract_global_users(data)
        assert isinstance(users, list)
        assert len(users) == 0

    def test_extract_users_empty_list(self):
        """Test extracting users when users list is empty."""
        data = {"users": []}
        users = extract_global_users(data)
        assert isinstance(users, list)
        assert len(users) == 0


class TestExtractDeviceProfileTemplates:
    """Tests for extract_device_profile_templates function."""

    def test_extract_templates_with_data(self):
        """Test extracting device profile templates from setup data."""
        data = {
            "device_profile_templates": [
                {
                    "name": "Template 1",
                    "region": "US915",
                }
            ]
        }
        templates = extract_device_profile_templates(data)
        assert isinstance(templates, list)
        assert len(templates) == 1
        assert templates[0]["name"] == "Template 1"

    def test_extract_templates_without_key(self):
        """Test extracting templates when key is missing."""
        data = {"tenants": []}
        templates = extract_device_profile_templates(data)
        assert isinstance(templates, list)
        assert len(templates) == 0

    def test_extract_templates_empty_list(self):
        """Test extracting templates when list is empty."""
        data = {"device_profile_templates": []}
        templates = extract_device_profile_templates(data)
        assert isinstance(templates, list)
        assert len(templates) == 0


class TestIntegrationWorkflow:
    """Integration tests for complete setup file workflow."""

    def test_load_and_extract_complete_setup(self, tmp_path):
        """Test loading and extracting from a complete setup file."""
        complete_setup = {
            "device_profile_templates": [{"name": "Template A"}],
            "users": [
                {
                    "id": "user-1",
                    "email": "admin@example.com",
                    "isAdmin": True,
                    "isActive": True,
                    "note": "Admin user",
                }
            ],
            "tenants": [
                {
                    "id": "tenant-1",
                    "name": "Tenant A",
                    "description": "First tenant",
                    "canHaveGateways": True,
                    "maxGatewayCount": 5,
                    "maxDeviceCount": 100,
                    "privateGatewaysUp": False,
                    "privateGatewaysDown": False,
                    "gateways": [{"gatewayId": "0102030405060708", "name": "GW1"}],
                    "applications": [
                        {
                            "id": "app-1",
                            "name": "App A",
                            "description": "First app",
                            "tenantId": "tenant-1",
                        }
                    ],
                    "device_profiles": [],
                }
            ],
        }

        # Write to file
        file_path = tmp_path / "complete_setup.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(complete_setup, f)

        # Load and extract
        data = load_setup_file(file_path)
        templates = extract_device_profile_templates(data)
        users = extract_global_users(data)
        tenants = extract_tenants(data)

        # Verify all components
        assert len(templates) == 1
        assert templates[0]["name"] == "Template A"

        assert len(users) == 1
        assert users[0]["email"] == "admin@example.com"

        assert len(tenants) == 1
        assert tenants[0]["name"] == "Tenant A"
        assert len(tenants[0]["gateways"]) == 1
        assert len(tenants[0]["applications"]) == 1

    def test_empty_setup_file(self, tmp_path):
        """Test handling of empty setup file."""
        file_path = tmp_path / "empty_setup.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({}, f)

        data = load_setup_file(file_path)
        templates = extract_device_profile_templates(data)
        users = extract_global_users(data)
        tenants = extract_tenants(data)

        assert templates == []
        assert users == []
        assert tenants == []

    def test_partial_setup_file(self, tmp_path):
        """Test handling of setup file with only some sections."""
        partial_setup = {"tenants": [{"name": "Only Tenant", "gateways": []}]}

        file_path = tmp_path / "partial_setup.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(partial_setup, f)

        data = load_setup_file(file_path)
        templates = extract_device_profile_templates(data)
        users = extract_global_users(data)
        tenants = extract_tenants(data)

        # Should handle missing sections gracefully
        assert templates == []
        assert users == []
        assert len(tenants) == 1
        assert tenants[0]["name"] == "Only Tenant"


class TestNestedStructures:
    """Tests for extracting nested structures from tenants."""

    def test_extract_gateways_from_tenant(self):
        """Test extracting gateways from a tenant."""
        data = {
            "tenants": [
                {
                    "name": "Tenant 1",
                    "gateways": [
                        {"gatewayId": "0102030405060708", "name": "Gateway 1"},
                        {"gatewayId": "0807060504030201", "name": "Gateway 2"},
                    ],
                }
            ]
        }
        tenants = extract_tenants(data)
        assert len(tenants) == 1
        assert "gateways" in tenants[0]
        assert len(tenants[0]["gateways"]) == 2
        assert tenants[0]["gateways"][0]["name"] == "Gateway 1"

    def test_extract_applications_from_tenant(self):
        """Test extracting applications from a tenant."""
        data = {
            "tenants": [
                {
                    "name": "Tenant 1",
                    "applications": [
                        {"id": "app-1", "name": "App 1"},
                        {"id": "app-2", "name": "App 2"},
                    ],
                }
            ]
        }
        tenants = extract_tenants(data)
        assert len(tenants) == 1
        assert "applications" in tenants[0]
        assert len(tenants[0]["applications"]) == 2
        assert tenants[0]["applications"][1]["name"] == "App 2"

    def test_extract_device_profiles_from_tenant(self):
        """Test extracting device profiles from a tenant."""
        data = {
            "tenants": [
                {
                    "name": "Tenant 1",
                    "device_profiles": [
                        {"id": "profile-1", "name": "Profile 1"},
                    ],
                }
            ]
        }
        tenants = extract_tenants(data)
        assert len(tenants) == 1
        assert "device_profiles" in tenants[0]
        assert len(tenants[0]["device_profiles"]) == 1

    def test_extract_integrations_from_application(self):
        """Test extracting integrations from an application."""
        data = {
            "tenants": [
                {
                    "name": "Tenant 1",
                    "applications": [
                        {
                            "name": "App 1",
                            "integrations": {
                                "InfluxDbIntegration": {
                                    "endpoint": "http://influxdb:8086"
                                }
                            },
                        }
                    ],
                }
            ]
        }
        tenants = extract_tenants(data)
        app = tenants[0]["applications"][0]
        assert "integrations" in app
        assert "InfluxDbIntegration" in app["integrations"]

    def test_multiple_tenants(self):
        """Test handling multiple tenants with complex structures."""
        data = {
            "tenants": [
                {
                    "name": "Tenant 1",
                    "gateways": [{"gatewayId": "0102030405060708"}],
                },
                {
                    "name": "Tenant 2",
                    "applications": [{"name": "App"}],
                },
                {"name": "Tenant 3"},
            ]
        }
        tenants = extract_tenants(data)
        assert len(tenants) == 3
        assert tenants[0]["name"] == "Tenant 1"
        assert tenants[1]["name"] == "Tenant 2"
        assert tenants[2]["name"] == "Tenant 3"
