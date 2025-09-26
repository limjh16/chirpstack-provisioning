# Data Format Documentation

This document describes the data formats supported by ChirpStack Provisioning for importing devices and gateways.

## Overview

ChirpStack Provisioning supports three data formats:
- **JSON**: Array of objects or single object
- **JSONL**: JSON Lines format with one object per line
- **CSV**: Comma-separated values with headers

Each data entry represents either a **device** or a **gateway**. The format follows a flat structure where each object/line corresponds to exactly one entity, identified by its EUI (Extended Unique Identifier).

## Entity Types

### Devices

Devices are LoRaWAN end-devices that send data through the network.

**Required Fields:**
- `type`: Must be `"device"`
- `dev_eui`: Device EUI (16 hexadecimal characters)
- `device_name`: Human-readable device name
- `app_key`: Application key (32 hexadecimal characters)
- `tenant_name`: Name of the tenant (must exist in ChirpStack)
- `application_name`: Name of the application (must exist in ChirpStack)
- `device_profile_name`: Name of the device profile (must exist in ChirpStack)

**Optional Fields:**
- `description`: Device description
- `app_eui`: Application EUI (16 hexadecimal characters)
- `variables`: Object with additional device variables
- `tags`: Object with device tags for organization
- `is_disabled`: Boolean, whether device is disabled (default: false)
- `skip_fcnt_check`: Boolean, skip frame counter validation (default: false)

### Gateways

Gateways are the infrastructure components that receive LoRaWAN transmissions.

**Required Fields:**
- `type`: Must be `"gateway"`
- `gateway_id`: Gateway ID (16 hexadecimal characters)
- `gateway_name`: Human-readable gateway name
- `tenant_name`: Name of the tenant (must exist in ChirpStack)

**Optional Fields:**
- `description`: Gateway description
- `latitude`: Latitude coordinate (-90 to 90)
- `longitude`: Longitude coordinate (-180 to 180)
- `altitude`: Altitude in meters
- `stats_interval`: Statistics reporting interval in seconds (1-86400, default: 30)
- `tags`: Object with gateway tags for organization
- `metadata`: Object with additional gateway metadata

## Data Format Examples

### JSON Format

**Single Object:**
```json
{
  "type": "device",
  "dev_eui": "0123456789ABCDEF",
  "device_name": "Temperature Sensor 01",
  "description": "Outdoor temperature sensor",
  "app_key": "0123456789ABCDEF0123456789ABCDEF",
  "app_eui": "FEDCBA9876543210",
  "tenant_name": "smart-city",
  "application_name": "environmental-monitoring",
  "device_profile_name": "class-a-sensor",
  "tags": {
    "location": "parking-lot",
    "sensor_type": "temperature"
  },
  "is_disabled": false
}
```

**Array of Objects:**
```json
[
  {
    "type": "device",
    "dev_eui": "0123456789ABCDEF", 
    "device_name": "Temperature Sensor 01",
    "app_key": "0123456789ABCDEF0123456789ABCDEF",
    "tenant_name": "smart-city",
    "application_name": "environmental-monitoring",
    "device_profile_name": "class-a-sensor"
  },
  {
    "type": "gateway",
    "gateway_id": "0000000000001234",
    "gateway_name": "Smart City Gateway 01",
    "tenant_name": "smart-city",
    "latitude": 52.520008,
    "longitude": 13.404954,
    "altitude": 25.5
  }
]
```

### JSONL Format

Each line contains a complete JSON object:

```jsonl
{"type": "device", "dev_eui": "0123456789ABCDEF", "device_name": "Temperature Sensor 01", "app_key": "0123456789ABCDEF0123456789ABCDEF", "tenant_name": "smart-city", "application_name": "environmental-monitoring", "device_profile_name": "class-a-sensor"}
{"type": "gateway", "gateway_id": "0000000000001234", "gateway_name": "Smart City Gateway 01", "tenant_name": "smart-city", "latitude": 52.520008, "longitude": 13.404954, "altitude": 25.5}
```

### CSV Format

CSV files must include a header row with column names matching the JSON field names.

**Device CSV Example:**
```csv
type,dev_eui,device_name,description,app_key,app_eui,tenant_name,application_name,device_profile_name,is_disabled
device,0123456789ABCDEF,Temperature Sensor 01,Outdoor temperature sensor,0123456789ABCDEF0123456789ABCDEF,FEDCBA9876543210,smart-city,environmental-monitoring,class-a-sensor,false
device,FEDCBA9876543210,Motion Sensor 01,PIR motion sensor,FEDCBA9876543210FEDCBA9876543210,ABCDEF0123456789,smart-city,security-monitoring,class-a-sensor,false
```

**Gateway CSV Example:**
```csv
type,gateway_id,gateway_name,description,tenant_name,latitude,longitude,altitude,stats_interval
gateway,0000000000001234,Smart City Gateway 01,Main gateway for downtown,smart-city,52.520008,13.404954,25.5,30
gateway,0000000000005678,Industrial Gateway 01,Gateway for industrial zone,smart-city,52.503399,13.424008,15.0,60
```

**Mixed CSV Example:**
```csv
type,dev_eui,gateway_id,device_name,gateway_name,app_key,tenant_name,application_name,device_profile_name,latitude,longitude
device,0123456789ABCDEF,,Temperature Sensor 01,,0123456789ABCDEF0123456789ABCDEF,smart-city,environmental-monitoring,class-a-sensor,,
gateway,,0000000000001234,,Smart City Gateway 01,,smart-city,,,52.520008,13.404954
```

## Validation Rules

### Format Validation
- **EUI Fields**: Must be exactly 16 hexadecimal characters (0-9, A-F, case insensitive)
- **App Key**: Must be exactly 32 hexadecimal characters
- **Names**: 1-100 characters, no leading/trailing whitespace
- **Descriptions**: Maximum 500 characters
- **Coordinates**: Latitude (-90 to 90), Longitude (-180 to 180)
- **Stats Interval**: Integer between 1 and 86400 seconds

### Business Logic Validation
- **Tenant Existence**: If the specified `tenant_name` doesn't exist in ChirpStack, it will be flagged
- **Application Existence**: If the specified `application_name` doesn't exist in the tenant, it will be flagged
- **Device Profile Existence**: If the specified `device_profile_name` doesn't exist in the tenant, it will be flagged
- **Unique EUIDs**: Device EUIs and Gateway IDs must be unique within the dataset
- **Entity Type**: Each entry must specify either "device" or "gateway" as the type

### CSV-Specific Notes
- Empty cells are treated as null/undefined values
- Boolean values should be represented as "true" or "false" (case insensitive)
- Complex objects (tags, variables, metadata) should be JSON-encoded strings or omitted in CSV
- Unused columns (e.g., gateway_id in device rows) should be left empty

## Error Handling

When validation fails, the system will provide specific error messages indicating:
- Which field is invalid
- What the expected format is
- Whether referenced entities (tenant, application, device profile) exist
- Line/row numbers for easier debugging

## Assumptions

The current implementation assumes:
- **Single Tenant Environment**: While multiple tenants can be referenced, the system is optimized for single-tenant scenarios
- **Single Application**: Devices typically belong to one primary application per tenant
- **Existing Infrastructure**: Tenants, applications, and device profiles should already exist in ChirpStack before importing devices/gateways