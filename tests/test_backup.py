"""
Tests for ChirpStack backup functionality.

Following TDD methodology - these tests are written before implementation.
The backup procedure should retrieve setup information from a ChirpStack server
and convert it to the setup.json format for restore operations.
"""

import grpc
import grpc_testing
import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def grpc_test_channel():
    """Create a gRPC testing channel."""
    return grpc_testing.channel([], time=grpc_testing.strict_real_time())


@pytest.fixture
def api_handler(grpc_test_channel):
    """Create API handler with test channel."""
    with patch("grpc.insecure_channel", return_value=grpc_test_channel):
        from chirpstack_provisioning.api_handler import ChirpStackAPIHandler

        handler = ChirpStackAPIHandler("localhost:8080", "test-token")
        handler._test_channel = grpc_test_channel
        return handler


class TestGetTenant:
    """Test getting tenant information from server."""

    def test_get_tenant_returns_tenant_data(self, api_handler):
        """Test that get_tenant returns tenant object."""
        # Mock response with tenant data
        mock_tenant = Mock()
        mock_tenant.id = "tenant-123"
        mock_tenant.name = "Test Tenant"
        mock_tenant.description = "Test Description"
        mock_tenant.can_have_gateways = True
        mock_tenant.max_gateway_count = 10
        mock_tenant.max_device_count = 100
        mock_tenant.private_gateways_up = False
        mock_tenant.private_gateways_down = False
        mock_tenant.tags = {"env": "test"}

        mock_response = Mock()
        mock_response.tenant = mock_tenant
        mock_response.created_at = "2024-01-01T00:00:00Z"
        mock_response.updated_at = "2024-01-01T00:00:00Z"

        api_handler.tenant_client.Get = Mock(return_value=mock_response)

        result = api_handler.get_tenant("tenant-123")

        assert result is not None
        assert result["id"] == "tenant-123"
        assert result["name"] == "Test Tenant"
        assert result["description"] == "Test Description"
        assert result["canHaveGateways"] is True
        assert result["maxGatewayCount"] == 10
        assert result["maxDeviceCount"] == 100

    def test_get_tenant_includes_auth_metadata(self, api_handler):
        """Test that get_tenant includes authentication metadata."""
        mock_response = Mock()
        mock_response.tenant = Mock()
        mock_response.tenant.id = "tenant-123"

        api_handler.tenant_client.Get = Mock(return_value=mock_response)

        api_handler.get_tenant("tenant-123")

        call_args = api_handler.tenant_client.Get.call_args
        assert call_args[1]["metadata"] == [("authorization", "Bearer test-token")]

    def test_get_tenant_handles_tags(self, api_handler):
        """Test that get_tenant properly handles tags dictionary."""
        mock_tenant = Mock()
        mock_tenant.id = "tenant-123"
        mock_tenant.tags = {"key1": "value1", "key2": "value2"}

        mock_response = Mock()
        mock_response.tenant = mock_tenant

        api_handler.tenant_client.Get = Mock(return_value=mock_response)

        result = api_handler.get_tenant("tenant-123")

        assert "tags" in result
        assert result["tags"] == {"key1": "value1", "key2": "value2"}


class TestListTenants:
    """Test listing all tenants from server."""

    def test_list_tenants_returns_all_tenants(self, api_handler):
        """Test that list_tenants returns all tenant items."""
        # Mock tenant list items
        tenant1 = Mock()
        tenant1.id = "tenant-1"
        tenant1.name = "Tenant 1"

        tenant2 = Mock()
        tenant2.id = "tenant-2"
        tenant2.name = "Tenant 2"

        mock_response = Mock()
        mock_response.result = [tenant1, tenant2]
        mock_response.total_count = 2

        api_handler.tenant_client.List = Mock(return_value=mock_response)

        result = api_handler.list_tenants()

        assert len(result) == 2
        assert result[0]["id"] == "tenant-1"
        assert result[1]["id"] == "tenant-2"

    def test_list_tenants_handles_empty_list(self, api_handler):
        """Test that list_tenants handles empty tenant list."""
        mock_response = Mock()
        mock_response.result = []
        mock_response.total_count = 0

        api_handler.tenant_client.List = Mock(return_value=mock_response)

        result = api_handler.list_tenants()

        assert result == []


