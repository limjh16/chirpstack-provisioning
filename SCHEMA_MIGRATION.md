# Schema Migration Guide

## Overview

The ChirpStack Provisioning tool has migrated from a single flat schema to a two-file approach with separate schemas for infrastructure setup and device provisioning.

## What Changed

### Old Approach (Deprecated)
- **Single schema file**: `schema.json`
- **Single data file**: Mixed devices and gateways in one file with a `type` field
- **Flat structure**: All entities at the same level
- **Formats**: JSON, JSONL, CSV

### New Approach (Current)
- **Two schema files**:
  - `setup.schema.json`: For infrastructure (tenants, applications, device profiles, gateways, integrations)
  - `devices.schema.json`: For device provisioning
- **Two data files**:
  - Setup file (JSON only): Hierarchical structure with nested entities
  - Device file (JSON, JSONL, CSV): Flat structure for individual devices
- **Processing order**: Setup file first, then device file

## Migration Steps

### 1. Split Your Data Files

**Old format** (`data.json`):
```json
[
  {"type": "device", "dev_eui": "...", "device_name": "...", ...},
  {"type": "gateway", "gateway_id": "...", "gateway_name": "...", ...}
]
```

**New format**:

Setup file (`setup.json`):
```json
{
  "tenants": [
    {
      "name": "my-tenant",
      "*id": "AUTO-GENERATED",
      "gateways": [
        {"gateway_id": "...", "name": "...", "*tenant_id": "AUTO-PARENT"}
      ],
      "applications": [...],
      "_deviceProfiles": [...]
    }
  ]
}
```

Device file (`devices.json`):
```json
[
  {
    "name": "Device 1",
    "dev_eui": "...",
    "**application_id": "AUTO-FILL",
    "**device_profile_id": "AUTO-FILL",
    "application_name": "my-app",
    "device_profile_name": "my-profile",
    "_deviceKeys": {
      "**dev_eui": "AUTO-PARENT",
      "nwk_key": "..."
    }
  }
]
```

### 2. Update Field Names

| Old Field | New Field | Notes |
|-----------|-----------|-------|
| `device_name` | `name` | Devices now use `name` instead of `device_name` |
| `gateway_name` | `name` | Gateways now use `name` instead of `gateway_name` |
| `app_key` | `_deviceKeys.nwk_key` | Keys moved to nested `_deviceKeys` object |
| `tenant_name` | N/A | Devices reference `application_name` instead |
| `skip_fcnt_check` | `skipFCntCheck` | Changed to camelCase |

### 3. Add AUTO-FILL Markers

The new schema uses special markers for automatic field handling:
- `*field`: `"AUTO-GENERATED"` for UUIDs that will be generated
- `**field`: `"AUTO-FILL"` for IDs looked up from names, or `"AUTO-PARENT"` for parent references
- `_entity`: Underscore prefix for nested/related entities

### 4. Update Validation Commands

**Old validation**:
```bash
python validate.py data.json
```

**New validation**:
```bash
# Validate setup file
python validate.py setup.json --schema=setup

# Validate device file  
python validate.py devices.json --schema=devices

# Auto-detection also works
python validate.py sample_setup.json  # Auto-detects 'setup' from filename
python validate.py sample_devices.csv # Auto-detects 'devices' from filename
```

## Backward Compatibility

The old `schema.json` file is retained for backward compatibility, but is considered **deprecated**. 

To use the old validation (not recommended):
```bash
python validate.py old_data.json  # Falls back to old schema if auto-detection fails
```

## Benefits of New Approach

1. **Clearer separation**: Infrastructure setup vs device provisioning
2. **Better organization**: Hierarchical structure shows relationships
3. **Easier maintenance**: Separate schemas are simpler to understand and modify
4. **Proper workflow**: Setup first, devices second ensures dependencies exist
5. **Auto-fill capabilities**: Less manual ID management with name-based lookups

## See Also

- [data.md](data.md) - Complete data format documentation
- [examples/](examples/) - Example files in new format
