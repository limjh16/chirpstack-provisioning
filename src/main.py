import json
import os
import logging
from ChirpStackClient import ChirpStackClient
from config import load_config

def create_influxdb_integration(client, app_config, app_id):
    """Create an InfluxDB integration using configuration from JSON."""
    # Build the integration configuration dynamically based on the JSON definition
    integration_config = {
        "application_id": app_id,  # Assuming application_id is resolved before this function is called
        "version": app_config['version']
    }

    # Loop through each configuration item specific to InfluxDB
    for key, env_var_name in app_config.items():
        if key.endswith("_env_var"):  # Only process environment variable entries
            # Map the end part of the key to remove '_env_var' and get the actual config key
            config_key = key.replace("_env_var", "")
            # Access the environment variable using the name provided in JSON
            integration_config[config_key] = os.getenv(env_var_name)

    # Call the ChirpStack client to create the integration with the built configuration
    client.create_influxdb_integration(integration_config)


def main():
    try:
        # Load the configuration from a config file.
        config = load_config()
        numeric_level = getattr(logging, config['log_level'].upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f'Invalid log level: {config["log_level"]}')

        # Set up logging configuration.
        logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Initialize the ChirpStack API client with server and API token from the config.
        client = ChirpStackClient(config['server'], config['api_token'])

        # Open and read the provisioning data from a JSON file.
        with open('/app/data/provisioning.json', 'r+') as f:
            data = json.load(f)
            # Iterate through each tenant defined in the provisioning data.
            for tenant in data['_tenants']:
                logging.debug(f"Processing tenant: {json.dumps(tenant, indent=2)}")
                tenant_args = {k: v for k, v in tenant.items() if not k.startswith('_') and k != '*id'}
                tenant_id = tenant['*id'] or client.create_tenant(**tenant_args)
                if tenant_id:
                    tenant['*id'] = tenant_id
                    logging.info(f"Processed tenant ID: {tenant_id}")

                    # Process each gateway associated with the tenant.
                    for gateway in tenant.get('_gateways', []):
                        gateway_args = {k: v for k, v in gateway.items() if not k.startswith('_')}
                        gateway_id = client.create_gateway(tenant_id, **gateway_args)
                        if gateway_id:
                            logging.info(f"Gateway created successfully, ID: {gateway_id}")

                    # Process each device profile associated with the tenant.
                    for profile in tenant.get('_deviceProfiles', []):
                        profile_args = {k: v for k, v in profile.items() if not k.startswith('_') and k != '*id'}
                        if 'payload_codec_script_path' in profile:
                            profile_args['payload_codec_script'] = client.read_js_script(profile['payload_codec_script_path'])
                        profile_id = client.create_device_profile(tenant_id, **profile_args)
                        if profile_id:
                            profile['*id'] = profile_id
                            logging.info(f"Device profile created successfully, ID: {profile_id}")

                            # Process each application associated with the device profile.
                            for app in profile.get('_applications', []):
                                app_args = {k: v for k, v in app.items() if not k.startswith('_') and k != '*id'}
                                app_id = client.create_application(tenant_id, **app_args)
                                if app_id:
                                    app['*id'] = app_id
                                    logging.info(f"Application created successfully, ID: {app_id}")
                                    if '_InfluxDbIntegration' in app:
                                        create_influxdb_integration(client, app['_InfluxDbIntegration'], app_id)
                                    # Process each device associated with the application.
                                    for device in app.get('_devices', []):
                                        logging.debug(f"Processing device: {device['name']}")
                                        device_args = {k: v for k, v in device.items() if not k.startswith('_') and not k.startswith('**')}
                                        device_id = client.create_device(app_id, profile_id, **device_args)
                                        if device_id:
                                            logging.info(f"Device created successfully, ID: {device_id}")
                                        if '_deviceKeys' in device:
                                            logging.debug(f"Processing device keys for DevEUI: {device['dev_eui']}")
                                            device_keys_args = device['_deviceKeys']
                                            client.create_device_keys(device['dev_eui'], **device_keys_args)

            # Rewrite the JSON file with updated IDs and any modifications.
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    
if __name__ == '__main__':
    main()
