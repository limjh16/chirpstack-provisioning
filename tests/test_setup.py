"""Tests for setup file ingestion using SetupFileIngestion class."""

import json
from pathlib import Path

import pytest

from chirpstack_provisioning.setup import SetupFileIngestion


@pytest.fixture
def minimal_setup_file(tmp_path):
    """Create a minimal setup file for testing."""
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
def setup_schema_path():
    """Get the path to the setup schema."""
    return Path(__file__).parent.parent / "setup.schema.json"


class TestSetupFileIngestion:
    """Tests for the SetupFileIngestion class."""

    def test_initialization_with_multiple_tenants(self, tmp_path, setup_schema_path):
        """Test class initialization with multiple tenants."""
        setup_data = {
            "tenants": [
                {
                    "id": "00000000-0000-0000-0000-000000000001",
                    "name": "Tenant 1",
                    "description": "Test tenant 1",
                    "canHaveGateways": True,
                    "maxGatewayCount": 10,
                    "maxDeviceCount": 100,
                    "privateGatewaysUp": False,
                    "privateGatewaysDown": False,
                    "gateways": [],
                    "applications": [],
                    "device_profiles": [],
                },
                {
                    "id": "00000000-0000-0000-0000-000000000002",
                    "name": "Tenant 2",
                    "description": "Test tenant 2",
                    "canHaveGateways": True,
                    "maxGatewayCount": 10,
                    "maxDeviceCount": 100,
                    "privateGatewaysUp": False,
                    "privateGatewaysDown": False,
                    "gateways": [],
                    "applications": [],
                    "device_profiles": [],
                },
            ]
        }

        file_path = tmp_path / "multi_setup.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(setup_data, f)

        ingestion = SetupFileIngestion(file_path, setup_schema_path)

        # Verify data was loaded correctly
        assert len(ingestion.tenants) == len(setup_data["tenants"])
        assert len(ingestion.users) == 0
        assert len(ingestion.gateways) == 0

    def test_property_access(self, tmp_path, setup_schema_path):
        """Test that properties work correctly."""
        setup_data = {"tenants": []}

        file_path = tmp_path / "empty_setup.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(setup_data, f)

        ingestion = SetupFileIngestion(file_path, setup_schema_path)

        # Test getters
        assert isinstance(ingestion.tenants, list)
        assert isinstance(ingestion.users, list)

        # Test setters
        new_users = [{"id": "new-user", "email": "new@example.com"}]
        ingestion.users = new_users
        assert ingestion.users == new_users

    def test_to_dict_method(self, tmp_path, setup_schema_path):
        """Test the to_dict method returns correct structure."""
        setup_data = {"tenants": []}

        file_path = tmp_path / "simple_setup.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(setup_data, f)

        ingestion = SetupFileIngestion(file_path, setup_schema_path)
        result = ingestion.to_dict()

        # Verify structure
        assert "tenants" in result
        assert "users" in result
        assert "device_profile_templates" in result
        assert "gateways" in result
        assert "applications" in result
        assert "device_profiles" in result

    def test_multiple_tenants_with_children(self, tmp_path, setup_schema_path):
        """Test handling multiple tenants with various child entities."""
        setup_data = {
            "tenants": [
                {
                    "id": "00000000-0000-0000-0000-000000000001",
                    "name": "Tenant 1",
                    "description": "Test tenant 1",
                    "canHaveGateways": True,
                    "maxGatewayCount": 10,
                    "maxDeviceCount": 100,
                    "privateGatewaysUp": False,
                    "privateGatewaysDown": False,
                    "gateways": [
                        {
                            "gatewayId": "0102030405060708",
                            "name": "Gateway 1",
                            "description": "Test gateway",
                            "tenantId": "00000000-0000-0000-0000-000000000001",
                            "statsInterval": 30,
                        }
                    ],
                    "applications": [],
                    "device_profiles": [],
                },
                {
                    "id": "00000000-0000-0000-0000-000000000002",
                    "name": "Tenant 2",
                    "description": "Test tenant 2",
                    "canHaveGateways": True,
                    "maxGatewayCount": 10,
                    "maxDeviceCount": 100,
                    "privateGatewaysUp": False,
                    "privateGatewaysDown": False,
                    "gateways": [],
                    "applications": [
                        {
                            "id": "00000000-0000-0000-0000-000000000003",
                            "name": "App 1",
                            "description": "Test app",
                            "tenantId": "00000000-0000-0000-0000-000000000002",
                        }
                    ],
                    "device_profiles": [],
                },
            ]
        }

        file_path = tmp_path / "multi_tenant_setup.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(setup_data, f)

        ingestion = SetupFileIngestion(file_path, setup_schema_path)

        # Verify counts
        assert len(ingestion.tenants) == len(setup_data["tenants"])
        assert len(ingestion.gateways) == len(setup_data["tenants"][0]["gateways"])
        assert len(ingestion.applications) == len(
            setup_data["tenants"][1]["applications"]
        )

        # Verify tenant associations
        assert ingestion.gateways[0]["tenant_id"] == setup_data["tenants"][0]["id"]
        assert ingestion.applications[0]["tenant_id"] == setup_data["tenants"][1]["id"]

    def test_empty_setup_file(self, tmp_path, setup_schema_path):
        """Test handling of empty setup file."""
        setup_data = {}

        file_path = tmp_path / "empty_setup.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(setup_data, f)

        ingestion = SetupFileIngestion(file_path, setup_schema_path)

        # Verify all lists are empty
        assert len(ingestion.tenants) == 0
        assert len(ingestion.users) == 0
        assert len(ingestion.device_profile_templates) == 0
        assert len(ingestion.gateways) == 0
        assert len(ingestion.applications) == 0
        assert len(ingestion.device_profiles) == 0

    def test_file_not_found(self, tmp_path, setup_schema_path):
        """Test handling of nonexistent file."""
        with pytest.raises(FileNotFoundError):
            SetupFileIngestion(tmp_path / "nonexistent.json", setup_schema_path)

    def test_invalid_json(self, tmp_path, setup_schema_path):
        """Test handling of invalid JSON file."""
        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json")

        with pytest.raises(json.JSONDecodeError):
            SetupFileIngestion(invalid_file, setup_schema_path)
