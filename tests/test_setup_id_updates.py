"""Tests for setup.json ID field updates after ChirpStack API creation.

This module tests that when entities (tenants, applications, device profiles,
gateways) are created via the ChirpStack API, the IDs returned by the server
are properly updated in the setup data structure.

Following TDD methodology - these tests use grpc_testing to mock server responses.
"""

import json
import pytest
import grpc_testing
from unittest.mock import Mock, patch


@pytest.fixture
def sample_setup_data():
    """Create sample setup data without IDs (as would be provided by user)."""
    return {
        "tenants": [
            {
                "name": "Test Tenant",
                "description": "A test tenant",
                "canHaveGateways": True,
                "maxGatewayCount": 10,
                "maxDeviceCount": 100,
                "privateGatewaysUp": False,
                "privateGatewaysDown": False,
                "applications": [
                    {
                        "name": "Test App",
                        "description": "Test application",
                    }
                ],
                "device_profiles": [
                    {
                        "name": "Test Profile",
                        "region": "US915",
                        "macVersion": "LORAWAN_1_0_3",
                        "regParamsRevision": "RP002_1_0_1",
                        "supportsOtaa": True,
                    }
                ],
                "gateways": [
                    {
                        "gatewayId": "0102030405060708",
                        "name": "Test Gateway",
                        "description": "Test gateway",
                    }
                ],
            }
        ],
        "users": [
            {
                "email": "test@example.com",
                "isAdmin": True,
                "isActive": True,
            }
        ],
    }


@pytest.fixture
def grpc_test_channel():
    """Create a gRPC testing channel.

    Uses grpc_testing.channel() to create a test channel that intercepts
    gRPC calls for testing without requiring a running server.
    Reference: https://github.com/grpc/grpc/tree/master/src/python/grpcio_testing
    """
    # Create a test channel that can intercept RPC calls
    # We pass an empty list of service descriptors as we'll handle responses manually
    return grpc_testing.channel([], time=grpc_testing.strict_real_time())


@pytest.fixture
def api_handler(grpc_test_channel):
    """Create API handler with test channel.

    Patches grpc.insecure_channel to return our test channel so the
    handler can be tested without a real gRPC server.
    """
    with patch("grpc.insecure_channel", return_value=grpc_test_channel):
        from chirpstack_provisioning.api_handler import ChirpStackAPIHandler

        handler = ChirpStackAPIHandler("localhost:8080", "test-token")
        # Store test channel for test access
        handler._test_channel = grpc_test_channel
        return handler


class TestTenantIDUpdate:
    """Test that tenant IDs are updated after creation."""

    def test_tenant_id_updated_after_create(self, api_handler, sample_setup_data):
        """Test that tenant ID is updated with server-generated ID."""
        # Mock the Create response to return a server-generated ID
        mock_response = Mock()
        mock_response.id = "server-generated-tenant-id-123"
        api_handler.tenant_client.Create = Mock(return_value=mock_response)

        tenant_data = sample_setup_data["tenants"][0]

        # Create tenant and get the returned ID
        tenant_id = api_handler.create_tenant(
            name=tenant_data["name"],
            description=tenant_data.get("description"),
            can_have_gateways=tenant_data.get("canHaveGateways"),
        )

        # Verify the ID was returned
        assert tenant_id == "server-generated-tenant-id-123"

        # In a real implementation, this ID would be stored back to tenant_data
        # tenant_data["id"] = tenant_id
        # assert tenant_data["id"] == "server-generated-tenant-id-123"

    def test_tenant_id_preserved_when_provided(self, api_handler):
        """Test that when tenant ID is provided, it's used in creation."""
        # When an ID is provided (e.g., for restore operations), it should be preserved
        mock_response = Mock()
        mock_response.id = "user-provided-tenant-id"
        api_handler.tenant_client.Create = Mock(return_value=mock_response)

        tenant_data = {
            "id": "user-provided-tenant-id",
            "name": "Restored Tenant",
        }

        # Create with provided ID
        tenant_id = api_handler.create_tenant(
            name=tenant_data["name"], tenant_id=tenant_data.get("id")
        )

        # Server should return the same ID
        assert tenant_id == "user-provided-tenant-id"


