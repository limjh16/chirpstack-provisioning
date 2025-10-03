# ChirpStack Provisioning – AI Agent Guide

This document contains important context and guidelines for AI coding agents working on this repository.

## Project Context

This project provisions ChirpStack v4 LoRa Network Servers via the gRPC API (`chirpstack-api` Python library). It enables bulk provisioning of devices and gateways, backup/restore of server configurations, and includes dry-run and duplicate management features.

### Internal Use

- Used in an internal, safe environment - basic safeguards needed but not enterprise-grade security
- Internal ChirpStack servers - no API rate limits or performance optimization needed
- Maintained by multiple people over time - **code clarity is paramount**

### Reference Projects

The `dstencil/chirpstack-deployment-assistant` project has similar objectives. You may reference it for `chirpstack-api` implementation details and examples, but **DO NOT** follow its coding style. Feature equivalence is not required.

## Development Environment

### Project Structure

- **Package**: `src/chirpstack_provisioning/` - Main source code
- **Dependencies**: Managed with [Poetry](https://python-poetry.org/) (`pyproject.toml`)
  - Install: `poetry install --with dev`
  - Run commands: `poetry run <command>`
  - Shell: `poetry shell` (activates virtual environment)
- **CLI Libraries**: `typer` and `rich`
- **Validation**: Main JSON schema in `setup.schema.json` and `devices.schema.json`, those reference other JSON schemas in `proto/jsonschema/` generated from protobuf definitions.
  - The JSON schemas in `proto/jsonschema/` **should not be edited**.

See [`README.md`](README.md) for project structure and [`data.md`](data.md) for data format details.

### Key Implementation Requirements

- **Atomic Commits**: Each feature/change must be a separate, atomic git commit
- **JSON Schemas**: Single source of truth for data validation (`setup.schema.json` and `devices.schema.json`)
- **Security**: Code that pushes changes to ChirpStack server (Create/Update/Delete) must live in a separate file and require user confirmation or `-y` flag
- **Dry Run**: Must NOT call server modification code when `--dry-run` is specified

## Coding Guidelines

### Methodology & Style

- **Test-Driven Development** - Write tests first
- **Atomic Commits** - One feature per commit for useful git blame
- **Simplicity First** - Short, simple, readable code is the priority
- **Reference**: See `validate.py` for the coding style to follow

### Code Organization

- **Clear Hierarchy** - Organize code in files/folders with intuitive structure
- **Function Extraction** - Factor out repeatable code into reusable functions
- **Complex Logic** - Extract into separate functions with clear names
- **OOP Usage** - Use objects when they shorten/clarify code; avoid unnecessary object wrappers
- **Related Functions** - Group in subfolders, not unnecessary classes

### Quality Standards

- **Linting**: Use `ruff` for both linting and formatting
  - Run `poetry run ruff format .` before committing
  - All code must pass `poetry run ruff check .` with no violations
  - Configure in `pyproject.toml` under `[tool.ruff]`
  
- **Large File Handling**: Support 50,000+ lines/devices
  - Use lazy loading, not loading all data at once
  - Stream device JSONL and CSV files line-by-line
  - Setup JSON file can be assumed to be relatively small enough, whole file can be injested at once
  
- **Security**: Separate dangerous operations
  - All server modification code (Create/Update/Delete) in separate file
  - Never call without user confirmation (`-y` flag) or dry-run check
  - ChirpStack lacks granular API permissions - we manage this in code

## Development Tools

- **Context7**: Always use Context7 MCP tools for code generation, setup, configuration, or library/API documentation. Automatically use these tools without explicit requests.

## Future Enhancements (Stretch Goals)

These are lower-priority features for future implementation:

- **State Management**: Resume capabilities and progress reporting for large files and poor connections
- **Integration Testing**: Run tests against actual ChirpStack server processes using Docker containers as pytest fixtures
- **Web Interface**: Simple UI (but code simplicity takes priority)
