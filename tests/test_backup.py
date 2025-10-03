"""Tests for ChirpStack backup functionality.

Following TDD methodology - these tests are written before implementation.
Tests use grpc_testing to simulate server responses for Get/List requests.
"""

import json
import pytest
import grpc_testing
from unittest.mock import patch
from chirpstack_api import api


@pytest.fixture
def grpc_test_channel():
    """Create a gRPC testing channel.

    Uses grpc_testing.channel() to create a test channel that intercepts
    gRPC calls for testing without requiring a running server.
    """
    return grpc_testing.channel([], time=grpc_testing.strict_real_time())


@pytest.fixture
def api_handler(grpc_test_channel):
    """Create API handler with test channel for backup operations.

    Patches grpc.insecure_channel to return our test channel.
    """
    with patch("grpc.insecure_channel", return_value=grpc_test_channel):
        from chirpstack_provisioning.api_handler import ChirpStackAPIHandler

        handler = ChirpStackAPIHandler("localhost:8080", "test-token")
        handler._test_channel = grpc_test_channel
        return handler


class TestListTenants:
    """Test listing tenants from the server."""

    def test_list_tenants_returns_tenant_list(self, api_handler):
        """Test that list_tenants returns a list of tenants."""
        # Mock response with two tenants
        mock_tenant_1 = api.Tenant(
            id="00000000-0000-0000-0000-000000000001",
            name="Tenant 1",
            description="First tenant",
            can_have_gateways=True,
            max_gateway_count=10,
            max_device_count=100,
        )
        mock_tenant_2 = api.Tenant(
            id="00000000-0000-0000-0000-000000000002",
            name="Tenant 2",
            description="Second tenant",
            can_have_gateways=False,
        )
        mock_response = api.ListTenantsResponse(
            total_count=2, result=[mock_tenant_1, mock_tenant_2]
        )

        api_handler.tenant_client.List = lambda req, metadata: mock_response

        tenants = api_handler.list_tenants()

        assert isinstance(tenants, list)
        assert len(tenants) == 2
        assert tenants[0].name == "Tenant 1"
        assert tenants[1].name == "Tenant 2"

    def test_list_tenants_empty(self, api_handler):
        """Test list_tenants with no tenants."""
        mock_response = api.ListTenantsResponse(total_count=0, result=[])
        api_handler.tenant_client.List = lambda req, metadata: mock_response

        tenants = api_handler.list_tenants()

        assert isinstance(tenants, list)
        assert len(tenants) == 0


class TestGetTenant:
    """Test getting a specific tenant from the server."""

    def test_get_tenant_returns_tenant_data(self, api_handler):
        """Test that get_tenant returns tenant data."""
        mock_tenant = api.Tenant(
            id="00000000-0000-0000-0000-000000000001",
            name="Test Tenant",
            description="A test tenant",
            can_have_gateways=True,
            max_gateway_count=10,
            max_device_count=100,
        )
        mock_response = api.GetTenantResponse(tenant=mock_tenant)

        api_handler.tenant_client.Get = lambda req, metadata: mock_response

        tenant = api_handler.get_tenant("00000000-0000-0000-0000-000000000001")

        assert tenant.name == "Test Tenant"
        assert tenant.description == "A test tenant"
        assert tenant.can_have_gateways is True


class TestListGateways:
    """Test listing gateways from the server."""

    def test_list_gateways_returns_gateway_list(self, api_handler):
        """Test that list_gateways returns a list of gateways."""
        mock_gateway = api.GatewayListItem(
            gateway_id="0102030405060708",
            name="Test Gateway",
            description="A test gateway",
            tenant_id="00000000-0000-0000-0000-000000000001",
        )
        mock_response = api.ListGatewaysResponse(total_count=1, result=[mock_gateway])

        api_handler.gateway_client.List = lambda req, metadata: mock_response

        gateways = api_handler.list_gateways("00000000-0000-0000-0000-000000000001")

        assert isinstance(gateways, list)
        assert len(gateways) == 1
        assert gateways[0].gateway_id == "0102030405060708"

    def test_list_gateways_empty(self, api_handler):
        """Test list_gateways with no gateways."""
        mock_response = api.ListGatewaysResponse(total_count=0, result=[])
        api_handler.gateway_client.List = lambda req, metadata: mock_response

        gateways = api_handler.list_gateways("00000000-0000-0000-0000-000000000001")

        assert isinstance(gateways, list)
        assert len(gateways) == 0


