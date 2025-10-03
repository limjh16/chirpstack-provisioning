# JSON Schema Bundler

This is a TypeScript utility that bundles `setup.schema.json` and all its dependencies into a single `bundled.schema.json` file.

## Purpose

The `setup.schema.json` file contains references (`$ref`) to external JSON schema files in `proto/jsonschema/`. This bundler resolves all those references and creates a self-contained schema file with all dependencies embedded in the `$defs` section.

## Dependencies

- **@hyperjump/json-schema**: Used for schema bundling according to JSON Schema 2020-12 specification
- **TypeScript**: For type-safe development
- **tsx**: For running TypeScript directly without compilation

## Usage

### Running the bundler

From the `proto/bundler` directory:

```bash
npm run bundle
```

This will:
1. Load `setup.schema.json` from the repository root
2. Recursively find and register all schema files in `proto/jsonschema/`
3. Bundle all references into a single schema
4. Output the result to `bundled.schema.json` in the repository root

### Building (optional)

To compile TypeScript to JavaScript:

```bash
npm run build
```

Then run the compiled version:

```bash
npm run bundle:compiled
```

## How It Works

1. **Schema Registration**: All JSON schema files from `proto/jsonschema/` are registered with unique URIs based on their file paths
2. **Main Schema**: The main `setup.schema.json` is registered as the entry point
3. **Bundling**: The `@hyperjump/json-schema` bundle function resolves all `$ref` references and embeds external schemas into a `$defs` section
4. **Output**: The bundled schema is written to `bundled.schema.json`

## Output

The `bundled.schema.json` file contains:
- All the properties from the original `setup.schema.json`
- A `$defs` section with all referenced schemas embedded
- All `$ref` references remain unchanged but now point to internal definitions

This makes the schema self-contained and easier to distribute or use in environments where external schema files are not available.
