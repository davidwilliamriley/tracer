"""
test_validation.py

Tests for property value type validation and required field enforcement.

Covers:
  - validate_property_value() directly (unit tests)
  - Type validation through the bulk write endpoint (integration tests)
  - Type validation through the individual upsert endpoint
  - Required field enforcement through bulk write
  - Edge cases: None values, whitespace, boundary values
"""
import pytest
from services.validation_service import validate_property_value
from exceptions import ValidationError


# ---------------------------------------------------------------------------
# Unit tests for validate_property_value()
# These test the validation logic directly without going through HTTP
# ---------------------------------------------------------------------------

class TestValidatePropertyValueString:
    def test_any_string_is_valid(self):
        validate_property_value("hello", "string")

    def test_empty_string_is_valid(self):
        validate_property_value("", "string")

    def test_none_is_valid(self):
        validate_property_value(None, "string")


class TestValidatePropertyValueInteger:
    def test_valid_positive_integer(self):
        validate_property_value("42", "integer")

    def test_valid_negative_integer(self):
        validate_property_value("-10", "integer")

    def test_valid_zero(self):
        validate_property_value("0", "integer")

    def test_none_is_valid(self):
        validate_property_value(None, "integer")

    def test_float_string_is_invalid(self):
        with pytest.raises(ValidationError):
            validate_property_value("3.14", "integer")

    def test_text_is_invalid(self):
        with pytest.raises(ValidationError):
            validate_property_value("abc", "integer")

    def test_empty_string_is_invalid(self):
        with pytest.raises(ValidationError):
            validate_property_value("", "integer")

    def test_error_includes_field_name(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_property_value("abc", "integer", field_name="MY_FIELD")
        assert "MY_FIELD" in exc_info.value.message


class TestValidatePropertyValueFloat:
    def test_valid_float(self):
        validate_property_value("3.14", "float")

    def test_integer_string_is_valid_float(self):
        validate_property_value("42", "float")

    def test_negative_float(self):
        validate_property_value("-1.5", "float")

    def test_none_is_valid(self):
        validate_property_value(None, "float")

    def test_text_is_invalid(self):
        with pytest.raises(ValidationError):
            validate_property_value("not-a-number", "float")


class TestValidatePropertyValueBoolean:
    def test_true_lowercase(self):
        validate_property_value("true", "boolean")

    def test_false_lowercase(self):
        validate_property_value("false", "boolean")

    def test_one_is_valid(self):
        validate_property_value("1", "boolean")

    def test_zero_is_valid(self):
        validate_property_value("0", "boolean")

    def test_yes_is_valid(self):
        validate_property_value("yes", "boolean")

    def test_no_is_valid(self):
        validate_property_value("no", "boolean")

    def test_none_is_valid(self):
        validate_property_value(None, "boolean")

    def test_arbitrary_string_is_invalid(self):
        with pytest.raises(ValidationError):
            validate_property_value("maybe", "boolean")

    def test_error_message_shows_valid_options(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_property_value("maybe", "boolean", field_name="IS_ACTIVE")
        assert "IS_ACTIVE" in exc_info.value.message


class TestValidatePropertyValueDate:
    def test_valid_iso_date(self):
        validate_property_value("2024-01-15", "date")

    def test_none_is_valid(self):
        validate_property_value(None, "date")

    def test_invalid_date_format(self):
        with pytest.raises(ValidationError):
            validate_property_value("15/01/2024", "date")

    def test_invalid_date_text(self):
        with pytest.raises(ValidationError):
            validate_property_value("not-a-date", "date")

    def test_invalid_date_month(self):
        with pytest.raises(ValidationError):
            validate_property_value("2024-13-01", "date")

    def test_error_shows_expected_format(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_property_value("01/01/2024", "date", field_name="START_DATE")
        assert "YYYY-MM-DD" in exc_info.value.message


# ---------------------------------------------------------------------------
# Integration tests — validation through the bulk write HTTP endpoint
# ---------------------------------------------------------------------------

class TestBulkWriteTypeValidation:

    def test_valid_integer_value_accepted(self, client, seeded):
        """Set up an integer property and write a valid value."""
        # Create an integer property definition
        p_int = client.post("/node-property-definitions/", json={
            "node_property_definition_identifier": "SEVERITY_SCORE",
            "node_property_definition_name": "Severity Score",
            "node_property_definition_type": "integer",
        }).json()

        # Assign to the node type
        client.post("/node-type-property-assignments/", json={
            "node_type_id_fk": seeded["node_type"]["id"],
            "node_property_definition_id_fk": p_int["id"],
            "is_required": False,
            "sort_order": 10,
        })

        node_id = seeded["node1"]["id"]
        r = client.post(f"/nodes/{node_id}/properties", json={
            "properties": [
                {"definition_id": seeded["prop_id"]["id"], "value": "HAZ-001"},
                {"definition_id": p_int["id"], "value": "42"},
            ],
        })
        assert r.status_code == 200

    def test_invalid_integer_value_rejected(self, client, seeded):
        p_int = client.post("/node-property-definitions/", json={
            "node_property_definition_identifier": "SCORE",
            "node_property_definition_name": "Score",
            "node_property_definition_type": "integer",
        }).json()
        client.post("/node-type-property-assignments/", json={
            "node_type_id_fk": seeded["node_type"]["id"],
            "node_property_definition_id_fk": p_int["id"],
            "is_required": False,
            "sort_order": 11,
        })

        node_id = seeded["node1"]["id"]
        r = client.post(f"/nodes/{node_id}/properties", json={
            "properties": [
                {"definition_id": seeded["prop_id"]["id"], "value": "HAZ-001"},
                {"definition_id": p_int["id"], "value": "not-a-number"},
            ],
        })
        assert r.status_code == 422

    def test_invalid_value_returns_validation_error(self, client, seeded):
        p_int = client.post("/node-property-definitions/", json={
            "node_property_definition_identifier": "COUNT",
            "node_property_definition_name": "Count",
            "node_property_definition_type": "integer",
        }).json()
        client.post("/node-type-property-assignments/", json={
            "node_type_id_fk": seeded["node_type"]["id"],
            "node_property_definition_id_fk": p_int["id"],
            "is_required": False,
            "sort_order": 12,
        })

        node_id = seeded["node1"]["id"]
        r = client.post(f"/nodes/{node_id}/properties", json={
            "properties": [
                {"definition_id": seeded["prop_id"]["id"], "value": "HAZ-001"},
                {"definition_id": p_int["id"], "value": "abc"},
            ],
        })
        body = r.json()
        assert body["error"] == "ValidationError"
        assert "COUNT" in body["message"]

    def test_null_value_always_accepted(self, client, seeded):
        """None/null values should always pass type validation."""
        p_int = client.post("/node-property-definitions/", json={
            "node_property_definition_identifier": "OPT_INT",
            "node_property_definition_name": "Optional Int",
            "node_property_definition_type": "integer",
        }).json()
        client.post("/node-type-property-assignments/", json={
            "node_type_id_fk": seeded["node_type"]["id"],
            "node_property_definition_id_fk": p_int["id"],
            "is_required": False,
            "sort_order": 13,
        })

        node_id = seeded["node1"]["id"]
        r = client.post(f"/nodes/{node_id}/properties", json={
            "properties": [
                {"definition_id": seeded["prop_id"]["id"], "value": "HAZ-001"},
                {"definition_id": p_int["id"], "value": None},
            ],
        })
        assert r.status_code == 200

    def test_invalid_date_format_rejected(self, client, seeded):
        p_date = client.post("/node-property-definitions/", json={
            "node_property_definition_identifier": "RAISED_DATE",
            "node_property_definition_name": "Raised Date",
            "node_property_definition_type": "date",
        }).json()
        client.post("/node-type-property-assignments/", json={
            "node_type_id_fk": seeded["node_type"]["id"],
            "node_property_definition_id_fk": p_date["id"],
            "is_required": False,
            "sort_order": 14,
        })

        node_id = seeded["node1"]["id"]
        r = client.post(f"/nodes/{node_id}/properties", json={
            "properties": [
                {"definition_id": seeded["prop_id"]["id"], "value": "HAZ-001"},
                {"definition_id": p_date["id"], "value": "15/01/2024"},
            ],
        })
        assert r.status_code == 422

    def test_no_writes_occur_if_any_value_invalid(self, client, seeded):
        """All-or-nothing: if one value fails, nothing should be written."""
        p_int = client.post("/node-property-definitions/", json={
            "node_property_definition_identifier": "BATCH_INT",
            "node_property_definition_name": "Batch Int",
            "node_property_definition_type": "integer",
        }).json()
        client.post("/node-type-property-assignments/", json={
            "node_type_id_fk": seeded["node_type"]["id"],
            "node_property_definition_id_fk": p_int["id"],
            "is_required": False,
            "sort_order": 15,
        })

        node_id = seeded["node2"]["id"]  # node2 has no values yet
        r = client.post(f"/nodes/{node_id}/properties", json={
            "properties": [
                {"definition_id": seeded["prop_id"]["id"], "value": "GOOD-VALUE"},
                {"definition_id": p_int["id"], "value": "NOT-AN-INT"},
            ],
        })
        assert r.status_code == 422

        # Verify nothing was written
        r2 = client.get(f"/nodes/{node_id}/full")
        values = [p["value"] for p in r2.json()["properties"] if p["value"] is not None]
        assert values == []


# ---------------------------------------------------------------------------
# Integration tests — required field enforcement
# ---------------------------------------------------------------------------

class TestRequiredFieldEnforcement:

    def test_required_field_provided_succeeds(self, client, seeded):
        """HAZ_ID is required — providing it should succeed."""
        node_id = seeded["node2"]["id"]
        r = client.post(f"/nodes/{node_id}/properties", json={
            "properties": [
                {"definition_id": seeded["prop_id"]["id"], "value": "HAZ-002"},
            ],
        })
        assert r.status_code == 200

    def test_missing_required_field_rejected(self, client, seeded):
        """Bulk write without the required HAZ_ID field should fail."""
        node_id = seeded["node2"]["id"]
        r = client.post(f"/nodes/{node_id}/properties", json={
            "properties": [
                # Only providing SEVERITY, not the required HAZ_ID
                {"definition_id": seeded["prop_severity"]["id"], "value": "Low"},
            ],
        })
        assert r.status_code == 422

    def test_missing_required_field_error_names_field(self, client, seeded):
        node_id = seeded["node2"]["id"]
        r = client.post(f"/nodes/{node_id}/properties", json={
            "properties": [
                {"definition_id": seeded["prop_severity"]["id"], "value": "Low"},
            ],
        })
        body = r.json()
        assert body["error"] == "ValidationError"
        assert "HAZ_ID" in body["message"]

    def test_null_value_for_required_field_rejected(self, client, seeded):
        """Explicitly sending null for a required field should also fail."""
        node_id = seeded["node2"]["id"]
        r = client.post(f"/nodes/{node_id}/properties", json={
            "properties": [
                {"definition_id": seeded["prop_id"]["id"], "value": None},
            ],
        })
        assert r.status_code == 422

    def test_optional_field_can_be_omitted(self, client, seeded):
        """SEVERITY is not required — omitting it should be fine."""
        node_id = seeded["node2"]["id"]
        r = client.post(f"/nodes/{node_id}/properties", json={
            "properties": [
                {"definition_id": seeded["prop_id"]["id"], "value": "HAZ-002"},
                # SEVERITY deliberately omitted
            ],
        })
        assert r.status_code == 200

    def test_optional_field_can_be_null(self, client, seeded):
        """SEVERITY is not required — sending null should be fine."""
        node_id = seeded["node2"]["id"]
        r = client.post(f"/nodes/{node_id}/properties", json={
            "properties": [
                {"definition_id": seeded["prop_id"]["id"], "value": "HAZ-002"},
                {"definition_id": seeded["prop_severity"]["id"], "value": None},
            ],
        })
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Integration tests — individual property value endpoint
# ---------------------------------------------------------------------------

class TestIndividualUpsertValidation:

    def test_valid_value_accepted_via_upsert(self, client, seeded):
        r = client.post("/node-property-values/", json={
            "node_id_fk": seeded["node1"]["id"],
            "node_property_definition_id_fk": seeded["prop_id"]["id"],
            "node_property_value": "HAZ-001-UPDATED",
        })
        assert r.status_code == 201

    def test_type_mismatch_rejected_via_upsert(self, client, seeded):
        """Create an integer definition, then try to write a non-integer via upsert."""
        p_int = client.post("/node-property-definitions/", json={
            "node_property_definition_identifier": "UPSERT_INT",
            "node_property_definition_name": "Upsert Int",
            "node_property_definition_type": "integer",
        }).json()
        client.post("/node-type-property-assignments/", json={
            "node_type_id_fk": seeded["node_type"]["id"],
            "node_property_definition_id_fk": p_int["id"],
            "is_required": False,
            "sort_order": 20,
        })

        r = client.post("/node-property-values/", json={
            "node_id_fk": seeded["node1"]["id"],
            "node_property_definition_id_fk": p_int["id"],
            "node_property_value": "not-an-integer",
        })
        assert r.status_code == 422
        assert r.json()["error"] == "ValidationError"
