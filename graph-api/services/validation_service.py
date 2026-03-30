"""
validation_service.py

Two responsibilities:
  1. Type validation  — verify a string value is castable to the declared
                        property type before writing it to the database.
  2. Required fields  — verify all is_required properties for a node/edge
                        type have values provided before creating the record.

Why here and not in the router or crud layer?
  - Routers should stay thin (HTTP concerns only)
  - Crud should stay close to single-table operations
  - This logic spans NodeType → assignments → definitions → values,
    which is exactly what the services layer is for
"""

from datetime import date as date_type
from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from exceptions import ValidationError
from models.node_type_property_assignment import NodeTypePropertyAssignment
from models.edge_type_property_assignment import EdgeTypePropertyAssignment
from models.node_property_definition import NodePropertyDefinition
from models.edge_property_definition import EdgePropertyDefinition


# ---------------------------------------------------------------------------
# Valid property types — single source of truth
# Also exported so routers can reference this set for definition CRUD
# ---------------------------------------------------------------------------

VALID_PROPERTY_TYPES = {"string", "integer", "float", "boolean", "date"}

BOOLEAN_TRUE_VALUES = {"true", "1", "yes"}
BOOLEAN_FALSE_VALUES = {"false", "0", "no"}


# ---------------------------------------------------------------------------
# Type validation — single value
# ---------------------------------------------------------------------------

def validate_property_value(
    value: Optional[str],
    declared_type: str,
    field_name: str = "value",
) -> None:
    """
    Validate that a string value is compatible with its declared type.
    Raises ValidationError if the value cannot be interpreted as that type.

    All values are stored as strings — this validates the string is a valid
    representation of the declared type, not that the Python type matches.

    Args:
        value:         The string value to validate. None is always valid
                       (represents an unset property).
        declared_type: One of "string" | "integer" | "float" | "boolean" | "date"
        field_name:    Used in the error message to identify the failing field.

    Examples:
        validate_property_value("42", "integer")     # passes
        validate_property_value("3.14", "float")     # passes
        validate_property_value("true", "boolean")   # passes
        validate_property_value("2024-01-15", "date")# passes
        validate_property_value("abc", "integer")    # raises ValidationError
        validate_property_value(None, "integer")     # passes (unset is ok)
    """
    if value is None:
        return  # None means unset — always valid

    if declared_type == "string":
        return  # any string is valid

    if declared_type == "integer":
        try:
            int(value)
        except (ValueError, TypeError):
            raise ValidationError(
                f"'{value}' is not a valid integer for field '{field_name}'",
                field=field_name,
            )

    elif declared_type == "float":
        try:
            float(value)
        except (ValueError, TypeError):
            raise ValidationError(
                f"'{value}' is not a valid float for field '{field_name}'",
                field=field_name,
            )

    elif declared_type == "boolean":
        normalised = value.strip().lower()
        if normalised not in BOOLEAN_TRUE_VALUES | BOOLEAN_FALSE_VALUES:
            raise ValidationError(
                f"'{value}' is not a valid boolean for field '{field_name}'. "
                f"Use one of: true, false, 1, 0, yes, no",
                field=field_name,
            )

    elif declared_type == "date":
        try:
            date_type.fromisoformat(value)
        except (ValueError, TypeError):
            raise ValidationError(
                f"'{value}' is not a valid date for field '{field_name}'. "
                f"Use ISO format: YYYY-MM-DD",
                field=field_name,
            )

    elif declared_type not in VALID_PROPERTY_TYPES:
        raise ValidationError(
            f"Unknown property type '{declared_type}'. "
            f"Must be one of: {sorted(VALID_PROPERTY_TYPES)}",
            field=field_name,
        )


# ---------------------------------------------------------------------------
# Bulk validation — validate a dict of {definition_id: value} pairs
# ---------------------------------------------------------------------------

