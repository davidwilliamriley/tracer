"""
seed_data.py  City Cross Station dataset.

Loads a representative built environment safety case dataset into a running
Tracer instance via the REST API. Covers all three schema layers:

  DESCRIPTION LAYER (Uniclass 2015)
    Complex  Entity  Space / Element / System  Product / Activity / Role

  ANALYSIS LAYER (STPA + Requirements)
    Loss  Hazard  UCA  Control Action  Controller (Uniclass node)
    UCA  Loss Scenario
    Hazard  Control Constraint  Requirement  Uniclass node

  ARGUMENT LAYER (GSN / ISO 15026-2)
    Goal  Strategy  Goal / Solution  Evidence
    Goal / Strategy  Context / Assumption

Domain: City Cross Station  metro station with platform screen doors,
        automated train operation, staffed concourse.

Standards basis: STPA (hazard analysis), GSN / ISO 15026-2 (argument),
                 Uniclass 2015 (description), EN 50129 (SIL integrity)

Usage:
    # Start the Tracer API first:
    cd graph_api && uvicorn main:app --reload

    # In another terminal:
    python seed_data.py

    # Wipe existing data first:
    python seed_data.py --clean

    # Optional: target a different host
    python seed_data.py --base-url http://yourserver:8000

Configuration:
    BASE_URL    Tracer API base URL (default: http://localhost:8000)
    USERNAME    admin username       (default: admin)
    PASSWORD    admin password       (default: change-me)
"""

import sys
import argparse
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "change-me"


# ---------------------------------------------------------------------------
# API client  identical to original seed_data.py
# ---------------------------------------------------------------------------


class TracerClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip("/")
        self.token = None
        self._login(username, password)

    def _login(self, username, password):
        r = requests.post(
            f"{self.base_url}/auth/token",
            data={"username": username, "password": password},
        )
        if r.status_code != 200:
            print(f"ERROR: Login failed  {r.status_code} {r.text}")
            sys.exit(1)
        self.token = r.json()["access_token"]
        print(f"  [OK] Logged in as {username}")

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def post(self, path, payload):
        r = requests.post(
            f"{self.base_url}{path}",
            json=payload,
            headers=self._headers(),
        )
        if r.status_code not in (200, 201):
            print(f"  ERROR POST {path}: {r.status_code} {r.text}")
            sys.exit(1)
        return r.json()

    def delete(self, path):
        r = requests.delete(
            f"{self.base_url}{path}",
            headers=self._headers(),
        )
        return r.status_code in (200, 204, 404)

    def get_all(self, path):
        r = requests.get(
            f"{self.base_url}{path}?limit=500",
            headers=self._headers(),
        )
        if r.status_code != 200:
            return []
        data = r.json()
        return data.get("items", data) if isinstance(data, dict) else data

    def put(self, path, payload):
        r = requests.put(
            f"{self.base_url}{path}",
            json=payload,
            headers=self._headers(),
        )
        if r.status_code != 200:
            print(f"  ERROR PUT {path}: {r.status_code} {r.text}")
            sys.exit(1)
        return r.json()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def create_node_type(client, identifier, name, description):
    return client.post(
        "/node-types/",
        {
            "node_type_identifier": identifier,
            "node_type_name": name,
            "node_type_description": description,
            "created_by": "seed",
        },
    )


def create_edge_type(client, identifier, name, description):
    return client.post(
        "/edge-types/",
        {
            "edge_type_identifier": identifier,
            "edge_type_name": name,
            "edge_type_description": description,
            "created_by": "seed",
        },
    )


def create_prop_def(
    client, identifier, name, prop_type, description="", default_value=None
):
    payload = {
        "node_property_definition_identifier": identifier,
        "node_property_definition_name": name,
        "node_property_definition_type": prop_type,
        "node_property_definition_description": description,
        "created_by": "seed",
    }
    if default_value is not None:
        payload["node_property_definition_default_value"] = default_value
    return client.post("/node-property-definitions/", payload)


def assign_prop(
    client, node_type_id, prop_def_id, is_required, sort_order, default_value=None
):
    payload = {
        "node_type_id_fk": node_type_id,
        "node_property_definition_id_fk": prop_def_id,
        "is_required": is_required,
        "sort_order": sort_order,
        "created_by": "seed",
    }
    if default_value is not None:
        payload["default_value"] = default_value
    return client.post("/node-type-property-assignments/", payload)


def create_node(client, node_type_id, identifier, name, created_by="seed"):
    return client.post(
        "/nodes/",
        {
            "node_type_id_fk": node_type_id,
            "node_identifier": identifier,
            "node_name": name,
            "created_by": created_by,
        },
    )


def set_properties(client, node_id, prop_values: dict):
    """prop_values: {definition_id: value_string}"""
    properties = [
        {"definition_id": def_id, "value": str(value)}
        for def_id, value in prop_values.items()
    ]
    return client.post(
        f"/nodes/{node_id}/properties",
        {
            "properties": properties,
            "modified_by": "seed",
        },
    )


def create_edge(client, edge_type_id, identifier, name, source_id, target_id):
    return client.post(
        "/edges/",
        {
            "edge_type_id_fk": edge_type_id,
            "edge_identifier": identifier,
            "edge_name": name,
            "source_node_id_fk": source_id,
            "target_node_id_fk": target_id,
            "created_by": "seed",
        },
    )


# ---------------------------------------------------------------------------
# Clean
# ---------------------------------------------------------------------------


def clean(client):
    """Remove all existing data in dependency order."""
    print("\n-- Cleaning existing data")

    edges = client.get_all("/edges/")
    for e in edges:
        client.delete(f"/edges/{e['id']}")
    print(f"  [OK] {len(edges)} edges removed")

    nodes = client.get_all("/nodes/")
    for n in nodes:
        client.delete(f"/nodes/{n['id']}")
    print(f"  [OK] {len(nodes)} nodes removed")

    assignments = client.get_all("/node-type-property-assignments/")
    for a in assignments:
        client.delete(f"/node-type-property-assignments/{a['id']}")
    print(f"  [OK] {len(assignments)} property assignments removed")

    prop_defs = client.get_all("/node-property-definitions/")
    for p in prop_defs:
        client.delete(f"/node-property-definitions/{p['id']}")
    print(f"  [OK] {len(prop_defs)} property definitions removed")

    node_types = client.get_all("/node-types/")
    for nt in node_types:
        client.delete(f"/node-types/{nt['id']}")
    print(f"  [OK] {len(node_types)} node types removed")

    edge_types = client.get_all("/edge-types/")
    for et in edge_types:
        client.delete(f"/edge-types/{et['id']}")
    print(f"  [OK] {len(edge_types)} edge types removed")


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------


