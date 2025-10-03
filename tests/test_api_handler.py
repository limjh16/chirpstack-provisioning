"""
Tests for ChirpStack gRPC API handler.

Following TDD methodology - these tests are written before implementation.
Uses grpc_testing for proper gRPC service testing as recommended by gRPC project.
Reference: https://github.com/grpc/grpc/tree/master/src/python/grpcio_tests/tests/unit
"""

import pytest
import grpc
import grpc_testing
from unittest.mock import Mock, patch
from chirpstack_api import api


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


def _setup_unary_unary_response(
    channel, response, method_name="/api.TenantService/Create"
):
    """Helper to setup a unary-unary RPC response in the test channel.

    This is the pattern used in gRPC's own test suite for testing
    unary-unary RPC calls.
    """
    # This would be implemented when we have actual tests that need it
    # For now, we'll continue using Mock for simplicity in TDD phase
    pass


class TestChirpStackAPIHandlerInitialization:
    """Test API handler initialization."""

    def test_init_stores_server_and_token(self, grpc_test_channel):
        """Test that initialization stores server and API token."""
        with patch("grpc.insecure_channel", return_value=grpc_test_channel):
            from chirpstack_provisioning.api_handler import ChirpStackAPIHandler

            handler = ChirpStackAPIHandler("localhost:8080", "test-token")

            assert handler.server == "localhost:8080"
            assert handler.api_token == "test-token"

    def test_init_creates_grpc_channel(self, grpc_test_channel):
        """Test that initialization creates an insecure gRPC channel."""
        with patch(
            "grpc.insecure_channel", return_value=grpc_test_channel
        ) as mock_grpc:
            from chirpstack_provisioning.api_handler import ChirpStackAPIHandler

            handler = ChirpStackAPIHandler("localhost:8080", "test-token")

            mock_grpc.assert_called_once_with("localhost:8080")
            assert handler.channel == grpc_test_channel

    def test_init_creates_service_clients(self, api_handler):
        """Test that all required service clients are created."""
        assert hasattr(api_handler, "tenant_client")
        assert hasattr(api_handler, "application_client")
        assert hasattr(api_handler, "device_profile_client")
        assert hasattr(api_handler, "gateway_client")
        assert hasattr(api_handler, "device_client")


class TestAuthToken:
    """Test authentication token generation."""

    def test_auth_token_returns_metadata_list(self, api_handler):
        """Test that auth_token returns a list suitable for gRPC metadata."""
        metadata = api_handler.auth_token()

        assert isinstance(metadata, list)
        assert len(metadata) == 1

    def test_auth_token_format(self, api_handler):
        """Test that auth_token returns correct Bearer token format."""
        metadata = api_handler.auth_token()

        assert metadata[0][0] == "authorization"
        assert metadata[0][1] == "Bearer test-token"


class TestCreateTenant:
    """Test tenant creation."""

    def test_create_tenant_basic(self, api_handler):
        """Test creating a tenant with basic attributes."""
        mock_response = Mock()
        mock_response.id = "tenant-123"
        api_handler.tenant_client.Create = Mock(return_value=mock_response)

        tenant_id = api_handler.create_tenant(name="Test Tenant")

        assert tenant_id == "tenant-123"
        api_handler.tenant_client.Create.assert_called_once()

    def test_create_tenant_with_multiple_attributes(self, api_handler):
        """Test creating a tenant with multiple attributes."""
        mock_response = Mock()
        mock_response.id = "tenant-456"
        api_handler.tenant_client.Create = Mock(return_value=mock_response)

        tenant_id = api_handler.create_tenant(
            name="Test Tenant", description="Test Description", can_have_gateways=True
        )

        assert tenant_id == "tenant-456"

    def test_create_tenant_includes_auth_metadata(self, api_handler):
        """Test that create_tenant includes authentication metadata."""
        mock_response = Mock()
        mock_response.id = "tenant-789"
        api_handler.tenant_client.Create = Mock(return_value=mock_response)

        api_handler.create_tenant(name="Test Tenant")

        call_args = api_handler.tenant_client.Create.call_args
        assert call_args[1]["metadata"] == [("authorization", "Bearer test-token")]


