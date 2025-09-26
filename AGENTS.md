# ChirpStack Provisioning – AI Agent Guide

## Goals

- The goal is to create a new project that communicates with an existing ChirpStack v4 LoRa Network Server via its gRPC API interface. This project aims to easily provision the server with all the data that is normally stored in its database instead of being defined in the `chirpstack.toml` or `region...toml` configuration files.
    - The gRPC API interface has a python library at `chirpstack-api`.
- This project should be able to bulk provision many devices and gateways at once. This allows for easy creations of new ChirpStack Servers.
- Similarly, in order to back up older ChirpStack servers, this project should be able to export all the device and gateway data for importing into another server.
- This project should include a dry run feature. This feature is important.
- This project should include conflict and duplicate management to facilitate easy updating of existing devices and gateways in existing servers.
- This project should have an interface for humans (CLI) as well as other programs or scripts (as a python package).

### Other projects

- There exists a project, `dstencil/chirpstack-deployment-assistant`, with similar objectives. The code is fully working, so we can refer to the project for working example codes while developing this current project. However, the coding styles MUST BE IGNORED because it is historical and coded by different people.
    - You can reference this project for implementation details and examples regarding the `chirpstack-api` package.
    - Feature equivalence is not important.
        - A web server is NOT IMPORTANT.
    - Following the same `.csv` format and schema is not important but good to have.

### Use Cases

- This project will be used to easily spin up quick test environments of ChirpStack network servers, with pre-provisioned gateways and devices.
    - From an empty and new ChirpStack server, this project should be able to provision everything required for bare minimum operation.
    - This should include (non-exhaustive):
        - Tenants
        - Device Profiles
        - Applications
        - Devices
        - Gateways
- This project will be used to back up existing production ChirpStack servers.
- This project will be used by CD pipelines to update existing ChirpStack network servers with new versions of device codecs.
- This project will be used when bulk-importing devices onto existing ChirpStack network servers, so that the details can be centralised in one CSV or JSON file rather than keyed in manually and individually on ChirpStack's web interface.

### Users

- This project will be used in an internal environment that is considered safe. As such, network security is not the most important factor, but the basic safeguards should still be implemented.
- Since the project is used internally, factors such as input validation is not of the utmost importance.
- Since the ChirpStack servers are also internal, we don't need to worry about API rate limits or parallel processing. Performance is not required.
- Since this project will be continuously maintained by different people, the code should be easy to understand so that it can be handed over easily.

## Specific implementation details

- CLI should be implemented with `typer` and `rich` libraries.
    - Necessary CLI flags:
        - `-y` or `--yes` for automatically committing changes
        - `--duplicate=` for defining the default action to apply to duplicates
            - skip, override, or error
        - `--dry-run` for only viewing the potential changes but not committing anything
- Python package should follow the `src` directory structure so that it can be easily exported.
- Data format should accept `json`, `jsonl`, and `csv`.
    - Definition and validation of data formats should be done through a single `jsonschema` file (`schema.json`).
    - The data should be in a flat format. Each `json` object or each line in the `csv` should correspond to either one device or one gateway, with a `type` field specifying which entity type it represents.
    - The main identifier is the EUI of the device or gateway (dev_eui for devices, gateway_id for gateways).
    - For simplified provisioning, assume there is only one tenant and one application in most scenarios.
        - If the tenant, device profile, or application referenced in the data does not exist, this should be flagged out for the user to address.
- Required connection details are the server address and API token.
    - Debug messages such as server not reachable, port not reachable, or API invalid, should be given.
    - These connection details should either be provided as a CLI flag or environment variable.
- All duplicates should be listed out, and the corresponding action should be specified by the user before the script continues to run.
    - 3 actions should be defined:
        - skip: Skip existing entities
        - override: Update existing entities with new data
        - error: Stop the script from running
    - If the `-y` or `--yes` flag is specified, a `--duplicate=` flag should also be required, which should specify the intended action upon meeting duplicates.
- Manage dependencies with Poetry (`pyproject.toml`); source lives under `src/chirpstack_provisioning`.
- The JSON schema (`schema.json`) should be the single source of truth for data validation.
- Documentation for data formats should be provided in `data.md` with examples of JSON, JSONL, and CSV formats.

### Coding Guidelines

- This project should follow a Test Driven Development methodology.
- This project should be able to handle large files of over 50000 lines and devices.
    - For memory management, the data should be lazily loaded, and not loaded all at once.
- Each change and commit should be atomic, limited to one feature, so that git blame will be useful.
- The priority should be code that is short and simple to understand.
    - If there are chunks of code and logic that cannot be shortened (e.g., input validation that has multiple factors to check against), it should be factored out in a separate function.
    - All code which is repeatable should be factored out into reusable functions.
    - OOP can and should be used wherever it is able to shorten code or make the code more intuitive to understand.
        - However, if there is no need for objects, do not unnecessarily lengthen the code by grouping functions into objects.
        - Instead, functions with similar objectives can be grouped in a separate subfolder.
- Wherever possible, this project should be cleverly organised in separate files and folders so that the hierachy is easily understood.
- All code that actually push changes to the ChirpStack network server (e.g., Create Update and Delete requests) should live in a separate file. IMPORTANT! This file should NOT be called if dry run is specified. User confirmation or a `-y` / `--yes` flag must be present for any of these requests to be run.
    - Since the ChirpStack server does not have granular API permissions and controls, it is important that we manage the permissions within this project. Changes to the server cannot be made without the user's confirmation.

### Development Tools

- Always use context7 when I need code generation, setup or configuration steps, or library/API documentation. This means you should automatically use the Context7 MCP tools to resolve library id and get library docs without me having to explicitly ask.

## Stretch goals

- For large files and poor connections, we might want to implement state management and resume capabilities or progress reporting in case of interrupted or slow operations.
- Tests should be ran against an actual ChirpStack server process, which are ran for the duration of the pytest session and shut down at the end of it.
    - These servers can be defined as a pytest fixture.
    - The server can make use of the ChirpStack docker containers.
- Import and export all server data that cannot be defined in `chirpstack.toml` or `region_...toml` configuration files, such as InfluxDB integrations or users.
- A simple web interface can be developed. However, priority should be given to clean and simple code over this functionality.
