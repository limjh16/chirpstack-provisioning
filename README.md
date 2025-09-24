# CSInit Service

## Overview

The CSInit service automates provisioning and configuration processes within a ChirpStack environment. This service uses structured JSON data to streamline the setup of tenants, device profiles, gateways, and applications. It interacts directly with the ChirpStack API through a Python-based client and operates within a Dockerized environment to ensure consistent and scalable deployments.

## Features

- **JSON-based Provisioning**: Uses a structured JSON file (`provisioning.json`) to automate the creation of ChirpStack resources.
- **Containerized Execution**: Runs within Docker containers to ensure consistency across different deployment environments.

## Prerequisites

- Docker and Docker Compose installed on the host machine.
- Network access to a ChirpStack instance.
- Appropriate API access tokens are configured to allow communication with the ChirpStack API.

## JSON Configuration Explanation

- **Field Prefixes**:
  - `"_"`: Defines entities at each level, marking keys associated with specific gRPC methods.
  - `"**"`: Indicates fields that the script will automatically replace with the appropriate ID based on their nesting context (e.g., `"**tenant_id"` becomes the ID of the parent tenant).
  - `"*"`: Indicates auto-generated values by ChirpStack, like `"*id"`, which should not be manually provided or edited in the initial JSON.

## Setup and Operation

1. **Prepare Git Submmodules**: If this repository was not cloned with `--recurse-submodules`, run `git submodule init` and `git submodule update` to pull the relevant device codecs
2. **Prepare Environment Variables**: Set all necessary environment variables in `.env` or pass them directly through the Docker Compose configuration. This includes ChirpStack API keys and server URLs.
3. **Configure `provisioning.json`**: Populate this file under the `data/` directory with the required configurations for tenants, device profiles, gateways, and applications as per ChirpStack API requirements.
4. **Build and Run the Container**:
   - Build the service: `docker compose build csinit`
   - Start the service: `docker compose up csinit`
5. **Monitor Logs**: Regularly check the `csinit` container's logs for any errors or confirmation messages about the setups being processed.

## Debugging and Troubleshooting

- **Detailed Request Logging**: The service includes detailed logging of all gRPC requests before they are sent. This is crucial for diagnosing issues with the request payloads.
- **Error Handling**: All functions are equipped with try-catch blocks to handle and log errors effectively, providing clear insights into any issues that occur during execution.
- **Environment Variable Verification**: The service checks and logs the status of all required environment variables to ensure they are correctly set before proceeding with operations.

## Directory Structure
```plaintext
/csinit/
|-- src/
|   |-- ChirpStackClient.py     # Client class to interact with ChirpStack API
|   |-- config.py               # Loader for environment-specific configurations
|   |-- main.py                 # Main script initializing provisioning from JSON
|-- data/
|   |-- provisioning.json       # JSON file detailing tenants, device profiles, gateways, and applications
|   |-- device-codecs           # Git Submodule for centralised management of device codecs
|   |   |-- codec_DMI-VA_v4.js          # JavaScript codec for DMI-VA device payload decoding
|   |   |-- Dockerfile.test             # Defines the Docker environment for running tests
|   |   |-- tests/
|   |   |   |-- codec_DMI-VA_v4.test.js # JavaScript test file for the DMI-VA codec
|   |   |   |-- package.json            # Node.js dependencies for testing
|-- Dockerfile                  # Defines the Docker environment for the service
|-- requirements.txt            # Lists dependencies required by the Python scripts
```

## Testing the DMI-VA Codec

Testing files for codecs have been moved to the [`device-codecs`](https://bitbucket.org/idtecnologiaintegral/device-codecs/) submodule