class TestGetGateway:
    """Test getting a specific gateway from the server."""

    def test_get_gateway_returns_gateway_data(self, api_handler):
        """Test that get_gateway returns gateway data."""
        mock_gateway = api.Gateway(
            gateway_id="0102030405060708",
            name="Test Gateway",
            description="A test gateway",
            tenant_id="00000000-0000-0000-0000-000000000001",
            stats_interval=30,
        )
        mock_response = api.GetGatewayResponse(gateway=mock_gateway)

        api_handler.gateway_client.Get = lambda req, metadata: mock_response

        gateway = api_handler.get_gateway("0102030405060708")

        assert gateway.gateway_id == "0102030405060708"
        assert gateway.name == "Test Gateway"
        assert gateway.stats_interval == 30


class TestListApplications:
    """Test listing applications from the server."""

    def test_list_applications_returns_application_list(self, api_handler):
        """Test that list_applications returns a list of applications."""
        mock_app = api.ApplicationListItem(
            id="00000000-0000-0000-0000-000000000010",
            name="Test Application",
            description="A test application",
            tenant_id="00000000-0000-0000-0000-000000000001",
        )
        mock_response = api.ListApplicationsResponse(total_count=1, result=[mock_app])

        api_handler.application_client.List = lambda req, metadata: mock_response

        apps = api_handler.list_applications("00000000-0000-0000-0000-000000000001")

        assert isinstance(apps, list)
        assert len(apps) == 1
        assert apps[0].name == "Test Application"


class TestGetApplication:
    """Test getting a specific application from the server."""

    def test_get_application_returns_application_data(self, api_handler):
        """Test that get_application returns application data."""
        mock_app = api.Application(
            id="00000000-0000-0000-0000-000000000010",
            name="Test Application",
            description="A test application",
            tenant_id="00000000-0000-0000-0000-000000000001",
        )
        mock_response = api.GetApplicationResponse(application=mock_app)

        api_handler.application_client.Get = lambda req, metadata: mock_response

        app = api_handler.get_application("00000000-0000-0000-0000-000000000010")

        assert app.id == "00000000-0000-0000-0000-000000000010"
        assert app.name == "Test Application"


class TestListDeviceProfiles:
    """Test listing device profiles from the server."""

    def test_list_device_profiles_returns_profile_list(self, api_handler):
        """Test that list_device_profiles returns a list of device profiles."""
        mock_profile = api.DeviceProfileListItem(
            id="00000000-0000-0000-0000-000000000020",
            name="Test Profile",
            tenant_id="00000000-0000-0000-0000-000000000001",
            region="US915",
        )
        mock_response = api.ListDeviceProfilesResponse(
            total_count=1, result=[mock_profile]
        )

        api_handler.device_profile_client.List = lambda req, metadata: mock_response

        profiles = api_handler.list_device_profiles(
            "00000000-0000-0000-0000-000000000001"
        )

        assert isinstance(profiles, list)
        assert len(profiles) == 1
        assert profiles[0].name == "Test Profile"


class TestGetDeviceProfile:
    """Test getting a specific device profile from the server."""

    def test_get_device_profile_returns_profile_data(self, api_handler):
        """Test that get_device_profile returns device profile data."""
        mock_profile = api.DeviceProfile(
            id="00000000-0000-0000-0000-000000000020",
            name="Test Profile",
            tenant_id="00000000-0000-0000-0000-000000000001",
            region="US915",
            mac_version=api.MacVersion.LORAWAN_1_0_3,
            reg_params_revision=api.RegParamsRevision.RP002_1_0_1,
            supports_otaa=True,
        )
        mock_response = api.GetDeviceProfileResponse(device_profile=mock_profile)

        api_handler.device_profile_client.Get = lambda req, metadata: mock_response

        profile = api_handler.get_device_profile("00000000-0000-0000-0000-000000000020")

        assert profile.name == "Test Profile"
        assert profile.region == "US915"
        assert profile.supports_otaa is True


class TestListUsers:
    """Test listing users from the server."""

    def test_list_users_returns_user_list(self, api_handler):
        """Test that list_users returns a list of users."""
        mock_user = api.UserListItem(
            id="00000000-0000-0000-0000-000000000030",
            email="test@example.com",
            is_admin=True,
            is_active=True,
        )
        mock_response = api.ListUsersResponse(total_count=1, result=[mock_user])

        api_handler.user_client.List = lambda req, metadata: mock_response

        users = api_handler.list_users()

        assert isinstance(users, list)
        assert len(users) == 1
        assert users[0].email == "test@example.com"