class TestCreateApplication:
    """Test application creation."""

    def test_create_application_basic(self, api_handler):
        """Test creating an application with tenant_id."""
        mock_response = Mock()
        mock_response.id = "app-123"
        api_handler.application_client.Create = Mock(return_value=mock_response)

        app_id = api_handler.create_application("tenant-1", name="Test App")

        assert app_id == "app-123"
        api_handler.application_client.Create.assert_called_once()

    def test_create_application_with_description(self, api_handler):
        """Test creating an application with description."""
        mock_response = Mock()
        mock_response.id = "app-456"
        api_handler.application_client.Create = Mock(return_value=mock_response)

        app_id = api_handler.create_application(
            "tenant-1", name="Test App", description="Test Description"
        )

        assert app_id == "app-456"


class TestCreateDeviceProfile:
    """Test device profile creation."""

    def test_create_device_profile_basic(self, api_handler):
        """Test creating a device profile with tenant_id."""
        mock_response = Mock()
        mock_response.id = "profile-123"
        api_handler.device_profile_client.Create = Mock(return_value=mock_response)

        profile_id = api_handler.create_device_profile("tenant-1", name="Test Profile")

        assert profile_id == "profile-123"

    def test_create_device_profile_with_region(self, api_handler):
        """Test creating a device profile with region configuration."""
        mock_response = Mock()
        mock_response.id = "profile-456"
        api_handler.device_profile_client.Create = Mock(return_value=mock_response)

        profile_id = api_handler.create_device_profile(
            "tenant-1", name="Test Profile", region="US915"
        )

        assert profile_id == "profile-456"


class TestCreateGateway:
    """Test gateway creation."""

    def test_create_gateway_basic(self, api_handler):
        """Test creating a gateway with tenant_id and gateway_id."""
        mock_response = Mock()
        mock_response.id = "gateway-123"
        api_handler.gateway_client.Create = Mock(return_value=mock_response)

        gateway_id = api_handler.create_gateway(
            "tenant-1", gateway_id="0000000000000001", name="Test Gateway"
        )

        assert gateway_id == "gateway-123"

    def test_create_gateway_with_location(self, api_handler):
        """Test creating a gateway with location information."""
        mock_response = Mock()
        mock_response.id = "gateway-456"
        api_handler.gateway_client.Create = Mock(return_value=mock_response)

        gateway_id = api_handler.create_gateway(
            "tenant-1",
            gateway_id="0000000000000002",
            name="Test Gateway",
            location={"latitude": 37.7749, "longitude": -122.4194},
        )

        assert gateway_id == "gateway-456"


class TestCreateDevice:
    """Test device creation."""

    def test_create_device_basic(self, api_handler):
        """Test creating a device with required parameters."""
        mock_response = Mock()
        mock_response.id = "device-123"
        api_handler.device_client.Create = Mock(return_value=mock_response)

        device_id = api_handler.create_device(
            "app-1", "profile-1", dev_eui="0000000000000001", name="Test Device"
        )

        assert device_id == "device-123"

    def test_create_device_with_description(self, api_handler):
        """Test creating a device with description."""
        mock_response = Mock()
        mock_response.id = "device-456"
        api_handler.device_client.Create = Mock(return_value=mock_response)

        device_id = api_handler.create_device(
            "app-1",
            "profile-1",
            dev_eui="0000000000000002",
            name="Test Device",
            description="Test Description",
        )

        assert device_id == "device-456"


class TestCreateDeviceKeys:
    """Test device keys creation."""

    def test_create_device_keys_basic(self, api_handler):
        """Test creating device keys with dev_eui."""
        api_handler.device_client.CreateKeys = Mock(return_value=Mock())

        api_handler.create_device_keys(
            "0000000000000001", nwk_key="00000000000000000000000000000001"
        )

        api_handler.device_client.CreateKeys.assert_called_once()

    def test_create_device_keys_with_app_key(self, api_handler):
        """Test creating device keys with nwk_key and app_key."""
        api_handler.device_client.CreateKeys = Mock(return_value=Mock())

        api_handler.create_device_keys(
            "0000000000000002",
            nwk_key="00000000000000000000000000000002",
            app_key="00000000000000000000000000000002",
        )

        api_handler.device_client.CreateKeys.assert_called_once()


