# ChirpStack API - Backup/Get Request Analysis

This document analyzes the ChirpStack gRPC API to understand what data is returned by `Get` requests, which is essential for implementing backup functionality.

## Overview

The ChirpStack API provides `Get` requests to retrieve individual entities and `List` requests to retrieve collections. Understanding the structure of these responses is critical for:
1. Backing up ChirpStack server configurations
2. Converting gRPC responses to setup.json format
3. Ensuring field name compatibility between API and setup.json

## Response Structures

### 1. Tenant

**GetTenantResponse structure:**
- `tenant` - The Tenant object (see below)
- `created_at` - Timestamp when tenant was created
- `updated_at` - Timestamp when tenant was last updated

**Tenant object fields:**
- `id` - Tenant UUID
- `name` - Tenant name
- `description` - Tenant description
- `can_have_gateways` - Boolean indicating if tenant can have gateways
- `max_gateway_count` - Maximum number of gateways allowed
- `max_device_count` - Maximum number of devices allowed
- `private_gateways_up` - Boolean for private gateway uplink
- `private_gateways_down` - Boolean for private gateway downlink
- `tags` - Dictionary of key-value tags

**Field Name Mapping (gRPC → setup.json):**
```
can_have_gateways      → canHaveGateways
max_gateway_count      → maxGatewayCount
max_device_count       → maxDeviceCount
private_gateways_up    → privateGatewaysUp
private_gateways_down  → privateGatewaysDown
```

### 2. Application

**GetApplicationResponse structure:**
- `application` - The Application object (see below)
- `created_at` - Timestamp when application was created
- `updated_at` - Timestamp when application was last updated
- `measurement_keys` - Available measurement keys for the application

**Application object fields:**
- `id` - Application UUID
- `name` - Application name
- `description` - Application description
- `tenant_id` - Parent tenant UUID
- `tags` - Dictionary of key-value tags

**Field Name Mapping (gRPC → setup.json):**
```
tenant_id → tenantId
```

### 3. Gateway

**GetGatewayResponse structure:**
- `gateway` - The Gateway object (see below)
- `created_at` - Timestamp when gateway was created
- `updated_at` - Timestamp when gateway was last updated
- `last_seen_at` - Timestamp when gateway was last seen

**Gateway object fields:**
- `gateway_id` - Gateway EUI (8 bytes hex)
- `name` - Gateway name
- `description` - Gateway description
- `location` - GPS location object
- `tenant_id` - Parent tenant UUID
- `tags` - Dictionary of key-value tags
- `metadata` - Additional metadata dictionary
- `stats_interval` - Statistics reporting interval in seconds

**Field Name Mapping (gRPC → setup.json):**
```
gateway_id     → gatewayId
tenant_id      → tenantId
stats_interval → statsInterval
```

### 4. Device Profile

**GetDeviceProfileResponse structure:**
- `device_profile` - The DeviceProfile object (see below)
- `created_at` - Timestamp when profile was created
- `updated_at` - Timestamp when profile was last updated

**DeviceProfile object fields (extensive - 54 fields):**

**Basic fields:**
- `id` - Device profile UUID
- `tenant_id` - Parent tenant UUID
- `name` - Profile name
- `description` - Profile description
- `region` - LoRaWAN region (e.g., "US915", "EU868")

**LoRaWAN configuration:**
- `mac_version` - MAC version (e.g., "LORAWAN_1_0_3")
- `reg_params_revision` - Regional parameters revision (e.g., "RP002_1_0_1")
- `adr_algorithm_id` - ADR algorithm identifier
- `payload_codec_runtime` - Codec runtime (e.g., "NONE", "JS")
- `payload_codec_script` - Codec script content

**Device capabilities:**
- `supports_otaa` - Supports OTAA activation
- `supports_class_b` - Supports Class B operation
- `supports_class_c` - Supports Class C operation

**Class B settings:**
- `class_b_timeout` - Class B timeout in seconds
- `class_b_ping_slot_periodicity` - Ping slot periodicity
- `class_b_ping_slot_dr` - Ping slot data rate
- `class_b_ping_slot_freq` - Ping slot frequency