def validate_node_property_values(
    db: Session,
    node_type_id: UUID,
    values: Dict[str, Optional[str]],
) -> None:
    """
    Validate a dict of {definition_id_str: value} pairs against the
    declared types for a NodeType's property definitions.

    Collects ALL type errors before raising, so the caller gets a
    complete list of problems rather than failing on the first one.

    Args:
        db:           Database session
        node_type_id: The NodeType whose property definitions to check against
        values:       Dict mapping definition ID (as string) to value string
    """
    if not values:
        return

    errors = []

    # Load all definitions for this node type in one query
    assignments = (
        db.query(NodeTypePropertyAssignment)
        .filter(NodeTypePropertyAssignment.node_type_id_fk == str(node_type_id))
        .all()
    )

    definition_map: Dict[str, NodePropertyDefinition] = {}
    for assignment in assignments:
        defn = db.query(NodePropertyDefinition).filter(
            NodePropertyDefinition.id == assignment.node_property_definition_id_fk
        ).first()
        if defn:
            definition_map[str(defn.id)] = defn

    for definition_id_str, value in values.items():
        defn = definition_map.get(definition_id_str)
        if not defn:
            continue  # unknown definition — let the FK constraint handle it

        try:
            validate_property_value(
                value=value,
                declared_type=defn.node_property_definition_type,
                field_name=defn.node_property_definition_identifier,
            )
        except ValidationError as e:
            errors.append(e.message)

    if errors:
        raise ValidationError(
            f"Property validation failed: {'; '.join(errors)}"
        )


def validate_edge_property_values(
    db: Session,
    edge_type_id: UUID,
    values: Dict[str, Optional[str]],
) -> None:
    """
    Same as validate_node_property_values but for EdgeType properties.
    """
    if not values:
        return

    errors = []

    assignments = (
        db.query(EdgeTypePropertyAssignment)
        .filter(EdgeTypePropertyAssignment.edge_type_id_fk == str(edge_type_id))
        .all()
    )

    definition_map: Dict[str, EdgePropertyDefinition] = {}
    for assignment in assignments:
        defn = db.query(EdgePropertyDefinition).filter(
            EdgePropertyDefinition.id == assignment.edge_property_definition_id_fk
        ).first()
        if defn:
            definition_map[str(defn.id)] = defn

    for definition_id_str, value in values.items():
        defn = definition_map.get(definition_id_str)
        if not defn:
            continue

        try:
            validate_property_value(
                value=value,
                declared_type=defn.edge_property_definition_type,
                field_name=defn.edge_property_definition_identifier,
            )
        except ValidationError as e:
            errors.append(e.message)

    if errors:
        raise ValidationError(
            f"Property validation failed: {'; '.join(errors)}"
        )


# ---------------------------------------------------------------------------
# Required field enforcement
# ---------------------------------------------------------------------------

def check_required_node_properties(
    db: Session,
    node_type_id: UUID,
    provided_values: Dict[str, Optional[str]],
) -> None:
    """
    Check that all is_required properties for a NodeType have values provided.
    Raises ValidationError listing all missing required fields.

    Args:
        db:               Database session
        node_type_id:     The NodeType to check requirements for
        provided_values:  Dict mapping definition ID (str) to value — the
                          values the caller intends to write
    """
    assignments = (
        db.query(NodeTypePropertyAssignment)
        .filter(
            NodeTypePropertyAssignment.node_type_id_fk == str(node_type_id),
            NodeTypePropertyAssignment.is_required == True,  # noqa: E712
        )
        .all()
    )

    missing = []
    for assignment in assignments:
        defn = db.query(NodePropertyDefinition).filter(
            NodePropertyDefinition.id == assignment.node_property_definition_id_fk
        ).first()
        if not defn:
            continue

        value = provided_values.get(str(defn.id))
        if value is None or (isinstance(value, str) and value.strip() == ""):
            missing.append(defn.node_property_definition_identifier)

    if missing:
        raise ValidationError(
            f"Missing required properties: {', '.join(missing)}"
        )


def check_required_edge_properties(
    db: Session,
    edge_type_id: UUID,
    provided_values: Dict[str, Optional[str]],
) -> None:
    """
    Same as check_required_node_properties but for EdgeType properties.
    """
    assignments = (
        db.query(EdgeTypePropertyAssignment)
        .filter(
            EdgeTypePropertyAssignment.edge_type_id_fk == str(edge_type_id),
            EdgeTypePropertyAssignment.is_required == True,  # noqa: E712
        )
        .all()
    )

    missing = []
    for assignment in assignments:
        defn = db.query(EdgePropertyDefinition).filter(
            EdgePropertyDefinition.id == assignment.edge_property_definition_id_fk
        ).first()
        if not defn:
            continue

        value = provided_values.get(str(defn.id))
        if value is None or (isinstance(value, str) and value.strip() == ""):
            missing.append(defn.edge_property_definition_identifier)

    if missing:
        raise ValidationError(
            f"Missing required properties: {', '.join(missing)}"
        )
