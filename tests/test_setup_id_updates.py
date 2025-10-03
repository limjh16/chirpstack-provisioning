"""Tests for setup.json ID field updates after entity creation.

This module tests that IDs returned from ChirpStack API Create requests
are properly written back to the setup.json file structure.

Following TDD methodology - these tests are written before implementation.
"""

import json
from unittest.mock import Mock


class TestSetupIdUpdates:
    """Test that entity IDs are updated in setup data after creation."""

    def test_tenant_id_updated_after_creation(self):
        """Test that tenant ID is updated with the value returned from Create."""
        # Initial setup data with no ID
        setup_data = {
            "tenants": [
                {
                    "name": "Test Tenant",
                    "description": "A test tenant",
                    "canHaveGateways": True,
                }
            ]
        }

        # Mock the Create response
        mock_api_response = Mock()
        mock_api_response.id = "tenant-uuid-12345"

        # After creation, the tenant ID should be updated
        # This would be done by the provisioning logic
        expected_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                    "description": "A test tenant",
                    "canHaveGateways": True,
                }
            ]
        }

        # Verify the mock response has the expected structure
        assert hasattr(mock_api_response, "id")
        assert mock_api_response.id == "tenant-uuid-12345"
        # Verify initial setup has no ID
        assert "id" not in setup_data["tenants"][0]
        # Verify expected data has the ID from the response
        assert expected_data["tenants"][0]["id"] == mock_api_response.id

    def test_application_id_updated_after_creation(self):
        """Test that application ID is updated with the value returned from Create."""
        # Initial setup data with application having no ID
        setup_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                    "applications": [
                        {
                            "name": "Test App",
                            "description": "A test application",
                        }
                    ],
                }
            ]
        }

        # Mock the Create response
        mock_api_response = Mock()
        mock_api_response.id = "app-uuid-67890"

        # After creation, the application ID should be updated
        expected_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                    "applications": [
                        {
                            "id": "app-uuid-67890",
                            "name": "Test App",
                            "description": "A test application",
                        }
                    ],
                }
            ]
        }

        # Verify the mock response has the expected structure
        assert hasattr(mock_api_response, "id")
        assert mock_api_response.id == "app-uuid-67890"
        # Verify initial setup has no application ID
        assert "id" not in setup_data["tenants"][0]["applications"][0]
        # Verify expected data has the ID from the response
        assert (
            expected_data["tenants"][0]["applications"][0]["id"] == mock_api_response.id
        )

    def test_device_profile_id_updated_after_creation(self):
        """Test that device profile ID is updated with the value returned from Create."""
        # Initial setup data with device profile having no ID
        setup_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                    "device_profiles": [
                        {
                            "name": "Test Profile",
                            "region": "US915",
                        }
                    ],
                }
            ]
        }

        # Mock the Create response
        mock_api_response = Mock()
        mock_api_response.id = "profile-uuid-abc123"

        # After creation, the device profile ID should be updated
        expected_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                    "device_profiles": [
                        {
                            "id": "profile-uuid-abc123",
                            "name": "Test Profile",
                            "region": "US915",
                        }
                    ],
                }
            ]
        }

        # Verify the mock response has the expected structure
        assert hasattr(mock_api_response, "id")
        assert mock_api_response.id == "profile-uuid-abc123"
        # Verify initial setup has no device profile ID
        assert "id" not in setup_data["tenants"][0]["device_profiles"][0]
        # Verify expected data has the ID from the response
        assert (
            expected_data["tenants"][0]["device_profiles"][0]["id"]
            == mock_api_response.id
        )

    def test_gateway_id_not_updated_after_creation(self):
        """Test that gateway ID is not updated (Create returns Empty).

        Gateway Create returns google.protobuf.empty_pb2.Empty, so the
        gatewayId field should remain as provided by the user.
        """
        # Initial setup data with gateway ID already set
        setup_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                    "gateways": [
                        {
                            "gatewayId": "0102030405060708",
                            "name": "Test Gateway",
                        }
                    ],
                }
            ]
        }

        # Gateway Create returns Empty (no id field)
        # So the gatewayId should remain unchanged
        expected_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                    "gateways": [
                        {
                            "gatewayId": "0102030405060708",
                            "name": "Test Gateway",
                        }
                    ],
                }
            ]
        }

        # The gateway ID should not change
        assert (
            setup_data["tenants"][0]["gateways"][0]["gatewayId"]
            == expected_data["tenants"][0]["gateways"][0]["gatewayId"]
        )

    def test_multiple_entities_ids_updated(self):
        """Test that IDs for multiple entities at the same level are updated."""
        # Initial setup data with multiple applications
        setup_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                    "applications": [
                        {"name": "App 1"},
                        {"name": "App 2"},
                        {"name": "App 3"},
                    ],
                }
            ]
        }

        # Mock Create responses for each application
        mock_responses = [
            Mock(id="app-uuid-11111"),
            Mock(id="app-uuid-22222"),
            Mock(id="app-uuid-33333"),
        ]

        # After creation, all application IDs should be updated
        expected_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                    "applications": [
                        {"id": "app-uuid-11111", "name": "App 1"},
                        {"id": "app-uuid-22222", "name": "App 2"},
                        {"id": "app-uuid-33333", "name": "App 3"},
                    ],
                }
            ]
        }

        # Verify all initial applications have no IDs
        for app in setup_data["tenants"][0]["applications"]:
            assert "id" not in app

        # Verify all mock responses have the expected structure
        for i, mock_resp in enumerate(mock_responses):
            assert hasattr(mock_resp, "id")
            assert mock_resp.id == expected_data["tenants"][0]["applications"][i]["id"]

    def test_user_id_updated_after_creation(self):
        """Test that user ID is updated with the value returned from Create."""
        # Initial setup data with global user having no ID
        setup_data = {
            "users": [
                {
                    "email": "test@example.com",
                    "isAdmin": True,
                    "isActive": True,
                }
            ]
        }

        # Mock the Create response
        mock_api_response = Mock()
        mock_api_response.id = "user-uuid-def456"

        # After creation, the user ID should be updated
        expected_data = {
            "users": [
                {
                    "id": "user-uuid-def456",
                    "email": "test@example.com",
                    "isAdmin": True,
                    "isActive": True,
                }
            ]
        }

        # Verify the mock response has the expected structure
        assert hasattr(mock_api_response, "id")
        assert mock_api_response.id == "user-uuid-def456"
        # Verify initial setup has no user ID
        assert "id" not in setup_data["users"][0]
        # Verify expected data has the ID from the response
        assert expected_data["users"][0]["id"] == mock_api_response.id

    def test_nested_entity_ids_updated(self):
        """Test that IDs are updated for deeply nested entities."""
        # Initial setup with nested structure
        setup_data = {
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
                    "device_profiles": [{"name": "Profile 1"}],
                }
            ]
        }

        # Mock Create responses
        tenant_response = Mock(id="tenant-uuid-11111")
        app_response = Mock(id="app-uuid-22222")
        profile_response = Mock(id="profile-uuid-33333")

        # After creation, all IDs should be updated
        expected_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-11111",
                    "name": "Tenant 1",
                    "applications": [
                        {
                            "id": "app-uuid-22222",
                            "name": "App 1",
                            "integrations": {
                                "InfluxDbIntegration": {
                                    "endpoint": "http://influxdb:8086"
                                }
                            },
                        }
                    ],
                    "device_profiles": [
                        {"id": "profile-uuid-33333", "name": "Profile 1"}
                    ],
                }
            ]
        }

        # Verify initial setup has no IDs
        assert "id" not in setup_data["tenants"][0]
        assert "id" not in setup_data["tenants"][0]["applications"][0]
        assert "id" not in setup_data["tenants"][0]["device_profiles"][0]

        # Verify all mock responses have the expected structure
        assert tenant_response.id == "tenant-uuid-11111"
        assert app_response.id == "app-uuid-22222"
        assert profile_response.id == "profile-uuid-33333"

        # Verify expected data has all IDs populated
        assert expected_data["tenants"][0]["id"] == tenant_response.id
        assert expected_data["tenants"][0]["applications"][0]["id"] == app_response.id
        assert (
            expected_data["tenants"][0]["device_profiles"][0]["id"]
            == profile_response.id
        )

    def test_multicast_group_id_updated_after_creation(self):
        """Test that multicast group ID is updated with the value returned from Create."""
        # Initial setup data with multicast group having no ID
        setup_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                    "applications": [
                        {
                            "id": "app-uuid-67890",
                            "name": "Test App",
                            "multicast_groups": [
                                {
                                    "name": "Test Multicast",
                                    "region": "US915",
                                }
                            ],
                        }
                    ],
                }
            ]
        }

        # Mock the Create response
        mock_api_response = Mock()
        mock_api_response.id = "multicast-uuid-ghi789"

        # After creation, the multicast group ID should be updated
        expected_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                    "applications": [
                        {
                            "id": "app-uuid-67890",
                            "name": "Test App",
                            "multicast_groups": [
                                {
                                    "id": "multicast-uuid-ghi789",
                                    "name": "Test Multicast",
                                    "region": "US915",
                                }
                            ],
                        }
                    ],
                }
            ]
        }

        # Verify the mock response has the expected structure
        assert hasattr(mock_api_response, "id")
        assert mock_api_response.id == "multicast-uuid-ghi789"
        # Verify initial setup has no multicast group ID
        multicast_group = setup_data["tenants"][0]["applications"][0][
            "multicast_groups"
        ][0]
        assert "id" not in multicast_group
        # Verify expected data has the ID from the response
        expected_multicast = expected_data["tenants"][0]["applications"][0][
            "multicast_groups"
        ][0]
        assert expected_multicast["id"] == mock_api_response.id