**Class C settings:**
- `class_c_timeout` - Class C timeout in seconds

**ABP settings:**
- `abp_rx1_delay` - RX1 delay for ABP
- `abp_rx1_dr_offset` - RX1 data rate offset
- `abp_rx2_dr` - RX2 data rate
- `abp_rx2_freq` - RX2 frequency

**Relay settings (LoRaWAN 1.1+):**
- `is_relay` - Device is a relay
- `is_relay_ed` - Device is relay end-device
- `relay_ed_relay_only` - Relay ED only mode
- `relay_enabled` - Relay functionality enabled
- `relay_cad_periodicity` - CAD periodicity
- `relay_default_channel_index` - Default channel index
- `relay_second_channel_freq` - Second channel frequency
- `relay_second_channel_dr` - Second channel data rate
- `relay_second_channel_ack_offset` - Second channel ACK offset
- `relay_ed_activation_mode` - Relay ED activation mode
- `relay_ed_smart_enable_level` - Smart enable level
- `relay_ed_back_off` - Back off setting
- `relay_ed_uplink_limit_bucket_size` - Uplink limit bucket size
- `relay_ed_uplink_limit_reload_rate` - Uplink limit reload rate
- `relay_join_req_limit_reload_rate` - Join request limit reload rate
- `relay_notify_limit_reload_rate` - Notify limit reload rate
- `relay_global_uplink_limit_reload_rate` - Global uplink limit reload rate
- `relay_overall_limit_reload_rate` - Overall limit reload rate
- `relay_join_req_limit_bucket_size` - Join request limit bucket size
- `relay_notify_limit_bucket_size` - Notify limit bucket size
- `relay_global_uplink_limit_bucket_size` - Global uplink limit bucket size
- `relay_overall_limit_bucket_size` - Overall limit bucket size

**Other settings:**
- `tags` - Dictionary of key-value tags
- `measurements` - Device measurements configuration
- `auto_detect_measurements` - Auto-detect measurements
- `region_config_id` - Region configuration ID
- `allow_roaming` - Allow roaming
- `rx1_delay` - RX1 delay
- `flush_queue_on_activate` - Flush queue on activation
- `uplink_interval` - Expected uplink interval in seconds
- `device_status_req_interval` - Device status request interval
- `app_layer_params` - Application layer parameters

**Field Name Mapping (gRPC → setup.json):**
All snake_case fields convert to camelCase. Examples:
```
tenant_id                           → tenantId
mac_version                         → macVersion
reg_params_revision                 → regParamsRevision
adr_algorithm_id                    → adrAlgorithmId
payload_codec_runtime               → payloadCodecRuntime
payload_codec_script                → payloadCodecScript
flush_queue_on_activate             → flushQueueOnActivate
uplink_interval                     → uplinkInterval
device_status_req_interval          → deviceStatusReqInterval
supports_otaa                       → supportsOtaa
supports_class_b                    → supportsClassB
supports_class_c                    → supportsClassC
class_b_timeout                     → classBTimeout
class_b_ping_slot_periodicity       → classBPingSlotPeriodicity
class_b_ping_slot_dr                → classBPingSlotDr
class_b_ping_slot_freq              → classBPingSlotFreq
class_c_timeout                     → classCTimeout
abp_rx1_delay                       → abpRx1Delay
abp_rx1_dr_offset                   → abpRx1DrOffset
abp_rx2_dr                          → abpRx2Dr
abp_rx2_freq                        → abpRx2Freq
auto_detect_measurements            → autoDetectMeasurements
region_config_id                    → regionConfigId
is_relay                            → isRelay
is_relay_ed                         → isRelayEd
relay_ed_relay_only                 → relayEdRelayOnly
relay_enabled                       → relayEnabled
relay_cad_periodicity               → relayCadPeriodicity
relay_default_channel_index         → relayDefaultChannelIndex
relay_second_channel_freq           → relaySecondChannelFreq
relay_second_channel_dr             → relaySecondChannelDr
relay_second_channel_ack_offset     → relaySecondChannelAckOffset
relay_ed_activation_mode            → relayEdActivationMode
relay_ed_smart_enable_level         → relayEdSmartEnableLevel
relay_ed_back_off                   → relayEdBackOff
relay_ed_uplink_limit_bucket_size   → relayEdUplinkLimitBucketSize
relay_ed_uplink_limit_reload_rate   → relayEdUplinkLimitReloadRate
relay_join_req_limit_reload_rate    → relayJoinReqLimitReloadRate
relay_notify_limit_reload_rate      → relayNotifyLimitReloadRate
relay_global_uplink_limit_reload_rate → relayGlobalUplinkLimitReloadRate
relay_overall_limit_reload_rate     → relayOverallLimitReloadRate
relay_join_req_limit_bucket_size    → relayJoinReqLimitBucketSize
relay_notify_limit_bucket_size      → relayNotifyLimitBucketSize
relay_global_uplink_limit_bucket_size → relayGlobalUplinkLimitBucketSize
relay_overall_limit_bucket_size     → relayOverallLimitBucketSize
allow_roaming                       → allowRoaming
rx1_delay                           → rx1Delay
```

