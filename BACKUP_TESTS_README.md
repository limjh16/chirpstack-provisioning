# Backup Functionality Tests - README

## Overview

This document explains the backup functionality tests created for ChirpStack Provisioning. These tests define the expected behavior of functions that will back up a ChirpStack server configuration into a `setup.json` file format.

## Problem Statement

The goal is to create a backup procedure that can:
1. Connect to a running ChirpStack server via the gRPC API
2. Retrieve all configuration data (tenants, applications, gateways, device profiles, etc.)
3. Convert the gRPC responses into the `setup.json` format
4. Save the backup file for later use in provisioning another identical server

## What We've Created

### 1. Test Suite (`tests/test_backup.py`)

A comprehensive test suite with 22 tests organized into the following test classes:

#### Individual Entity Operations
- **TestGetTenant** - Tests for retrieving a single tenant's full details
- **TestListTenants** - Tests for listing all tenants
- **TestGetApplication** - Tests for retrieving a single application's details
- **TestListApplications** - Tests for listing applications in a tenant
- **TestGetGateway** - Tests for retrieving a single gateway's details
- **TestListGateways** - Tests for listing gateways in a tenant
- **TestGetDeviceProfile** - Tests for retrieving a device profile's details
- **TestListDeviceProfiles** - Tests for listing device profiles in a tenant

#### Complete Backup Operations
- **TestBackupTenant** - Tests for backing up a complete tenant with all nested entities
- **TestBackupServer** - Tests for backing up the entire server (all tenants)

#### Field Conversion
- **TestFieldConversion** - Tests for converting gRPC field names (snake_case) to setup.json format (camelCase)

#### Error Handling
- **TestErrorHandling** - Tests for handling gRPC errors (NOT_FOUND, PERMISSION_DENIED, UNAVAILABLE)

### 2. API Analysis Documentation (`BACKUP_API_ANALYSIS.md`)

A detailed analysis of the ChirpStack gRPC API including:
- Complete field listings for all entity types (Tenant, Application, Gateway, DeviceProfile)
- Response structure patterns for Get and List operations
- Field name mapping tables (snake_case → camelCase)
- Recommended backup workflow
- Implementation notes and best practices

### 3. Key Findings

Through our analysis of the `chirpstack-api` library, we discovered:

#### Response Patterns
```python
# Get responses include the entity plus timestamps
GetTenantResponse {
    tenant: Tenant,          # The actual entity object
    created_at: Timestamp,   # When it was created
    updated_at: Timestamp    # When it was last updated
}

# List responses include count and simplified items
ListTenantsResponse {
    total_count: int,        # Total number of items
    result: [TenantListItem] # Array of simplified items
}
```

#### Field Naming Differences
The gRPC API uses snake_case while setup.json uses camelCase:
```
gRPC API              → setup.json
-----------------------------------------
can_have_gateways     → canHaveGateways
max_gateway_count     → maxGatewayCount
tenant_id             → tenantId
gateway_id            → gatewayId
supports_otaa         → supportsOtaa
```

#### List vs Get Differences
- **List operations** return simplified objects with fewer fields (optimized for browsing)
- **Get operations** return complete objects with all configuration details
- For backup, we must use Get operations to retrieve complete data

## Test-Driven Development Approach

These tests were written following TDD methodology:

1. ✅ **Write tests first** - Define expected behavior before implementation
2. ⏳ **Run tests (they fail)** - All tests currently fail because api_handler doesn't exist
3. ⏳ **Implement functionality** - Next step is to implement the backup functions
4. ⏳ **Run tests (they pass)** - Tests will pass once implementation is complete
5. ⏳ **Refactor if needed** - Clean up code while keeping tests green

**Current Status:** Step 2 - Tests are written and properly failing, waiting for implementation.

## Expected Implementation

The tests expect the following functions to be implemented in `chirpstack_provisioning.api_handler`:

### Individual Entity Operations
```python
# Get single entity details
api_handler.get_tenant(tenant_id: str) -> dict
api_handler.get_application(app_id: str) -> dict
api_handler.get_gateway(gateway_id: str) -> dict
api_handler.get_device_profile(profile_id: str) -> dict

# List entities
api_handler.list_tenants() -> list[dict]
api_handler.list_applications(tenant_id: str) -> list[dict]
api_handler.list_gateways(tenant_id: str) -> list[dict]
api_handler.list_device_profiles(tenant_id: str) -> list[dict]
```

### Complete Backup Operations
```python
# Backup a single tenant with all nested entities
api_handler.backup_tenant(tenant_id: str) -> dict

# Backup entire server (all tenants)
api_handler.backup_server() -> dict
```

### Expected Behavior

1. **Get Functions** should:
   - Call the appropriate gRPC Get method
   - Convert the response entity to a dictionary
   - Convert field names from snake_case to camelCase
   - Return None on errors

2. **List Functions** should:
   - Call the appropriate gRPC List method
   - Iterate through result items
   - Convert each item to a dictionary with camelCase field names
   - Return empty list on errors

3. **Backup Functions** should:
   - Call List to get all entity IDs
   - Call Get for each ID to retrieve full details
   - Recursively fetch nested entities
   - Build hierarchical structure matching setup.json format
   - Return None on errors

## Example Usage (After Implementation)

```python
from chirpstack_provisioning.api_handler import ChirpStackAPIHandler

# Connect to server
handler = ChirpStackAPIHandler("localhost:8080", "api-token")

# Backup entire server
setup_data = handler.backup_server()

# Save to file
import json
with open("backup.json", "w") as f:
    json.dump(setup_data, f, indent=2)

# Validate against schema
from chirpstack_provisioning.setup import validate_setup_data
validate_setup_data(setup_data, "setup.schema.json")
```

## Running the Tests

```bash
# Run all backup tests
poetry run pytest tests/test_backup.py -v

# Run specific test class
poetry run pytest tests/test_backup.py::TestGetTenant -v

# Run with detailed output
poetry run pytest tests/test_backup.py -vv
```

## Next Steps

1. **Implement ChirpStackAPIHandler** - Create the api_handler module with connection handling
2. **Implement Get/List functions** - Add functions to retrieve individual entities
3. **Implement field conversion** - Add snake_case to camelCase conversion utility
4. **Implement backup functions** - Add functions to backup tenants and entire server
5. **Run tests iteratively** - Test each function as it's implemented
6. **Handle edge cases** - Add pagination support, rate limiting, etc.
7. **Add integration tests** - Test against real ChirpStack server (optional, for later)

## Related Files

- `tests/test_backup.py` - The test suite
- `BACKUP_API_ANALYSIS.md` - Detailed API analysis and field mappings
- `tests/test_api_handler.py` - Related tests for API handler (Create operations)
- `src/chirpstack_provisioning/setup.py` - Setup file parsing (reads setup.json)
- `setup.schema.json` - JSON schema for setup files

## Notes

- Tests use mocking to avoid requiring a real ChirpStack server
- All field names must be converted from snake_case (API) to camelCase (setup.json)
- Timestamps (created_at, updated_at) are informational and not included in backup
- Error handling is important - network issues, authentication failures, missing entities
- The backup format must be compatible with setup.schema.json for validation