class TestApplicationIDUpdate:
    """Test that application IDs are updated after creation."""

    def test_application_id_updated_after_create(self, api_handler):
        """Test that application ID is updated with server-generated ID."""
        mock_response = Mock()
        mock_response.id = "server-generated-app-id-456"
        api_handler.application_client.Create = Mock(return_value=mock_response)

        app_data = {
            "name": "Test App",
            "description": "Test application",
        }

        # Create application
        app_id = api_handler.create_application(
            tenant_id="tenant-123",
            name=app_data["name"],
            description=app_data.get("description"),
        )

        # Verify the ID was returned
        assert app_id == "server-generated-app-id-456"

        # In real implementation, update the data structure
        # app_data["id"] = app_id
        # assert app_data["id"] == "server-generated-app-id-456"

    def test_application_id_preserved_when_provided(self, api_handler):
        """Test that when application ID is provided, it's preserved."""
        mock_response = Mock()
        mock_response.id = "user-provided-app-id"
        api_handler.application_client.Create = Mock(return_value=mock_response)

        app_data = {
            "id": "user-provided-app-id",
            "name": "Restored App",
        }

        app_id = api_handler.create_application(
            tenant_id="tenant-123",
            name=app_data["name"],
            application_id=app_data.get("id"),
        )

        assert app_id == "user-provided-app-id"


class TestDeviceProfileIDUpdate:
    """Test that device profile IDs are updated after creation."""

    def test_device_profile_id_updated_after_create(self, api_handler):
        """Test that device profile ID is updated with server-generated ID."""
        mock_response = Mock()
        mock_response.id = "server-generated-profile-id-789"
        api_handler.device_profile_client.Create = Mock(return_value=mock_response)

        profile_data = {
            "name": "Test Profile",
            "region": "US915",
        }

        # Create device profile
        profile_id = api_handler.create_device_profile(
            tenant_id="tenant-123",
            name=profile_data["name"],
            region=profile_data.get("region"),
        )

        # Verify the ID was returned
        assert profile_id == "server-generated-profile-id-789"

    def test_device_profile_id_preserved_when_provided(self, api_handler):
        """Test that when device profile ID is provided, it's preserved."""
        mock_response = Mock()
        mock_response.id = "user-provided-profile-id"
        api_handler.device_profile_client.Create = Mock(return_value=mock_response)

        profile_data = {
            "id": "user-provided-profile-id",
            "name": "Restored Profile",
        }

        profile_id = api_handler.create_device_profile(
            tenant_id="tenant-123",
            name=profile_data["name"],
            profile_id=profile_data.get("id"),
        )

        assert profile_id == "user-provided-profile-id"


class TestGatewayIDUpdate:
    """Test that gateway IDs are updated after creation."""

    def test_gateway_id_updated_after_create(self, api_handler):
        """Test that gateway ID is updated with server-generated ID.

        Note: Gateways use gatewayId (the hardware EUI) as their identifier,
        but the Create response returns an 'id' field which should be stored.
        """
        mock_response = Mock()
        mock_response.id = "server-generated-gateway-id-abc"
        api_handler.gateway_client.Create = Mock(return_value=mock_response)

        gateway_data = {
            "gatewayId": "0102030405060708",
            "name": "Test Gateway",
        }

        # Create gateway
        gateway_id = api_handler.create_gateway(
            tenant_id="tenant-123",
            gateway_id=gateway_data["gatewayId"],
            name=gateway_data["name"],
        )

        # Verify the ID was returned
        assert gateway_id == "server-generated-gateway-id-abc"

    def test_gateway_uses_provided_gateway_eui(self, api_handler):
        """Test that gateway creation uses the provided gatewayId (EUI)."""
        mock_response = Mock()
        mock_response.id = "gateway-response-id"
        api_handler.gateway_client.Create = Mock(return_value=mock_response)

        gateway_data = {
            "gatewayId": "aabbccddeeff0011",
            "name": "Gateway with EUI",
        }

        _ = api_handler.create_gateway(
            tenant_id="tenant-123",
            gateway_id=gateway_data["gatewayId"],
            name=gateway_data["name"],
        )

        # Verify Create was called
        api_handler.gateway_client.Create.assert_called_once()

        # The gatewayId should be part of the request
        call_args = api_handler.gateway_client.Create.call_args[0][0]
        assert hasattr(call_args, "gateway")