class TestGetUser:
    """Test getting a specific user from the server."""

    def test_get_user_returns_user_data(self, api_handler):
        """Test that get_user returns user data."""
        mock_user = api.User(
            id="00000000-0000-0000-0000-000000000030",
            email="test@example.com",
            is_admin=True,
            is_active=True,
            note="Test user",
        )
        mock_response = api.GetUserResponse(user=mock_user)

        api_handler.user_client.Get = lambda req, metadata: mock_response

        user = api_handler.get_user("00000000-0000-0000-0000-000000000030")

        assert user.email == "test@example.com"
        assert user.is_admin is True
        assert user.note == "Test user"


class TestListDeviceProfileTemplates:
    """Test listing device profile templates from the server."""

    def test_list_device_profile_templates_returns_template_list(self, api_handler):
        """Test that list_device_profile_templates returns a list of templates."""
        mock_template = api.DeviceProfileTemplateListItem(
            id="00000000-0000-0000-0000-000000000040",
            name="Test Template",
        )
        mock_response = api.ListDeviceProfileTemplatesResponse(
            total_count=1, result=[mock_template]
        )

        api_handler.device_profile_template_client.List = (
            lambda req, metadata: mock_response
        )

        templates = api_handler.list_device_profile_templates()

        assert isinstance(templates, list)
        assert len(templates) == 1
        assert templates[0].name == "Test Template"


class TestGetDeviceProfileTemplate:
    """Test getting a specific device profile template from the server."""

    def test_get_device_profile_template_returns_template_data(self, api_handler):
        """Test that get_device_profile_template returns template data."""
        mock_template = api.DeviceProfileTemplate(
            id="00000000-0000-0000-0000-000000000040",
            name="Test Template",
            description="A test template",
            vendor="Test Vendor",
            firmware="1.0.0",
            region="US915",
            mac_version=api.MacVersion.LORAWAN_1_0_3,
            reg_params_revision=api.RegParamsRevision.RP002_1_0_1,
            supports_otaa=True,
        )
        mock_response = api.GetDeviceProfileTemplateResponse(
            device_profile_template=mock_template
        )

        api_handler.device_profile_template_client.Get = (
            lambda req, metadata: mock_response
        )

        template = api_handler.get_device_profile_template(
            "00000000-0000-0000-0000-000000000040"
        )

        assert template.name == "Test Template"
        assert template.vendor == "Test Vendor"
        assert template.region == "US915"


