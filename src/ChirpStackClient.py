import os
import grpc
from chirpstack_api import api, common
import logging

class ChirpStackClient:
    """Client to interact with ChirpStack API for device and gateway management."""
    
    def __init__(self, server, api_token):
        """Initialize the client with the server address and API token."""
        self.server = server
        self.api_token = api_token
        self.channel = grpc.insecure_channel(server)
        self.initialize_clients()
        
    def initialize_clients(self):
        """Initialize all gRPC service clients."""
        self.tenant_client = api.TenantServiceStub(self.channel)
        self.gateway_client = api.GatewayServiceStub(self.channel)
        self.device_profile_client = api.DeviceProfileServiceStub(self.channel)
        self.application_client = api.ApplicationServiceStub(self.channel)
        self.device_client = api.DeviceServiceStub(self.channel)

    def create_gateway(self, tenant_id, **kwargs):
        """Create a gateway with the specified tenant ID and additional properties."""
        req = api.CreateGatewayRequest()
        req.gateway.tenant_id = tenant_id
        self._set_attributes(req.gateway, kwargs)
        return self._send_request(self.gateway_client.Create, req, self.auth_token())

    def create_tenant(self, **kwargs):
        """Create a tenant with the specified properties."""
        req = api.CreateTenantRequest()
        self._set_attributes(req.tenant, kwargs)
        return self._send_request(self.tenant_client.Create, req, self.auth_token())

    def create_device_profile(self, tenant_id, **kwargs):
        """Create a device profile for a specific tenant."""
        req = api.CreateDeviceProfileRequest()
        req.device_profile.tenant_id = tenant_id
        self._set_attributes(req.device_profile, kwargs)
        return self._send_request(self.device_profile_client.Create, req, self.auth_token())

    def create_application(self, tenant_id, **kwargs):
        """Create an application under a specific tenant."""
        req = api.CreateApplicationRequest()
        req.application.tenant_id = tenant_id
        self._set_attributes(req.application, kwargs)
        return self._send_request(self.application_client.Create, req, self.auth_token())

    def create_device(self, application_id, device_profile_id, **kwargs):
        """Create a device under a specific application and device profile."""
        req = api.CreateDeviceRequest()
        req.device.application_id = application_id
        req.device.device_profile_id = device_profile_id
        self._set_attributes(req.device, kwargs)
        return self._send_request(self.device_client.Create, req, self.auth_token())

    def create_device_keys(self, dev_eui, **kwargs):
        """Set keys for a device specified by DevEUI."""
        req = api.CreateDeviceKeysRequest()
        req.device_keys.dev_eui = dev_eui
        self._set_attributes(req.device_keys, kwargs)
        return self._send_request(self.device_client.CreateKeys, req, self.auth_token())
    
    def create_influxdb_integration(self, config):
        """Create an InfluxDB integration for an application."""
        req = api.CreateInfluxDbIntegrationRequest()
        req.integration.CopyFrom(api.InfluxDbIntegration(**config))
        # Correctly call the auth_token method to pass the authentication tokens
        return self._send_request(self.application_client.CreateInfluxDbIntegration, req, self.auth_token())

    def _set_attributes(self, obj, attrs):
        """Helper method to set attributes on request objects."""
        for key, value in attrs.items():
            if isinstance(value, dict) and hasattr(obj, key):
                for sub_key, sub_value in value.items():
                    getattr(obj, key)[sub_key] = sub_value
            elif hasattr(obj, key):
                setattr(obj, key, value)

    def _send_request(self, method, req, metadata):
        """Send a gRPC request with detailed logging."""
        try:
            # # Log the request details before sending
            # logging.debug(f"Preparing to send request: {method.__name__} with payload: {req}")
            response = method(req, metadata=metadata)
            if hasattr(response, 'id'):
                logging.info(f"{req.DESCRIPTOR.name} created successfully, ID: {response.id}")
                return response.id
            else:
                logging.info(f"{req.DESCRIPTOR.name} created successfully, no ID in the response.")
                return None
        except grpc.RpcError as e:
            logging.error(f"gRPC error {e.code()}: {e.details()}")
            return None

    def auth_token(self):
        """Generate authorization token metadata."""
        return [("authorization", f"Bearer {self.api_token}")]

    def read_js_script(self, script_path):
        """Reads the content of a JavaScript file from the specified path."""
        try:
            with open(script_path, 'r') as file:
                script_content = file.read()
                if not script_content:
                    logging.error(f"JavaScript file is empty: {script_path}")
                return script_content
        except FileNotFoundError:
            logging.error(f"JavaScript file not found: {script_path}")
            return ""
        except Exception as e:
            logging.error(f"Error reading JavaScript file: {str(e)}")
            return ""