class TestGetApplication:
    """Test getting application information from server."""

    def test_get_application_returns_application_data(self, api_handler):
        """Test that get_application returns application object."""
        mock_app = Mock()
        mock_app.id = "app-123"
        mock_app.name = "Test Application"
        mock_app.description = "Test Description"
        mock_app.tenant_id = "tenant-123"
        mock_app.tags = {"type": "test"}

        mock_response = Mock()
        mock_response.application = mock_app

        api_handler.application_client.Get = Mock(return_value=mock_response)

        result = api_handler.get_application("app-123")

        assert result is not None
        assert result["id"] == "app-123"
        assert result["name"] == "Test Application"
        assert result["description"] == "Test Description"
        assert result["tenantId"] == "tenant-123"
        assert result["tags"] == {"type": "test"}


class TestListApplications:
    """Test listing applications for a tenant."""

    def test_list_applications_returns_tenant_applications(self, api_handler):
        """Test that list_applications returns applications for a tenant."""
        app1 = Mock()
        app1.id = "app-1"
        app1.name = "App 1"

        app2 = Mock()
        app2.id = "app-2"
        app2.name = "App 2"

        mock_response = Mock()
        mock_response.result = [app1, app2]
        mock_response.total_count = 2

        api_handler.application_client.List = Mock(return_value=mock_response)

        result = api_handler.list_applications("tenant-123")

        assert len(result) == 2
        assert result[0]["id"] == "app-1"
        assert result[1]["id"] == "app-2"


class TestGetGateway:
    """Test getting gateway information from server."""

    def test_get_gateway_returns_gateway_data(self, api_handler):
        """Test that get_gateway returns gateway object."""
        mock_gateway = Mock()
        mock_gateway.gateway_id = "0102030405060708"
        mock_gateway.name = "Test Gateway"
        mock_gateway.description = "Test Description"
        mock_gateway.tenant_id = "tenant-123"
        mock_gateway.stats_interval = 30
        mock_gateway.tags = {"location": "test"}

        mock_response = Mock()
        mock_response.gateway = mock_gateway

        api_handler.gateway_client.Get = Mock(return_value=mock_response)

        result = api_handler.get_gateway("0102030405060708")

        assert result is not None
        assert result["gatewayId"] == "0102030405060708"
        assert result["name"] == "Test Gateway"
        assert result["description"] == "Test Description"
        assert result["tenantId"] == "tenant-123"


class TestListGateways:
    """Test listing gateways for a tenant."""

    def test_list_gateways_returns_tenant_gateways(self, api_handler):
        """Test that list_gateways returns gateways for a tenant."""
        gw1 = Mock()
        gw1.gateway_id = "0102030405060708"
        gw1.name = "Gateway 1"

        gw2 = Mock()
        gw2.gateway_id = "0807060504030201"
        gw2.name = "Gateway 2"

        mock_response = Mock()
        mock_response.result = [gw1, gw2]
        mock_response.total_count = 2

        api_handler.gateway_client.List = Mock(return_value=mock_response)

        result = api_handler.list_gateways("tenant-123")

        assert len(result) == 2
        assert result[0]["gatewayId"] == "0102030405060708"
        assert result[1]["gatewayId"] == "0807060504030201"


class TestGetDeviceProfile:
    """Test getting device profile information from server."""

    def test_get_device_profile_returns_profile_data(self, api_handler):
        """Test that get_device_profile returns device profile object."""
        mock_profile = Mock()
        mock_profile.id = "profile-123"
        mock_profile.tenant_id = "tenant-123"
        mock_profile.name = "Test Profile"
        mock_profile.description = "Test Description"
        mock_profile.region = "US915"
        mock_profile.mac_version = "LORAWAN_1_0_3"
        mock_profile.reg_params_revision = "RP002_1_0_1"
        mock_profile.supports_otaa = True

        mock_response = Mock()
        mock_response.device_profile = mock_profile

        api_handler.device_profile_client.Get = Mock(return_value=mock_response)

        result = api_handler.get_device_profile("profile-123")

        assert result is not None
        assert result["id"] == "profile-123"
        assert result["name"] == "Test Profile"
        assert result["region"] == "US915"
        assert result["supportsOtaa"] is True


