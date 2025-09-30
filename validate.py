#!/usr/bin/env python3
"""
Simple validation script for ChirpStack provisioning data.

Validates JSON, JSONL, and CSV files against the schema.json schema.
"""

import json
import csv
from pathlib import Path

import jsonschema
import typer
from rich import print


class ChirpStackValidator:
    """Validator for ChirpStack provisioning data files."""

    def __init__(self, schema_path: str | Path | None = None):
        """Initialize the validator with a schema.

        Args:
            schema_path: Path to the JSON schema file. If None, uses default schema.json
        """
        self.total_count = 0
        self.error_count = 0

        if schema_path is None:
            schema_path: Path = Path(__file__).parent / "schema.json"

        self.schema = self._load_schema(schema_path)

    @property
    def total_count(self) -> int:
        return self._total_count

    @total_count.setter
    def total_count(self, value: int) -> None:
        if value < 0:
            raise ValueError("Total count cannot be negative")
        self._total_count = value

    @property
    def error_count(self) -> int:
        return self._error_count

    @error_count.setter
    def error_count(self, value: int) -> None:
        if value < 0:
            raise ValueError("Error count cannot be negative")
        if value > self._total_count:
            raise ValueError("Error count cannot exceed total count")
        self._error_count = value

    @staticmethod
    def _load_schema(schema_path: str | Path) -> object:
        """Load the JSON schema."""
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _get_property_type(self, key: str) -> str:
        """Get the expected type for a property from the schema.

        Args:
            key: Property name to look up

        Returns:
            str: The type ('boolean', 'number', 'integer', 'string', or None)
        """
        # Check both device and gateway schemas since they're in oneOf
        for schema_def in self.schema.get("oneOf", []):
            properties = schema_def.get("properties", {})
            if key in properties:
                prop_schema = properties[key]
                return prop_schema.get("type")

        raise KeyError(f"Property '{key}' not found in schema")

    @staticmethod
    def _convert_to_boolean(value: str) -> bool:
        """Convert a string value to boolean.

        Args:
            value: String value to convert

        Returns:
            bool: Converted boolean value

        Raises:
            ValueError: If value cannot be converted to boolean
        """
        if value.lower() in ("true", "1", "yes"):
            return True
        elif value.lower() in ("false", "0", "no"):
            return False
        else:
            raise ValueError(f"Cannot convert '{value}' to boolean")

    @staticmethod
    def _convert_to_number(value: str, target_type: str) -> float | int:
        """Convert a string value to a number (float or int).

        Args:
            value: String value to convert
            target_type: Target type ('number' for float, 'integer' for int)

        Returns:
            float or int: Converted numeric value

        Raises:
            ValueError: If value cannot be converted to the target type
        """
        if target_type == "integer":
            return int(value)
        elif target_type == "number":
            return float(value)
        else:
            raise ValueError(f"Unknown numeric target type: {target_type}")

    def validate_entity(self, entity, line_num) -> bool:
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
        with open(file_path, "r", encoding="utf-8") as f:
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
        with open(file_path, "r", encoding="utf-8") as f:
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
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, 1):
                # Convert CSV string values to appropriate types based on schema
                entity = {}
                for key, value in row.items():
                    if value == "":
                        continue

                    try:
                        # Get the expected type from the schema
                        expected_type = self._get_property_type(key)

                        if expected_type == "boolean":
                            entity[key] = self._convert_to_boolean(value)
                        elif expected_type in ("number", "integer"):
                            entity[key] = self._convert_to_number(value, expected_type)
                    except (ValueError, KeyError):
                        # If conversion fails or key is not found, keep as string and let schema validation catch the error
                        entity[key] = value

                self.validate_entity(entity, i)


app = typer.Typer()


@app.command()
def main(
    file_path: Path = typer.Argument(
        ..., help="Path to the file to validate (JSON, JSONL, or CSV)"
    ),
):
    """Validate ChirpStack provisioning data files against the schema."""
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist")
        raise typer.Abort()

    # Create validator
    try:
        validator = ChirpStackValidator()
    except Exception as e:
        print(f"Error loading schema: {e}")
        raise typer.Abort()

    # Print validation header
    print(f"Validating {file_path.name}...")

    # Determine file type and select appropriate validation method
    suffix = file_path.suffix.lower()

    match suffix:
        case ".json":
            validation_method = validator.validate_json_file
        case ".jsonl":
            validation_method = validator.validate_jsonl_file
        case ".csv":
            validation_method = validator.validate_csv_file
        case _:
            print(
                f"Error: Unsupported file type {suffix}. Supported: .json, .jsonl, .csv"
            )
            raise typer.Abort()

    # Execute validation in try-except block
    try:
        validation_method(file_path)
    except Exception as e:
        print(f"Error validating file: {e}")
        raise typer.Abort()

    # Print summary only if there were any entries processed
    if validator.total_count > 0:
        valid_count = validator.total_count - validator.error_count
        print(f"\nResult: {valid_count}/{validator.total_count} entries valid")

    if validator.error_count > 0:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