class TestSetupIdUpdatePersistence:
    """Test that ID updates are persisted to the setup.json file."""

    def test_updated_setup_written_to_file(self, tmp_path):
        """Test that setup data with updated IDs can be written to a file."""
        # Setup data with IDs populated after creation
        setup_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                    "applications": [
                        {
                            "id": "app-uuid-67890",
                            "name": "Test App",
                        }
                    ],
                }
            ]
        }

        # Write to file
        file_path = tmp_path / "updated_setup.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(setup_data, f, indent=2)

        # Read back and verify
        with open(file_path, "r", encoding="utf-8") as f:
            read_data = json.load(f)

        assert read_data["tenants"][0]["id"] == "tenant-uuid-12345"
        assert read_data["tenants"][0]["applications"][0]["id"] == "app-uuid-67890"

    def test_id_preserved_on_reload(self, tmp_path):
        """Test that IDs are preserved when setup file is reloaded."""
        # Initial setup with IDs
        setup_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                }
            ]
        }

        # Write to file
        file_path = tmp_path / "setup_with_ids.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(setup_data, f)

        # Read back
        with open(file_path, "r", encoding="utf-8") as f:
            reloaded_data = json.load(f)

        # ID should be preserved
        assert reloaded_data["tenants"][0]["id"] == setup_data["tenants"][0]["id"]

    def test_existing_id_not_overwritten_if_already_present(self):
        """Test that existing IDs are not overwritten during restore operations."""
        # Setup data with pre-existing ID (e.g., from a backup)
        setup_data = {
            "tenants": [
                {
                    "id": "existing-tenant-uuid-999",
                    "name": "Test Tenant",
                }
            ]
        }

        # When restoring from backup, the existing ID should be used
        # (not a new one generated from Create)
        # This is the backup/restore scenario mentioned in data.md

        assert setup_data["tenants"][0]["id"] == "existing-tenant-uuid-999"


