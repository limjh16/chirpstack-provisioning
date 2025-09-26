# JSON Schema Documentation

This document describes the JSON schemas used by ChirpStack Provisioning for validating input data.

## Overview

The ChirpStack Provisioning tool uses JSON Schema to validate input data for provisioning ChirpStack entities. This approach ensures data integrity and provides clear error messages when data doesn't match the expected format.

## Supported Entity Types

### 1. Device Schema

Devices are LoRaWAN end-devices that send data through the network.

**Required Fields:**
- `dev_eui`: Device EUI in hexadecimal format (16 characters)
- `device_name`: Human-readable name for the device
- `app_key`: Application key in hexadecimal format (32 characters)
- One of: `tenant_id` (UUID) or `tenant_name` (string)
- One of: `application_id` (UUID) or `application_name` (string)  
- One of: `device_profile_id` (UUID) or `device_profile_name` (string)

**Optional Fields:**
- `description`: Optional description of the device
- `app_eui`: Application EUI in hexadecimal format (16 characters)
- `variables`: Object with additional device variables
- `tags`: Object with device tags for organization
- `is_disabled`: Boolean indicating if device is disabled (default: false)
- `skip_fcnt_check`: Boolean to skip frame counter validation (default: false)

**Example:**
```json
{
  "dev_eui": "0123456789ABCDEF",
  "device_name": "Temperature Sensor 01",
  "description": "Outdoor temperature sensor",
  "app_key": "0123456789ABCDEF0123456789ABCDEF",
  "app_eui": "FEDCBA9876543210",
  "tenant_name": "smart-city",
  "application_name": "environmental-monitoring",
  "device_profile_name": "class-a-sensor",
  "tags": {
    "environment": "production",
    "deployment": "phase-1"
  }
}
```

### 2. Gateway Schema

Gateways are the bridge between LoRaWAN devices and the network server.

**Required Fields:**
- `gateway_id`: Gateway ID in hexadecimal format (16 characters)
- `gateway_name`: Human-readable name for the gateway
- One of: `tenant_id` (UUID) or `tenant_name` (string)

**Optional Fields:**
- `description`: Optional description of the gateway
- `latitude`: Latitude coordinate (-90 to 90)
- `longitude`: Longitude coordinate (-180 to 180)
- `altitude`: Altitude in meters
- `stats_interval`: Statistics reporting interval in seconds (1-86400, default: 30)
- `tags`: Object with gateway tags for organization
- `metadata`: Object with additional gateway metadata

**Example:**
```json
{
  "gateway_id": "0000000000001234",
  "gateway_name": "Smart City Gateway 01",
  "description": "Main gateway for downtown area",
  "tenant_name": "smart-city",
  "latitude": 52.520008,
  "longitude": 13.404954,
  "altitude": 25.5,
  "stats_interval": 30,
  "tags": {
    "location": "downtown",
    "coverage": "primary"
  }
}
```

### 3. Tenant Schema

Tenants represent organizations or groups that can manage devices and gateways.

**Required Fields:**
- `name`: Tenant name (must be unique)

**Optional Fields:**
- `description`: Optional description of the tenant
- `can_have_gateways`: Boolean indicating if tenant can have gateways (default: true)
- `max_device_count`: Maximum number of devices allowed (0 = unlimited, default: 0)
- `max_gateway_count`: Maximum number of gateways allowed (0 = unlimited, default: 0)
- `tags`: Object with tenant tags for organization

### 4. Application Schema

Applications group related devices together within a tenant.

**Required Fields:**
- `name`: Application name
- One of: `tenant_id` (UUID) or `tenant_name` (string)

**Optional Fields:**
- `description`: Optional description of the application
- `tags`: Object with application tags for organization

### 5. Device Profile Schema

Device profiles define the capabilities and configuration of device types.

**Required Fields:**
- `name`: Device profile name
- `region`: LoRaWAN region (EU868, US915, CN779, EU433, AU915, CN470, AS923, AS923-2, AS923-3, AS923-4, KR920, IN865, RU864)
- One of: `tenant_id` (UUID) or `tenant_name` (string)

**Optional Fields:**
- `description`: Optional description of the device profile
- `mac_version`: LoRaWAN MAC version (default: "1.0.3")
- `reg_params_revision`: Regional parameters revision (default: "RP002-1.0.3")
- `adr_algorithm_id`: ADR algorithm identifier (default: "default")
- `payload_codec_runtime`: Payload codec runtime (NONE, CAYENNE_LPP, JS, default: NONE)
- `payload_codec_script`: JavaScript payload codec script
- `uplink_interval`: Expected uplink interval in seconds (default: 0)
- `device_status_req_interval`: Device status request interval (default: 0)
- `flush_queue_on_activate`: Flush queue on device activation (default: false)
- `supports_otaa`: Device supports OTAA activation (default: true)
- `supports_class_b`: Device supports Class B (default: false)
- `supports_class_c`: Device supports Class C (default: false)
- `class_b_timeout`: Class B timeout in seconds (default: 0)
- `class_c_timeout`: Class C timeout in seconds (default: 0)
- `tags`: Object with device profile tags for organization

## Data Formats

### JSON Format

Data can be provided as JSON arrays or individual JSON objects:

```json
[
  {
    "dev_eui": "0123456789ABCDEF",
    "device_name": "Device 1",
    ...
  },
  {
    "dev_eui": "FEDCBA9876543210", 
    "device_name": "Device 2",
    ...
  }
]
```

### JSONL Format

Data can be provided as JSON Lines (one JSON object per line):

```jsonl
{"dev_eui": "0123456789ABCDEF", "device_name": "Device 1", ...}
{"dev_eui": "FEDCBA9876543210", "device_name": "Device 2", ...}
```

### CSV Format

Data can be provided as CSV with column headers matching the JSON field names:

```csv
dev_eui,device_name,app_key,tenant_name,application_name,device_profile_name
0123456789ABCDEF,Device 1,0123456789ABCDEF0123456789ABCDEF,tenant1,app1,profile1
FEDCBA9876543210,Device 2,FEDCBA9876543210FEDCBA9876543210,tenant1,app1,profile1
```

## Usage

### Python API

```python
from chirpstack_provisioning.validation import validate_device, validate_gateway

# Validate a single device
device_data = {...}
result = validate_device(device_data)
if result.is_valid:
    print("Device is valid")
else:
    print("Validation errors:", result.errors)

# Validate multiple devices
devices = [...]
results = validate_batch(devices, "device")
```

### Entity Type Detection

The library can automatically detect entity types based on the data structure:

```python
from chirpstack_provisioning.validation import detect_entity_type

data = {"dev_eui": "0123456789ABCDEF", "device_name": "Test"}
entity_type = detect_entity_type(data)  # Returns "device"
```

## Validation Rules

1. **EUI Format**: All EUI fields must be exactly 16 hexadecimal characters
2. **App Key Format**: App keys must be exactly 32 hexadecimal characters  
3. **UUID Format**: All ID fields must be valid UUIDs
4. **Coordinate Ranges**: Latitude must be -90 to 90, longitude must be -180 to 180
5. **Required Associations**: Entities must reference existing tenants, applications, or device profiles
6. **String Lengths**: Names and descriptions have maximum length limits
7. **Enum Values**: Fields like region and mac_version must match predefined values

## Error Handling

Validation errors provide specific information about what went wrong:

- Missing required fields
- Invalid field formats (EUI, UUID, etc.)
- Values outside allowed ranges
- Invalid enum values
- String length violations

This detailed error reporting helps users quickly identify and fix data issues.