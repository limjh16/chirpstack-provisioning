"""Tests for schema utilities."""

import json
from pathlib import Path

import pytest

from chirpstack_provisioning.schema import load_schema


class TestLoadSchema:
    """Tests for load_schema function."""

    def test_load_valid_schema(self, tmp_path):
        """Test loading a valid JSON schema."""
        schema_data = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }
        schema_path = tmp_path / "test_schema.json"
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema_data, f)

        result = load_schema(schema_path)
        assert isinstance(result, dict)
        assert result["type"] == "object"
        assert "properties" in result

    def test_load_schema_nonexistent_file(self):
        """Test loading a schema file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_schema("/nonexistent/schema.json")

    def test_load_schema_invalid_json(self, tmp_path):
        """Test loading a file with invalid JSON."""
        schema_path = tmp_path / "invalid_schema.json"
        with open(schema_path, "w", encoding="utf-8") as f:
            f.write("{ not valid json }")

        with pytest.raises(json.JSONDecodeError):
            load_schema(schema_path)

    def test_load_schema_with_string_path(self, tmp_path):
        """Test loading schema with string path instead of Path object."""
        schema_data = {"type": "string"}
        schema_path = tmp_path / "test_schema.json"
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema_data, f)

        # Pass as string instead of Path
        result = load_schema(str(schema_path))
        assert isinstance(result, dict)
        assert result["type"] == "string"

    def test_load_schema_with_path_object(self, tmp_path):
        """Test loading schema with Path object."""
        schema_data = {"type": "number"}
        schema_path = tmp_path / "test_schema.json"
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema_data, f)

        # Pass as Path object
        result = load_schema(Path(schema_path))
        assert isinstance(result, dict)
        assert result["type"] == "number"

    def test_load_empty_schema(self, tmp_path):
        """Test loading an empty schema file."""
        schema_path = tmp_path / "empty_schema.json"
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump({}, f)

        result = load_schema(schema_path)
        assert isinstance(result, dict)
        assert result == {}