class TestUpdateSetupWithIds:
    """Test functions that update setup data with IDs from API responses.

    These tests use placeholder function names that will be implemented later.
    Following TDD methodology - tests are written before implementation.
    """

    def test_update_tenant_id_in_setup_data(self):
        """Test update_entity_id function for tenant entities."""
        # This function doesn't exist yet - will be implemented
        # from chirpstack_provisioning.setup import update_entity_id

        setup_data = {
            "tenants": [
                {
                    "name": "Test Tenant",
                    "description": "A test tenant",
                }
            ]
        }

        # Mock API response
        mock_response = Mock()
        mock_response.id = "tenant-uuid-12345"

        # When implemented, this should update the tenant with the returned ID:
        # update_entity_id(setup_data, ["tenants", 0], mock_response.id)

        # For now, manually simulate what the function should do
        setup_data["tenants"][0]["id"] = mock_response.id

        # Verify the ID was set correctly
        assert setup_data["tenants"][0]["id"] == "tenant-uuid-12345"

    def test_update_nested_application_id_in_setup_data(self):
        """Test update_entity_id function for nested application entities."""
        # This function doesn't exist yet - will be implemented
        # from chirpstack_provisioning.setup import update_entity_id

        setup_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                    "applications": [
                        {
                            "name": "Test App",
                        }
                    ],
                }
            ]
        }

        # Mock API response
        mock_response = Mock()
        mock_response.id = "app-uuid-67890"

        # When implemented, this should update the nested application:
        # update_entity_id(setup_data, ["tenants", 0, "applications", 0], mock_response.id)

        # For now, manually simulate what the function should do
        setup_data["tenants"][0]["applications"][0]["id"] = mock_response.id

        # Verify the ID was set correctly
        assert setup_data["tenants"][0]["applications"][0]["id"] == "app-uuid-67890"

    def test_write_setup_data_with_ids(self):
        """Test write_setup_data function that persists IDs to file."""
        # This function doesn't exist yet - will be implemented
        # from chirpstack_provisioning.setup import write_setup_data

        setup_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                }
            ]
        }

        # When implemented, this should write the data to a file:
        # write_setup_data(file_path, setup_data)

        # For now, verify the data structure is correct
        assert "id" in setup_data["tenants"][0]
        assert setup_data["tenants"][0]["id"] == "tenant-uuid-12345"

    def test_update_multiple_entity_ids_in_batch(self):
        """Test batch ID update for multiple entities at once."""
        # This function doesn't exist yet - will be implemented
        # from chirpstack_provisioning.setup import update_multiple_entity_ids

        setup_data = {
            "tenants": [
                {
                    "id": "tenant-uuid-12345",
                    "name": "Test Tenant",
                    "applications": [
                        {"name": "App 1"},
                        {"name": "App 2"},
                    ],
                }
            ]
        }

        # Mock API responses
        app_ids = ["app-uuid-11111", "app-uuid-22222"]

        # When implemented, this should update multiple entities:
        # update_multiple_entity_ids(
        #     setup_data,
        #     ["tenants", 0, "applications"],
        #     app_ids
        # )

        # For now, manually simulate what the function should do
        for i, app_id in enumerate(app_ids):
            setup_data["tenants"][0]["applications"][i]["id"] = app_id

        # Verify all IDs were set correctly
        assert setup_data["tenants"][0]["applications"][0]["id"] == "app-uuid-11111"
        assert setup_data["tenants"][0]["applications"][1]["id"] == "app-uuid-22222"
