# Data Format Documentation

This document describes the data formats, validation, and management approach used in ChirpStack Provisioning.

## Overview

ChirpStack Provisioning accepts two types of data files:

1. **Devices File** - Contains flat device data (devices that connect to the LoRa Network Server)
2. **Setup File** - Contains hierarchical setup data (tenants, applications, gateways, device profiles, etc.)

## Data Validation

All data is validated against JSON Schema files:

- `devices.schema.json` - Validates device data
- `setup.schema.json` - Validates setup data

The JSON schemas are the **single source of truth** for data validation.

### Schema Generation

Schemas are generated from ChirpStack's Protocol Buffer (protobuf) definitions:

- We use [`google.protobuf.json_format`](https://googleapis.dev/python/protobuf/latest/google/protobuf/json_format.html) to parse JSON data into protobuf messages
- Data files must follow the fields defined in the `proto` files
- JSON schemas are generated from proto files using [`bufbuild/protoschema-plugins`](https://github.com/bufbuild/protoschema-plugins) with `--jsonschema_opt=target=json-strict`
- Individual objects conform strictly to the required proto messages, but we nest messages together in a tree format for easier provisioning

For details on schema generation, see [`proto/doc.md`](proto/doc.md).

## Devices File Format

The devices file defines all devices that should be connected to the LoRa Network Server.

### Key Characteristics

- **Format Support**: JSON, JSONL, and CSV
- **Structure**: Flat format where each JSON object or CSV line corresponds to one device
- **Primary Identifier**: `dev_eui` (Device EUI)

### JSON Format

Single device:
```json
{
  "dev_eui": "0102030405060708",
  "name": "sensor-001",
  "description": "Temperature sensor",
  "application_id": "app-warehouse-01",
  "device_profile_id": "profile-temp-sensor"
}
```

Multiple devices (array):
```json
[
  {
    "dev_eui": "0102030405060708",
    "name": "sensor-001",
    "description": "Temperature sensor",
    "application_id": "app-warehouse-01",
    "device_profile_id": "profile-temp-sensor"
  },
  {
    "dev_eui": "0102030405060709",
    "name": "sensor-002",
    "description": "Humidity sensor",
    "application_id": "app-warehouse-01",
    "device_profile_id": "profile-humidity-sensor"
  }
]
```

### JSONL Format

One JSON object per line:
```jsonl
{"dev_eui": "0102030405060708", "name": "sensor-001", "description": "Temperature sensor", "application_id": "app-warehouse-01", "device_profile_id": "profile-temp-sensor"}
{"dev_eui": "0102030405060709", "name": "sensor-002", "description": "Humidity sensor", "application_id": "app-warehouse-01", "device_profile_id": "profile-humidity-sensor"}
```

### CSV Format

Header row followed by data rows:
```csv
dev_eui,name,description,application_id,device_profile_id
0102030405060708,sensor-001,Temperature sensor,app-warehouse-01,profile-temp-sensor
0102030405060709,sensor-002,Humidity sensor,app-warehouse-01,profile-humidity-sensor
```

## Setup File Format

The setup file defines everything else needed to provision a ChirpStack server: tenants, device profiles, gateways, applications, users, etc.

### Key Characteristics

- **Format Support**: JSON (TOML and YAML may be supported in the future)
- **Structure**: Hierarchical/nested format
- **Identification**: Tenants, applications, and device profiles are identified by **name** instead of EUI for simplified provisioning

### Hierarchical Structure

```text
.
├── device_profile_templates
├── users
└── tenants
    ├── applications
    │   ├── integrations
    │   └── multicast_groups
    ├── device_profiles
    └── gateways
```

### JSON Format

```json
{
  "device_profile_templates": {
    "template-1": {
      "name": "LoRaWAN 1.0.3 Class A",
      "region": "US915",
      "mac_version": "1.0.3",
      "reg_params_revision": "A",
      "supports_otaa": true
    }
  },
  "users": {
    "admin-user": {
      "email": "admin@example.com",
      "is_admin": true
    }
  },
  "tenants": {
    "tenant1": {
      "name": "Main Tenant",
      "description": "Primary tenant for production",
      "applications": {
        "app1": {
          "name": "Warehouse Monitoring",
          "description": "Temperature and humidity sensors",
          "integrations": {
            "http-integration": {
              "endpoint": "https://example.com/webhook"
            }
          },
          "multicast_groups": {}
        }
      },
      "device_profiles": {
        "profile-temp-sensor": {
          "name": "Temperature Sensor Profile",
          "template": "template-1"
        }
      },
      "gateways": {
        "gateway-001": {
          "gateway_id": "0001020304050607",
          "name": "Gateway 001",
          "description": "Main warehouse gateway"
        }
      },
      "users": {
        "tenant-user": {
          "email": "user@example.com"
        }
      }
    }
  }
}
```

## Reference Handling

### Name-Based References

For simplified provisioning, entities are referenced by name rather than ID:

- **Tenants** - Referenced by name (key in the `tenants` object)
- **Applications** - Referenced by name (key in the tenant's `applications` object)
- **Device Profiles** - Referenced by name (key in the tenant's `device_profiles` object)

### Missing References

If a tenant, device profile, or application referenced in the data does not exist, the tool will flag this for the user to address before provisioning.

## Memory Management for Large Files

The project is designed to handle large files with over 50,000 lines and devices.

### Lazy Loading

Data is **lazily loaded** rather than loaded all at once to manage memory efficiently:

- For JSONL files: Process one line at a time
- For CSV files: Stream rows using CSV reader
- For JSON files: Use streaming parsers when possible

This ensures the tool can handle very large datasets without excessive memory consumption.

## Validation Usage

To validate data files against schemas:

```bash
python validate.py <data-file> <schema-file>
```

Examples:
```bash
python validate.py devices.json devices.schema.json
python validate.py devices.jsonl devices.schema.json
python validate.py devices.csv devices.schema.json
python validate.py setup.json setup.schema.json
```

The validator supports:
- Type coercion from CSV strings to appropriate JSON types
- Detailed error messages with line numbers
- Summary statistics showing valid/invalid entries
