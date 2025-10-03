# Parallel Implementation Strategy

This document breaks down the ChirpStack Provisioning implementation tasks for parallel execution by up to 5 coding agents working simultaneously and asynchronously.

## Overview

The implementation is organized into **5 workstreams** that can be executed in parallel with minimal dependencies. Each workstream is assigned to one agent and focuses on a distinct area of functionality.

## Agent Assignments

### 🔵 Agent 1: Foundation & Schemas
**Focus**: Data schemas, validation, and project infrastructure

**Priority**: HIGH - Required by all other agents

#### Phase 1A: Schemas & Configuration (Week 1)
- [ ] Create `devices.schema.json` from proto definitions
  - Reference `proto/jsonschema/device/` schemas
  - Support flat structure (one device per entry)
  - Primary identifier: `dev_eui`
- [ ] Create `devices.example.json` and `devices.example.csv`
- [ ] Add ruff configuration to `pyproject.toml`
  - Line length: 88
  - Target Python version: 3.12
  - Select common rules (E, F, W, I, N)
- [ ] Configure pre-commit hooks for ruff formatting
- [ ] Add CLI entry point in `pyproject.toml` under `[project.scripts]`

#### Phase 1B: Enhanced Validation (Week 2)
- [ ] Extend `validate.py` to support both schemas
- [ ] Add validation summary with statistics
- [ ] Create comprehensive test suite for validation
- [ ] Document schema generation process in `proto/doc.md`

**Deliverables**: 
- `devices.schema.json`, example files
- Configured linting and pre-commit
- Enhanced validation framework

**Dependencies**: None (can start immediately)

---

### 🟢 Agent 2: Data Loaders
**Focus**: Efficient data loading for large files

**Priority**: HIGH - Required by agents 3, 4, and 5

#### Phase 2A: Core Loaders (Week 1)
- [ ] Create `src/chirpstack_provisioning/loaders/__init__.py`
- [ ] Implement `src/chirpstack_provisioning/loaders/json_loader.py`
  - Lazy loading for setup.json (can load entire file - relatively small)
  - Generator-based loading for devices.json (if array)
- [ ] Implement `src/chirpstack_provisioning/loaders/jsonl_loader.py`
  - Stream line-by-line for devices.jsonl
  - Generator-based with proper error handling
  - Memory-efficient for 50,000+ lines

#### Phase 2B: CSV & Integration (Week 2)
- [ ] Implement `src/chirpstack_provisioning/loaders/csv_loader.py`
  - Stream CSV rows as dictionaries
  - Type coercion (strings to appropriate JSON types)
  - Handle missing fields gracefully
- [ ] Create `src/chirpstack_provisioning/loaders/validator.py`
  - Wrapper around jsonschema validation
  - Schema caching for performance
  - Detailed error messages with line numbers
- [ ] Add comprehensive tests for all loaders
  - Test with large files (>10,000 entries)
  - Memory profiling tests
  - Error case testing

**Deliverables**:
- Complete `loaders/` module with JSON, JSONL, CSV support
- Validator wrapper
- Performance-tested code

**Dependencies**: 
- Requires Agent 1's `devices.schema.json` (can mock initially)

---

### 🟡 Agent 3: ChirpStack API Client
**Focus**: gRPC client and connection management

**Priority**: MEDIUM - Required by agents 4 and 5

#### Phase 3A: Client Infrastructure (Week 1-2)
- [ ] Create `src/chirpstack_provisioning/client/__init__.py`
- [ ] Implement `src/chirpstack_provisioning/client/connection.py`
  - gRPC channel management
  - Connection validation (server reachable, port accessible)
  - API token validation
  - Error handling with informative messages
  - Support for environment variables (`CHIRPSTACK_SERVER`, `CHIRPSTACK_TOKEN`)
- [ ] Create `src/chirpstack_provisioning/client/tenants.py`
  - List tenants
  - Get tenant by ID/name
  - Query tenant existence
- [ ] Create `src/chirpstack_provisioning/client/applications.py`
  - List applications (filtered by tenant)
  - Get application by ID/name
  - Query application existence

