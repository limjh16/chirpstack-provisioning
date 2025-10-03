# ChirpStack Provisioning

A Python tool for bulk provisioning and managing ChirpStack v4 LoRa Network Servers via the gRPC API.

## Features

- 🚀 **Bulk Provisioning** - Provision many devices and gateways at once
- 📦 **Backup & Restore** - Export and import ChirpStack server configurations
- 🔍 **Dry Run Mode** - Preview changes before applying them
- 🔄 **Duplicate Handling** - Skip, override, or error on conflicts
- 📊 **Multiple Formats** - Support for JSON, JSONL, and CSV data files
- 🎯 **CLI & Library** - Use as a command-line tool or Python package

## Installation

```bash
pip install -e .
```

## Quick Start

### Validate Data Files

```bash
python validate.py devices.csv devices.schema.json
python validate.py setup.json setup.schema.json
```

### Provision a ChirpStack Server

```bash
# Dry run (preview changes)
chirpstack-provision --dry-run setup.json devices.csv

# Apply changes with duplicate handling
chirpstack-provision -y --duplicate=skip setup.json devices.csv

# Interactive mode (prompt for duplicates)
chirpstack-provision setup.json devices.csv
```

## Usage

### Data Files

ChirpStack Provisioning uses two types of data files:

1. **Setup File** (`setup.json`) - Defines tenants, applications, gateways, device profiles, etc.
2. **Devices File** (`devices.json/jsonl/csv`) - Defines individual devices to provision

See [data.md](data.md) for detailed format documentation and examples.

### Command-Line Interface

```bash
chirpstack-provision [OPTIONS] <setup-file> <devices-file>
```

**Options:**
- `-y, --yes` - Automatically confirm changes (requires `--duplicate`)
- `--dry-run` - Preview changes without applying them
- `--duplicate=<action>` - How to handle duplicates: `skip`, `override`, or `error`
- `--server=<url>` - ChirpStack server address (or set `CHIRPSTACK_SERVER` env var)
- `--token=<token>` - API token (or set `CHIRPSTACK_TOKEN` env var)

### As a Python Library

```python
from chirpstack_provisioning import provision

# Provision with options
provision(
    setup_file="setup.json",
    devices_file="devices.csv",
    server="localhost:8080",
    token="your-api-token",
    dry_run=False,
    duplicate_action="skip"
)
```

## Project Structure

```
.
├── src/chirpstack_provisioning/   # Main package source
├── tests/                          # Test suite
├── proto/                          # Protocol buffer definitions and schemas
│   ├── jsonschema/                 # Generated JSON schemas
│   └── doc.md                      # Schema generation documentation
├── validate.py                     # Standalone validation script
├── data.md                         # Data format documentation
├── AGENTS.md                       # Developer/AI agent guide
└── pyproject.toml                  # Project configuration
```

## Use Cases

- **Test Environments** - Quickly spin up ChirpStack servers with pre-provisioned data
- **Production Backups** - Export configurations from existing servers
- **CI/CD Pipelines** - Update servers with new device codec versions
- **Bulk Operations** - Import many devices from centralized CSV/JSON files

## Development

### Setup

```bash
# Install dependencies
pip install -e .

# Install development tools
pip install pytest ruff
```

### Testing

```bash
pytest
```

### Linting & Formatting

```bash
# Check code
ruff check .

# Format code
ruff format .
```

### Code Style

This project follows these principles:

- **Atomic commits** - One feature per commit
- **Simple and readable** - Prefer clarity over cleverness
- **Test-driven development** - Write tests first
- **Lazy loading** - Handle large files (50,000+ lines) efficiently

See [AGENTS.md](AGENTS.md) for detailed development guidelines.

## Roadmap

- [x] Data validation framework
- [ ] Core provisioning logic
- [ ] CLI implementation
- [ ] Backup/export functionality
- [ ] Duplicate detection and handling
- [ ] Error handling and recovery
- [ ] Integration tests with real ChirpStack server
- [ ] Progress reporting for large operations
- [ ] State management for interrupted operations

## Connection Details

The tool requires ChirpStack server connection details:

- **Server Address** - Via `--server` flag or `CHIRPSTACK_SERVER` environment variable
- **API Token** - Via `--token` flag or `CHIRPSTACK_TOKEN` environment variable

The tool provides helpful error messages for connection issues:
- Server not reachable
- Port not accessible
- Invalid API token

## Contributing

This project is maintained internally but contributions are welcome. Please ensure:

1. Code passes `ruff check` and `ruff format`
2. All tests pass
3. Each commit is atomic (one feature/fix)
4. Code is well-documented and readable

## License

[License information to be added]
