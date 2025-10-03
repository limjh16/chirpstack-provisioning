"""Tests for setup file ingestion."""

import json
from pathlib import Path

import pytest

from chirpstack_provisioning.setup import (
    decompose_gateways,
    decompose_applications,
    decompose_device_profiles,
    extract_device_profile_templates,
    extract_global_users,
    extract_tenants,
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
def setup_schema_path():
    """Get the path to the setup schema."""
    return Path(__file__).parent.parent / "setup.schema.json"


class TestExtractTenants:
    """Tests for extract_tenants function."""

    def test_extract_tenants_with_data(self, temp_setup_file):
        """Test extracting tenants from setup data."""
        with open(temp_setup_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        tenants = extract_tenants(data)
        assert isinstance(tenants, list)
        assert len(tenants) == len(data["tenants"])
        assert tenants[0]["name"] == data["tenants"][0]["name"]

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
        with open(temp_setup_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        users = extract_global_users(data)
        assert isinstance(users, list)
        assert len(users) == len(data["users"])
        assert users[0]["email"] == data["users"][0]["email"]

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
        assert len(templates) == len(data["device_profile_templates"])
        assert templates[0]["name"] == data["device_profile_templates"][0]["name"]

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
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        templates = extract_device_profile_templates(data)
        users = extract_global_users(data)
        tenants = extract_tenants(data)

        # Verify all components match the complete_setup data
        assert len(templates) == len(complete_setup["device_profile_templates"])
        assert (
            templates[0]["name"]
            == complete_setup["device_profile_templates"][0]["name"]
        )

        assert len(users) == len(complete_setup["users"])
        assert users[0]["email"] == complete_setup["users"][0]["email"]

        assert len(tenants) == len(complete_setup["tenants"])
        assert tenants[0]["name"] == complete_setup["tenants"][0]["name"]
        assert len(tenants[0]["gateways"]) == len(
            complete_setup["tenants"][0]["gateways"]
        )
        assert len(tenants[0]["applications"]) == len(
            complete_setup["tenants"][0]["applications"]
        )

    def test_empty_setup_file(self, tmp_path):
        """Test handling of empty setup file."""
        file_path = tmp_path / "empty_setup.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({}, f)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
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

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        templates = extract_device_profile_templates(data)
        users = extract_global_users(data)
        tenants = extract_tenants(data)

        # Should handle missing sections gracefully
        assert templates == []
        assert users == []
        assert len(tenants) == len(partial_setup["tenants"])
        assert tenants[0]["name"] == partial_setup["tenants"][0]["name"]


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
        assert len(tenants) == len(data["tenants"])
        assert "gateways" in tenants[0]
        assert len(tenants[0]["gateways"]) == len(data["tenants"][0]["gateways"])
        assert (
            tenants[0]["gateways"][0]["name"]
            == data["tenants"][0]["gateways"][0]["name"]
        )

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
        assert len(tenants) == len(data["tenants"])
        assert "applications" in tenants[0]
        assert len(tenants[0]["applications"]) == len(
            data["tenants"][0]["applications"]
        )
        assert (
            tenants[0]["applications"][1]["name"]
            == data["tenants"][0]["applications"][1]["name"]
        )

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
        assert len(tenants) == len(data["tenants"])
        assert "device_profiles" in tenants[0]
        assert len(tenants[0]["device_profiles"]) == len(
            data["tenants"][0]["device_profiles"]
        )

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
        assert len(tenants) == len(data["tenants"])
        assert tenants[0]["name"] == data["tenants"][0]["name"]
        assert tenants[1]["name"] == data["tenants"][1]["name"]
        assert tenants[2]["name"] == data["tenants"][2]["name"]


class TestDecomposeGateways:
    """Tests for decomposing gateways from tenants."""

    def test_decompose_gateways_single_tenant(self):
        """Test decomposing gateways from a single tenant."""
        tenants = [
            {
                "id": "tenant-1",
                "name": "Tenant 1",
                "gateways": [
                    {"gatewayId": "0102030405060708", "name": "Gateway 1"},
                    {"gatewayId": "0807060504030201", "name": "Gateway 2"},
                ],
            }
        ]
        gateways = decompose_gateways(tenants)
        assert len(gateways) == 2
        assert gateways[0]["gatewayId"] == "0102030405060708"
        assert gateways[0]["name"] == "Gateway 1"
        assert gateways[0]["tenant_id"] == "tenant-1"
        assert gateways[1]["gatewayId"] == "0807060504030201"
        assert gateways[1]["name"] == "Gateway 2"
        assert gateways[1]["tenant_id"] == "tenant-1"

    def test_decompose_gateways_multiple_tenants(self):
        """Test decomposing gateways from multiple tenants."""
        tenants = [
            {
                "id": "tenant-1",
                "name": "Tenant 1",
                "gateways": [{"gatewayId": "0102030405060708", "name": "Gateway 1"}],
            },
            {
                "id": "tenant-2",
                "name": "Tenant 2",
                "gateways": [{"gatewayId": "0807060504030201", "name": "Gateway 2"}],
            },
        ]
        gateways = decompose_gateways(tenants)
        assert len(gateways) == 2
        assert gateways[0]["tenant_id"] == "tenant-1"
        assert gateways[1]["tenant_id"] == "tenant-2"

    def test_decompose_gateways_no_gateways(self):
        """Test decomposing when tenants have no gateways."""
        tenants = [{"id": "tenant-1", "name": "Tenant 1"}]
        gateways = decompose_gateways(tenants)
        assert len(gateways) == 0

    def test_decompose_gateways_empty_list(self):
        """Test decomposing with empty tenant list."""
        gateways = decompose_gateways([])
        assert len(gateways) == 0


class TestDecomposeApplications:
    """Tests for decomposing applications from tenants."""

    def test_decompose_applications_single_tenant(self):
        """Test decomposing applications from a single tenant."""
        tenants = [
            {
                "id": "tenant-1",
                "name": "Tenant 1",
                "applications": [
                    {"id": "app-1", "name": "App 1", "description": "First app"},
                    {"id": "app-2", "name": "App 2"},
                ],
            }
        ]
        apps = decompose_applications(tenants)
        assert len(apps) == 2
        assert apps[0]["id"] == "app-1"
        assert apps[0]["name"] == "App 1"
        assert apps[0]["tenant_id"] == "tenant-1"
        assert apps[1]["id"] == "app-2"
        assert apps[1]["tenant_id"] == "tenant-1"

    def test_decompose_applications_multiple_tenants(self):
        """Test decomposing applications from multiple tenants."""
        tenants = [
            {
                "id": "tenant-1",
                "name": "Tenant 1",
                "applications": [{"id": "app-1", "name": "App 1"}],
            },
            {
                "id": "tenant-2",
                "name": "Tenant 2",
                "applications": [{"id": "app-2", "name": "App 2"}],
            },
        ]
        apps = decompose_applications(tenants)
        assert len(apps) == 2
        assert apps[0]["tenant_id"] == "tenant-1"
        assert apps[1]["tenant_id"] == "tenant-2"

    def test_decompose_applications_no_applications(self):
        """Test decomposing when tenants have no applications."""
        tenants = [{"id": "tenant-1", "name": "Tenant 1"}]
        apps = decompose_applications(tenants)
        assert len(apps) == 0


class TestDecomposeDeviceProfiles:
    """Tests for decomposing device profiles from tenants."""

    def test_decompose_device_profiles_single_tenant(self):
        """Test decomposing device profiles from a single tenant."""
        tenants = [
            {
                "id": "tenant-1",
                "name": "Tenant 1",
                "device_profiles": [
                    {"id": "profile-1", "name": "Profile 1"},
                    {"id": "profile-2", "name": "Profile 2"},
                ],
            }
        ]
        profiles = decompose_device_profiles(tenants)
        assert len(profiles) == 2
        assert profiles[0]["id"] == "profile-1"
        assert profiles[0]["name"] == "Profile 1"
        assert profiles[0]["tenant_id"] == "tenant-1"
        assert profiles[1]["id"] == "profile-2"
        assert profiles[1]["tenant_id"] == "tenant-1"

    def test_decompose_device_profiles_multiple_tenants(self):
        """Test decomposing device profiles from multiple tenants."""
        tenants = [
            {
                "id": "tenant-1",
                "name": "Tenant 1",
                "device_profiles": [{"id": "profile-1", "name": "Profile 1"}],
            },
            {
                "id": "tenant-2",
                "name": "Tenant 2",
                "device_profiles": [{"id": "profile-2", "name": "Profile 2"}],
            },
        ]
        profiles = decompose_device_profiles(tenants)
        assert len(profiles) == 2
        assert profiles[0]["tenant_id"] == "tenant-1"
        assert profiles[1]["tenant_id"] == "tenant-2"

    def test_decompose_device_profiles_no_profiles(self):
        """Test decomposing when tenants have no device profiles."""
        tenants = [{"id": "tenant-1", "name": "Tenant 1"}]
        profiles = decompose_device_profiles(tenants)
        assert len(profiles) == 0