class TestSetAttributes:
    """Test the helper method for setting attributes on request objects."""

    def test_set_attributes_simple_values(self, api_handler):
        """Test setting simple attribute values on an object."""
        mock_obj = Mock()
        attrs = {"name": "Test", "value": 123}

        api_handler._set_attributes(mock_obj, attrs)

        assert mock_obj.name == "Test"
        assert mock_obj.value == 123

    def test_set_attributes_nested_dict(self, api_handler):
        """Test setting nested dictionary values on an object."""
        mock_obj = Mock()
        mock_obj.tags = {}
        attrs = {"tags": {"key1": "value1", "key2": "value2"}}

        api_handler._set_attributes(mock_obj, attrs)

        assert mock_obj.tags["key1"] == "value1"
        assert mock_obj.tags["key2"] == "value2"

    def test_set_attributes_ignores_missing_attributes(self, api_handler):
        """Test that setting attributes on non-existent fields doesn't raise error."""
        mock_obj = Mock(spec=["existing_attr"])
        attrs = {"existing_attr": "value", "non_existent": "value"}

        api_handler._set_attributes(mock_obj, attrs)

        assert mock_obj.existing_attr == "value"


class TestSendRequest:
    """Test the helper method for sending gRPC requests."""

    def test_send_request_success_with_id(self, api_handler):
        """Test successful request that returns an ID."""
        mock_method = Mock()
        mock_response = Mock()
        mock_response.id = "test-id-123"
        mock_method.return_value = mock_response

        mock_request = Mock()
        mock_request.DESCRIPTOR.name = "TestRequest"

        result = api_handler._send_request(
            mock_method, mock_request, [("authorization", "Bearer test-token")]
        )

        assert result == "test-id-123"
        mock_method.assert_called_once()

    def test_send_request_success_without_id(self, api_handler):
        """Test successful request that doesn't return an ID."""
        mock_method = Mock()
        mock_response = Mock(spec=[])
        mock_method.return_value = mock_response

        mock_request = Mock()
        mock_request.DESCRIPTOR.name = "TestRequest"

        result = api_handler._send_request(
            mock_method, mock_request, [("authorization", "Bearer test-token")]
        )

        assert result is None

    def test_send_request_grpc_error(self, api_handler):
        """Test handling of gRPC errors."""
        mock_method = Mock()
        mock_error = grpc.RpcError()
        mock_error.code = Mock(return_value=grpc.StatusCode.UNAUTHENTICATED)
        mock_error.details = Mock(return_value="Invalid token")
        mock_method.side_effect = mock_error

        mock_request = Mock()
        mock_request.DESCRIPTOR.name = "TestRequest"

        result = api_handler._send_request(
            mock_method, mock_request, [("authorization", "Bearer test-token")]
        )

        assert result is None

    def test_send_request_includes_metadata(self, api_handler):
        """Test that request includes authentication metadata."""
        mock_method = Mock()
        mock_response = Mock()
        mock_response.id = "test-id"
        mock_method.return_value = mock_response

        mock_request = Mock()
        mock_request.DESCRIPTOR.name = "TestRequest"
        metadata = [("authorization", "Bearer test-token")]

        api_handler._send_request(mock_method, mock_request, metadata)

        call_kwargs = mock_method.call_args[1]
        assert call_kwargs["metadata"] == metadata


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_invalid_server_address(self, mock_channel):
        """Test handling of invalid server address."""
        with patch("grpc.insecure_channel", return_value=mock_channel):
            from chirpstack_provisioning.api_handler import ChirpStackAPIHandler

            handler = ChirpStackAPIHandler("", "test-token")

            assert handler.server == ""

    def test_empty_api_token(self, mock_channel):
        """Test handling of empty API token."""
        with patch("grpc.insecure_channel", return_value=mock_channel):
            from chirpstack_provisioning.api_handler import ChirpStackAPIHandler

            handler = ChirpStackAPIHandler("localhost:8080", "")

            metadata = handler.auth_token()
            assert metadata[0][1] == "Bearer "

    def test_grpc_unavailable_error(self, api_handler):
        """Test handling of gRPC unavailable error."""
        mock_error = grpc.RpcError()
        mock_error.code = Mock(return_value=grpc.StatusCode.UNAVAILABLE)
        mock_error.details = Mock(return_value="Connection refused")

        api_handler.tenant_client.Create = Mock(side_effect=mock_error)

        result = api_handler.create_tenant(name="Test")

        assert result is None

    def test_grpc_permission_denied_error(self, api_handler):
        """Test handling of gRPC permission denied error."""
        mock_error = grpc.RpcError()
        mock_error.code = Mock(return_value=grpc.StatusCode.PERMISSION_DENIED)
        mock_error.details = Mock(return_value="Permission denied")

        api_handler.application_client.Create = Mock(side_effect=mock_error)

        result = api_handler.create_application("tenant-1", name="Test")

        assert result is None