class TestListDeviceProfiles:
    """Test listing device profiles for a tenant."""

    def test_list_device_profiles_returns_tenant_profiles(self, api_handler):
        """Test that list_device_profiles returns profiles for a tenant."""
        profile1 = Mock()
        profile1.id = "profile-1"
        profile1.name = "Profile 1"

        profile2 = Mock()
        profile2.id = "profile-2"
        profile2.name = "Profile 2"

        mock_response = Mock()
        mock_response.result = [profile1, profile2]
        mock_response.total_count = 2

        api_handler.device_profile_client.List = Mock(return_value=mock_response)

        result = api_handler.list_device_profiles("tenant-123")

        assert len(result) == 2
        assert result[0]["id"] == "profile-1"
        assert result[1]["id"] == "profile-2"


class TestBackupTenant:
    """Test backing up a complete tenant with all nested entities."""

    def test_backup_tenant_retrieves_all_data(self, api_handler):
        """Test that backup_tenant retrieves tenant with nested entities."""
        # Mock tenant Get
        mock_tenant = Mock()
        mock_tenant.id = "tenant-123"
        mock_tenant.name = "Test Tenant"
        mock_tenant.can_have_gateways = True
        mock_tenant.tags = {}

        tenant_response = Mock()
        tenant_response.tenant = mock_tenant

        api_handler.tenant_client.Get = Mock(return_value=tenant_response)

        # Mock empty lists for nested entities
        api_handler.application_client.List = Mock(
            return_value=Mock(result=[], total_count=0)
        )
        api_handler.gateway_client.List = Mock(
            return_value=Mock(result=[], total_count=0)
        )
        api_handler.device_profile_client.List = Mock(
            return_value=Mock(result=[], total_count=0)
        )

        result = api_handler.backup_tenant("tenant-123")

        assert result is not None
        assert result["id"] == "tenant-123"
        assert result["name"] == "Test Tenant"
        assert "applications" in result
        assert "gateways" in result
        assert "device_profiles" in result

    def test_backup_tenant_includes_applications(self, api_handler):
        """Test that backup_tenant includes nested applications."""
        # Mock tenant
        tenant_response = Mock()
        tenant_response.tenant = Mock()
        tenant_response.tenant.id = "tenant-123"
        tenant_response.tenant.name = "Test"
        tenant_response.tenant.tags = {}

        api_handler.tenant_client.Get = Mock(return_value=tenant_response)

        # Mock application list
        app1 = Mock()
        app1.id = "app-1"
        app1.name = "App 1"

        api_handler.application_client.List = Mock(
            return_value=Mock(result=[app1], total_count=1)
        )

        # Mock application Get
        app_response = Mock()
        app_response.application = Mock()
        app_response.application.id = "app-1"
        app_response.application.name = "App 1"
        app_response.application.tenant_id = "tenant-123"
        app_response.application.tags = {}

        api_handler.application_client.Get = Mock(return_value=app_response)

        # Mock empty lists for other entities
        api_handler.gateway_client.List = Mock(
            return_value=Mock(result=[], total_count=0)
        )
        api_handler.device_profile_client.List = Mock(
            return_value=Mock(result=[], total_count=0)
        )

        result = api_handler.backup_tenant("tenant-123")

        assert len(result["applications"]) == 1
        assert result["applications"][0]["id"] == "app-1"

    def test_backup_tenant_includes_gateways(self, api_handler):
        """Test that backup_tenant includes nested gateways."""
        # Mock tenant
        tenant_response = Mock()
        tenant_response.tenant = Mock()
        tenant_response.tenant.id = "tenant-123"
        tenant_response.tenant.name = "Test"
        tenant_response.tenant.tags = {}

        api_handler.tenant_client.Get = Mock(return_value=tenant_response)

        # Mock gateway list
        gw1 = Mock()
        gw1.gateway_id = "0102030405060708"
        gw1.name = "Gateway 1"

        api_handler.gateway_client.List = Mock(
            return_value=Mock(result=[gw1], total_count=1)
        )

        # Mock gateway Get
        gw_response = Mock()
        gw_response.gateway = Mock()
        gw_response.gateway.gateway_id = "0102030405060708"
        gw_response.gateway.name = "Gateway 1"
        gw_response.gateway.tenant_id = "tenant-123"
        gw_response.gateway.tags = {}

        api_handler.gateway_client.Get = Mock(return_value=gw_response)

        # Mock empty lists for other entities
        api_handler.application_client.List = Mock(
            return_value=Mock(result=[], total_count=0)
        )
        api_handler.device_profile_client.List = Mock(
            return_value=Mock(result=[], total_count=0)
        )

        result = api_handler.backup_tenant("tenant-123")

        assert len(result["gateways"]) == 1
        assert result["gateways"][0]["gatewayId"] == "0102030405060708"


