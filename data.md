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
- Data fields will be determined by the final `devices.schema.json` schema

### Format Descriptions

**JSON Format**:
- Single device: A JSON object representing one device
- Multiple devices: A JSON array of device objects

**JSONL Format**:
- One JSON object per line
- Each line is a complete, valid JSON object representing a device

**CSV Format**:
- Header row containing field names
- Subsequent rows containing device data
- Type coercion applied from strings to appropriate JSON types during validation

### Memory Management for Large Device Files

The devices file is designed to handle large files with over 50,000 lines and devices.

**Lazy Loading Strategy**:
- **JSONL files**: Process one line at a time for memory efficiency
- **CSV files**: Stream rows using CSV reader to avoid loading entire file
- **JSON files**: Loaded entirely into memory (assumed to be reasonably sized)

This approach ensures the tool can handle very large device datasets without excessive memory consumption, particularly for JSONL and CSV formats which are designed for streaming.

## Setup File Format

The setup file defines everything else needed to provision a ChirpStack server: tenants, device profiles, gateways, applications, users, etc.

### Key Characteristics

- **Format Support**: JSON (TOML and YAML may be supported in the future)
- **Structure**: Hierarchical/nested format
- **Identification**: Tenants, applications, and device profiles are identified by **name** instead of EUI for simplified provisioning
- Data fields will be determined by the final `setup.schema.json` schema

### Hierarchical Structure

The setup file follows this nested structure:

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

Each level in the hierarchy:
- **device_profile_templates**: Reusable templates for device profiles
- **users**: Global users (e.g., administrators)
- **tenants**: Top-level organizational units
  - **applications**: Application definitions within each tenant
    - **integrations**: Third-party integrations for each application
    - **multicast_groups**: Multicast group configurations
  - **device_profiles**: Device profile definitions specific to the tenant
  - **gateways**: Gateway configurations within the tenant
  - **users**: Users specific to the tenant

## Reference Handling

### Name-Based References

For simplified provisioning, entities are referenced by name rather than ID:

- **Tenants** - Referenced by name (key in the `tenants` object)
- **Applications** - Referenced by name (key in the tenant's `applications` object)
- **Device Profiles** - Referenced by name (key in the tenant's `device_profiles` object)

### Missing References

If a tenant, device profile, or application referenced in the data does not exist, the tool will flag this for the user to address before provisioning.

## Validation Usage

To validate data files against schemas using Poetry:

```bash
poetry run python validate.py <data-file> <schema-file>
```

Examples:
```bash
poetry run python validate.py devices.json devices.schema.json
poetry run python validate.py devices.jsonl devices.schema.json
poetry run python validate.py devices.csv devices.schema.json
poetry run python validate.py setup.json setup.schema.json
```

The validator supports:
- Type coercion from CSV strings to appropriate JSON types
- Detailed error messages with line numbers
- Summary statistics showing valid/invalid entries
