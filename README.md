# ChirpStack Provisioning

A tool for provisioning ChirpStack v4 LoRaWAN Network Server via its gRPC API interface. This project enables easy setup of ChirpStack infrastructure and bulk provisioning of devices and gateways.

## Features

- **Two-file workflow**: Separate setup and device files for clear organization
- **Hierarchical infrastructure setup**: Define tenants, applications, device profiles, gateways, and integrations in a structured format
- **Bulk device provisioning**: Import thousands of devices from JSON, JSONL, or CSV files
- **Auto-fill capabilities**: Automatic ID lookups using names instead of UUIDs
- **Dry-run mode**: Preview changes before committing
- **Duplicate handling**: Configurable actions for existing entities (skip, override, error)
- **Validation**: Built-in schema validation for all data files

## Quick Start

### Installation

```bash
# Install dependencies with Poetry
poetry install
```

### Data Files

The tool uses a two-file approach:

1. **Setup file** (`setup.json`): Define infrastructure
   - Tenants with nested gateways, applications, device profiles, and integrations
   - JSON format only (YAML/TOML support planned)
   - Processed first to establish the infrastructure

2. **Device file** (`devices.json/jsonl/csv`): Define individual devices
   - Flat structure with one device per line/object
   - Supports JSON, JSONL, and CSV formats
   - References applications and device profiles by name

### Validation

Validate your data files before provisioning:

```bash
# Validate setup file
poetry run python validate.py examples/sample_setup.json

# Validate device file (auto-detects format)
poetry run python validate.py examples/sample_devices.json
poetry run python validate.py examples/sample_devices.jsonl
poetry run python validate.py examples/sample_devices.csv

# Specify schema explicitly
poetry run python validate.py myfile.json --schema=setup
poetry run python validate.py myfile.json --schema=devices
```

## Documentation

- [data.md](data.md) - Complete data format documentation with examples
- [SCHEMA_MIGRATION.md](SCHEMA_MIGRATION.md) - Migration guide from old single-file format
- [examples/](examples/) - Example setup and device files
- [AGENTS.md](AGENTS.md) - Development guidelines for AI agents

## Usage

### Provisioning Workflow

1. **Create Setup File**: Define your infrastructure in `setup.json`
2. **Validate Setup**: `poetry run python validate.py setup.json --schema=setup`
3. **Process Setup**: Run provisioning tool with setup file (implementation in progress)
4. **Create Device File**: Define devices in `devices.json`, `devices.jsonl`, or `devices.csv`
5. **Validate Devices**: `poetry run python validate.py devices.csv --schema=devices`
6. **Process Devices**: Run provisioning tool with device file (implementation in progress)

### Command-Line Options (Planned)

```bash
chirpstack-provision setup setup.json --server=localhost:8080 --token=<API_TOKEN>
chirpstack-provision devices devices.csv --server=localhost:8080 --token=<API_TOKEN> --dry-run
chirpstack-provision devices devices.json --duplicate=skip --yes
```

## Data Format Examples

### Setup File (setup.json)

```json
{
  "tenants": [
    {
      "name": "my-tenant",
      "*id": "AUTO-GENERATED",
      "gateways": [
        {
          "gateway_id": "0000000000001234",
          "name": "Gateway 1",
          "*tenant_id": "AUTO-PARENT"
        }
      ],
      "applications": [
        {
          "name": "my-app",
          "*id": "AUTO-GENERATED",
          "*tenant_id": "AUTO-PARENT"
        }
      ],
      "_deviceProfiles": [
        {
          "name": "class-a-sensor",
          "*id": "AUTO-GENERATED",
          "*tenant_id": "AUTO-PARENT",
          "region": "AU915",
          "mac_version": "LORAWAN_1_0_4",
          "reg_params_revision": "RP002_1_0_1",
          "supports_otaa": true
        }
      ]
    }
  ]
}
```

### Device File (devices.csv)

```csv
name,dev_eui,application_name,device_profile_name,nwk_key
Sensor 01,0123456789ABCDEF,my-app,class-a-sensor,0123456789ABCDEF0123456789ABCDEF
Sensor 02,FEDCBA9876543210,my-app,class-a-sensor,FEDCBA9876543210FEDCBA9876543210
```

See [examples/](examples/) for more complete examples.

## Project Structure

```
chirpstack-provisioning/
├── setup.schema.json          # JSON schema for setup files
├── devices.schema.json        # JSON schema for device files
├── validate.py                # Validation script
├── data.md                    # Complete data format documentation
├── examples/                  # Example data files
│   ├── sample_setup.json
│   ├── sample_devices.json
│   ├── sample_devices.jsonl
│   └── sample_devices.csv
├── src/chirpstack_provisioning/  # Python package (in development)
└── tests/                     # Test files
```

## Requirements

- Python 3.12+
- Poetry for dependency management
- ChirpStack v4 server with API access
- Required Python packages (managed by Poetry):
  - chirpstack-api
  - typer
  - rich
  - jsonschema

## Development

This project follows Test-Driven Development (TDD) principles and uses:
- **Linting/Formatting**: `ruff` for code style consistency
- **Testing**: `pytest` for unit and integration tests
- **API**: `chirpstack-api` Python package for gRPC communication

See [AGENTS.md](AGENTS.md) for detailed development guidelines.

## License

[To be determined]

## Contributing

[To be determined]

## Support

For questions or issues, please refer to the documentation files or create an issue in the repository.