class TestBackupServer:
    """Test backing up complete server configuration."""

    def test_backup_server_returns_setup_format(self, api_handler):
        """Test that backup_server returns data in setup.json format."""
        # Mock tenant list
        tenant1 = Mock()
        tenant1.id = "tenant-1"
        tenant1.name = "Tenant 1"

        api_handler.tenant_client.List = Mock(
            return_value=Mock(result=[tenant1], total_count=1)
        )

        # Mock tenant Get
        tenant_response = Mock()
        tenant_response.tenant = Mock()
        tenant_response.tenant.id = "tenant-1"
        tenant_response.tenant.name = "Tenant 1"
        tenant_response.tenant.tags = {}

        api_handler.tenant_client.Get = Mock(return_value=tenant_response)

        # Mock empty lists for nested entities
        api_handler.application_client.List = Mock(
            return_value=Mock(result=[], total_count=0)
        )
        api_handler.gateway_client.List = Mock(
            return_value=Mock(result=[], total_count=0)
        )
        api_handler.device_profile_client.List = Mock(
            return_value=Mock(result=[], total_count=0)
        )

        result = api_handler.backup_server()

        assert "tenants" in result
        assert len(result["tenants"]) == 1
        assert result["tenants"][0]["id"] == "tenant-1"

    def test_backup_server_includes_all_tenants(self, api_handler):
        """Test that backup_server includes all tenants."""
        # Mock tenant list
        tenant1 = Mock()
        tenant1.id = "tenant-1"
        tenant1.name = "Tenant 1"

        tenant2 = Mock()
        tenant2.id = "tenant-2"
        tenant2.name = "Tenant 2"

        api_handler.tenant_client.List = Mock(
            return_value=Mock(result=[tenant1, tenant2], total_count=2)
        )

        # Mock tenant Get responses
        def get_tenant_side_effect(request, metadata):
            tenant_id = request.id
            response = Mock()
            response.tenant = Mock()
            response.tenant.id = tenant_id
            response.tenant.name = f"Tenant {tenant_id[-1]}"
            response.tenant.tags = {}
            return response

        api_handler.tenant_client.Get = Mock(side_effect=get_tenant_side_effect)

        # Mock empty lists for nested entities
        api_handler.application_client.List = Mock(
            return_value=Mock(result=[], total_count=0)
        )
        api_handler.gateway_client.List = Mock(
            return_value=Mock(result=[], total_count=0)
        )
        api_handler.device_profile_client.List = Mock(
            return_value=Mock(result=[], total_count=0)
        )

        result = api_handler.backup_server()

        assert len(result["tenants"]) == 2
        assert result["tenants"][0]["id"] == "tenant-1"
        assert result["tenants"][1]["id"] == "tenant-2"


