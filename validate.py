#!/usr/bin/env python3
"""
Simple validation script for ChirpStack provisioning data.

Validates JSON, JSONL, and CSV files against the schema.json schema.
"""

import json
import csv
import sys
from pathlib import Path

import jsonschema


def load_schema():
    """Load the JSON schema."""
    schema_path = Path(__file__).parent / "schema.json"
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_entity(entity, schema, line_num):
    """Validate a single entity against the schema.
    
    Args:
        entity: The entity data to validate
        schema: The JSON schema to validate against
        line_num: Line number for error reporting
        
    Returns:
        tuple: (line_num, is_valid, error_message)
    """
    try:
        jsonschema.validate(entity, schema)
        return (line_num, True, None)
    except jsonschema.ValidationError as e:
        return (line_num, False, str(e.message))


def validate_json_file(file_path, schema):
    """Validate a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both single objects and arrays
    if isinstance(data, list):
        entities = data
    else:
        entities = [data]
    
    results = []
    for i, entity in enumerate(entities, 1):
        results.append(validate_entity(entity, schema, i))
    
    return results


def validate_jsonl_file(file_path, schema):
    """Validate a JSONL file."""
    results = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entity = json.loads(line)
                results.append(validate_entity(entity, schema, i))
            except json.JSONDecodeError as e:
                results.append((i, False, str(e)))
    
    return results


def validate_csv_file(file_path, schema):
    """Validate a CSV file."""
    results = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            # Convert string booleans to actual booleans, numbers, and clean empty values
            entity = {}
            for key, value in row.items():
                if value == '':
                    continue
                elif value.lower() in ('true', 'false'):
                    entity[key] = value.lower() == 'true'
                elif key in ['latitude', 'longitude', 'altitude', 'stats_interval']:
                    # Convert numeric fields
                    try:
                        if '.' in value:
                            entity[key] = float(value)
                        else:
                            entity[key] = int(value)
                    except ValueError:
                        entity[key] = value  # Keep as string if conversion fails
                else:
                    entity[key] = value
            
            results.append(validate_entity(entity, schema, i))
    
    return results


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate.py <file_path>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist")
        sys.exit(1)
    
    # Load schema
    try:
        schema = load_schema()
    except Exception as e:
        print(f"Error loading schema: {e}")
        sys.exit(1)
    
    # Determine file type and validate
    suffix = file_path.suffix.lower()
    
    try:
        if suffix == '.json':
            results = validate_json_file(file_path, schema)
        elif suffix == '.jsonl':
            results = validate_jsonl_file(file_path, schema)
        elif suffix == '.csv':
            results = validate_csv_file(file_path, schema)
        else:
            print(f"Error: Unsupported file type {suffix}. Supported: .json, .jsonl, .csv")
            sys.exit(1)
    except Exception as e:
        print(f"Error validating file: {e}")
        sys.exit(1)
    
    # Print results
    print(f"Validating {file_path.name}...")
    
    valid_count = sum(1 for _, is_valid, _ in results if is_valid)
    total_count = len(results)
    
    for line_num, is_valid, error in results:
        if is_valid:
            print(f"  Line {line_num}: ✓ Valid")
        else:
            print(f"  Line {line_num}: ✗ Invalid - {error}")
    
    print(f"\nResult: {valid_count}/{total_count} entries valid")
    
    if valid_count != total_count:
        sys.exit(1)


if __name__ == "__main__":
    main()