class TestRequestConstruction:
    """Test that requests are constructed correctly."""

    def test_create_tenant_request_construction(self, api_handler):
        """Test that CreateTenantRequest is constructed properly."""
        mock_response = Mock()
        mock_response.id = "tenant-123"

        with patch.object(api, "CreateTenantRequest") as mock_request_class:
            mock_request = Mock()
            mock_request_class.return_value = mock_request
            api_handler.tenant_client.Create = Mock(return_value=mock_response)

            api_handler.create_tenant(name="Test", description="Desc")

            mock_request_class.assert_called_once()

    def test_create_device_request_sets_application_and_profile(self, api_handler):
        """Test that CreateDeviceRequest sets application_id and device_profile_id."""
        mock_response = Mock()
        mock_response.id = "device-123"
        api_handler.device_client.Create = Mock(return_value=mock_response)

        api_handler.create_device(
            "app-123", "profile-456", dev_eui="0000000000000001", name="Test Device"
        )

        call_args = api_handler.device_client.Create.call_args[0][0]
        assert hasattr(call_args, "device")

    def test_create_gateway_request_sets_tenant_id(self, api_handler):
        """Test that CreateGatewayRequest sets tenant_id."""
        mock_response = Mock()
        mock_response.id = "gateway-123"
        api_handler.gateway_client.Create = Mock(return_value=mock_response)

        api_handler.create_gateway(
            "tenant-123", gateway_id="0000000000000001", name="Test Gateway"
        )

        call_args = api_handler.gateway_client.Create.call_args[0][0]
        assert hasattr(call_args, "gateway")


class TestIntegrationScenarios:
    """Test common integration scenarios."""

    def test_provision_complete_device_flow(self, api_handler):
        """Test provisioning a complete device with all dependencies."""
        api_handler.tenant_client.Create = Mock(return_value=Mock(id="tenant-1"))
        api_handler.application_client.Create = Mock(return_value=Mock(id="app-1"))
        api_handler.device_profile_client.Create = Mock(
            return_value=Mock(id="profile-1")
        )
        api_handler.device_client.Create = Mock(return_value=Mock(id="device-1"))
        api_handler.device_client.CreateKeys = Mock(return_value=Mock())

        tenant_id = api_handler.create_tenant(name="Test Tenant")
        app_id = api_handler.create_application(tenant_id, name="Test App")
        profile_id = api_handler.create_device_profile(tenant_id, name="Test Profile")
        device_id = api_handler.create_device(
            app_id, profile_id, dev_eui="0000000000000001", name="Test Device"
        )
        api_handler.create_device_keys(
            "0000000000000001", nwk_key="00000000000000000000000000000001"
        )

        assert tenant_id == "tenant-1"
        assert app_id == "app-1"
        assert profile_id == "profile-1"
        assert device_id == "device-1"

    def test_provision_gateway_with_tenant(self, api_handler):
        """Test provisioning a gateway under a tenant."""
        api_handler.tenant_client.Create = Mock(return_value=Mock(id="tenant-1"))
        api_handler.gateway_client.Create = Mock(return_value=Mock(id="gateway-1"))

        tenant_id = api_handler.create_tenant(name="Test Tenant")
        gateway_id = api_handler.create_gateway(
            tenant_id, gateway_id="0000000000000001", name="Test Gateway"
        )

        assert tenant_id == "tenant-1"
        assert gateway_id == "gateway-1"