class TestFieldConversion:
    """Test conversion between gRPC field names and setup.json field names."""

    def test_snake_case_to_camel_case_conversion(self, api_handler):
        """Test that snake_case gRPC fields are converted to camelCase."""
        # Test with tenant fields
        mock_tenant = Mock()
        mock_tenant.id = "tenant-123"
        mock_tenant.can_have_gateways = True
        mock_tenant.max_gateway_count = 10
        mock_tenant.max_device_count = 100
        mock_tenant.private_gateways_up = False
        mock_tenant.private_gateways_down = False
        mock_tenant.tags = {}

        tenant_response = Mock()
        tenant_response.tenant = mock_tenant

        api_handler.tenant_client.Get = Mock(return_value=tenant_response)

        result = api_handler.get_tenant("tenant-123")

        # Check camelCase conversion
        assert "canHaveGateways" in result
        assert "maxGatewayCount" in result
        assert "maxDeviceCount" in result
        assert "privateGatewaysUp" in result
        assert "privateGatewaysDown" in result

    def test_gateway_id_field_conversion(self, api_handler):
        """Test that gateway_id is converted to gatewayId."""
        mock_gateway = Mock()
        mock_gateway.gateway_id = "0102030405060708"
        mock_gateway.name = "Test Gateway"
        mock_gateway.tenant_id = "tenant-123"
        mock_gateway.tags = {}

        gw_response = Mock()
        gw_response.gateway = mock_gateway

        api_handler.gateway_client.Get = Mock(return_value=gw_response)

        result = api_handler.get_gateway("0102030405060708")

        assert "gatewayId" in result
        assert "tenantId" in result
        assert result["gatewayId"] == "0102030405060708"

    def test_device_profile_field_conversion(self, api_handler):
        """Test that device profile fields are properly converted."""
        mock_profile = Mock()
        mock_profile.id = "profile-123"
        mock_profile.tenant_id = "tenant-123"
        mock_profile.mac_version = "LORAWAN_1_0_3"
        mock_profile.reg_params_revision = "RP002_1_0_1"
        mock_profile.supports_otaa = True
        mock_profile.supports_class_b = False
        mock_profile.supports_class_c = False

        profile_response = Mock()
        profile_response.device_profile = mock_profile

        api_handler.device_profile_client.Get = Mock(return_value=profile_response)

        result = api_handler.get_device_profile("profile-123")

        assert "tenantId" in result
        assert "macVersion" in result
        assert "regParamsRevision" in result
        assert "supportsOtaa" in result
        assert "supportsClassB" in result
        assert "supportsClassC" in result


class TestErrorHandling:
    """Test error handling during backup operations."""

    def test_get_tenant_handles_not_found_error(self, api_handler):
        """Test that get_tenant handles NOT_FOUND gRPC error."""
        mock_error = grpc.RpcError()
        mock_error.code = Mock(return_value=grpc.StatusCode.NOT_FOUND)
        mock_error.details = Mock(return_value="Tenant not found")

        api_handler.tenant_client.Get = Mock(side_effect=mock_error)

        result = api_handler.get_tenant("non-existent-tenant")

        assert result is None

    def test_backup_tenant_handles_permission_denied(self, api_handler):
        """Test that backup_tenant handles PERMISSION_DENIED error."""
        mock_error = grpc.RpcError()
        mock_error.code = Mock(return_value=grpc.StatusCode.PERMISSION_DENIED)
        mock_error.details = Mock(return_value="Permission denied")

        api_handler.tenant_client.Get = Mock(side_effect=mock_error)

        result = api_handler.backup_tenant("tenant-123")

        assert result is None

    def test_list_tenants_handles_unavailable_error(self, api_handler):
        """Test that list_tenants handles UNAVAILABLE gRPC error."""
        mock_error = grpc.RpcError()
        mock_error.code = Mock(return_value=grpc.StatusCode.UNAVAILABLE)
        mock_error.details = Mock(return_value="Server unavailable")

        api_handler.tenant_client.List = Mock(side_effect=mock_error)

        result = api_handler.list_tenants()

        assert result == []
