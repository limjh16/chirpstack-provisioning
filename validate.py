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


class ChirpStackValidator:
    """Validator for ChirpStack provisioning data files."""
    
    def __init__(self, schema_path=None):
        """Initialize the validator with a schema.
        
        Args:
            schema_path: Path to the JSON schema file. If None, uses default schema.json
        """
        self.total_count = 0
        self.error_count = 0
        
        if schema_path is None:
            schema_path = Path(__file__).parent / "schema.json"
        
        self.schema = self._load_schema(schema_path)
    
    def _load_schema(self, schema_path):
        """Load the JSON schema."""
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def validate_entity(self, entity, line_num):
        """Validate a single entity and print errors immediately.
        
        Args:
            entity: The entity data to validate
            line_num: Line number for error reporting
        """
        self.total_count += 1
        
        try:
            jsonschema.validate(entity, self.schema)
        except jsonschema.ValidationError as e:
            self.error_count += 1
            print(f"  Line {line_num}: ✗ Invalid - {str(e.message)}")
            return False
        
        return True
    
    def validate_json_file(self, file_path):
        """Validate a JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle both single objects and arrays
        if isinstance(data, list):
            entities = data
        else:
            entities = [data]

        for i, entity in enumerate(entities, 1):
            self.validate_entity(entity, i)
    
    def validate_jsonl_file(self, file_path):
        """Validate a JSONL file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entity = json.loads(line)
                    self.validate_entity(entity, i)
                except json.JSONDecodeError as e:
                    self.total_count += 1
                    self.error_count += 1
                    print(f"  Line {i}: ✗ Invalid - {str(e)}")
    
    def validate_csv_file(self, file_path):
        """Validate a CSV file."""
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

                self.validate_entity(entity, i)


def load_schema():
    """Load the JSON schema."""
    schema_path = Path(__file__).parent / "schema.json"
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_entity(entity, schema):
    """Validate a single entity against the schema.

    Args:
        entity: The entity data to validate
        schema: The JSON schema to validate against

    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        jsonschema.validate(entity, schema)
        return True
    except jsonschema.ValidationError as e:
        return str(e.message)


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
        results.append((i, validate_entity(entity, schema)))

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
                results.append((i, validate_entity(entity, schema)))
            except json.JSONDecodeError as e:
                results.append((i, str(e)))

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

            results.append((i, validate_entity(entity, schema)))

    return results


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist")
        sys.exit(1)

    # Create validator
    try:
        validator = ChirpStackValidator()
    except Exception as e:
        print(f"Error loading schema: {e}")
        sys.exit(1)

    # Print validation header
    print(f"Validating {file_path.name}...")

    # Determine file type and validate
    suffix = file_path.suffix.lower()

    try:
        if suffix == '.json':
            validator.validate_json_file(file_path)
        elif suffix == '.jsonl':
            validator.validate_jsonl_file(file_path)
        elif suffix == '.csv':
            validator.validate_csv_file(file_path)
        else:
            print(f"Error: Unsupported file type {suffix}. Supported: .json, .jsonl, .csv")
            sys.exit(1)
    except Exception as e:
        print(f"Error validating file: {e}")
        sys.exit(1)

    # Print summary only if there were any entries processed
    if validator.total_count > 0:
        valid_count = validator.total_count - validator.error_count
        print(f"\nResult: {valid_count}/{validator.total_count} entries valid")

    if validator.error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()