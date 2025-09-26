#!/usr/bin/env python3
"""
Utility script to validate example data files against the JSON schemas.

This script demonstrates how to use the schema validation functionality
and validates the example data files to ensure they are correct.
"""

import json
import csv
from pathlib import Path
import sys

# Add the parent directory to the path so we can import our package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chirpstack_provisioning.validation import validate_device, validate_gateway, validate_batch


def load_json_file(file_path: Path) -> list:
    """Load JSON data from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_csv_file(file_path: Path) -> list:
    """Load CSV data from a file and convert to list of dictionaries."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert string boolean values to actual booleans and handle empty values
            for key, value in row.items():
                if value == '':
                    # Remove empty fields from the row instead of setting to None
                    # This allows optional fields to be handled properly by the schema
                    continue
                elif value.lower() in ('true', 'false'):
                    row[key] = value.lower() == 'true'
            
            # Remove empty string values entirely
            row = {k: v for k, v in row.items() if v != ''}
            data.append(row)
    return data


def validate_file(file_path: Path, entity_type: str) -> None:
    """Validate a single file and print results."""
    print(f"\n=== Validating {file_path.name} ===")
    
    try:
        if file_path.suffix == '.json':
            data = load_json_file(file_path)
        elif file_path.suffix == '.csv':
            data = load_csv_file(file_path)
        else:
            print(f"Unsupported file format: {file_path.suffix}")
            return
        
        if not isinstance(data, list):
            data = [data]
        
        results = validate_batch(data, entity_type)
        
        valid_count = sum(1 for result in results if result.is_valid)
        total_count = len(results)
        
        print(f"Valid entries: {valid_count}/{total_count}")
        
        for i, result in enumerate(results, 1):
            if not result.is_valid:
                print(f"Entry {i} validation errors:")
                for error in result.errors:
                    print(f"  - {error}")
            else:
                print(f"Entry {i}: ✓ Valid")
                
    except Exception as e:
        print(f"Error processing file: {e}")


def main():
    """Main function to validate all example files."""
    examples_dir = Path(__file__).parent
    
    # Validate device files
    device_json = examples_dir / "sample_devices.json"
    device_csv = examples_dir / "sample_devices.csv"
    
    if device_json.exists():
        validate_file(device_json, "device")
    
    if device_csv.exists():
        validate_file(device_csv, "device")
    
    # Validate gateway files
    gateway_json = examples_dir / "sample_gateways.json"
    
    if gateway_json.exists():
        validate_file(gateway_json, "gateway")


if __name__ == "__main__":
    main()