def seed(client):

    # -----------------------------------------------------------------------
    # 1. NODE TYPES
    # -----------------------------------------------------------------------
    print("\n-- Creating node types")

    nt = {}

    # Description layer  Uniclass 2015
    nt["COMPLEX"] = create_node_type(
        client,
        "COMPLEX",
        "Complex",
        "Uniclass Co  Networks, campuses, whole systems. Top-level scoping node.",
    )
    nt["ENTITY"] = create_node_type(
        client,
        "ENTITY",
        "Entity",
        "Uniclass En  Discrete built assets: buildings, structures, infrastructure.",
    )
    nt["SPACE"] = create_node_type(
        client, "SPACE", "Space", "Uniclass Sp  Rooms, zones, volumes within entities."
    )
    nt["ELEMENT"] = create_node_type(
        client,
        "ELEMENT",
        "Element",
        "Uniclass EF  Functional parts of entities: facades, roofs, structures.",
    )
    nt["SYSTEM"] = create_node_type(
        client,
        "SYSTEM",
        "System",
        "Uniclass Ss  Technical systems. Can act as STPA controller or controlled process.",
    )
    nt["PRODUCT"] = create_node_type(
        client,
        "PRODUCT",
        "Product",
        "Uniclass Pr  Physical components and products within systems.",
    )
    nt["ACTIVITY"] = create_node_type(
        client,
        "ACTIVITY",
        "Activity",
        "Uniclass Ac  Operations, processes, and events.",
    )
    nt["ROLE"] = create_node_type(
        client,
        "ROLE",
        "Role",
        "Uniclass Ro  Organisations and individuals. Can act as STPA controller.",
    )

    # Analysis layer  STPA
    nt["LOSS"] = create_node_type(
        client,
        "LOSS",
        "Loss",
        "STPA  Top-level consequence to prevent. Not a system state  a consequence in the world.",
    )
    nt["HAZARD"] = create_node_type(
        client,
        "HAZARD",
        "Hazard",
        "STPA  System state or condition that, combined with worst-case environment, leads to a loss.",
    )
    nt["CONTROL_ACTION"] = create_node_type(
        client,
        "CONTROL_ACTION",
        "Control Action",
        "STPA  A control action between a controller and a controlled process. First-class node.",
    )
    nt["UNDESIRABLE_CONTROL_ACTION"] = create_node_type(
        client,
        "UNDESIRABLE_CONTROL_ACTION",
        "Undesirable Control Action",
        "STPA  A control action that is undesirable in a specific context. Typed by the four UCA types. Applies to any loss category  safety, security, financial, environmental, operational.",
    )
    nt["LOSS_SCENARIO"] = create_node_type(
        client,
        "LOSS_SCENARIO",
        "Loss Scenario",
        "STPA  Causal mechanism explaining how a UCA leads to a hazard.",
    )
    nt["CONTROL_CONSTRAINT"] = create_node_type(
        client,
        "CONTROL_CONSTRAINT",
        "Control Constraint",
        "STPA  Constraint on controller behaviour that prevents the unsafe control action.",
    )
    nt["REQUIREMENT"] = create_node_type(
        client,
        "REQUIREMENT",
        "Requirement",
        "Formally stated requirement derived from control constraints. Bridge between STPA analysis and design specification. Applies to any loss category  not limited to safety.",
    )

    # Argument layer  GSN / ISO 15026-2
    nt["GSN_GOAL"] = create_node_type(
        client,
        "GSN_GOAL",
        "GSN Goal",
        "GSN  A claim to be argued. Top-level or sub-goal.",
    )
    nt["GSN_STRATEGY"] = create_node_type(
        client,
        "GSN_STRATEGY",
        "GSN Strategy",
        "GSN  An argument pattern decomposing a goal into sub-goals or solutions.",
    )
    nt["GSN_SOLUTION"] = create_node_type(
        client,
        "GSN_SOLUTION",
        "GSN Solution",
        "GSN  A leaf node in the argument, pointing to evidence.",
    )
    nt["GSN_CONTEXT"] = create_node_type(
        client,
        "GSN_CONTEXT",
        "GSN Context",
        "GSN  Contextual information scoping a goal or strategy.",
    )
    nt["GSN_ASSUMPTION"] = create_node_type(
        client,
        "GSN_ASSUMPTION",
        "GSN Assumption",
        "GSN / ISO 15026-2  A claim taken as given without proof. Distinct from context.",
    )
    nt["EVIDENCE"] = create_node_type(
        client,
        "EVIDENCE",
        "Evidence",
        "Objective evidence supporting a GSN solution or verifying a safety requirement.",
    )

    print(f"  [OK] {len(nt)} node types created")

    # -----------------------------------------------------------------------
    # 2. EDGE TYPES
    # -----------------------------------------------------------------------
    print("\n-- Creating edge types")

    et = {}

    # Uniclass hierarchy
    et["CONTAINS"] = create_edge_type(
        client,
        "CONTAINS",
        "Contains",
        "Top-down hierarchy: ComplexEntity, EntitySpace/Element/System, SystemProduct. Canonical direction.",
    )
    et["PART_OF"] = create_edge_type(
        client,
        "PART_OF",
        "Part Of",
        "Reverse of CONTAINS. Bottom-up for SysML/UML practitioners.",
    )

    # STPA control structure
    et["CONTROLS"] = create_edge_type(
        client,
        "CONTROLS",
        "Controls",
        "A Uniclass node (System or Role) controls a Control Action.",
    )
    et["RECEIVES"] = create_edge_type(
        client,
        "RECEIVES",
        "Receives",
        "A Control Action is received by a Uniclass node (the controlled process).",
    )
    et["PROVIDES_FEEDBACK"] = create_edge_type(
        client,
        "PROVIDES_FEEDBACK",
        "Provides Feedback",
        "A controlled process provides feedback to a controller.",
    )
    et["BECOMES_UNSAFE_AS"] = create_edge_type(
        client,
        "BECOMES_UNSAFE_AS",
        "Becomes Unsafe As",
        "A Control Action becomes unsafe as an Undesirable Control Action in a specific context.",
    )
    et["LEADS_TO"] = create_edge_type(
        client,
        "LEADS_TO",
        "Leads To",
        "An Undesirable Control Action leads to a Hazard.",
    )
    et["EXPLAINED_BY"] = create_edge_type(
        client, "EXPLAINED_BY", "Explained By", "A UCA is explained by a Loss Scenario."
    )
    et["CAUSES"] = create_edge_type(
        client, "CAUSES", "Causes", "A Hazard causes a Loss."
    )
    et["MITIGATED_BY"] = create_edge_type(
        client,
        "MITIGATED_BY",
        "Mitigated By",
        "A Hazard is mitigated by a Control Constraint.",
    )
    et["MITIGATES"] = create_edge_type(
        client, "MITIGATES", "Mitigates", "Reverse of MITIGATED_BY."
    )
    et["INFORMS"] = create_edge_type(
        client, "INFORMS", "Informs", "A Control Constraint informs a Requirement."
    )
    et["ENABLES_HAZARD"] = create_edge_type(
        client,
        "ENABLES_HAZARD",
        "Enables Hazard",
        "An Activity creates the conditions for a Hazard.",
    )

    # Requirements
    et["ALLOCATED_TO"] = create_edge_type(
        client,
        "ALLOCATED_TO",
        "Allocated To",
        "A Requirement is allocated to a Uniclass node (System or Entity).",
    )
    et["IMPLEMENTS"] = create_edge_type(
        client, "IMPLEMENTS", "Implements", "Reverse of ALLOCATED_TO."
    )
    et["DERIVED_FROM"] = create_edge_type(
        client,
        "DERIVED_FROM",
        "Derived From",
        "A Requirement is derived from a parent Requirement.",
    )
    et["VERIFIED_BY"] = create_edge_type(
        client, "VERIFIED_BY", "Verified By", "A Requirement is verified by Evidence."
    )

    # GSN argument
    et["SUPPORTED_BY"] = create_edge_type(
        client,
        "SUPPORTED_BY",
        "Supported By",
        "Top-down GSN relationship. GoalStrategy, StrategyGoal/Solution.",
    )
    et["IN_CONTEXT_OF"] = create_edge_type(
        client,
        "IN_CONTEXT_OF",
        "In Context Of",
        "A Goal or Strategy is scoped by a Context node.",
    )
    et["IN_ASSUMPTION_OF"] = create_edge_type(
        client,
        "IN_ASSUMPTION_OF",
        "In Assumption Of",
        "A Goal or Strategy rests on an Assumption node.",
    )
    et["EVIDENCED_BY"] = create_edge_type(
        client,
        "EVIDENCED_BY",
        "Evidenced By",
        "A GSN Solution is evidenced by an Evidence node.",
    )

    # Cross-layer
    et["ADDRESSES"] = create_edge_type(
        client, "ADDRESSES", "Addresses", "A GSN Goal addresses a Hazard or Loss."
    )
    et["REFERENCES"] = create_edge_type(
        client,
        "REFERENCES",
        "References",
        "An Evidence item references a Uniclass node.",
    )

    print(f"  [OK] {len(et)} edge types created")

    # -----------------------------------------------------------------------
    # 3. PROPERTY DEFINITIONS
    # -----------------------------------------------------------------------
    print("\n-- Creating property definitions")

    pd = {}

    # Shared  all types
    pd["status"] = create_prop_def(
        client,
        "status",
        "Status",
        "string",
        "Lifecycle status: Draft | Proposed | Under Review | Approved | Baselined | Superseded | Withdrawn | Closed",
        "Draft",
    )
    pd["notes"] = create_prop_def(
        client, "notes", "Notes", "string", "Free text annotation"
    )

    # Shared  Uniclass types
    pd["uniclass_code"] = create_prop_def(
        client,
        "uniclass_code",
        "Uniclass Code",
        "string",
        "Uniclass 2015 classification code e.g. Ss_65_70_47",
    )
    pd["uniclass_name"] = create_prop_def(
        client,
        "uniclass_name",
        "Uniclass Name",
        "string",
        "Uniclass 2015 classification name for this code",
    )
    pd["description"] = create_prop_def(
        client, "description", "Description", "string", "Descriptive text for this node"
    )
    pd["location"] = create_prop_def(
        client, "location", "Location", "string", "Physical location reference"
    )

    # SYSTEM specific
    pd["sil_level"] = create_prop_def(
        client,
        "sil_level",
        "SIL Level",
        "string",
        "Safety Integrity Level assigned to this system: SIL 0 | SIL 1 | SIL 2 | SIL 3 | SIL 4",
    )

    # PRODUCT specific
    pd["manufacturer"] = create_prop_def(
        client, "manufacturer", "Manufacturer", "string", "Product manufacturer name"
    )
    pd["model_ref"] = create_prop_def(
        client,
        "model_ref",
        "Model Reference",
        "string",
        "Manufacturer model or part reference",
    )

    # ACTIVITY specific
    pd["activity_type"] = create_prop_def(
        client,
        "activity_type",
        "Activity Type",
        "string",
        "Normal | Degraded | Emergency | Maintenance",
    )

    # ROLE specific
    pd["role_type"] = create_prop_def(
        client,
        "role_type",
        "Role Type",
        "string",
        "Human | Organisation | Automated System",
    )

    # LOSS specific
    pd["loss_category"] = create_prop_def(
        client,
        "loss_category",
        "Loss Category",
        "string",
        "Life | Property | Environment | Mission | Reputation",
    )

    # HAZARD specific
    pd["system_state"] = create_prop_def(
        client,
        "system_state",
        "System State",
        "string",
        "The system state or condition that constitutes this hazard (STPA definition)",
    )
    pd["worst_case_environment"] = create_prop_def(
        client,
        "worst_case_environment",
        "Worst Case Environment",
        "string",
        "The environmental conditions that would combine with this system state to cause a loss",
    )

    # CONTROL_ACTION specific
    pd["ca_description"] = create_prop_def(
        client,
        "ca_description",
        "Control Action Description",
        "string",
        "Description of what this control action commands",
    )

    # UNDESIRABLE_CONTROL_ACTION specific
    pd["uca_type"] = create_prop_def(
        client,
        "uca_type",
        "UCA Type",
        "string",
        "Not Provided | Provided Causes Hazard | Wrong Timing | Stopped Too Soon  applies to any undesirable outcome, not only safety",
    )
    pd["uca_context"] = create_prop_def(
        client,
        "uca_context",
        "UCA Context",
        "string",
        "The operational context in which this control action is undesirable",
    )

    # LOSS_SCENARIO specific
    pd["scenario_type"] = create_prop_def(
        client,
        "scenario_type",
        "Scenario Type",
        "string",
        "Inadequate Control | Inadequate Feedback | Flawed Process Model | Disturbance",
    )

    # CONTROL_CONSTRAINT specific
    pd["constraint_type"] = create_prop_def(
        client,
        "constraint_type",
        "Constraint Type",
        "string",
        "Functional | Temporal | Procedural",
    )

    # REQUIREMENT specific
    pd["requirement_type"] = create_prop_def(
        client,
        "requirement_type",
        "Requirement Type",
        "string",
        "Functional | Performance | Integrity | Interface",
    )
    pd["sil_target"] = create_prop_def(
        client,
        "sil_target",
        "SIL Target",
        "string",
        "SIL 0 | SIL 1 | SIL 2 | SIL 3 | SIL 4",
    )
    pd["verification_method"] = create_prop_def(
        client,
        "verification_method",
        "Verification Method",
        "string",
        "Test | Analysis | Inspection | Demonstration",
    )
    pd["source_doc"] = create_prop_def(
        client,
        "source_doc",
        "Source Document",
        "string",
        "Reference to the document from which this requirement is derived",
    )

    # GSN_GOAL specific
    pd["claim_text"] = create_prop_def(
        client,
        "claim_text",
        "Claim Text",
        "string",
        "The full text of the claim made by this goal",
    )
    pd["is_defeated"] = create_prop_def(
        client,
        "is_defeated",
        "Is Defeated",
        "boolean",
        "True if this goal has been defeated  per ISO 15026-2",
        "false",
    )

    # GSN_STRATEGY specific
    pd["argument_pattern"] = create_prop_def(
        client,
        "argument_pattern",
        "Argument Pattern",
        "string",
        "Description of the argument pattern used in this strategy",
    )
    pd["decomposition_basis"] = create_prop_def(
        client,
        "decomposition_basis",
        "Decomposition Basis",
        "string",
        "The basis on which the goal is decomposed by this strategy",
    )

    # GSN_SOLUTION specific
    pd["is_undischarged"] = create_prop_def(
        client,
        "is_undischarged",
        "Is Undischarged",
        "boolean",
        "True if this solution node has not yet been connected to evidence",
        "true",
    )

    # GSN_CONTEXT / GSN_ASSUMPTION shared
    pd["context_source_doc"] = create_prop_def(
        client,
        "context_source_doc",
        "Source Document",
        "string",
        "Reference to the document that establishes this context or assumption",
    )

    # EVIDENCE specific
    pd["doc_type"] = create_prop_def(
        client,
        "doc_type",
        "Document Type",
        "string",
        "Test Report | Analysis | Design Document | Inspection Record | Standards Matrix | Certificate | Survey",
    )
    pd["doc_ref"] = create_prop_def(
        client,
        "doc_ref",
        "Document Reference",
        "string",
        "Document identifier and revision reference",
    )
    pd["revision"] = create_prop_def(
        client,
        "revision",
        "Revision",
        "string",
        "Document revision  separate from version for formal safety submissions",
    )
    pd["evidence_date"] = create_prop_def(
        client,
        "evidence_date",
        "Evidence Date",
        "string",
        "Date of the evidence document (ISO 8601)",
    )
    pd["approved_by"] = create_prop_def(
        client,
        "approved_by",
        "Approved By",
        "string",
        "Name or role of the person who approved this evidence document",
    )

    print(f"  [OK] {len(pd)} property definitions created")

    # -----------------------------------------------------------------------
    # 4. PROPERTY ASSIGNMENTS
    # -----------------------------------------------------------------------
    print("\n-- Assigning properties to node types")

    shared = [pd["status"]["id"], pd["notes"]["id"]]
    uniclass = shared + [
        pd["uniclass_code"]["id"],
        pd["uniclass_name"]["id"],
        pd["description"]["id"],
    ]

    def assign_list(node_type_id, def_ids, required_ids=None, start=1):
        required_ids = required_ids or []
        for i, did in enumerate(def_ids):
            assign_prop(client, node_type_id, did, did in required_ids, start + i)

    # COMPLEX
    assign_list(
        nt["COMPLEX"]["id"],
        uniclass + [pd["location"]["id"]],
        required_ids=[pd["uniclass_code"]["id"], pd["uniclass_name"]["id"]],
    )

    # ENTITY
    assign_list(
        nt["ENTITY"]["id"],
        uniclass + [pd["location"]["id"]],
        required_ids=[pd["uniclass_code"]["id"], pd["uniclass_name"]["id"]],
    )

    # SPACE
    assign_list(
        nt["SPACE"]["id"],
        uniclass,
        required_ids=[pd["uniclass_code"]["id"], pd["uniclass_name"]["id"]],
    )

    # ELEMENT
    assign_list(
        nt["ELEMENT"]["id"],
        uniclass,
        required_ids=[pd["uniclass_code"]["id"], pd["uniclass_name"]["id"]],
    )

    # SYSTEM
    assign_list(
        nt["SYSTEM"]["id"],
        uniclass + [pd["sil_level"]["id"]],
        required_ids=[pd["uniclass_code"]["id"], pd["uniclass_name"]["id"]],
    )

    # PRODUCT
    assign_list(
        nt["PRODUCT"]["id"],
        uniclass + [pd["manufacturer"]["id"], pd["model_ref"]["id"]],
        required_ids=[pd["uniclass_code"]["id"], pd["uniclass_name"]["id"]],
    )

    # ACTIVITY
    assign_list(
        nt["ACTIVITY"]["id"],
        uniclass + [pd["activity_type"]["id"]],
        required_ids=[pd["uniclass_code"]["id"], pd["uniclass_name"]["id"]],
    )

    # ROLE
    assign_list(
        nt["ROLE"]["id"],
        uniclass + [pd["role_type"]["id"]],
        required_ids=[pd["uniclass_code"]["id"], pd["uniclass_name"]["id"]],
    )

    # LOSS
    assign_list(
        nt["LOSS"]["id"],
        shared + [pd["loss_category"]["id"], pd["description"]["id"]],
        required_ids=[pd["description"]["id"]],
    )

    # HAZARD
    assign_list(
        nt["HAZARD"]["id"],
        shared
        + [
            pd["system_state"]["id"],
            pd["worst_case_environment"]["id"],
            pd["description"]["id"],
        ],
        required_ids=[pd["system_state"]["id"]],
    )

    # CONTROL_ACTION
    assign_list(nt["CONTROL_ACTION"]["id"], shared + [pd["ca_description"]["id"]])

    # UNDESIRABLE_CONTROL_ACTION
    assign_list(
        nt["UNDESIRABLE_CONTROL_ACTION"]["id"],
        shared
        + [pd["uca_type"]["id"], pd["uca_context"]["id"], pd["description"]["id"]],
        required_ids=[pd["uca_type"]["id"]],
    )

    # LOSS_SCENARIO
    assign_list(
        nt["LOSS_SCENARIO"]["id"],
        shared + [pd["scenario_type"]["id"], pd["description"]["id"]],
        required_ids=[pd["description"]["id"]],
    )

    # CONTROL_CONSTRAINT
    assign_list(
        nt["CONTROL_CONSTRAINT"]["id"],
        shared + [pd["constraint_type"]["id"], pd["description"]["id"]],
        required_ids=[pd["description"]["id"]],
    )

    # REQUIREMENT
    assign_list(
        nt["REQUIREMENT"]["id"],
        shared
        + [
            pd["requirement_type"]["id"],
            pd["sil_target"]["id"],
            pd["verification_method"]["id"],
            pd["source_doc"]["id"],
            pd["description"]["id"],
        ],
        required_ids=[pd["description"]["id"]],
    )

    # GSN_GOAL
    assign_list(
        nt["GSN_GOAL"]["id"],
        shared + [pd["claim_text"]["id"], pd["is_defeated"]["id"]],
        required_ids=[pd["claim_text"]["id"]],
    )

    # GSN_STRATEGY
    assign_list(
        nt["GSN_STRATEGY"]["id"],
        shared
        + [
            pd["description"]["id"],
            pd["argument_pattern"]["id"],
            pd["decomposition_basis"]["id"],
        ],
    )

    # GSN_SOLUTION
    assign_list(
        nt["GSN_SOLUTION"]["id"],
        shared + [pd["description"]["id"], pd["is_undischarged"]["id"]],
    )

    # GSN_CONTEXT
    assign_list(
        nt["GSN_CONTEXT"]["id"],
        shared + [pd["description"]["id"], pd["context_source_doc"]["id"]],
    )

    # GSN_ASSUMPTION
    assign_list(
        nt["GSN_ASSUMPTION"]["id"],
        shared + [pd["description"]["id"], pd["context_source_doc"]["id"]],
    )

    # EVIDENCE
    assign_list(
        nt["EVIDENCE"]["id"],
        shared
        + [
            pd["doc_type"]["id"],
            pd["doc_ref"]["id"],
            pd["revision"]["id"],
            pd["evidence_date"]["id"],
            pd["approved_by"]["id"],
            pd["description"]["id"],
        ],
        required_ids=[pd["doc_ref"]["id"]],
    )

    print("  [OK] Property assignments complete")

    # -----------------------------------------------------------------------
    # 5. NODES  DESCRIPTION LAYER
    # -----------------------------------------------------------------------
    print("\n-- Creating description layer nodes (Uniclass)")

    co = {}
    en = {}
    sp = {}
    ef = {}
    ss = {}
    pr = {}
    ac = {}
    ro = {}

    # COMPLEX
    co["CCX"] = create_node(client, nt["COMPLEX"]["id"], "CO-001", "City Cross Station")
    set_properties(
        client,
        co["CCX"]["id"],
        {
            pd["uniclass_code"]["id"]: "Co_40_50",
            pd["uniclass_name"]["id"]: "Metro and Light Rail Complexes",
            pd["description"][
                "id"
            ]: "Underground metro station  two platforms, automated train operation, staffed concourse",
            pd["location"]["id"]: "City Centre",
            pd["status"]["id"]: "Approved",
        },
    )

    # ENTITY
    en["PLT"] = create_node(client, nt["ENTITY"]["id"], "EN-001", "Platform Level")
    set_properties(
        client,
        en["PLT"]["id"],
        {
            pd["uniclass_code"]["id"]: "En_40_50_27",
            pd["uniclass_name"]["id"]: "Metro Station Platform Entities",
            pd["description"][
                "id"
            ]: "Underground platform level  two platforms with platform screen doors",
            pd["status"]["id"]: "Approved",
        },
    )

    en["CON"] = create_node(client, nt["ENTITY"]["id"], "EN-002", "Concourse Level")
    set_properties(
        client,
        en["CON"]["id"],
        {
            pd["uniclass_code"]["id"]: "En_40_50_25",
            pd["uniclass_name"]["id"]: "Metro Station Concourse Entities",
            pd["description"][
                "id"
            ]: "Ticketing, passenger circulation, and retail concourse",
            pd["status"]["id"]: "Approved",
        },
    )

    en["SCR"] = create_node(
        client, nt["ENTITY"]["id"], "EN-003", "Station Control Room"
    )
    set_properties(
        client,
        en["SCR"]["id"],
        {
            pd["uniclass_code"]["id"]: "En_65_50",
            pd["uniclass_name"]["id"]: "Control and Monitoring Entities",
            pd["description"][
                "id"
            ]: "Staffed station control room  operator workstations and CCTV monitoring",
            pd["status"]["id"]: "Approved",
        },
    )

    # SPACE
    sp["PLA"] = create_node(
        client, nt["SPACE"]["id"], "SP-001", "Platform A  Northbound"
    )
    set_properties(
        client,
        sp["PLA"]["id"],
        {
            pd["uniclass_code"]["id"]: "Sp_40_50_27",
            pd["uniclass_name"]["id"]: "Railway Platform Spaces",
            pd["description"][
                "id"
            ]: "Northbound platform  6 car length, full-height platform screen doors",
            pd["status"]["id"]: "Approved",
        },
    )

    sp["PLB"] = create_node(
        client, nt["SPACE"]["id"], "SP-002", "Platform B  Southbound"
    )
    set_properties(
        client,
        sp["PLB"]["id"],
        {
            pd["uniclass_code"]["id"]: "Sp_40_50_27",
            pd["uniclass_name"]["id"]: "Railway Platform Spaces",
            pd["description"][
                "id"
            ]: "Southbound platform  6 car length, full-height platform screen doors",
            pd["status"]["id"]: "Approved",
        },
    )

    sp["PCC"] = create_node(client, nt["SPACE"]["id"], "SP-003", "Passenger Concourse")
    set_properties(
        client,
        sp["PCC"]["id"],
        {
            pd["uniclass_code"]["id"]: "Sp_40_50_25",
            pd["uniclass_name"]["id"]: "Railway Station Concourse Spaces",
            pd["description"][
                "id"
            ]: "Main passenger circulation space  ticketing gates, escalators, exits",
            pd["status"]["id"]: "Approved",
        },
    )

    sp["SCR"] = create_node(client, nt["SPACE"]["id"], "SP-004", "Station Control Room")
    set_properties(
        client,
        sp["SCR"]["id"],
        {
            pd["uniclass_code"]["id"]: "Sp_65_50",
            pd["uniclass_name"]["id"]: "Control Room Spaces",
            pd["description"]["id"]: "Operator workstation area  restricted access",
            pd["status"]["id"]: "Approved",
        },
    )

    # ELEMENT
    ef["PES"] = create_node(
        client, nt["ELEMENT"]["id"], "EF-001", "Platform Edge Structure"
    )
    set_properties(
        client,
        ef["PES"]["id"],
        {
            pd["uniclass_code"]["id"]: "EF_25_10",
            pd["uniclass_name"]["id"]: "Floor and Ground Elements",
            pd["description"][
                "id"
            ]: "Reinforced concrete platform edge  structural interface with PSD system",
            pd["status"]["id"]: "Approved",
        },
    )

    ef["EER"] = create_node(
        client, nt["ELEMENT"]["id"], "EF-002", "Emergency Exit Routes"
    )
    set_properties(
        client,
        ef["EER"]["id"],
        {
            pd["uniclass_code"]["id"]: "EF_90_50",
            pd["uniclass_name"]["id"]: "Circulation and Access Elements",
            pd["description"][
                "id"
            ]: "Designated emergency exit routes  stairways and emergency cross-passages",
            pd["status"]["id"]: "Approved",
        },
    )

    ef["VIF"] = create_node(
        client, nt["ELEMENT"]["id"], "EF-003", "Ventilation Infrastructure"
    )
    set_properties(
        client,
        ef["VIF"]["id"],
        {
            pd["uniclass_code"]["id"]: "EF_60_10",
            pd["uniclass_name"]["id"]: "HVAC Elements",
            pd["description"][
                "id"
            ]: "Ventilation shafts and ductwork  connected to emergency fan units",
            pd["status"]["id"]: "Approved",
        },
    )

    # SYSTEM
    ss["PSD"] = create_node(
        client, nt["SYSTEM"]["id"], "SS-001", "Platform Screen Door System"
    )
    set_properties(
        client,
        ss["PSD"]["id"],
        {
            pd["uniclass_code"]["id"]: "Ss_65_70_47",
            pd["uniclass_name"]["id"]: "Passenger Signalling and Control Systems",
            pd["description"][
                "id"
            ]: "Full-height automated platform screen doors  12 door units per platform",
            pd["sil_level"]["id"]: "SIL 2",
            pd["status"]["id"]: "Approved",
        },
    )

    ss["TDS"] = create_node(
        client, nt["SYSTEM"]["id"], "SS-002", "Train Detection System"
    )
    set_properties(
        client,
        ss["TDS"]["id"],
        {
            pd["uniclass_code"]["id"]: "Ss_65_70_27",
            pd["uniclass_name"]["id"]: "Railway Signalling Systems",
            pd["description"][
                "id"
            ]: "Track circuit and transponder-based train detection  provides berthed and stopped signals",
            pd["sil_level"]["id"]: "SIL 2",
            pd["status"]["id"]: "Approved",
        },
    )

    ss["PIS"] = create_node(
        client, nt["SYSTEM"]["id"], "SS-003", "Passenger Information System"
    )
    set_properties(
        client,
        ss["PIS"]["id"],
        {
            pd["uniclass_code"]["id"]: "Ss_65_70_47",
            pd["uniclass_name"]["id"]: "Passenger Signalling and Control Systems",
            pd["description"][
                "id"
            ]: "Dynamic passenger information displays and public address system",
            pd["sil_level"]["id"]: "SIL 0",
            pd["status"]["id"]: "Approved",
        },
    )

    ss["EVS"] = create_node(
        client, nt["SYSTEM"]["id"], "SS-004", "Emergency Ventilation System"
    )
    set_properties(
        client,
        ss["EVS"]["id"],
        {
            pd["uniclass_code"]["id"]: "Ss_40_30_95",
            pd["uniclass_name"]["id"]: "Ventilation Systems",
            pd["description"][
                "id"
            ]: "Smoke extraction and emergency ventilation  activated by fire alarm or manual override",
            pd["sil_level"]["id"]: "SIL 1",
            pd["status"]["id"]: "Approved",
        },
    )

    ss["SCS"] = create_node(
        client, nt["SYSTEM"]["id"], "SS-005", "Station Control System"
    )
    set_properties(
        client,
        ss["SCS"]["id"],
        {
            pd["uniclass_code"]["id"]: "Ss_65_50",
            pd["uniclass_name"]["id"]: "Control and Monitoring Systems",
            pd["description"][
                "id"
            ]: "Integrated station control  PSD interlock, CCTV, alarm management, departure authorisation",
            pd["sil_level"]["id"]: "SIL 1",
            pd["status"]["id"]: "Approved",
        },
    )

    # PRODUCT
    pr["PDU"] = create_node(
        client, nt["PRODUCT"]["id"], "PR-001", "Platform Screen Door Unit"
    )
    set_properties(
        client,
        pr["PDU"]["id"],
        {
            pd["uniclass_code"]["id"]: "Pr_65_70_47_30",
            pd["uniclass_name"]["id"]: "Platform Screen Door Products",
            pd["description"][
                "id"
            ]: "Individual PSD leaf assembly  motor drive, obstruction sensor, position feedback",
            pd["status"]["id"]: "Approved",
        },
    )

    pr["TCD"] = create_node(
        client, nt["PRODUCT"]["id"], "PR-002", "Track Circuit Detector"
    )
    set_properties(
        client,
        pr["TCD"]["id"],
        {
            pd["uniclass_code"]["id"]: "Pr_65_70_27_65",
            pd["uniclass_name"]["id"]: "Track Detection Products",
            pd["description"][
                "id"
            ]: "Axle counter and track circuit detector  train presence and stopped confirmation",
            pd["status"]["id"]: "Approved",
        },
    )

    pr["PCU"] = create_node(client, nt["PRODUCT"]["id"], "PR-003", "PSD Control Unit")
    set_properties(
        client,
        pr["PCU"]["id"],
        {
            pd["uniclass_code"]["id"]: "Pr_65_50_27",
            pd["uniclass_name"]["id"]: "Control Unit Products",
            pd["description"][
                "id"
            ]: "PSD supervisory control unit  interlock logic, SIL 2 rated processor",
            pd["status"]["id"]: "Approved",
        },
    )

    pr["EFU"] = create_node(client, nt["PRODUCT"]["id"], "PR-004", "Emergency Fan Unit")
    set_properties(
        client,
        pr["EFU"]["id"],
        {
            pd["uniclass_code"]["id"]: "Pr_40_30_95_25",
            pd["uniclass_name"]["id"]: "Fan and Ventilation Products",
            pd["description"][
                "id"
            ]: "Reversible axial fan  normal ventilation and smoke extraction modes",
            pd["status"]["id"]: "Approved",
        },
    )

    pr["SMC"] = create_node(
        client, nt["PRODUCT"]["id"], "PR-005", "Station Management Console"
    )
    set_properties(
        client,
        pr["SMC"]["id"],
        {
            pd["uniclass_code"]["id"]: "Pr_65_50_15",
            pd["uniclass_name"]["id"]: "Operator Console Products",
            pd["description"][
                "id"
            ]: "Operator workstation  SCADA interface, alarm display, manual override controls",
            pd["status"]["id"]: "Approved",
        },
    )

    # ACTIVITY
    ac["NTB"] = create_node(
        client, nt["ACTIVITY"]["id"], "AC-001", "Normal Train Berthing"
    )
    set_properties(
        client,
        ac["NTB"]["id"],
        {
            pd["uniclass_code"]["id"]: "Ac_35_50_25",
            pd["uniclass_name"]["id"]: "Railway Operations Activities",
            pd["description"][
                "id"
            ]: "Train arrives at platform, stops at designated berthing point, passengers board and alight",
            pd["activity_type"]["id"]: "Normal",
            pd["status"]["id"]: "Approved",
        },
    )

    ac["PBA"] = create_node(
        client, nt["ACTIVITY"]["id"], "AC-002", "Passenger Boarding and Alighting"
    )
    set_properties(
        client,
        ac["PBA"]["id"],
        {
            pd["uniclass_code"]["id"]: "Ac_35_50_25",
            pd["uniclass_name"]["id"]: "Railway Operations Activities",
            pd["description"][
                "id"
            ]: "Passenger movement through open PSDs between platform and train",
            pd["activity_type"]["id"]: "Normal",
            pd["status"]["id"]: "Approved",
        },
    )

    ac["EEV"] = create_node(
        client, nt["ACTIVITY"]["id"], "AC-003", "Emergency Evacuation"
    )
    set_properties(
        client,
        ac["EEV"]["id"],
        {
            pd["uniclass_code"]["id"]: "Ac_35_90_25",
            pd["uniclass_name"]["id"]: "Emergency Response Activities",
            pd["description"][
                "id"
            ]: "Controlled evacuation of passengers from platform via emergency exits",
            pd["activity_type"]["id"]: "Emergency",
            pd["status"]["id"]: "Approved",
        },
    )

    ac["DMO"] = create_node(
        client, nt["ACTIVITY"]["id"], "AC-004", "Degraded Mode Operation"
    )
    set_properties(
        client,
        ac["DMO"]["id"],
        {
            pd["uniclass_code"]["id"]: "Ac_35_50_25",
            pd["uniclass_name"]["id"]: "Railway Operations Activities",
            pd["description"][
                "id"
            ]: "Station operation with reduced automation  manual control of PSD, reduced train frequency",
            pd["activity_type"]["id"]: "Degraded",
            pd["status"]["id"]: "Approved",
        },
    )

    # ROLE
    ro["SCO"] = create_node(
        client, nt["ROLE"]["id"], "RO-001", "Station Control Operator"
    )
    set_properties(
        client,
        ro["SCO"]["id"],
        {
            pd["uniclass_code"]["id"]: "Ro_50_60_12",
            pd["uniclass_name"]["id"]: "Station Control Roles",
            pd["description"][
                "id"
            ]: "Trained operator responsible for station control system, departure authorisation, and emergency response",
            pd["role_type"]["id"]: "Human",
            pd["status"]["id"]: "Approved",
        },
    )

    ro["TDR"] = create_node(client, nt["ROLE"]["id"], "RO-002", "Train Driver")
    set_properties(
        client,
        ro["TDR"]["id"],
        {
            pd["uniclass_code"]["id"]: "Ro_50_60_27",
            pd["uniclass_name"]["id"]: "Train Crew Roles",
            pd["description"][
                "id"
            ]: "Train driver  responsible for train operation, interacts with station via cab signal and departure signal",
            pd["role_type"]["id"]: "Human",
            pd["status"]["id"]: "Approved",
        },
    )

    ro["ATO"] = create_node(
        client, nt["ROLE"]["id"], "RO-003", "Automatic Train Operation System"
    )
    set_properties(
        client,
        ro["ATO"]["id"],
        {
            pd["uniclass_code"]["id"]: "Ro_65_70_27",
            pd["uniclass_name"]["id"]: "Automated Control Roles",
            pd["description"][
                "id"
            ]: "ATO system  controls train berthing, stopping, and departure in automatic mode",
            pd["role_type"]["id"]: "Automated System",
            pd["status"]["id"]: "Approved",
        },
    )

    desc_count = (
        len(co) + len(en) + len(sp) + len(ef) + len(ss) + len(pr) + len(ac) + len(ro)
    )
    print(f"  [OK] {desc_count} description layer nodes created")

    # -----------------------------------------------------------------------
    # 6. NODES  ANALYSIS LAYER
    # -----------------------------------------------------------------------
    print("\n-- Creating analysis layer nodes (STPA + Requirements)")

    loss = {}
    haz = {}
    ca = {}
    uca = {}
    ls = {}
    cc = {}
    sr = {}

    # LOSS
    loss["L1"] = create_node(
        client,
        nt["LOSS"]["id"],
        "L-001",
        "Passenger fatality or serious injury at platform edge",
    )
    set_properties(
        client,
        loss["L1"]["id"],
        {
            pd["loss_category"]["id"]: "Life",
            pd["description"][
                "id"
            ]: "One or more passengers killed or seriously injured at the platform edge as a result of contact with a train or falling onto the track",
            pd["status"]["id"]: "Approved",
        },
    )

    loss["L2"] = create_node(
        client, nt["LOSS"]["id"], "L-002", "Passenger trapped between train and PSD"
    )
    set_properties(
        client,
        loss["L2"]["id"],
        {
            pd["loss_category"]["id"]: "Life",
            pd["description"][
                "id"
            ]: "Passenger becomes trapped in the gap between train doors and platform screen doors during closing sequence",
            pd["status"]["id"]: "Approved",
        },
    )

    loss["L3"] = create_node(
        client,
        nt["LOSS"]["id"],
        "L-003",
        "Mass casualty event during emergency evacuation",
    )
    set_properties(
        client,
        loss["L3"]["id"],
        {
            pd["loss_category"]["id"]: "Life",
            pd["description"][
                "id"
            ]: "Multiple fatalities or serious injuries occurring during emergency evacuation of the station due to inadequate evacuation provision or smoke inhalation",
            pd["status"]["id"]: "Approved",
        },
    )

    # HAZARD
    haz["H1"] = create_node(
        client, nt["HAZARD"]["id"], "H-001", "PSD open while train not berthed"
    )
    set_properties(
        client,
        haz["H1"]["id"],
        {
            pd["system_state"][
                "id"
            ]: "Platform screen doors are in the open position when no train is present and stopped at the platform",
            pd["worst_case_environment"][
                "id"
            ]: "Platform occupied by passengers  risk of falling onto live track",
            pd["description"][
                "id"
            ]: "PSDs open without a berthed and stopped train  exposes live track to passengers",
            pd["status"]["id"]: "Approved",
        },
    )

    haz["H2"] = create_node(
        client, nt["HAZARD"]["id"], "H-002", "PSD closed during passenger flow"
    )
    set_properties(
        client,
        haz["H2"]["id"],
        {
            pd["system_state"][
                "id"
            ]: "Platform screen doors close while passengers are in the doorway zone between PSD and train",
            pd["worst_case_environment"][
                "id"
            ]: "High passenger density boarding or alighting  obstruction sensor degraded",
            pd["description"][
                "id"
            ]: "PSDs close with passengers occupying the doorway zone  risk of trapping and injury",
            pd["status"]["id"]: "Approved",
        },
    )

    haz["H3"] = create_node(
        client,
        nt["HAZARD"]["id"],
        "H-003",
        "Train departs with obstructed platform gap",
    )
    set_properties(
        client,
        haz["H3"]["id"],
        {
            pd["system_state"][
                "id"
            ]: "Train departure is authorised when the gap between train and PSD is obstructed",
            pd["worst_case_environment"][
                "id"
            ]: "Obstruction not visible to operator or driver  CCTV coverage degraded",
            pd["description"][
                "id"
            ]: "Train departs while a passenger or object is trapped in the gap  risk of serious injury or fatality",
            pd["status"]["id"]: "Approved",
        },
    )

    haz["H4"] = create_node(
        client, nt["HAZARD"]["id"], "H-004", "Evacuation routes unavailable"
    )
    set_properties(
        client,
        haz["H4"]["id"],
        {
            pd["system_state"][
                "id"
            ]: "Emergency exit routes are blocked or ventilation system has failed during an emergency event",
            pd["worst_case_environment"][
                "id"
            ]: "Fire or smoke event on platform  passengers unable to egress",
            pd["description"][
                "id"
            ]: "Passengers cannot safely evacuate  risk of smoke inhalation and mass casualty event",
            pd["status"]["id"]: "Approved",
        },
    )

    # CONTROL ACTION
    ca["OPSD"] = create_node(
        client, nt["CONTROL_ACTION"]["id"], "CA-001", "Open Platform Screen Doors"
    )
    set_properties(
        client,
        ca["OPSD"]["id"],
        {
            pd["ca_description"][
                "id"
            ]: "Command to open all PSDs on a specified platform  issued by Station Control System",
            pd["status"]["id"]: "Approved",
        },
    )

    ca["CPSD"] = create_node(
        client, nt["CONTROL_ACTION"]["id"], "CA-002", "Close Platform Screen Doors"
    )
    set_properties(
        client,
        ca["CPSD"]["id"],
        {
            pd["ca_description"][
                "id"
            ]: "Command to close all PSDs on a specified platform  issued by Station Control System",
            pd["status"]["id"]: "Approved",
        },
    )

    ca["ATDP"] = create_node(
        client, nt["CONTROL_ACTION"]["id"], "CA-003", "Authorise Train Departure"
    )
    set_properties(
        client,
        ca["ATDP"]["id"],
        {
            pd["ca_description"][
                "id"
            ]: "Operator authorisation for train departure  enables departure signal to train driver or ATO",
            pd["status"]["id"]: "Approved",
        },
    )

    ca["ACEV"] = create_node(
        client, nt["CONTROL_ACTION"]["id"], "CA-004", "Activate Emergency Ventilation"
    )
    set_properties(
        client,
        ca["ACEV"]["id"],
        {
            pd["ca_description"][
                "id"
            ]: "Command to activate emergency ventilation fans in smoke extraction mode",
            pd["status"]["id"]: "Approved",
        },
    )

    # UNSAFE CONTROL ACTION
    uca["UCA1"] = create_node(
        client,
        nt["UNDESIRABLE_CONTROL_ACTION"]["id"],
        "UCA-001",
        "Open PSDs when train not present at platform",
    )
    set_properties(
        client,
        uca["UCA1"]["id"],
        {
            pd["uca_type"]["id"]: "Provided Causes Hazard",
            pd["uca_context"][
                "id"
            ]: "No train berthed at platform or train not fully stopped",
            pd["description"][
                "id"
            ]: "PSD open command is executed when no train is present  exposes live track to passengers",
            pd["status"]["id"]: "Approved",
        },
    )

    uca["UCA2"] = create_node(
        client,
        nt["UNDESIRABLE_CONTROL_ACTION"]["id"],
        "UCA-002",
        "Open PSDs before train has fully stopped",
    )
    set_properties(
        client,
        uca["UCA2"]["id"],
        {
            pd["uca_type"]["id"]: "Provided Too Early",
            pd["uca_context"][
                "id"
            ]: "Train is decelerating into the platform but has not yet reached zero speed",
            pd["description"][
                "id"
            ]: "PSDs begin opening while train is still moving  risk of passenger contact with moving train",
            pd["status"]["id"]: "Approved",
        },
    )

    uca["UCA3"] = create_node(
        client,
        nt["UNDESIRABLE_CONTROL_ACTION"]["id"],
        "UCA-003",
        "Close PSDs while passengers are in doorway",
    )
    set_properties(
        client,
        uca["UCA3"]["id"],
        {
            pd["uca_type"]["id"]: "Provided Causes Hazard",
            pd["uca_context"][
                "id"
            ]: "Passengers occupying the doorway zone during boarding or alighting",
            pd["description"][
                "id"
            ]: "PSD close command executed while doorway zone is occupied  risk of trapping",
            pd["status"]["id"]: "Approved",
        },
    )

    uca["UCA4"] = create_node(
        client,
        nt["UNDESIRABLE_CONTROL_ACTION"]["id"],
        "UCA-004",
        "Authorise departure without confirming platform clear",
    )
    set_properties(
        client,
        uca["UCA4"]["id"],
        {
            pd["uca_type"]["id"]: "Provided Causes Hazard",
            pd["uca_context"][
                "id"
            ]: "Platform gap obstructed  CCTV degraded or operator distracted",
            pd["description"][
                "id"
            ]: "Departure authorised before platform clear confirmation  risk of train departing with obstruction in gap",
            pd["status"]["id"]: "Approved",
        },
    )

    uca["UCA5"] = create_node(
        client,
        nt["UNDESIRABLE_CONTROL_ACTION"]["id"],
        "UCA-005",
        "Fail to open PSDs when train present and stopped",
    )
    set_properties(
        client,
        uca["UCA5"]["id"],
        {
            pd["uca_type"]["id"]: "Not Provided",
            pd["uca_context"][
                "id"
            ]: "Train berthed and stopped  PSD open command not received",
            pd["description"][
                "id"
            ]: "PSDs remain closed when train is present and stopped  passengers cannot board or alight, potential for secondary incidents",
            pd["status"]["id"]: "Approved",
        },
    )

    uca["UCA6"] = create_node(
        client,
        nt["UNDESIRABLE_CONTROL_ACTION"]["id"],
        "UCA-006",
        "Fail to activate ventilation during confirmed fire event",
    )
    set_properties(
        client,
        uca["UCA6"]["id"],
        {
            pd["uca_type"]["id"]: "Not Provided",
            pd["uca_context"][
                "id"
            ]: "Fire alarm confirmed on platform or in tunnel  emergency ventilation command not issued",
            pd["description"][
                "id"
            ]: "Emergency ventilation not activated during fire  smoke accumulates, evacuation compromised",
            pd["status"]["id"]: "Approved",
        },
    )

    # LOSS SCENARIO
    ls["LS1"] = create_node(
        client,
        nt["LOSS_SCENARIO"]["id"],
        "LS-001",
        "Train position signal lost  PSD opens on false berthed indication",
    )
    set_properties(
        client,
        ls["LS1"]["id"],
        {
            pd["scenario_type"]["id"]: "Inadequate Feedback",
            pd["description"][
                "id"
            ]: "Track circuit failure or communication fault causes Station Control System to receive a false train-berthed signal  PSDs open with no train present",
            pd["status"]["id"]: "Approved",
        },
    )

    ls["LS2"] = create_node(
        client,
        nt["LOSS_SCENARIO"]["id"],
        "LS-002",
        "Operator bypasses interlock under time pressure",
    )
    set_properties(
        client,
        ls["LS2"]["id"],
        {
            pd["scenario_type"]["id"]: "Inadequate Control",
            pd["description"][
                "id"
            ]: "Station Control Operator uses manual override to authorise departure without completing platform clear check  schedule pressure or distraction",
            pd["status"]["id"]: "Approved",
        },
    )

    ls["LS3"] = create_node(
        client,
        nt["LOSS_SCENARIO"]["id"],
        "LS-003",
        "PSD obstruction sensor fails to detect passenger in doorway",
    )
    set_properties(
        client,
        ls["LS3"]["id"],
        {
            pd["scenario_type"]["id"]: "Flawed Process Model",
            pd["description"][
                "id"
            ]: "Obstruction sensor degraded or dirty  closing sequence proceeds with passenger in doorway zone undetected",
            pd["status"]["id"]: "Approved",
        },
    )

    ls["LS4"] = create_node(
        client,
        nt["LOSS_SCENARIO"]["id"],
        "LS-004",
        "Emergency alarm not received by operator in degraded comms mode",
    )
    set_properties(
        client,
        ls["LS4"]["id"],
        {
            pd["scenario_type"]["id"]: "Inadequate Feedback",
            pd["description"][
                "id"
            ]: "Fire alarm signal not transmitted to Station Control System during communications fault  operator unaware of fire event, ventilation not activated",
            pd["status"]["id"]: "Approved",
        },
    )

    # CONTROL CONSTRAINT
    cc["CC1"] = create_node(
        client,
        nt["CONTROL_CONSTRAINT"]["id"],
        "CC-001",
        "PSDs shall only open on confirmed berthed and stopped train",
    )
    set_properties(
        client,
        cc["CC1"]["id"],
        {
            pd["constraint_type"]["id"]: "Functional",
            pd["description"][
                "id"
            ]: "The PSD open command shall only be executed when a valid train-berthed AND train-stopped signal has been received and validated from the train detection system",
            pd["status"]["id"]: "Approved",
        },
    )

    cc["CC2"] = create_node(
        client,
        nt["CONTROL_CONSTRAINT"]["id"],
        "CC-002",
        "PSDs shall not close when doorway obstruction detected",
    )
    set_properties(
        client,
        cc["CC2"]["id"],
        {
            pd["constraint_type"]["id"]: "Functional",
            pd["description"][
                "id"
            ]: "The PSD close sequence shall be inhibited and reversed if the doorway obstruction sensor detects presence in the doorway zone",
            pd["status"]["id"]: "Approved",
        },
    )

    cc["CC3"] = create_node(
        client,
        nt["CONTROL_CONSTRAINT"]["id"],
        "CC-003",
        "Departure shall not be authorised without platform clear confirmation",
    )
    set_properties(
        client,
        cc["CC3"]["id"],
        {
            pd["constraint_type"]["id"]: "Procedural",
            pd["description"][
                "id"
            ]: "Train departure authorisation shall require positive confirmation that the platform gap is clear  CCTV check and PSD closed indication",
            pd["status"]["id"]: "Approved",
        },
    )

    cc["CC4"] = create_node(
        client,
        nt["CONTROL_CONSTRAINT"]["id"],
        "CC-004",
        "Emergency ventilation shall activate within 30 seconds of confirmed fire",
    )
    set_properties(
        client,
        cc["CC4"]["id"],
        {
            pd["constraint_type"]["id"]: "Temporal",
            pd["description"][
                "id"
            ]: "On receipt of a confirmed fire alarm signal the Station Control System shall activate emergency ventilation within 30 seconds",
            pd["status"]["id"]: "Approved",
        },
    )

    # SAFETY REQUIREMENT
    sr["SR1"] = create_node(
        client,
        nt["REQUIREMENT"]["id"],
        "SR-001",
        "PSD system shall only open doors on valid train-berthed signal",
    )
    set_properties(
        client,
        sr["SR1"]["id"],
        {
            pd["requirement_type"]["id"]: "Functional",
            pd["sil_target"]["id"]: "SIL 2",
            pd["verification_method"]["id"]: "Test",
            pd["source_doc"]["id"]: "CC-001",
            pd["description"][
                "id"
            ]: "The PSD system shall only open platform screen doors upon receipt of a valid and confirmed train-berthed signal from the train detection system, validated by independent check",
            pd["status"]["id"]: "Approved",
        },
    )

    sr["SR2"] = create_node(
        client,
        nt["REQUIREMENT"]["id"],
        "SR-002",
        "PSD system shall detect doorway obstruction and inhibit closure",
    )
    set_properties(
        client,
        sr["SR2"]["id"],
        {
            pd["requirement_type"]["id"]: "Functional",
            pd["sil_target"]["id"]: "SIL 2",
            pd["verification_method"]["id"]: "Test",
            pd["source_doc"]["id"]: "CC-002",
            pd["description"][
                "id"
            ]: "The PSD system shall detect the presence of any obstruction in the doorway zone and inhibit or reverse the door closing sequence",
            pd["status"]["id"]: "Approved",
        },
    )

    sr["SR3"] = create_node(
        client,
        nt["REQUIREMENT"]["id"],
        "SR-003",
        "Station control system shall require platform-clear confirmation before departure",
    )
    set_properties(
        client,
        sr["SR3"]["id"],
        {
            pd["requirement_type"]["id"]: "Functional",
            pd["sil_target"]["id"]: "SIL 1",
            pd["verification_method"]["id"]: "Test",
            pd["source_doc"]["id"]: "CC-003",
            pd["description"][
                "id"
            ]: "The station control system shall require positive platform-clear confirmation before enabling the train departure authorisation function",
            pd["status"]["id"]: "Approved",
        },
    )

    sr["SR4"] = create_node(
        client,
        nt["REQUIREMENT"]["id"],
        "SR-004",
        "Emergency ventilation shall activate within 30 seconds of confirmed fire alarm",
    )
    set_properties(
        client,
        sr["SR4"]["id"],
        {
            pd["requirement_type"]["id"]: "Performance",
            pd["sil_target"]["id"]: "SIL 1",
            pd["verification_method"]["id"]: "Test",
            pd["source_doc"]["id"]: "CC-004",
            pd["description"][
                "id"
            ]: "The emergency ventilation system shall enter smoke extraction mode within 30 seconds of receipt of a confirmed fire alarm signal",
            pd["status"]["id"]: "Approved",
        },
    )

    sr["SR5"] = create_node(
        client,
        nt["REQUIREMENT"]["id"],
        "SR-005",
        "PSD interlock shall remain effective in degraded train detection mode",
    )
    set_properties(
        client,
        sr["SR5"]["id"],
        {
            pd["requirement_type"]["id"]: "Integrity",
            pd["sil_target"]["id"]: "SIL 2",
            pd["verification_method"]["id"]: "Analysis",
            pd["source_doc"]["id"]: "SR-001",
            pd["description"][
                "id"
            ]: "The PSD interlock function of SR-001 shall remain effective when the primary train detection system is operating in degraded mode  fail-safe default to doors closed",
            pd["status"]["id"]: "Approved",
        },
    )

    analysis_count = (
        len(loss) + len(haz) + len(ca) + len(uca) + len(ls) + len(cc) + len(sr)
    )
    print(f"  [OK] {analysis_count} analysis layer nodes created")

    # -----------------------------------------------------------------------
    # 7. NODES  ARGUMENT LAYER
    # -----------------------------------------------------------------------
    print("\n-- Creating argument layer nodes (GSN + Evidence)")

    gsn_g = {}
    gsn_s = {}
    gsn_sn = {}
    gsn_c = {}
    gsn_a = {}
    ev = {}

    # GSN_GOAL
    gsn_g["G1"] = create_node(
        client,
        nt["GSN_GOAL"]["id"],
        "G-001",
        "City Cross Station is acceptably safe for passenger operation",
    )
    set_properties(
        client,
        gsn_g["G1"]["id"],
        {
            pd["claim_text"][
                "id"
            ]: "City Cross Station is acceptably safe for passenger operation under all defined normal, degraded, and emergency operating conditions",
            pd["is_defeated"]["id"]: "false",
            pd["status"]["id"]: "Approved",
        },
    )

    gsn_g["G2"] = create_node(
        client,
        nt["GSN_GOAL"]["id"],
        "G-002",
        "Risks associated with PSD operation are reduced to ALARP",
    )
    set_properties(
        client,
        gsn_g["G2"]["id"],
        {
            pd["claim_text"][
                "id"
            ]: "All risks arising from platform screen door operation have been identified through STPA and reduced to ALARP through implementation of derived safety requirements",
            pd["is_defeated"]["id"]: "false",
            pd["status"]["id"]: "Approved",
        },
    )

    gsn_g["G3"] = create_node(
        client,
        nt["GSN_GOAL"]["id"],
        "G-003",
        "Risks associated with train departure are reduced to ALARP",
    )
    set_properties(
        client,
        gsn_g["G3"]["id"],
        {
            pd["claim_text"][
                "id"
            ]: "All risks arising from train departure authorisation have been identified and reduced to ALARP through confirmed platform-clear procedures",
            pd["is_defeated"]["id"]: "false",
            pd["status"]["id"]: "Approved",
        },
    )

    gsn_g["G4"] = create_node(
        client,
        nt["GSN_GOAL"]["id"],
        "G-004",
        "Emergency evacuation provisions are adequate",
    )
    set_properties(
        client,
        gsn_g["G4"]["id"],
        {
            pd["claim_text"][
                "id"
            ]: "Emergency evacuation provisions  exit routes and emergency ventilation  are adequate for all credible emergency scenarios within the defined operating context",
            pd["is_defeated"]["id"]: "false",
            pd["status"]["id"]: "Approved",
        },
    )

    gsn_g["G5"] = create_node(
        client,
        nt["GSN_GOAL"]["id"],
        "G-005",
        "PSD system meets its SIL 2 integrity requirements",
    )
    set_properties(
        client,
        gsn_g["G5"]["id"],
        {
            pd["claim_text"][
                "id"
            ]: "The Platform Screen Door System has been developed and verified to meet SIL 2 integrity requirements in accordance with EN 50129",
            pd["is_defeated"]["id"]: "false",
            pd["status"]["id"]: "Approved",
        },
    )

    # GSN_STRATEGY
    gsn_s["S1"] = create_node(
        client,
        nt["GSN_STRATEGY"]["id"],
        "S-001",
        "Argue over STPA-identified hazard categories",
    )
    set_properties(
        client,
        gsn_s["S1"]["id"],
        {
            pd["description"][
                "id"
            ]: "Decompose the top-level safety claim by arguing over each of the four hazard categories identified in the City Cross Station STPA",
            pd["argument_pattern"]["id"]: "Argument by hazard category",
            pd["decomposition_basis"][
                "id"
            ]: "STPA hazard identification  H-001 to H-004",
            pd["status"]["id"]: "Approved",
        },
    )

    gsn_s["S2"] = create_node(
        client,
        nt["GSN_STRATEGY"]["id"],
        "S-002",
        "Argue by STPA-derived safety requirements for PSD operation",
    )
    set_properties(
        client,
        gsn_s["S2"]["id"],
        {
            pd["description"][
                "id"
            ]: "Argue PSD risk reduction by reference to control constraints CC-001 and CC-002 and the safety requirements derived from them",
            pd["argument_pattern"]["id"]: "Argument by safety requirement satisfaction",
            pd["decomposition_basis"]["id"]: "CC-001, CC-002  SR-001, SR-002",
            pd["status"]["id"]: "Approved",
        },
    )

    gsn_s["S3"] = create_node(
        client,
        nt["GSN_STRATEGY"]["id"],
        "S-003",
        "Argue SIL compliance by verification evidence",
    )
    set_properties(
        client,
        gsn_s["S3"]["id"],
        {
            pd["description"][
                "id"
            ]: "Argue SIL 2 compliance by reference to independent verification test evidence against SR-001 and SR-002",
            pd["argument_pattern"]["id"]: "Argument by independent verification",
            pd["decomposition_basis"]["id"]: "EN 50129 SIL verification approach",
            pd["status"]["id"]: "Approved",
        },
    )

    # GSN_SOLUTION
    gsn_sn["Sn1"] = create_node(
        client,
        nt["GSN_SOLUTION"]["id"],
        "Sn-001",
        "STPA analysis report confirms hazard identification completeness",
    )
    set_properties(
        client,
        gsn_sn["Sn1"]["id"],
        {
            pd["description"][
                "id"
            ]: "City Cross Station STPA report demonstrates systematic and complete identification of all hazardous system states",
            pd["is_undischarged"]["id"]: "false",
            pd["status"]["id"]: "Approved",
        },
    )

    gsn_sn["Sn2"] = create_node(
        client,
        nt["GSN_SOLUTION"]["id"],
        "Sn-002",
        "PSD system SIL 2 verification test report",
    )
    set_properties(
        client,
        gsn_sn["Sn2"]["id"],
        {
            pd["description"][
                "id"
            ]: "Independent verification test report demonstrating PSD system compliance with SIL 2 requirements SR-001 and SR-002",
            pd["is_undischarged"]["id"]: "false",
            pd["status"]["id"]: "Approved",
        },
    )

    gsn_sn["Sn3"] = create_node(
        client,
        nt["GSN_SOLUTION"]["id"],
        "Sn-003",
        "Platform clear confirmation functional test report",
    )
    set_properties(
        client,
        gsn_sn["Sn3"]["id"],
        {
            pd["description"][
                "id"
            ]: "Functional test report demonstrating station control system platform-clear confirmation function meets SR-003",
            pd["is_undischarged"]["id"]: "false",
            pd["status"]["id"]: "Approved",
        },
    )

    gsn_sn["Sn4"] = create_node(
        client,
        nt["GSN_SOLUTION"]["id"],
        "Sn-004",
        "Emergency ventilation response time test report",
    )
    set_properties(
        client,
        gsn_sn["Sn4"]["id"],
        {
            pd["description"][
                "id"
            ]: "Test report demonstrating emergency ventilation activation within 30 seconds  meets SR-004",
            pd["is_undischarged"]["id"]: "false",
            pd["status"]["id"]: "Approved",
        },
    )

    # GSN_CONTEXT
    gsn_c["C1"] = create_node(
        client,
        nt["GSN_CONTEXT"]["id"],
        "C-001",
        "City Cross Station operating within defined Metro network boundary",
    )
    set_properties(
        client,
        gsn_c["C1"]["id"],
        {
            pd["description"][
                "id"
            ]: "This safety case applies to City Cross Station as defined in the station boundary document. External interfaces with the train control system are covered by separate safety case arrangements.",
            pd["context_source_doc"]["id"]: "CCX-BOUND-001",
            pd["status"]["id"]: "Approved",
        },
    )

    gsn_c["C2"] = create_node(
        client,
        nt["GSN_CONTEXT"]["id"],
        "C-002",
        "Automated train operation with platform screen doors",
    )
    set_properties(
        client,
        gsn_c["C2"]["id"],
        {
            pd["description"][
                "id"
            ]: "Station operates with automated train operation (ATO) under normal conditions, with manual fallback. Full-height platform screen doors on both platforms.",
            pd["context_source_doc"]["id"]: "CCX-OPS-001",
            pd["status"]["id"]: "Approved",
        },
    )

    gsn_c["C3"] = create_node(
        client,
        nt["GSN_CONTEXT"]["id"],
        "C-003",
        "Passenger throughput up to 40,000 persons per day",
    )
    set_properties(
        client,
        gsn_c["C3"]["id"],
        {
            pd["description"][
                "id"
            ]: "Design throughput of 40,000 passengers per day  peak hour flow of 4,000 passengers per hour in each direction.",
            pd["context_source_doc"]["id"]: "CCX-CAP-001",
            pd["status"]["id"]: "Approved",
        },
    )

    # GSN_ASSUMPTION
    gsn_a["A1"] = create_node(
        client,
        nt["GSN_ASSUMPTION"]["id"],
        "A-001",
        "External train control system provides valid and timely berthing signals",
    )
    set_properties(
        client,
        gsn_a["A1"]["id"],
        {
            pd["description"][
                "id"
            ]: "It is assumed that the external train control system provides valid, timely, and appropriately integrity-rated train-berthed and train-stopped signals at the station interface. This is the subject of a separate safety case.",
            pd["context_source_doc"]["id"]: "CCX-SRACS-001",
            pd["status"]["id"]: "Approved",
        },
    )

    gsn_a["A2"] = create_node(
        client,
        nt["GSN_ASSUMPTION"]["id"],
        "A-002",
        "Civil structure meets building regulations independently of this safety case",
    )
    set_properties(
        client,
        gsn_a["A2"]["id"],
        {
            pd["description"][
                "id"
            ]: "It is assumed that the civil and structural elements of the station comply with relevant building regulations and structural standards. Structural adequacy is not argued within this safety case.",
            pd["context_source_doc"]["id"]: "CCX-CIVIL-CERT-001",
            pd["status"]["id"]: "Approved",
        },
    )

    # EVIDENCE
    ev["EV1"] = create_node(
        client, nt["EVIDENCE"]["id"], "EV-001", "City Cross Station STPA Report"
    )
    set_properties(
        client,
        ev["EV1"]["id"],
        {
            pd["doc_type"]["id"]: "Analysis",
            pd["doc_ref"]["id"]: "STPA-CCX-001",
            pd["revision"]["id"]: "Rev A",
            pd["evidence_date"]["id"]: "2026-01-15",
            pd["approved_by"]["id"]: "Chief Safety Engineer",
            pd["description"][
                "id"
            ]: "System-Theoretic Process Analysis for City Cross Station  identifies losses, hazards, control structure, unsafe control actions, and control constraints",
            pd["status"]["id"]: "Approved",
        },
    )

    ev["EV2"] = create_node(
        client, nt["EVIDENCE"]["id"], "EV-002", "PSD System SIL 2 Verification Report"
    )
    set_properties(
        client,
        ev["EV2"]["id"],
        {
            pd["doc_type"]["id"]: "Test Report",
            pd["doc_ref"]["id"]: "VER-PSD-001",
            pd["revision"]["id"]: "Rev B",
            pd["evidence_date"]["id"]: "2026-02-10",
            pd["approved_by"]["id"]: "Independent Safety Assessor",
            pd["description"][
                "id"
            ]: "Independent verification test report for Platform Screen Door System  SIL 2 compliance against SR-001 and SR-002",
            pd["status"]["id"]: "Approved",
        },
    )

    ev["EV3"] = create_node(
        client,
        nt["EVIDENCE"]["id"],
        "EV-003",
        "Station Control System Functional Test Report",
    )
    set_properties(
        client,
        ev["EV3"]["id"],
        {
            pd["doc_type"]["id"]: "Test Report",
            pd["doc_ref"]["id"]: "VER-SCS-001",
            pd["revision"]["id"]: "Rev A",
            pd["evidence_date"]["id"]: "2026-02-18",
            pd["approved_by"]["id"]: "Test Manager",
            pd["description"][
                "id"
            ]: "Functional test report for Station Control System  platform clear confirmation function meets SR-003",
            pd["status"]["id"]: "Approved",
        },
    )

    ev["EV4"] = create_node(
        client,
        nt["EVIDENCE"]["id"],
        "EV-004",
        "Emergency Ventilation Response Time Test Report",
    )
    set_properties(
        client,
        ev["EV4"]["id"],
        {
            pd["doc_type"]["id"]: "Test Report",
            pd["doc_ref"]["id"]: "VER-EVS-001",
            pd["revision"]["id"]: "Rev A",
            pd["evidence_date"]["id"]: "2026-02-20",
            pd["approved_by"]["id"]: "Test Manager",
            pd["description"][
                "id"
            ]: "Test report demonstrating emergency ventilation activation within 30 seconds of confirmed fire alarm  meets SR-004",
            pd["status"]["id"]: "Approved",
        },
    )

    arg_count = (
        len(gsn_g) + len(gsn_s) + len(gsn_sn) + len(gsn_c) + len(gsn_a) + len(ev)
    )
    print(f"  [OK] {arg_count} argument layer nodes created")

    # -----------------------------------------------------------------------
    # 8. EDGES
    # -----------------------------------------------------------------------
    print("\n-- Creating edges")
    edge_count = 0

    def e(etype_key, eid, ename, src_id, tgt_id):
        nonlocal edge_count
        create_edge(client, et[etype_key]["id"], eid, ename, src_id, tgt_id)
        edge_count += 1

    # -- Uniclass hierarchy --
    e(
        "CONTAINS",
        "CO-EN-001",
        "City Cross Station contains Platform Level",
        co["CCX"]["id"],
        en["PLT"]["id"],
    )
    e(
        "CONTAINS",
        "CO-EN-002",
        "City Cross Station contains Concourse Level",
        co["CCX"]["id"],
        en["CON"]["id"],
    )
    e(
        "CONTAINS",
        "CO-EN-003",
        "City Cross Station contains Station Control Room",
        co["CCX"]["id"],
        en["SCR"]["id"],
    )

    e(
        "CONTAINS",
        "EN-SP-001",
        "Platform Level contains Platform A",
        en["PLT"]["id"],
        sp["PLA"]["id"],
    )
    e(
        "CONTAINS",
        "EN-SP-002",
        "Platform Level contains Platform B",
        en["PLT"]["id"],
        sp["PLB"]["id"],
    )
    e(
        "CONTAINS",
        "EN-SP-003",
        "Concourse Level contains Passenger Concourse",
        en["CON"]["id"],
        sp["PCC"]["id"],
    )
    e(
        "CONTAINS",
        "EN-SP-004",
        "Station Control Room contains Control Room Space",
        en["SCR"]["id"],
        sp["SCR"]["id"],
    )

    e(
        "CONTAINS",
        "EN-EF-001",
        "Platform Level contains Platform Edge Structure",
        en["PLT"]["id"],
        ef["PES"]["id"],
    )
    e(
        "CONTAINS",
        "EN-EF-002",
        "Platform Level contains Emergency Exit Routes",
        en["PLT"]["id"],
        ef["EER"]["id"],
    )
    e(
        "CONTAINS",
        "EN-EF-003",
        "Platform Level contains Ventilation Infrastructure",
        en["PLT"]["id"],
        ef["VIF"]["id"],
    )

    e(
        "CONTAINS",
        "EN-SS-001",
        "Platform Level contains PSD System",
        en["PLT"]["id"],
        ss["PSD"]["id"],
    )
    e(
        "CONTAINS",
        "EN-SS-002",
        "Platform Level contains Train Detection System",
        en["PLT"]["id"],
        ss["TDS"]["id"],
    )
    e(
        "CONTAINS",
        "EN-SS-003",
        "Concourse Level contains Passenger Information System",
        en["CON"]["id"],
        ss["PIS"]["id"],
    )
    e(
        "CONTAINS",
        "EN-SS-004",
        "Platform Level contains Emergency Ventilation System",
        en["PLT"]["id"],
        ss["EVS"]["id"],
    )
    e(
        "CONTAINS",
        "EN-SS-005",
        "Station Control Room contains Station Control System",
        en["SCR"]["id"],
        ss["SCS"]["id"],
    )

    e(
        "CONTAINS",
        "SS-PR-001",
        "PSD System contains PSD Unit",
        ss["PSD"]["id"],
        pr["PDU"]["id"],
    )
    e(
        "CONTAINS",
        "SS-PR-002",
        "Train Detection System contains Track Circuit Detector",
        ss["TDS"]["id"],
        pr["TCD"]["id"],
    )
    e(
        "CONTAINS",
        "SS-PR-003",
        "PSD System contains PSD Control Unit",
        ss["PSD"]["id"],
        pr["PCU"]["id"],
    )
    e(
        "CONTAINS",
        "SS-PR-004",
        "Emergency Ventilation System contains Emergency Fan Unit",
        ss["EVS"]["id"],
        pr["EFU"]["id"],
    )
    e(
        "CONTAINS",
        "SS-PR-005",
        "Station Control System contains Station Management Console",
        ss["SCS"]["id"],
        pr["SMC"]["id"],
    )

    # -- STPA control structure --
    # Station Control System controls CA-001 and CA-002 (PSD commands)
    e(
        "CONTROLS",
        "SCS-CA-001",
        "Station Control System controls Open PSD",
        ss["SCS"]["id"],
        ca["OPSD"]["id"],
    )
    e(
        "CONTROLS",
        "SCS-CA-002",
        "Station Control System controls Close PSD",
        ss["SCS"]["id"],
        ca["CPSD"]["id"],
    )

    # Station Control Operator controls CA-003 and CA-004
    e(
        "CONTROLS",
        "SCO-CA-003",
        "Station Control Operator controls Authorise Departure",
        ro["SCO"]["id"],
        ca["ATDP"]["id"],
    )
    e(
        "CONTROLS",
        "SCO-CA-004",
        "Station Control Operator controls Activate Emergency Ventilation",
        ro["SCO"]["id"],
        ca["ACEV"]["id"],
    )

    # Control actions received by controlled processes
    e(
        "RECEIVES",
        "CA-001-PSD",
        "Open PSD received by PSD System",
        ca["OPSD"]["id"],
        ss["PSD"]["id"],
    )
    e(
        "RECEIVES",
        "CA-002-PSD",
        "Close PSD received by PSD System",
        ca["CPSD"]["id"],
        ss["PSD"]["id"],
    )
    e(
        "RECEIVES",
        "CA-003-ATO",
        "Authorise Departure received by ATO System",
        ca["ATDP"]["id"],
        ro["ATO"]["id"],
    )
    e(
        "RECEIVES",
        "CA-004-EVS",
        "Activate Ventilation received by Emergency Ventilation System",
        ca["ACEV"]["id"],
        ss["EVS"]["id"],
    )

    # Feedback loops
    e(
        "PROVIDES_FEEDBACK",
        "TDS-SCS",
        "Train Detection System provides feedback to Station Control System",
        ss["TDS"]["id"],
        ss["SCS"]["id"],
    )
    e(
        "PROVIDES_FEEDBACK",
        "PSD-SCS",
        "PSD System provides door status feedback to Station Control System",
        ss["PSD"]["id"],
        ss["SCS"]["id"],
    )
    e(
        "PROVIDES_FEEDBACK",
        "EVS-SCS",
        "Emergency Ventilation System provides status to Station Control System",
        ss["EVS"]["id"],
        ss["SCS"]["id"],
    )

    # Control actions become unsafe as UCAs
    e(
        "BECOMES_UNSAFE_AS",
        "CA-001-UCA1",
        "Open PSD becomes unsafe as UCA-001",
        ca["OPSD"]["id"],
        uca["UCA1"]["id"],
    )
    e(
        "BECOMES_UNSAFE_AS",
        "CA-001-UCA2",
        "Open PSD becomes unsafe as UCA-002",
        ca["OPSD"]["id"],
        uca["UCA2"]["id"],
    )
    e(
        "BECOMES_UNSAFE_AS",
        "CA-002-UCA3",
        "Close PSD becomes unsafe as UCA-003",
        ca["CPSD"]["id"],
        uca["UCA3"]["id"],
    )
    e(
        "BECOMES_UNSAFE_AS",
        "CA-003-UCA4",
        "Authorise Departure becomes unsafe as UCA-004",
        ca["ATDP"]["id"],
        uca["UCA4"]["id"],
    )
    e(
        "BECOMES_UNSAFE_AS",
        "CA-001-UCA5",
        "Open PSD becomes unsafe as UCA-005",
        ca["OPSD"]["id"],
        uca["UCA5"]["id"],
    )
    e(
        "BECOMES_UNSAFE_AS",
        "CA-004-UCA6",
        "Activate Ventilation becomes unsafe as UCA-006",
        ca["ACEV"]["id"],
        uca["UCA6"]["id"],
    )

    # UCAs lead to hazards
    e(
        "LEADS_TO",
        "UCA1-H1",
        "UCA-001 leads to H-001",
        uca["UCA1"]["id"],
        haz["H1"]["id"],
    )
    e(
        "LEADS_TO",
        "UCA2-H1",
        "UCA-002 leads to H-001",
        uca["UCA2"]["id"],
        haz["H1"]["id"],
    )
    e(
        "LEADS_TO",
        "UCA3-H2",
        "UCA-003 leads to H-002",
        uca["UCA3"]["id"],
        haz["H2"]["id"],
    )
    e(
        "LEADS_TO",
        "UCA4-H3",
        "UCA-004 leads to H-003",
        uca["UCA4"]["id"],
        haz["H3"]["id"],
    )
    e(
        "LEADS_TO",
        "UCA6-H4",
        "UCA-006 leads to H-004",
        uca["UCA6"]["id"],
        haz["H4"]["id"],
    )

    # UCAs explained by loss scenarios
    e(
        "EXPLAINED_BY",
        "UCA1-LS1",
        "UCA-001 explained by LS-001",
        uca["UCA1"]["id"],
        ls["LS1"]["id"],
    )
    e(
        "EXPLAINED_BY",
        "UCA4-LS2",
        "UCA-004 explained by LS-002",
        uca["UCA4"]["id"],
        ls["LS2"]["id"],
    )
    e(
        "EXPLAINED_BY",
        "UCA3-LS3",
        "UCA-003 explained by LS-003",
        uca["UCA3"]["id"],
        ls["LS3"]["id"],
    )
    e(
        "EXPLAINED_BY",
        "UCA6-LS4",
        "UCA-006 explained by LS-004",
        uca["UCA6"]["id"],
        ls["LS4"]["id"],
    )

    # Hazards cause losses
    e("CAUSES", "H1-L1", "H-001 causes L-001", haz["H1"]["id"], loss["L1"]["id"])
    e("CAUSES", "H2-L2", "H-002 causes L-002", haz["H2"]["id"], loss["L2"]["id"])
    e("CAUSES", "H3-L1", "H-003 causes L-001", haz["H3"]["id"], loss["L1"]["id"])
    e("CAUSES", "H4-L3", "H-004 causes L-003", haz["H4"]["id"], loss["L3"]["id"])

    # Hazards mitigated by control constraints
    e(
        "MITIGATED_BY",
        "H1-CC1",
        "H-001 mitigated by CC-001",
        haz["H1"]["id"],
        cc["CC1"]["id"],
    )
    e(
        "MITIGATED_BY",
        "H2-CC2",
        "H-002 mitigated by CC-002",
        haz["H2"]["id"],
        cc["CC2"]["id"],
    )
    e(
        "MITIGATED_BY",
        "H3-CC3",
        "H-003 mitigated by CC-003",
        haz["H3"]["id"],
        cc["CC3"]["id"],
    )
    e(
        "MITIGATED_BY",
        "H4-CC4",
        "H-004 mitigated by CC-004",
        haz["H4"]["id"],
        cc["CC4"]["id"],
    )

    # Control constraints inform safety requirements
    e("INFORMS", "CC1-SR1", "CC-001 informs SR-001", cc["CC1"]["id"], sr["SR1"]["id"])
    e("INFORMS", "CC2-SR2", "CC-002 informs SR-002", cc["CC2"]["id"], sr["SR2"]["id"])
    e("INFORMS", "CC3-SR3", "CC-003 informs SR-003", cc["CC3"]["id"], sr["SR3"]["id"])
    e("INFORMS", "CC4-SR4", "CC-004 informs SR-004", cc["CC4"]["id"], sr["SR4"]["id"])

    # SR-005 derived from SR-001
    e(
        "DERIVED_FROM",
        "SR5-SR1",
        "SR-005 derived from SR-001",
        sr["SR5"]["id"],
        sr["SR1"]["id"],
    )

    # Safety requirements allocated to systems
    e(
        "ALLOCATED_TO",
        "SR1-PSD",
        "SR-001 allocated to PSD System",
        sr["SR1"]["id"],
        ss["PSD"]["id"],
    )
    e(
        "ALLOCATED_TO",
        "SR2-PSD",
        "SR-002 allocated to PSD System",
        sr["SR2"]["id"],
        ss["PSD"]["id"],
    )
    e(
        "ALLOCATED_TO",
        "SR3-SCS",
        "SR-003 allocated to Station Control System",
        sr["SR3"]["id"],
        ss["SCS"]["id"],
    )
    e(
        "ALLOCATED_TO",
        "SR4-EVS",
        "SR-004 allocated to Emergency Ventilation System",
        sr["SR4"]["id"],
        ss["EVS"]["id"],
    )
    e(
        "ALLOCATED_TO",
        "SR5-PSD",
        "SR-005 allocated to PSD System",
        sr["SR5"]["id"],
        ss["PSD"]["id"],
    )

    # Activities enable hazards
    e(
        "ENABLES_HAZARD",
        "PBA-H2",
        "Passenger boarding and alighting enables H-002",
        ac["PBA"]["id"],
        haz["H2"]["id"],
    )
    e(
        "ENABLES_HAZARD",
        "EEV-H4",
        "Emergency evacuation context enables H-004",
        ac["EEV"]["id"],
        haz["H4"]["id"],
    )
    e(
        "ENABLES_HAZARD",
        "DMO-H1",
        "Degraded mode operation enables H-001",
        ac["DMO"]["id"],
        haz["H1"]["id"],
    )

    # -- GSN argument structure --
    # G1 supported by S1, in context of C1 C2 C3, assumes A1 A2
    e(
        "SUPPORTED_BY",
        "G1-S1",
        "G-001 supported by S-001",
        gsn_g["G1"]["id"],
        gsn_s["S1"]["id"],
    )
    e(
        "IN_CONTEXT_OF",
        "G1-C1",
        "G-001 in context of station boundary",
        gsn_g["G1"]["id"],
        gsn_c["C1"]["id"],
    )
    e(
        "IN_CONTEXT_OF",
        "G1-C2",
        "G-001 in context of ATO with PSD",
        gsn_g["G1"]["id"],
        gsn_c["C2"]["id"],
    )
    e(
        "IN_CONTEXT_OF",
        "G1-C3",
        "G-001 in context of passenger throughput",
        gsn_g["G1"]["id"],
        gsn_c["C3"]["id"],
    )
    e(
        "IN_ASSUMPTION_OF",
        "G1-A1",
        "G-001 assumes external train control safety case",
        gsn_g["G1"]["id"],
        gsn_a["A1"]["id"],
    )
    e(
        "IN_ASSUMPTION_OF",
        "G1-A2",
        "G-001 assumes civil structure compliance",
        gsn_g["G1"]["id"],
        gsn_a["A2"]["id"],
    )

    # S1 supported by Sn1 (STPA completeness) and sub-goals G2 G3 G4
    e(
        "SUPPORTED_BY",
        "S1-Sn1",
        "S-001 supported by Sn-001 (STPA report)",
        gsn_s["S1"]["id"],
        gsn_sn["Sn1"]["id"],
    )
    e(
        "SUPPORTED_BY",
        "S1-G2",
        "S-001 supported by G-002 (PSD risks)",
        gsn_s["S1"]["id"],
        gsn_g["G2"]["id"],
    )
    e(
        "SUPPORTED_BY",
        "S1-G3",
        "S-001 supported by G-003 (departure risks)",
        gsn_s["S1"]["id"],
        gsn_g["G3"]["id"],
    )
    e(
        "SUPPORTED_BY",
        "S1-G4",
        "S-001 supported by G-004 (evacuation)",
        gsn_s["S1"]["id"],
        gsn_g["G4"]["id"],
    )

    # G2 supported by S2 (PSD STPA argument)
    e(
        "SUPPORTED_BY",
        "G2-S2",
        "G-002 supported by S-002",
        gsn_g["G2"]["id"],
        gsn_s["S2"]["id"],
    )

    # S2 supported by G5 (SIL compliance) and Sn2 (verification)
    e(
        "SUPPORTED_BY",
        "S2-G5",
        "S-002 supported by G-005 (SIL 2)",
        gsn_s["S2"]["id"],
        gsn_g["G5"]["id"],
    )
    e(
        "SUPPORTED_BY",
        "S2-Sn3",
        "S-002 supported by Sn-003 (platform clear test)",
        gsn_s["S2"]["id"],
        gsn_sn["Sn3"]["id"],
    )

    # G5 supported by S3 (SIL verification argument)
    e(
        "SUPPORTED_BY",
        "G5-S3",
        "G-005 supported by S-003",
        gsn_g["G5"]["id"],
        gsn_s["S3"]["id"],
    )

    # S3 supported by Sn2 (SIL 2 verification)
    e(
        "SUPPORTED_BY",
        "S3-Sn2",
        "S-003 supported by Sn-002 (SIL 2 verification)",
        gsn_s["S3"]["id"],
        gsn_sn["Sn2"]["id"],
    )

    # G3 supported by Sn3 (platform clear test)
    e(
        "SUPPORTED_BY",
        "G3-Sn3",
        "G-003 supported by Sn-003",
        gsn_g["G3"]["id"],
        gsn_sn["Sn3"]["id"],
    )

    # G4 supported by Sn4 (ventilation test)
    e(
        "SUPPORTED_BY",
        "G4-Sn4",
        "G-004 supported by Sn-004",
        gsn_g["G4"]["id"],
        gsn_sn["Sn4"]["id"],
    )

    # GSN solutions evidenced by evidence items
    e(
        "EVIDENCED_BY",
        "Sn1-EV1",
        "Sn-001 evidenced by STPA report",
        gsn_sn["Sn1"]["id"],
        ev["EV1"]["id"],
    )
    e(
        "EVIDENCED_BY",
        "Sn2-EV2",
        "Sn-002 evidenced by PSD verification report",
        gsn_sn["Sn2"]["id"],
        ev["EV2"]["id"],
    )
    e(
        "EVIDENCED_BY",
        "Sn3-EV3",
        "Sn-003 evidenced by SCS functional test",
        gsn_sn["Sn3"]["id"],
        ev["EV3"]["id"],
    )
    e(
        "EVIDENCED_BY",
        "Sn4-EV4",
        "Sn-004 evidenced by EVS response time test",
        gsn_sn["Sn4"]["id"],
        ev["EV4"]["id"],
    )

    # Safety requirements verified by evidence
    e(
        "VERIFIED_BY",
        "SR1-EV2",
        "SR-001 verified by PSD verification report",
        sr["SR1"]["id"],
        ev["EV2"]["id"],
    )
    e(
        "VERIFIED_BY",
        "SR2-EV2",
        "SR-002 verified by PSD verification report",
        sr["SR2"]["id"],
        ev["EV2"]["id"],
    )
    e(
        "VERIFIED_BY",
        "SR3-EV3",
        "SR-003 verified by SCS functional test",
        sr["SR3"]["id"],
        ev["EV3"]["id"],
    )
    e(
        "VERIFIED_BY",
        "SR4-EV4",
        "SR-004 verified by EVS response time test",
        sr["SR4"]["id"],
        ev["EV4"]["id"],
    )

    # GSN goals address hazards and losses (cross-layer)
    e("ADDRESSES", "G2-H1", "G-002 addresses H-001", gsn_g["G2"]["id"], haz["H1"]["id"])
    e("ADDRESSES", "G2-H2", "G-002 addresses H-002", gsn_g["G2"]["id"], haz["H2"]["id"])
    e("ADDRESSES", "G3-H3", "G-003 addresses H-003", gsn_g["G3"]["id"], haz["H3"]["id"])
    e("ADDRESSES", "G4-H4", "G-004 addresses H-004", gsn_g["G4"]["id"], haz["H4"]["id"])
    e(
        "ADDRESSES",
        "G1-L1",
        "G-001 addresses L-001",
        gsn_g["G1"]["id"],
        loss["L1"]["id"],
    )
    e(
        "ADDRESSES",
        "G1-L2",
        "G-001 addresses L-002",
        gsn_g["G1"]["id"],
        loss["L2"]["id"],
    )
    e(
        "ADDRESSES",
        "G1-L3",
        "G-001 addresses L-003",
        gsn_g["G1"]["id"],
        loss["L3"]["id"],
    )

    # Evidence references architecture (cross-layer)
    e(
        "REFERENCES",
        "EV1-PSD",
        "STPA report references PSD System",
        ev["EV1"]["id"],
        ss["PSD"]["id"],
    )
    e(
        "REFERENCES",
        "EV1-SCS",
        "STPA report references Station Control System",
        ev["EV1"]["id"],
        ss["SCS"]["id"],
    )
    e(
        "REFERENCES",
        "EV2-PSD",
        "PSD verification report references PSD System",
        ev["EV2"]["id"],
        ss["PSD"]["id"],
    )
    e(
        "REFERENCES",
        "EV2-PCU",
        "PSD verification report references PSD Control Unit",
        ev["EV2"]["id"],
        pr["PCU"]["id"],
    )
    e(
        "REFERENCES",
        "EV3-SCS",
        "SCS test report references Station Control System",
        ev["EV3"]["id"],
        ss["SCS"]["id"],
    )
    e(
        "REFERENCES",
        "EV4-EVS",
        "EVS test report references Emergency Ventilation System",
        ev["EV4"]["id"],
        ss["EVS"]["id"],
    )
    e(
        "REFERENCES",
        "EV4-EFU",
        "EVS test report references Emergency Fan Unit",
        ev["EV4"]["id"],
        pr["EFU"]["id"],
    )

    print(f"  [OK] {edge_count} edges created")

    # -----------------------------------------------------------------------
    # 9. SUMMARY
    # -----------------------------------------------------------------------
    total_nodes = desc_count + analysis_count + arg_count

    print(
        f"""
==================================================
  Seed complete  City Cross Station

  Schema
  ------
  Node types       : {len(nt)} (20)
  Edge types       : {len(et)}
  Property defs    : {len(pd)}

  Nodes
  -----
  Total            : {total_nodes}

  Description layer (Uniclass)
    Complexes      : {len(co)}
    Entities       : {len(en)}
    Spaces         : {len(sp)}
    Elements       : {len(ef)}
    Systems        : {len(ss)}
    Products       : {len(pr)}
    Activities     : {len(ac)}
    Roles          : {len(ro)}

  Analysis layer (STPA + Requirements)
    Losses                   : {len(loss)}
    Hazards                  : {len(haz)}
    Control Actions          : {len(ca)}
    Undesirable Control Actions: {len(uca)}
    Loss Scenarios           : {len(ls)}
    Control Constraints      : {len(cc)}
    Requirements             : {len(sr)}

  Argument layer (GSN + Evidence)
    GSN Goals        : {len(gsn_g)}
    GSN Strategies   : {len(gsn_s)}
    GSN Solutions    : {len(gsn_sn)}
    GSN Contexts     : {len(gsn_c)}
    GSN Assumptions  : {len(gsn_a)}
    Evidence         : {len(ev)}

  Edges            : {edge_count}

  Open Tracer and explore the City Cross Station
  safety case graph.
==================================================
"""
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed Tracer with City Cross Station dataset "
        "(GSN + STPA + Uniclass schema)"
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--username", default=DEFAULT_USERNAME)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument(
        "--clean", action="store_true", help="Remove all existing data before seeding"
    )
    args = parser.parse_args()

    print("\nTracer seed  City Cross Station")
    print(f"Target : {args.base_url}")
    print(f"Schema : GSN + STPA + Uniclass 2015\n")

    client = TracerClient(args.base_url, args.username, args.password)

    if args.clean:
        clean(client)

    seed(client)
