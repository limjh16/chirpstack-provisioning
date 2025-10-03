"""Setup file ingestion for ChirpStack provisioning.

This module handles parsing and extracting data from setup files that define
the hierarchical structure of tenants, applications, gateways, device profiles, etc.
"""

import json
from pathlib import Path

import jsonschema


class SetupFileIngestion:
    """Handles ingestion and decomposition of ChirpStack setup files.

    This class loads a setup file, validates it, and decomposes the hierarchical
    structure into individual entities ready for API provisioning.
    """

    def __init__(self, file_path: str | Path, schema_path: str | Path):
        """Initialize the setup file ingestion.

        Args:
            file_path: Path to the setup JSON file
            schema_path: Path to the setup.schema.json file

        Raises:
            FileNotFoundError: If the file does not exist
            json.JSONDecodeError: If the file is not valid JSON
            jsonschema.ValidationError: If the data doesn't match the schema
        """
        self._file_path = Path(file_path)
        self._schema_path = Path(schema_path)
        self._setup_data = None
        self._tenants = None
        self._users = None
        self._device_profile_templates = None
        self._gateways = None
        self._applications = None
        self._device_profiles = None

        # Load and process data on initialization
        self._load_and_validate()
        self._extract_and_decompose()

    def _load_and_validate(self) -> None:
        """Load setup file and validate against schema."""
        with open(self._file_path, "r", encoding="utf-8") as f:
            self._setup_data = json.load(f)
        self._validate_setup_data()

    def _validate_setup_data(self) -> None:
        """Validate setup data against the setup schema."""
        schema_path = self._schema_path.resolve()
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Create a resolver to handle $ref references relative to the schema file
        resolver = jsonschema.RefResolver(
            base_uri=schema_path.as_uri(),
            referrer=schema,
        )

        validator = jsonschema.Draft202012Validator(schema, resolver=resolver)
        validator.validate(self._setup_data)

    def _extract_and_decompose(self) -> None:
        """Extract top-level entities and decompose nested structures."""
        # Extract top-level entities
        raw_tenants = self._setup_data.get("tenants", [])
        self._users = self._setup_data.get("users", [])
        self._device_profile_templates = self._setup_data.get(
            "device_profile_templates", []
        )

        # Decompose tenants in a single pass
        (
            self._tenants,
            self._gateways,
            self._applications,
            self._device_profiles,
        ) = self._decompose_tenants(raw_tenants)

    @staticmethod
    def _extract_child_entities(
        tenant: dict, child_key: str, tenant_id: str
    ) -> list[dict]:
        """Extract child entities from a tenant and add tenant_id reference.

        Args:
            tenant: The tenant object
            child_key: Key of the child entities list (e.g., 'gateways', 'applications')
            tenant_id: The tenant ID to add to each child entity

        Returns:
            List of child entities with tenant_id added
        """
        entities = []
        for entity in tenant.get(child_key, []):
            entity_copy = entity.copy()
            entity_copy["tenant_id"] = tenant_id
            entities.append(entity_copy)
        return entities

    def _decompose_tenants(
        self, tenants: list[dict]
    ) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
        """Decompose tenants into clean tenant objects and child entities.

        This function performs a single pass through the tenants list to extract
        all child entities (gateways, applications, device_profiles) and create
        clean tenant objects without nested children.

        Args:
            tenants: List of tenant objects

        Returns:
            Tuple containing:
            - List of clean tenant objects (without nested children)
            - List of gateway objects with tenant_id added
            - List of application objects with tenant_id added
            - List of device profile objects with tenant_id added
        """
        clean_tenants = []
        gateways = []
        applications = []
        device_profiles = []

        for tenant in tenants:
            tenant_id = tenant.get("id")

            # Extract and decompose child entities
            gateways.extend(self._extract_child_entities(tenant, "gateways", tenant_id))
            applications.extend(
                self._extract_child_entities(tenant, "applications", tenant_id)
            )
            device_profiles.extend(
                self._extract_child_entities(tenant, "device_profiles", tenant_id)
            )

            # Create clean tenant without nested children
            tenant_copy = tenant.copy()
            tenant_copy.pop("gateways", None)
            tenant_copy.pop("applications", None)
            tenant_copy.pop("device_profiles", None)
            clean_tenants.append(tenant_copy)

        return clean_tenants, gateways, applications, device_profiles

    @property
    def tenants(self) -> list[dict]:
        """Get the list of clean tenant objects without nested children."""
        return self._tenants

    @tenants.setter
    def tenants(self, value: list[dict]) -> None:
        """Set the list of tenant objects."""
        self._tenants = value

    @property
    def users(self) -> list[dict]:
        """Get the list of global user objects."""
        return self._users

    @users.setter
    def users(self, value: list[dict]) -> None:
        """Set the list of user objects."""
        self._users = value

    @property
    def device_profile_templates(self) -> list[dict]:
        """Get the list of device profile template objects."""
        return self._device_profile_templates

    @device_profile_templates.setter
    def device_profile_templates(self, value: list[dict]) -> None:
        """Set the list of device profile template objects."""
        self._device_profile_templates = value

    @property
    def gateways(self) -> list[dict]:
        """Get the list of gateway objects with tenant_id references."""
        return self._gateways

    @gateways.setter
    def gateways(self, value: list[dict]) -> None:
        """Set the list of gateway objects."""
        self._gateways = value

    @property
    def applications(self) -> list[dict]:
        """Get the list of application objects with tenant_id references."""
        return self._applications

    @applications.setter
    def applications(self, value: list[dict]) -> None:
        """Set the list of application objects."""
        self._applications = value

    @property
    def device_profiles(self) -> list[dict]:
        """Get the list of device profile objects with tenant_id references."""
        return self._device_profiles

    @device_profiles.setter
    def device_profiles(self, value: list[dict]) -> None:
        """Set the list of device profile objects."""
        self._device_profiles = value

    def to_dict(self) -> dict[str, list[dict]]:
        """Convert the ingested and decomposed data to a dictionary.

        Returns:
            Dictionary containing all decomposed entities
        """
        return {
            "tenants": self.tenants,
            "users": self.users,
            "device_profile_templates": self.device_profile_templates,
            "gateways": self.gateways,
            "applications": self.applications,
            "device_profiles": self.device_profiles,
        }