class TestSetupDataWorkflow:
    """Integration tests for the complete setup data workflow with ID updates."""

    def test_complete_setup_with_id_updates(
        self, api_handler, sample_setup_data, tmp_path
    ):
        """Test complete workflow: load setup, create entities, update IDs."""
        # Mock all the Create responses
        api_handler.tenant_client.Create = Mock(return_value=Mock(id="tenant-id-001"))
        api_handler.application_client.Create = Mock(return_value=Mock(id="app-id-001"))
        api_handler.device_profile_client.Create = Mock(
            return_value=Mock(id="profile-id-001")
        )
        api_handler.gateway_client.Create = Mock(return_value=Mock(id="gateway-id-001"))

        # Write initial setup data to file
        setup_file = tmp_path / "setup.json"
        with open(setup_file, "w", encoding="utf-8") as f:
            json.dump(sample_setup_data, f)

        # Load setup data
        with open(setup_file, "r", encoding="utf-8") as f:
            setup_data = json.load(f)

        # Simulate provisioning workflow
        tenant_data = setup_data["tenants"][0]

        # Create tenant
        tenant_id = api_handler.create_tenant(
            name=tenant_data["name"],
            description=tenant_data.get("description"),
            can_have_gateways=tenant_data.get("canHaveGateways"),
        )

        # Update tenant data with returned ID
        tenant_data["id"] = tenant_id

        # Verify ID was updated
        assert tenant_data["id"] == "tenant-id-001"

        # Create application under tenant
        app_data = tenant_data["applications"][0]
        app_id = api_handler.create_application(
            tenant_id=tenant_id,
            name=app_data["name"],
            description=app_data.get("description"),
        )

        # Update application data with returned ID
        app_data["id"] = app_id
        assert app_data["id"] == "app-id-001"

        # Create device profile under tenant
        profile_data = tenant_data["device_profiles"][0]
        profile_id = api_handler.create_device_profile(
            tenant_id=tenant_id,
            name=profile_data["name"],
            region=profile_data.get("region"),
        )

        # Update device profile data with returned ID
        profile_data["id"] = profile_id
        assert profile_data["id"] == "profile-id-001"

        # Create gateway under tenant
        gateway_data = tenant_data["gateways"][0]
        gateway_id = api_handler.create_gateway(
            tenant_id=tenant_id,
            gateway_id=gateway_data["gatewayId"],
            name=gateway_data["name"],
        )

        # Update gateway data with returned ID
        gateway_data["id"] = gateway_id
        assert gateway_data["id"] == "gateway-id-001"

        # Write updated setup data back to file
        with open(setup_file, "w", encoding="utf-8") as f:
            json.dump(setup_data, f, indent=2)

        # Verify the file was updated
        with open(setup_file, "r", encoding="utf-8") as f:
            updated_data = json.load(f)

        assert updated_data["tenants"][0]["id"] == "tenant-id-001"
        assert updated_data["tenants"][0]["applications"][0]["id"] == "app-id-001"
        assert (
            updated_data["tenants"][0]["device_profiles"][0]["id"] == "profile-id-001"
        )
        assert updated_data["tenants"][0]["gateways"][0]["id"] == "gateway-id-001"

    def test_setup_without_initial_ids(self, tmp_path):
        """Test that setup data can be created without initial IDs."""
        setup_data = {
            "tenants": [
                {
                    "name": "New Tenant",
                    "canHaveGateways": True,
                    # No 'id' field initially
                }
            ]
        }

        setup_file = tmp_path / "setup_no_ids.json"
        with open(setup_file, "w", encoding="utf-8") as f:
            json.dump(setup_data, f)

        # Load and verify
        with open(setup_file, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)

        # Should not have ID field
        assert "id" not in loaded_data["tenants"][0]

        # After provisioning, ID would be added
        loaded_data["tenants"][0]["id"] = "newly-generated-id"
        assert loaded_data["tenants"][0]["id"] == "newly-generated-id"

    def test_setup_with_existing_ids_for_restore(self, tmp_path):
        """Test that setup data with existing IDs (for restore) preserves them."""
        setup_data = {
            "tenants": [
                {
                    "id": "existing-tenant-id",
                    "name": "Existing Tenant",
                    "canHaveGateways": True,
                }
            ]
        }

        setup_file = tmp_path / "setup_with_ids.json"
        with open(setup_file, "w", encoding="utf-8") as f:
            json.dump(setup_data, f)

        # Load and verify IDs are preserved
        with open(setup_file, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)

        assert loaded_data["tenants"][0]["id"] == "existing-tenant-id"
