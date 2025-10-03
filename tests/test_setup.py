"""Tests for setup file ingestion."""

import json
from pathlib import Path

import pytest

from chirpstack_provisioning.setup import (
    decompose_tenants,
    extract_device_profile_templates,
    extract_global_users,
    extract_tenants,
    ingest_setup_file,
    load_setup_file,
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


class TestDecomposeTenants:
    """Tests for decomposing tenants and extracting child entities."""

    def test_decompose_single_tenant_with_all_children(self):
        """Test decomposing a single tenant with all child entities."""
        tenants = [
            {
                "id": "tenant-1",
                "name": "Tenant 1",
                "gateways": [
                    {"gatewayId": "0102030405060708", "name": "Gateway 1"},
                    {"gatewayId": "0807060504030201", "name": "Gateway 2"},
                ],
                "applications": [
                    {"id": "app-1", "name": "App 1", "description": "First app"},
                    {"id": "app-2", "name": "App 2"},
                ],
                "device_profiles": [
                    {"id": "profile-1", "name": "Profile 1"},
                    {"id": "profile-2", "name": "Profile 2"},
                ],
            }
        ]
        clean_tenants, gateways, apps, profiles = decompose_tenants(tenants)

        # Verify counts match input
        assert len(clean_tenants) == len(tenants)
        assert len(gateways) == len(tenants[0]["gateways"])
        assert len(apps) == len(tenants[0]["applications"])
        assert len(profiles) == len(tenants[0]["device_profiles"])

        # Verify gateways
        for i, gateway in enumerate(gateways):
            assert gateway["gatewayId"] == tenants[0]["gateways"][i]["gatewayId"]
            assert gateway["name"] == tenants[0]["gateways"][i]["name"]
            assert gateway["tenant_id"] == tenants[0]["id"]

        # Verify applications
        for i, app in enumerate(apps):
            assert app["id"] == tenants[0]["applications"][i]["id"]
            assert app["name"] == tenants[0]["applications"][i]["name"]
            assert app["tenant_id"] == tenants[0]["id"]

        # Verify device profiles
        for i, profile in enumerate(profiles):
            assert profile["id"] == tenants[0]["device_profiles"][i]["id"]
            assert profile["name"] == tenants[0]["device_profiles"][i]["name"]
            assert profile["tenant_id"] == tenants[0]["id"]

        # Verify clean tenants don't have nested children
        assert "gateways" not in clean_tenants[0]
        assert "applications" not in clean_tenants[0]
        assert "device_profiles" not in clean_tenants[0]

    def test_decompose_multiple_tenants(self):
        """Test decomposing multiple tenants with various children."""
        tenants = [
            {
                "id": "tenant-1",
                "name": "Tenant 1",
                "gateways": [{"gatewayId": "0102030405060708", "name": "Gateway 1"}],
            },
            {
                "id": "tenant-2",
                "name": "Tenant 2",
                "applications": [{"id": "app-1", "name": "App 1"}],
            },
            {
                "id": "tenant-3",
                "name": "Tenant 3",
                "device_profiles": [{"id": "profile-1", "name": "Profile 1"}],
            },
        ]
        clean_tenants, gateways, apps, profiles = decompose_tenants(tenants)

        # Verify counts
        assert len(clean_tenants) == len(tenants)
        assert len(gateways) == 1
        assert len(apps) == 1
        assert len(profiles) == 1

        # Verify tenant associations
        assert gateways[0]["tenant_id"] == tenants[0]["id"]
        assert apps[0]["tenant_id"] == tenants[1]["id"]
        assert profiles[0]["tenant_id"] == tenants[2]["id"]

    def test_decompose_tenants_no_children(self):
        """Test decomposing tenants with no child entities."""
        tenants = [
            {"id": "tenant-1", "name": "Tenant 1"},
            {"id": "tenant-2", "name": "Tenant 2"},
        ]
        clean_tenants, gateways, apps, profiles = decompose_tenants(tenants)

        assert len(clean_tenants) == len(tenants)
        assert len(gateways) == 0
        assert len(apps) == 0
        assert len(profiles) == 0

    def test_decompose_empty_tenant_list(self):
        """Test decomposing with empty tenant list."""
        clean_tenants, gateways, apps, profiles = decompose_tenants([])

        assert len(clean_tenants) == 0
        assert len(gateways) == 0
        assert len(apps) == 0
        assert len(profiles) == 0


class TestLoadSetupFile:
    """Tests for loading setup files."""

    def test_load_valid_setup_file(self, temp_setup_file):
        """Test loading a valid setup file."""
        data = load_setup_file(temp_setup_file)
        assert isinstance(data, dict)
        assert "tenants" in data
        assert "users" in data

    def test_load_nonexistent_file(self, tmp_path):
        """Test loading a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_setup_file(tmp_path / "nonexistent.json")

    def test_load_invalid_json(self, tmp_path):
        """Test loading a file with invalid JSON."""
        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json")
        with pytest.raises(json.JSONDecodeError):
            load_setup_file(invalid_file)


class TestIngestSetupFile:
    """Tests for complete setup file ingestion."""

    def test_ingest_complete_setup_file_without_validation(self, tmp_path):
        """Test ingesting a complete setup file without schema validation."""
        complete_setup = {
            "device_profile_templates": [{"name": "Template A"}],
            "users": [
                {
                    "id": "00000000-0000-0000-0000-000000000001",
                    "email": "admin@example.com",
                }
            ],
            "tenants": [
                {
                    "id": "00000000-0000-0000-0000-000000000002",
                    "name": "Tenant A",
                    "gateways": [
                        {
                            "gatewayId": "0102030405060708",
                            "name": "Gateway 1",
                        }
                    ],
                    "applications": [
                        {
                            "id": "00000000-0000-0000-0000-000000000003",
                            "name": "App A",
                        }
                    ],
                    "device_profiles": [
                        {
                            "id": "00000000-0000-0000-0000-000000000004",
                            "name": "Profile 1",
                        }
                    ],
                }
            ],
        }

        file_path = tmp_path / "complete_setup.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(complete_setup, f)

        # Load and extract without full validation
        setup_data = load_setup_file(file_path)
        tenants = extract_tenants(setup_data)
        users = extract_global_users(setup_data)
        templates = extract_device_profile_templates(setup_data)

        clean_tenants, gateways, applications, device_profiles = decompose_tenants(
            tenants
        )

        # Verify decomposed entities match input
        assert len(gateways) == len(complete_setup["tenants"][0]["gateways"])
        assert gateways[0]["tenant_id"] == complete_setup["tenants"][0]["id"]
        assert (
            gateways[0]["gatewayId"]
            == complete_setup["tenants"][0]["gateways"][0]["gatewayId"]
        )

        assert len(applications) == len(complete_setup["tenants"][0]["applications"])
        assert applications[0]["tenant_id"] == complete_setup["tenants"][0]["id"]
        assert (
            applications[0]["id"]
            == complete_setup["tenants"][0]["applications"][0]["id"]
        )

        assert len(device_profiles) == len(
            complete_setup["tenants"][0]["device_profiles"]
        )
        assert device_profiles[0]["tenant_id"] == complete_setup["tenants"][0]["id"]
        assert (
            device_profiles[0]["id"]
            == complete_setup["tenants"][0]["device_profiles"][0]["id"]
        )

        # Verify top-level entities match input
        assert len(users) == len(complete_setup["users"])
        assert len(templates) == len(complete_setup["device_profile_templates"])

    def test_ingest_minimal_setup_file(self, tmp_path, setup_schema_path):
        """Test ingesting a minimal setup file."""
        minimal_setup = {
            "tenants": [
                {
                    "id": "00000000-0000-0000-0000-000000000001",
                    "name": "Minimal Tenant",
                    "description": "A minimal tenant",
                    "canHaveGateways": True,
                    "maxGatewayCount": 0,
                    "maxDeviceCount": 0,
                    "privateGatewaysUp": False,
                    "privateGatewaysDown": False,
                }
            ]
        }

        file_path = tmp_path / "minimal_setup.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(minimal_setup, f)

        result = ingest_setup_file(file_path, setup_schema_path)

        # Verify counts match input
        assert len(result["tenants"]) == len(minimal_setup["tenants"])
        assert len(result["users"]) == 0
        assert len(result["device_profile_templates"]) == 0
        assert len(result["gateways"]) == 0
        assert len(result["applications"]) == 0
        assert len(result["device_profiles"]) == 0

    def test_ingest_multiple_tenants_with_children_without_validation(self, tmp_path):
        """Test ingesting multiple tenants with various nested children."""
        setup = {
            "tenants": [
                {
                    "id": "00000000-0000-0000-0000-000000000001",
                    "name": "Tenant 1",
                    "gateways": [
                        {
                            "gatewayId": "0102030405060708",
                            "name": "GW1",
                        },
                    ],
                },
                {
                    "id": "00000000-0000-0000-0000-000000000002",
                    "name": "Tenant 2",
                    "applications": [
                        {
                            "id": "00000000-0000-0000-0000-000000000003",
                            "name": "App 1",
                        }
                    ],
                    "device_profiles": [
                        {
                            "id": "00000000-0000-0000-0000-000000000004",
                            "name": "Profile 1",
                        }
                    ],
                },
            ]
        }

        file_path = tmp_path / "multi_tenant_setup.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(setup, f)

        # Load and extract without validation
        setup_data = load_setup_file(file_path)
        tenants = extract_tenants(setup_data)
        clean_tenants, gateways, applications, device_profiles = decompose_tenants(
            tenants
        )

        # Verify correct decomposition based on input
        assert len(tenants) == len(setup["tenants"])
        assert len(gateways) == len(setup["tenants"][0]["gateways"])
        assert len(applications) == len(setup["tenants"][1]["applications"])
        assert len(device_profiles) == len(setup["tenants"][1]["device_profiles"])

        # Verify tenant associations match input
        assert gateways[0]["tenant_id"] == setup["tenants"][0]["id"]
        assert applications[0]["tenant_id"] == setup["tenants"][1]["id"]
        assert device_profiles[0]["tenant_id"] == setup["tenants"][1]["id"]