#### Phase 3B: Entity Clients (Week 2-3)
- [ ] Create `src/chirpstack_provisioning/client/device_profiles.py`
  - List device profiles (filtered by tenant)
  - Get device profile by ID/name
  - Query device profile existence
- [ ] Create `src/chirpstack_provisioning/client/gateways.py`
  - List gateways (filtered by tenant)
  - Get gateway by ID
  - Query gateway existence
- [ ] Create `src/chirpstack_provisioning/client/devices.py`
  - List devices (filtered by application)
  - Get device by dev_eui
  - Query device existence
- [ ] Add comprehensive tests with mocked gRPC responses
  - Mock server responses
  - Test connection error scenarios
  - Test authentication failures

**Deliverables**:
- Complete `client/` module with read operations
- Connection management
- Comprehensive tests with mocks

**Dependencies**: 
- Uses `chirpstack-api` Python package (already in dependencies)

---

### 🟠 Agent 4: Diff Engine & Dry Run
**Focus**: Compare desired vs current state, display changes

**Priority**: MEDIUM - Depends on agents 2 and 3

#### Phase 4A: Diff Calculator (Week 2-3)
- [ ] Create `src/chirpstack_provisioning/diff/__init__.py`
- [ ] Implement `src/chirpstack_provisioning/diff/comparator.py`
  - Compare desired state (from loaders) vs current state (from client)
  - Detect new entities (CREATE)
  - Detect existing entities with changes (UPDATE)
  - Detect entities only in current state (optionally DELETE)
  - Handle name-based references (tenant/app/profile by name)
- [ ] Implement `src/chirpstack_provisioning/diff/resolver.py`
  - Resolve name references to IDs
  - Detect missing references (flag for user)
  - Build dependency graph (tenants → apps → devices)

#### Phase 4B: Rich Output (Week 3-4)
- [ ] Implement `src/chirpstack_provisioning/diff/formatter.py`
  - Rich-formatted tables for changes
  - Color-coded output (green=CREATE, yellow=UPDATE, red=DELETE)
  - Summary statistics (total changes by type)
  - Duplicate detection and reporting
- [ ] Create `src/chirpstack_provisioning/diff/duplicate_handler.py`
  - Detect duplicates by primary key (dev_eui, gateway_id, name)
  - Implement skip/override/error strategies
  - Generate duplicate resolution prompts
- [ ] Add comprehensive tests
  - Test diff calculation with various scenarios
  - Test output formatting
  - Test duplicate detection

**Deliverables**:
- Complete `diff/` module
- Rich-formatted dry run output
- Duplicate detection and handling

**Dependencies**:
- Requires Agent 2's loaders
- Requires Agent 3's client (read operations)

---

### 🔴 Agent 5: Provisioning Engine & CLI
**Focus**: Write operations and command-line interface

**Priority**: MEDIUM - Depends on agents 2, 3, and 4

#### Phase 5A: Provisioning Engine (Week 3-4)
- [ ] Create `src/chirpstack_provisioning/provisioner.py` (**ISOLATED FILE**)
  - **IMPORTANT**: All Create/Update/Delete operations ONLY in this file
  - Implement tenant creation/update
  - Implement application creation/update
  - Implement device profile creation/update
  - Implement gateway creation/update
  - Implement device creation/update
  - Implement integration creation/update
  - User confirmation checks (require `-y` flag or prompt)
  - Duplicate handling (skip/override/error)
  - Transaction-like behavior (rollback on errors where possible)
  - Progress reporting for large batches

#### Phase 5B: CLI Implementation (Week 4-5)
- [ ] Create `src/chirpstack_provisioning/cli.py`
  - Main `provision` command with typer
  - `--dry-run` flag (never calls provisioner when set)
  - `-y/--yes` flag (auto-confirm, requires `--duplicate`)
  - `--duplicate=skip|override|error` flag
  - `--server=<url>` flag (or `CHIRPSTACK_SERVER` env var)
  - `--token=<token>` flag (or `CHIRPSTACK_TOKEN` env var)
  - Rich progress bars and status updates
  - Error handling with helpful messages