class TestBackupSetup:
    """Test backing up ChirpStack server setup to setup.json."""

    def test_backup_setup_creates_valid_structure(self, api_handler, tmp_path):
        """Test that backup_setup creates a valid setup.json structure."""
        # Mock responses for all entities
        mock_tenant = api.Tenant(
            id="00000000-0000-0000-0000-000000000001",
            name="Backup Tenant",
            description="A tenant for backup",
            can_have_gateways=True,
            max_gateway_count=10,
            max_device_count=100,
        )
        mock_gateway = api.Gateway(
            gateway_id="0102030405060708",
            name="Backup Gateway",
            tenant_id="00000000-0000-0000-0000-000000000001",
            stats_interval=30,
        )
        mock_app = api.Application(
            id="00000000-0000-0000-0000-000000000010",
            name="Backup App",
            tenant_id="00000000-0000-0000-0000-000000000001",
        )
        mock_profile = api.DeviceProfile(
            id="00000000-0000-0000-0000-000000000020",
            name="Backup Profile",
            tenant_id="00000000-0000-0000-0000-000000000001",
            region="US915",
            mac_version=api.MacVersion.LORAWAN_1_0_3,
            reg_params_revision=api.RegParamsRevision.RP002_1_0_1,
            supports_otaa=True,
        )
        mock_user = api.User(
            id="00000000-0000-0000-0000-000000000030",
            email="backup@example.com",
            is_admin=True,
            is_active=True,
        )

        # Setup mock responses
        api_handler.tenant_client.List = lambda req, metadata: api.ListTenantsResponse(
            total_count=1, result=[mock_tenant]
        )
        api_handler.tenant_client.Get = lambda req, metadata: api.GetTenantResponse(
            tenant=mock_tenant
        )
        api_handler.gateway_client.List = (
            lambda req, metadata: api.ListGatewaysResponse(
                total_count=1,
                result=[api.GatewayListItem(gateway_id="0102030405060708")],
            )
        )
        api_handler.gateway_client.Get = lambda req, metadata: api.GetGatewayResponse(
            gateway=mock_gateway
        )
        api_handler.application_client.List = (
            lambda req, metadata: api.ListApplicationsResponse(
                total_count=1,
                result=[
                    api.ApplicationListItem(id="00000000-0000-0000-0000-000000000010")
                ],
            )
        )
        api_handler.application_client.Get = (
            lambda req, metadata: api.GetApplicationResponse(application=mock_app)
        )
        api_handler.device_profile_client.List = (
            lambda req, metadata: api.ListDeviceProfilesResponse(
                total_count=1,
                result=[
                    api.DeviceProfileListItem(id="00000000-0000-0000-0000-000000000020")
                ],
            )
        )
        api_handler.device_profile_client.Get = (
            lambda req, metadata: api.GetDeviceProfileResponse(
                device_profile=mock_profile
            )
        )
        api_handler.user_client.List = lambda req, metadata: api.ListUsersResponse(
            total_count=1,
            result=[api.UserListItem(id="00000000-0000-0000-0000-000000000030")],
        )
        api_handler.user_client.Get = lambda req, metadata: api.GetUserResponse(
            user=mock_user
        )
        api_handler.device_profile_template_client.List = (
            lambda req, metadata: api.ListDeviceProfileTemplatesResponse(
                total_count=0, result=[]
            )
        )

        from chirpstack_provisioning.backup import backup_setup

        output_file = tmp_path / "backup.json"
        backup_setup(api_handler, output_file)

        # Verify file was created and has correct structure
        assert output_file.exists()
        with open(output_file, "r", encoding="utf-8") as f:
            backup_data = json.load(f)

        assert "tenants" in backup_data
        assert "users" in backup_data
        assert "device_profile_templates" in backup_data
        assert len(backup_data["tenants"]) == 1
        assert backup_data["tenants"][0]["name"] == "Backup Tenant"
        assert len(backup_data["tenants"][0]["gateways"]) == 1
        assert len(backup_data["tenants"][0]["applications"]) == 1
        assert len(backup_data["tenants"][0]["device_profiles"]) == 1

    def test_backup_setup_empty_server(self, api_handler, tmp_path):
        """Test backup_setup with an empty server."""
        # Mock empty responses
        api_handler.tenant_client.List = lambda req, metadata: api.ListTenantsResponse(
            total_count=0, result=[]
        )
        api_handler.user_client.List = lambda req, metadata: api.ListUsersResponse(
            total_count=0, result=[]
        )
        api_handler.device_profile_template_client.List = (
            lambda req, metadata: api.ListDeviceProfileTemplatesResponse(
                total_count=0, result=[]
            )
        )

        from chirpstack_provisioning.backup import backup_setup

        output_file = tmp_path / "empty_backup.json"
        backup_setup(api_handler, output_file)

        assert output_file.exists()
        with open(output_file, "r", encoding="utf-8") as f:
            backup_data = json.load(f)

        assert backup_data["tenants"] == []
        assert backup_data["users"] == []
        assert backup_data["device_profile_templates"] == []

    def test_backup_setup_validates_against_schema(self, api_handler, tmp_path):
        """Test that backup_setup output validates against setup.schema.json."""
        # Mock minimal valid responses
        api_handler.tenant_client.List = lambda req, metadata: api.ListTenantsResponse(
            total_count=0, result=[]
        )
        api_handler.user_client.List = lambda req, metadata: api.ListUsersResponse(
            total_count=0, result=[]
        )
        api_handler.device_profile_template_client.List = (
            lambda req, metadata: api.ListDeviceProfileTemplatesResponse(
                total_count=0, result=[]
            )
        )

        from chirpstack_provisioning.backup import backup_setup
        from chirpstack_provisioning.setup import validate_setup_data
        from pathlib import Path

        output_file = tmp_path / "schema_test_backup.json"
        backup_setup(api_handler, output_file)

        # Load and validate against schema
        with open(output_file, "r", encoding="utf-8") as f:
            backup_data = json.load(f)

        schema_path = Path(__file__).parent.parent / "setup.schema.json"
        # Should not raise any validation errors
        validate_setup_data(backup_data, schema_path)