## List Response Structures

All List responses follow the same pattern:

```python
{
    "total_count": int,  # Total number of items available
    "result": [...]      # Array of list items
}
```

### List Item Structures

List items contain a **subset** of fields compared to full Get responses. They are optimized for listing/browsing.

**TenantListItem fields:**
- `id`, `name`, `created_at`, `updated_at`
- `can_have_gateways`, `private_gateways_up`, `private_gateways_down`
- `max_gateway_count`, `max_device_count`

**ApplicationListItem fields:**
- `id`, `name`, `description`
- `created_at`, `updated_at`

**GatewayListItem fields:**
- `tenant_id`, `gateway_id`, `name`, `description`
- `location`, `properties`, `state`
- `created_at`, `updated_at`, `last_seen_at`

**DeviceProfileListItem fields:**
- `id`, `name`, `region`
- `mac_version`, `reg_params_revision`
- `supports_otaa`, `supports_class_b`, `supports_class_c`
- `created_at`, `updated_at`

## Backup Strategy

Based on this analysis, the backup procedure should:

1. **Use List operations** to get IDs of all entities at each level
2. **Use Get operations** to retrieve full details for each entity
3. **Convert field names** from snake_case (gRPC) to camelCase (setup.json)
4. **Handle nested structures** by recursively fetching child entities
5. **Preserve metadata** like timestamps for informational purposes

### Recommended Backup Workflow

```
1. List all tenants
2. For each tenant:
   a. Get full tenant details
   b. List applications in tenant
      - Get full details for each application
      - List integrations for each application
      - Get full details for each integration
      - List multicast groups for each application
      - Get full details for each multicast group
   c. List gateways in tenant
      - Get full details for each gateway
   d. List device profiles in tenant
      - Get full details for each device profile
   e. List users in tenant
      - Get full details for each user
3. List global users
   - Get full details for each global user
4. List device profile templates (if any)
   - Get full details for each template
```

## Key Observations

1. **Timestamps are informational only**: `created_at`, `updated_at`, `last_seen_at` are provided by responses but shouldn't be included in setup.json for restore operations

2. **List items are incomplete**: List responses return simplified objects. Always use Get to retrieve complete entity data for backup

3. **Field naming convention**: gRPC uses snake_case, setup.json uses camelCase. A conversion function is needed

4. **Tags are preserved**: All entities support tags (key-value pairs) which should be backed up

5. **IDs must be preserved**: For restore operations, the original IDs should be preserved in the backup to maintain relationships

6. **Nested structure**: setup.json uses a nested/hierarchical format (applications under tenants), but the API requires separate List calls for each level

## Implementation Notes

The backup implementation should:
- Handle pagination for large lists (using `limit` and `offset` parameters)
- Handle gRPC errors gracefully (NOT_FOUND, PERMISSION_DENIED, etc.)
- Provide progress indication for large backups
- Support selective backup (e.g., only specific tenants)
- Validate the backup data against setup.schema.json before writing