- [ ] Add comprehensive tests
  - Test CLI argument parsing
  - Test dry-run mode (ensure no write operations)
  - Test confirmation flow
  - Mock provisioner calls

**Deliverables**:
- `provisioner.py` with all write operations
- Complete CLI with rich output
- Comprehensive tests

**Dependencies**:
- Requires Agent 2's loaders
- Requires Agent 3's client
- Requires Agent 4's diff engine

---

## Coordination & Integration

### Shared Interfaces

To work in parallel, agents must agree on interfaces:

1. **Loader Interface** (Agent 2 → Agents 4, 5):
   ```python
   def load_setup(file_path: Path) -> dict
   def load_devices(file_path: Path) -> Generator[dict, None, None]
   ```

2. **Client Interface** (Agent 3 → Agents 4, 5):
   ```python
   def list_tenants() -> List[Tenant]
   def get_tenant(name: str) -> Optional[Tenant]
   # Similar for other entities
   ```

3. **Diff Interface** (Agent 4 → Agent 5):
   ```python
   def calculate_diff(desired: State, current: State) -> DiffResult
   def format_diff(diff: DiffResult) -> str  # Rich output
   ```

### Integration Points

**Week 1:**
- Agent 1: Delivers schemas (used by Agent 2 for validation)

**Week 2:**
- Agent 2: Delivers loaders (used by Agents 4, 5)
- Agent 3: Delivers basic client (used by Agent 4)

**Week 3:**
- Agent 4: Delivers diff engine (used by Agent 5)
- Agent 3: Completes client (used by Agent 5)

**Week 4:**
- Agent 5: Integrates everything into CLI and provisioner

### Communication Protocol

1. **Define interfaces first**: Each agent creates interface stubs in Week 1
2. **Use mocks during development**: Agents can mock dependencies
3. **Integration testing**: Week 4-5, all agents collaborate on E2E tests
4. **Code reviews**: Cross-agent reviews to ensure compatibility

## Sequential vs Parallel Tasks

### Must Be Sequential
- Agent 1 → Agent 2 (schemas needed for validation)
- Agent 3 → Agent 4 (client needed for current state)
- Agent 4 → Agent 5 (diff needed for CLI)

### Can Be Parallel
- Agent 1 (schemas) parallel with Agent 3 (client)
- Agent 2 (loaders) parallel with Agent 3 (client)
- Agent 4 (diff) can start once Agent 2 and 3 are partially complete

## Timeline Summary

| Week | Agent 1 | Agent 2 | Agent 3 | Agent 4 | Agent 5 |
|------|---------|---------|---------|---------|---------|
| 1    | Schemas, Config | Core loaders | Client infra | (waiting) | (waiting) |
| 2    | Enhanced validation | CSV, validator | Entity clients | Diff calculator | (waiting) |
| 3    | Testing, docs | Testing | Testing | Rich output | Provisioner |
| 4    | Support | Support | Support | Testing | CLI |
| 5    | Integration | Integration | Integration | Integration | Integration |

## Future Work (Not Parallelized)

After parallel implementation:

- **Export/Backup** (Agent 5): Reverse direction - read from server, write to files
- **Integration Tests** (All agents): E2E tests with real ChirpStack Docker container
- **Advanced Features**: State management, progress reporting, TOML/YAML support

## Success Criteria

Each agent should:
- ✅ Deliver working code with tests (>80% coverage)
- ✅ Pass `ruff check` and `ruff format` with no violations
- ✅ Make atomic commits (one feature per commit)
- ✅ Document interfaces and usage
- ✅ Handle errors gracefully with informative messages
- ✅ Support large files (50,000+ lines) efficiently

Final integration:
- ✅ All modules work together seamlessly
- ✅ CLI accepts all required flags
- ✅ Dry-run shows correct diff without making changes
- ✅ Provisioning works end-to-end with real ChirpStack server
- ✅ All tests pass
