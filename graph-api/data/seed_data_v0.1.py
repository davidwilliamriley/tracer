"""
seed_data.py  ATP Emergency Braking test dataset.

Loads a representative railway safety case dataset into a running Tracer
instance via the REST API. Covers:

  - System architecture (ATP subsystems and components)
  - Safety requirements (functional and integrity)
  - Hazards and controls with causal links
  - Goal Structuring Notation (goals, strategies, solutions, contexts)
  - Evidence items linked to GSN solutions and architecture

Domain: Automatic Train Protection  Emergency Braking Function
        Based loosely on EN 50128 / EN 50129 safety case structure

Usage:
    # Start the Tracer API first:
    cd graph-api && uvicorn main:app --reload

    # In another terminal:
    python seed_data.py

    # Optional: target a different host
    python seed_data.py --base-url http://yourserver:8000

Configuration:
    BASE_URL    Tracer API base URL (default: http://localhost:8000)
    USERNAME    admin username (default: admin)
    PASSWORD    admin password (default: tracer-dev-password)
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
# API client
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
        # 404 is fine  already gone
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
    return client.post("/node-types/", {
        "node_type_identifier": identifier,
        "node_type_name": name,
        "node_type_description": description,
        "created_by": "seed",
    })

def create_edge_type(client, identifier, name, description):
    return client.post("/edge-types/", {
        "edge_type_identifier": identifier,
        "edge_type_name": name,
        "edge_type_description": description,
        "created_by": "seed",
    })

def create_prop_def(client, identifier, name, prop_type, description="", default_value=None):
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

def assign_prop(client, node_type_id, prop_def_id, is_required, sort_order, default_value=None):
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
    return client.post("/nodes/", {
        "node_type_id_fk": node_type_id,
        "node_identifier": identifier,
        "node_name": name,
        "created_by": created_by,
    })

def set_properties(client, node_id, prop_values: dict):
    """prop_values: {definition_id: value_string}"""
    properties = [
        {"definition_id": def_id, "value": value}
        for def_id, value in prop_values.items()
    ]
    return client.post(f"/nodes/{node_id}/properties", {
        "properties": properties,
        "modified_by": "seed",
    })

def create_edge(client, edge_type_id, identifier, name, source_id, target_id):
    return client.post("/edges/", {
        "edge_type_id_fk": edge_type_id,
        "edge_identifier": identifier,
        "edge_name": name,
        "source_node_id_fk": source_id,
        "target_node_id_fk": target_id,
        "created_by": "seed",
    })


# ---------------------------------------------------------------------------
# Main seed function
# ---------------------------------------------------------------------------

def clean(client):
    """Remove all existing data in dependency order."""
    print("\n-- Cleaning existing data")

    # Edges first
    edges = client.get_all("/edges/")
    for e in edges:
        client.delete(f"/edges/{e['id']}")
    print(f"  [OK] {len(edges)} edges removed")

    # Nodes
    nodes = client.get_all("/nodes/")
    for n in nodes:
        client.delete(f"/nodes/{n['id']}")
    print(f"  [OK] {len(nodes)} nodes removed")

    # Assignments before types
    for path in ["/node-type-property-assignments/", "/edge-type-property-assignments/"]:
        items = client.get_all(path)
        for item in items:
            client.delete(f"{path}{item['id']}")

    # Property definitions
    for path in ["/node-property-definitions/", "/edge-property-definitions/"]:
        items = client.get_all(path)
        for item in items:
            client.delete(f"{path}{item['id']}")
    print(f"  [OK] Property definitions removed")

    # Types
    nts = client.get_all("/node-types/")
    for nt in nts:
        client.delete(f"/node-types/{nt['id']}")

    ets = client.get_all("/edge-types/")
    for et in ets:
        client.delete(f"/edge-types/{et['id']}")
    print(f"  [OK] Node/edge types removed")



def seed(client):

    # -----------------------------------------------------------------------
    # STEP 1  Node types
    # -----------------------------------------------------------------------
    print("\n-- Node types")

    nt = {}

    nt["ARCH_ELEMENT"] = create_node_type(client,
        "ARCH_ELEMENT", "Architecture Element",
        "A subsystem or component in the ATP system architecture")
    print(f"  [OK] ARCH_ELEMENT")

    nt["SAFETY_REQ"] = create_node_type(client,
        "SAFETY_REQ", "Safety Requirement",
        "A functional or integrity safety requirement derived from hazard analysis")
    print(f"  [OK] SAFETY_REQ")

    nt["HAZARD"] = create_node_type(client,
        "HAZARD", "Hazard",
        "A system state or condition that could lead to an accident")
    print(f"  [OK] HAZARD")

    nt["CONTROL"] = create_node_type(client,
        "CONTROL", "Control Measure",
        "A design or operational measure that reduces the likelihood or severity of a hazard")
    print(f"  [OK] CONTROL")

    nt["GSN_GOAL"] = create_node_type(client,
        "GSN_GOAL", "GSN Goal",
        "A claim that must be supported  the top-level safety claim or a sub-claim")
    print(f"  [OK] GSN_GOAL")

    nt["GSN_STRATEGY"] = create_node_type(client,
        "GSN_STRATEGY", "GSN Strategy",
        "An approach taken to support a goal  describes how the argument is structured")
    print(f"  [OK] GSN_STRATEGY")

    nt["GSN_SOLUTION"] = create_node_type(client,
        "GSN_SOLUTION", "GSN Solution",
        "A leaf node  references evidence that directly supports a goal")
    print(f"  [OK] GSN_SOLUTION")

    nt["GSN_CONTEXT"] = create_node_type(client,
        "GSN_CONTEXT", "GSN Context",
        "Background information that scopes or qualifies a goal or strategy")
    print(f"  [OK] GSN_CONTEXT")

    nt["EVIDENCE"] = create_node_type(client,
        "EVIDENCE", "Evidence Item",
        "A document, test result, analysis or record that provides objective evidence")
    print(f"  [OK] EVIDENCE")


    # -----------------------------------------------------------------------
    # STEP 2  Edge types
    # -----------------------------------------------------------------------
    print("\n-- Edge types")

    et = {}

    et["ALLOCATED_TO"] = create_edge_type(client,
        "ALLOCATED_TO", "Allocated To",
        "A safety requirement is allocated to an architecture element for implementation")
    print(f"  [OK] ALLOCATED_TO")

    et["AFFECTS"] = create_edge_type(client,
        "AFFECTS", "Affects",
        "A hazard affects an architecture element  i.e. the element is a contributor or victim")
    print(f"  [OK] AFFECTS")

    et["MITIGATED_BY"] = create_edge_type(client,
        "MITIGATED_BY", "Mitigated By",
        "A hazard is mitigated by a control measure")
    print(f"  [OK] MITIGATED_BY")

    et["IMPLEMENTED_BY"] = create_edge_type(client,
        "IMPLEMENTED_BY", "Implemented By",
        "A control measure is implemented by an architecture element")
    print(f"  [OK] IMPLEMENTED_BY")

    et["CAUSES"] = create_edge_type(client,
        "CAUSES", "Causes",
        "One hazard causes or contributes to another hazard")
    print(f"  [OK] CAUSES")

    et["SUPPORTED_BY"] = create_edge_type(client,
        "SUPPORTED_BY", "Supported By",
        "GSN: a goal or strategy is supported by a sub-goal, strategy, or solution")
    print(f"  [OK] SUPPORTED_BY")

    et["IN_CONTEXT_OF"] = create_edge_type(client,
        "IN_CONTEXT_OF", "In Context Of",
        "GSN: a goal or strategy is scoped by a context node")
    print(f"  [OK] IN_CONTEXT_OF")

    et["EVIDENCED_BY"] = create_edge_type(client,
        "EVIDENCED_BY", "Evidenced By",
        "A GSN solution or requirement references an evidence item")
    print(f"  [OK] EVIDENCED_BY")

    et["REFERENCES"] = create_edge_type(client,
        "REFERENCES", "References",
        "An evidence item references an architecture element (e.g. a test covers a component)")
    print(f"  [OK] REFERENCES")

    et["DERIVED_FROM"] = create_edge_type(client,
        "DERIVED_FROM", "Derived From",
        "A safety requirement is derived from a higher-level requirement or goal")
    print(f"  [OK] DERIVED_FROM")


    # -----------------------------------------------------------------------
    # STEP 3  Property definitions
    # -----------------------------------------------------------------------
    print("\n-- Property definitions")

    pd = {}

    # Shared across multiple types
    pd["IDENTIFIER"]  = create_prop_def(client, "IDENTIFIER",  "Identifier",  "string",  "Unique document or item identifier")
    pd["STATUS"]      = create_prop_def(client, "STATUS",      "Status",      "string",  "Lifecycle status", "Draft")
    pd["VERSION"]     = create_prop_def(client, "VERSION",     "Version",     "string",  "Document or item version", "0.1")
    pd["AUTHOR"]      = create_prop_def(client, "AUTHOR",      "Author",      "string",  "Person responsible for this item")
    pd["DESCRIPTION"] = create_prop_def(client, "DESCRIPTION", "Description", "string",  "Detailed description")
    pd["SOURCE_DOC"]  = create_prop_def(client, "SOURCE_DOC",  "Source Document", "string", "Document this item originates from")
    pd["RATIONALE"]   = create_prop_def(client, "RATIONALE",   "Rationale",   "string",  "Justification or reasoning")
    pd["NOTES"]       = create_prop_def(client, "NOTES",       "Notes",       "string",  "Additional notes or comments")

    # Architecture element properties
    pd["ARCH_LEVEL"]  = create_prop_def(client, "ARCH_LEVEL",  "Architecture Level", "string",
        "Level in the architecture hierarchy e.g. System, Subsystem, Component")
    pd["SIL_LEVEL"]   = create_prop_def(client, "SIL_LEVEL",   "SIL Level",   "string",
        "Safety Integrity Level assigned to this element (SIL 0-4 per EN 50129)")
    pd["TECH_TYPE"]   = create_prop_def(client, "TECH_TYPE",   "Technology Type", "string",
        "Implementation technology e.g. Hardware, Software, Firmware, Procedure")

    # Safety requirement properties
    pd["REQ_TYPE"]    = create_prop_def(client, "REQ_TYPE",    "Requirement Type", "string",
        "Functional, Performance, Interface, or Integrity")
    pd["SIL_TARGET"]  = create_prop_def(client, "SIL_TARGET",  "SIL Target",  "string",
        "Target SIL level for this requirement")
    pd["VERIF_METHOD"] = create_prop_def(client, "VERIF_METHOD", "Verification Method", "string",
        "How this requirement will be verified e.g. Test, Analysis, Inspection, Demonstration")

    # Hazard properties
    pd["HAZARD_CLASS"] = create_prop_def(client, "HAZARD_CLASS", "Hazard Class", "string",
        "Classification of hazard type e.g. Loss of Function, Inadvertent Activation")
    pd["SEVERITY"]    = create_prop_def(client, "SEVERITY",    "Severity",    "string",
        "Consequence severity: Catastrophic, Critical, Marginal, Negligible")
    pd["LIKELIHOOD"]  = create_prop_def(client, "LIKELIHOOD",  "Likelihood",  "string",
        "Frequency classification: Frequent, Probable, Occasional, Remote, Improbable")
    pd["RISK_LEVEL"]  = create_prop_def(client, "RISK_LEVEL",  "Risk Level",  "string",
        "Unmitigated risk level: Intolerable, ALARP, Broadly Acceptable")

    # Control properties
    pd["CONTROL_TYPE"] = create_prop_def(client, "CONTROL_TYPE", "Control Type", "string",
        "Prevention, Detection, Mitigation, or Recovery")
    pd["EFFECTIVENESS"] = create_prop_def(client, "EFFECTIVENESS", "Effectiveness", "string",
        "High, Medium, or Low  assessed effectiveness of this control")

    # GSN properties
    pd["GSN_ID"]      = create_prop_def(client, "GSN_ID",      "GSN ID",      "string",
        "GSN node reference e.g. G1, S1, Sn1, C1")
    pd["CLAIM_TEXT"]  = create_prop_def(client, "CLAIM_TEXT",  "Claim Text",  "string",
        "The full text of the goal claim or strategy description")
    pd["DECOMP_BASIS"] = create_prop_def(client, "DECOMP_BASIS", "Decomposition Basis", "string",
        "The basis on which this goal or strategy is decomposed")
    pd["UNDISCHARGED"] = create_prop_def(client, "UNDISCHARGED", "Undischarged", "boolean",
        "True if this solution or goal has not yet been fully evidenced", "false")

    # Evidence properties
    pd["DOC_REF"]     = create_prop_def(client, "DOC_REF",     "Document Reference", "string",
        "Formal document reference number")
    pd["DOC_TYPE"]    = create_prop_def(client, "DOC_TYPE",    "Document Type", "string",
        "Test Report, Analysis Report, Inspection Record, Design Document, Standard")
    pd["EVIDENCE_DATE"] = create_prop_def(client, "EVIDENCE_DATE", "Evidence Date", "date",
        "Date the evidence was produced or approved")
    pd["APPROVED_BY"] = create_prop_def(client, "APPROVED_BY", "Approved By",  "string",
        "Name of approver or approving authority")

    print(f"  [OK] {len(pd)} property definitions created")


    # -----------------------------------------------------------------------
    # STEP 4  Assign properties to node types
    # -----------------------------------------------------------------------
    print("\n-- Property assignments")

    # Architecture Element
    for i, (key, req) in enumerate([
        ("IDENTIFIER", True), ("ARCH_LEVEL", True), ("SIL_LEVEL", False),
        ("TECH_TYPE", False), ("STATUS", False), ("DESCRIPTION", False),
        ("RATIONALE", False), ("NOTES", False),
    ]):
        assign_prop(client, nt["ARCH_ELEMENT"]["id"], pd[key]["id"], req, i)

    # Safety Requirement
    for i, (key, req) in enumerate([
        ("IDENTIFIER", True), ("REQ_TYPE", True), ("SIL_TARGET", False),
        ("VERIF_METHOD", False), ("STATUS", False), ("SOURCE_DOC", False),
        ("DESCRIPTION", False), ("RATIONALE", False), ("NOTES", False),
    ]):
        assign_prop(client, nt["SAFETY_REQ"]["id"], pd[key]["id"], req, i)

    # Hazard
    for i, (key, req) in enumerate([
        ("IDENTIFIER", True), ("HAZARD_CLASS", False), ("SEVERITY", True),
        ("LIKELIHOOD", False), ("RISK_LEVEL", False), ("STATUS", False),
        ("DESCRIPTION", False), ("NOTES", False),
    ]):
        assign_prop(client, nt["HAZARD"]["id"], pd[key]["id"], req, i)

    # Control
    for i, (key, req) in enumerate([
        ("IDENTIFIER", True), ("CONTROL_TYPE", True), ("EFFECTIVENESS", False),
        ("STATUS", False), ("DESCRIPTION", False), ("RATIONALE", False), ("NOTES", False),
    ]):
        assign_prop(client, nt["CONTROL"]["id"], pd[key]["id"], req, i)

    # GSN Goal
    for i, (key, req) in enumerate([
        ("GSN_ID", True), ("CLAIM_TEXT", True), ("STATUS", False),
        ("DECOMP_BASIS", False), ("RATIONALE", False), ("NOTES", False),
    ]):
        assign_prop(client, nt["GSN_GOAL"]["id"], pd[key]["id"], req, i)

    # GSN Strategy
    for i, (key, req) in enumerate([
        ("GSN_ID", True), ("CLAIM_TEXT", True), ("DECOMP_BASIS", True),
        ("STATUS", False), ("RATIONALE", False), ("NOTES", False),
    ]):
        assign_prop(client, nt["GSN_STRATEGY"]["id"], pd[key]["id"], req, i)

    # GSN Solution
    for i, (key, req) in enumerate([
        ("GSN_ID", True), ("CLAIM_TEXT", True), ("UNDISCHARGED", False),
        ("STATUS", False), ("NOTES", False),
    ]):
        assign_prop(client, nt["GSN_SOLUTION"]["id"], pd[key]["id"], req, i)

    # GSN Context
    for i, (key, req) in enumerate([
        ("GSN_ID", True), ("CLAIM_TEXT", True), ("SOURCE_DOC", False), ("NOTES", False),
    ]):
        assign_prop(client, nt["GSN_CONTEXT"]["id"], pd[key]["id"], req, i)

    # Evidence
    for i, (key, req) in enumerate([
        ("IDENTIFIER", True), ("DOC_REF", True), ("DOC_TYPE", True),
        ("EVIDENCE_DATE", False), ("APPROVED_BY", False), ("STATUS", False),
        ("DESCRIPTION", False), ("VERSION", False), ("NOTES", False),
    ]):
        assign_prop(client, nt["EVIDENCE"]["id"], pd[key]["id"], req, i)

    print(f"  [OK] Properties assigned to all node types")


    # -----------------------------------------------------------------------
    # STEP 5  Architecture nodes
    # -----------------------------------------------------------------------
    print("\n-- Architecture elements")

    arch = {}

    arch["ATP_SYS"] = create_node(client, nt["ARCH_ELEMENT"]["id"],
        "ATP-SYS-001", "ATP System")
    arch["EB_FUNC"] = create_node(client, nt["ARCH_ELEMENT"]["id"],
        "ATP-SYS-002", "Emergency Braking Function")
    arch["SPEED_MON"] = create_node(client, nt["ARCH_ELEMENT"]["id"],
        "ATP-SUB-001", "Speed Monitoring Subsystem")
    arch["BRAKE_CMD"] = create_node(client, nt["ARCH_ELEMENT"]["id"],
        "ATP-SUB-002", "Brake Command Subsystem")
    arch["TRACK_INT"] = create_node(client, nt["ARCH_ELEMENT"]["id"],
        "ATP-SUB-003", "Track Interface Subsystem")
    arch["SPEED_SENS"] = create_node(client, nt["ARCH_ELEMENT"]["id"],
        "ATP-COM-001", "Speed Sensor Assembly")
    arch["BRAKE_ACT"] = create_node(client, nt["ARCH_ELEMENT"]["id"],
        "ATP-COM-002", "Brake Actuator Interface")
    arch["ATP_CPU"] = create_node(client, nt["ARCH_ELEMENT"]["id"],
        "ATP-COM-003", "ATP Processing Unit")
    arch["BALISE_RDR"] = create_node(client, nt["ARCH_ELEMENT"]["id"],
        "ATP-COM-004", "Balise Reader")
    arch["WATCHDOG"] = create_node(client, nt["ARCH_ELEMENT"]["id"],
        "ATP-COM-005", "Watchdog Timer")

    # Set architecture properties
    arch_props = {
        "ATP_SYS":    ("System",    "SIL 4", "System",   "Approved"),
        "EB_FUNC":    ("Function",  "SIL 4", "Software", "Approved"),
        "SPEED_MON":  ("Subsystem", "SIL 4", "Software", "Approved"),
        "BRAKE_CMD":  ("Subsystem", "SIL 4", "Firmware", "Approved"),
        "TRACK_INT":  ("Subsystem", "SIL 3", "Hardware", "Approved"),
        "SPEED_SENS": ("Component", "SIL 4", "Hardware", "Approved"),
        "BRAKE_ACT":  ("Component", "SIL 4", "Hardware", "In Review"),
        "ATP_CPU":    ("Component", "SIL 4", "Hardware", "Approved"),
        "BALISE_RDR": ("Component", "SIL 3", "Hardware", "Approved"),
        "WATCHDOG":   ("Component", "SIL 4", "Hardware", "Approved"),
    }

    for key, (level, sil, tech, status) in arch_props.items():
        set_properties(client, arch[key]["id"], {
            pd["IDENTIFIER"]["id"]:  arch[key]["node_identifier"],
            pd["ARCH_LEVEL"]["id"]:  level,
            pd["SIL_LEVEL"]["id"]:   sil,
            pd["TECH_TYPE"]["id"]:   tech,
            pd["STATUS"]["id"]:      status,
        })

    print(f"  [OK] {len(arch)} architecture elements created")


    # -----------------------------------------------------------------------
    # STEP 6  Safety requirements
    # -----------------------------------------------------------------------
    print("\n-- Safety requirements")

    req = {}

    req["SR001"] = create_node(client, nt["SAFETY_REQ"]["id"],
        "SR-001", "The ATP system shall apply emergency braking when train speed exceeds the permitted speed profile")
    req["SR002"] = create_node(client, nt["SAFETY_REQ"]["id"],
        "SR-002", "The ATP system shall initiate emergency braking within 2 seconds of detecting an overspeed condition")
    req["SR003"] = create_node(client, nt["SAFETY_REQ"]["id"],
        "SR-003", "The speed monitoring function shall be implemented to SIL 4 in accordance with EN 50128")
    req["SR004"] = create_node(client, nt["SAFETY_REQ"]["id"],
        "SR-004", "The brake command output shall remain active until train speed is confirmed below 5 km/h")
    req["SR005"] = create_node(client, nt["SAFETY_REQ"]["id"],
        "SR-005", "The ATP system shall detect failures in the speed sensor assembly within one processing cycle")
    req["SR006"] = create_node(client, nt["SAFETY_REQ"]["id"],
        "SR-006", "On detection of any safety-critical failure the ATP system shall default to emergency braking")
    req["SR007"] = create_node(client, nt["SAFETY_REQ"]["id"],
        "SR-007", "The track interface subsystem shall validate balise telegrams against a known-good checksum")
    req["SR008"] = create_node(client, nt["SAFETY_REQ"]["id"],
        "SR-008", "The ATP processing unit shall execute the speed comparison function at no less than 100ms cycle time")

    req_props = {
        "SR001": ("Functional",  "SIL 4", "Test",       "Approved",  "SYSTEM-SPEC-001"),
        "SR002": ("Performance", "SIL 4", "Test",       "Approved",  "SYSTEM-SPEC-001"),
        "SR003": ("Integrity",   "SIL 4", "Inspection", "Approved",  "SAFETY-PLAN-001"),
        "SR004": ("Functional",  "SIL 4", "Test",       "Approved",  "SYSTEM-SPEC-001"),
        "SR005": ("Functional",  "SIL 4", "Analysis",   "In Review", "HAZARD-LOG-001"),
        "SR006": ("Functional",  "SIL 4", "Test",       "Approved",  "HAZARD-LOG-001"),
        "SR007": ("Functional",  "SIL 3", "Test",       "Approved",  "SYSTEM-SPEC-002"),
        "SR008": ("Performance", "SIL 4", "Test",       "Draft",     "SYSTEM-SPEC-001"),
    }

    for key, (rtype, sil, verif, status, src) in req_props.items():
        set_properties(client, req[key]["id"], {
            pd["IDENTIFIER"]["id"]:    req[key]["node_identifier"],
            pd["REQ_TYPE"]["id"]:      rtype,
            pd["SIL_TARGET"]["id"]:    sil,
            pd["VERIF_METHOD"]["id"]:  verif,
            pd["STATUS"]["id"]:        status,
            pd["SOURCE_DOC"]["id"]:    src,
        })

    print(f"  [OK] {len(req)} safety requirements created")


    # -----------------------------------------------------------------------
    # STEP 7  Hazards
    # -----------------------------------------------------------------------
    print("\n-- Hazards")

    haz = {}

    haz["H001"] = create_node(client, nt["HAZARD"]["id"],
        "H-001", "Failure to apply emergency braking on overspeed")
    haz["H002"] = create_node(client, nt["HAZARD"]["id"],
        "H-002", "Delayed application of emergency braking")
    haz["H003"] = create_node(client, nt["HAZARD"]["id"],
        "H-003", "Erroneous speed measurement causing spurious braking")
    haz["H004"] = create_node(client, nt["HAZARD"]["id"],
        "H-004", "Loss of communication with track infrastructure")
    haz["H005"] = create_node(client, nt["HAZARD"]["id"],
        "H-005", "Undetected failure of ATP processing unit")
    haz["H006"] = create_node(client, nt["HAZARD"]["id"],
        "H-006", "Corruption of permitted speed profile data")
    haz["H007"] = create_node(client, nt["HAZARD"]["id"],
        "H-007", "Inadvertent release of emergency brakes before safe speed")

    haz_props = {
        "H001": ("Loss of Function",       "Catastrophic", "Remote",      "Intolerable", "Approved"),
        "H002": ("Loss of Function",       "Catastrophic", "Occasional",  "Intolerable", "Approved"),
        "H003": ("Inadvertent Activation", "Marginal",     "Probable",    "ALARP",       "Approved"),
        "H004": ("Loss of Function",       "Critical",     "Occasional",  "Intolerable", "Approved"),
        "H005": ("Loss of Function",       "Catastrophic", "Remote",      "Intolerable", "In Review"),
        "H006": ("Incorrect Output",       "Catastrophic", "Improbable",  "ALARP",       "Approved"),
        "H007": ("Inadvertent Activation", "Critical",     "Remote",      "ALARP",       "Draft"),
    }

    for key, (hclass, severity, likelihood, risk, status) in haz_props.items():
        set_properties(client, haz[key]["id"], {
            pd["IDENTIFIER"]["id"]:   haz[key]["node_identifier"],
            pd["HAZARD_CLASS"]["id"]: hclass,
            pd["SEVERITY"]["id"]:     severity,
            pd["LIKELIHOOD"]["id"]:   likelihood,
            pd["RISK_LEVEL"]["id"]:   risk,
            pd["STATUS"]["id"]:       status,
        })

    print(f"  [OK] {len(haz)} hazards created")


    # -----------------------------------------------------------------------
    # STEP 8  Controls
    # -----------------------------------------------------------------------
    print("\n-- Controls")

    ctrl = {}

    ctrl["C001"] = create_node(client, nt["CONTROL"]["id"],
        "C-001", "Dual redundant speed sensor channels with cross-comparison")
    ctrl["C002"] = create_node(client, nt["CONTROL"]["id"],
        "C-002", "Watchdog timer to detect ATP CPU lockup or hang")
    ctrl["C003"] = create_node(client, nt["CONTROL"]["id"],
        "C-003", "Fail-safe output  brake command defaults to active on loss of signal")
    ctrl["C004"] = create_node(client, nt["CONTROL"]["id"],
        "C-004", "Balise telegram checksum validation with error detection")
    ctrl["C005"] = create_node(client, nt["CONTROL"]["id"],
        "C-005", "Speed measurement plausibility check against acceleration limits")
    ctrl["C006"] = create_node(client, nt["CONTROL"]["id"],
        "C-006", "Permitted speed profile stored with CRC integrity check")
    ctrl["C007"] = create_node(client, nt["CONTROL"]["id"],
        "C-007", "Brake release interlock  speed must be below threshold for defined hold period")

    ctrl_props = {
        "C001": ("Detection",   "High",   "Approved"),
        "C002": ("Detection",   "High",   "Approved"),
        "C003": ("Prevention",  "High",   "Approved"),
        "C004": ("Detection",   "High",   "Approved"),
        "C005": ("Detection",   "Medium", "Approved"),
        "C006": ("Prevention",  "High",   "In Review"),
        "C007": ("Prevention",  "High",   "Draft"),
    }

    for key, (ctype, eff, status) in ctrl_props.items():
        set_properties(client, ctrl[key]["id"], {
            pd["IDENTIFIER"]["id"]:   ctrl[key]["node_identifier"],
            pd["CONTROL_TYPE"]["id"]: ctype,
            pd["EFFECTIVENESS"]["id"]: eff,
            pd["STATUS"]["id"]:       status,
        })

    print(f"  [OK] {len(ctrl)} controls created")


    # -----------------------------------------------------------------------
    # STEP 9  GSN nodes
    # -----------------------------------------------------------------------
    print("\n-- GSN nodes")

    gsn = {}

    # Top level goal
    gsn["G1"] = create_node(client, nt["GSN_GOAL"]["id"],
        "G1", "The ATP Emergency Braking function is acceptably safe for operation on Network Rail infrastructure")
    gsn["G2"] = create_node(client, nt["GSN_GOAL"]["id"],
        "G2", "All identified hazards have been reduced to tolerable risk levels")
    gsn["G3"] = create_node(client, nt["GSN_GOAL"]["id"],
        "G3", "All SIL 4 safety requirements have been implemented and verified")
    gsn["G4"] = create_node(client, nt["GSN_GOAL"]["id"],
        "G4", "H-001 Failure to apply emergency braking has been reduced to tolerable risk")
    gsn["G5"] = create_node(client, nt["GSN_GOAL"]["id"],
        "G5", "H-002 Delayed braking has been reduced to tolerable risk")
    gsn["G6"] = create_node(client, nt["GSN_GOAL"]["id"],
        "G6", "The speed monitoring subsystem meets SIL 4 requirements")
    gsn["G7"] = create_node(client, nt["GSN_GOAL"]["id"],
        "G7", "The brake command subsystem meets SIL 4 requirements")

    # Strategies
    gsn["S1"] = create_node(client, nt["GSN_STRATEGY"]["id"],
        "S1", "Argument over completeness of hazard identification and risk reduction")
    gsn["S2"] = create_node(client, nt["GSN_STRATEGY"]["id"],
        "S2", "Argument by hazard  each identified hazard addressed individually")
    gsn["S3"] = create_node(client, nt["GSN_STRATEGY"]["id"],
        "S3", "Argument over SIL 4 development lifecycle compliance per EN 50128")

    # Solutions (leaf nodes  point to evidence)
    gsn["Sn1"] = create_node(client, nt["GSN_SOLUTION"]["id"],
        "Sn1", "Hazard log shows all hazards identified and risk assessed")
    gsn["Sn2"] = create_node(client, nt["GSN_SOLUTION"]["id"],
        "Sn2", "Risk assessment shows H-001 residual risk within tolerable region")
    gsn["Sn3"] = create_node(client, nt["GSN_SOLUTION"]["id"],
        "Sn3", "Integration test report confirms emergency braking response time < 2s")
    gsn["Sn4"] = create_node(client, nt["GSN_SOLUTION"]["id"],
        "Sn4", "SIL 4 assessment report for speed monitoring subsystem")
    gsn["Sn5"] = create_node(client, nt["GSN_SOLUTION"]["id"],
        "Sn5", "Verification test report for SR-001 and SR-004")
    gsn["Sn6"] = create_node(client, nt["GSN_SOLUTION"]["id"],
        "Sn6", "FMEA report for ATP processing unit showing failure modes bounded")

    # Contexts
    gsn["C1"] = create_node(client, nt["GSN_CONTEXT"]["id"],
        "C1", "System boundary: ATP on-board unit  does not cover wayside or RBC")
    gsn["C2"] = create_node(client, nt["GSN_CONTEXT"]["id"],
        "C2", "Applicable standards: EN 50126, EN 50128, EN 50129, GERT8075")
    gsn["C3"] = create_node(client, nt["GSN_CONTEXT"]["id"],
        "C3", "Operating environment: Mainline passenger operations, max 125 mph")

    gsn_goal_props = {
        "G1":  ("G1",  "Approved",  "By hazard analysis and SIL compliance"),
        "G2":  ("G2",  "Approved",  "Argument over hazard log completeness"),
        "G3":  ("G3",  "In Review", "Argument over verification evidence"),
        "G4":  ("G4",  "Approved",  "By control measure effectiveness"),
        "G5":  ("G5",  "Approved",  "By timing analysis and testing"),
        "G6":  ("G6",  "In Review", "By SIL assessment"),
        "G7":  ("G7",  "Draft",     "By SIL assessment"),
    }
    for key, (gsn_id, status, rationale) in gsn_goal_props.items():
        set_properties(client, gsn[key]["id"], {
            pd["GSN_ID"]["id"]:    gsn_id,
            pd["STATUS"]["id"]:    status,
            pd["RATIONALE"]["id"]: rationale,
            pd["CLAIM_TEXT"]["id"]: gsn[key]["node_name"],
        })

    gsn_strat_props = {
        "S1": ("S1", "Argument over completeness of hazard identification and risk reduction",
               "Systematic hazard identification using HAZOP and FMEA",  "Approved"),
        "S2": ("S2", "Argument by hazard  each identified hazard addressed individually",
               "One sub-goal per hazard in the hazard log",              "Approved"),
        "S3": ("S3", "Argument over SIL 4 development lifecycle compliance per EN 50128",
               "Argument by lifecycle phase per EN 50128 Table A.1",     "In Review"),
    }
    for key, (gsn_id, claim, decomp, status) in gsn_strat_props.items():
        set_properties(client, gsn[key]["id"], {
            pd["GSN_ID"]["id"]:        gsn_id,
            pd["CLAIM_TEXT"]["id"]:    claim,
            pd["DECOMP_BASIS"]["id"]:  decomp,
            pd["STATUS"]["id"]:        status,
        })

    gsn_soln_props = {
        "Sn1": ("Sn1", "false", "Approved"),
        "Sn2": ("Sn2", "false", "Approved"),
        "Sn3": ("Sn3", "false", "Approved"),
        "Sn4": ("Sn4", "true",  "In Review"),
        "Sn5": ("Sn5", "false", "Approved"),
        "Sn6": ("Sn6", "false", "Approved"),
    }
    for key, (gsn_id, undisch, status) in gsn_soln_props.items():
        set_properties(client, gsn[key]["id"], {
            pd["GSN_ID"]["id"]:       gsn_id,
            pd["CLAIM_TEXT"]["id"]:   gsn[key]["node_name"],
            pd["UNDISCHARGED"]["id"]: undisch,
            pd["STATUS"]["id"]:       status,
        })

    for key, (gsn_id, src) in [
        ("C1", ("C1", "ATP-SCOPE-DOC-001")),
        ("C2", ("C2", "ATP-STDS-LIST-001")),
        ("C3", ("C3", "ATP-ODD-001")),
    ]:
        set_properties(client, gsn[key]["id"], {
            pd["GSN_ID"]["id"]:      gsn_id,
            pd["CLAIM_TEXT"]["id"]:  gsn[key]["node_name"],
            pd["SOURCE_DOC"]["id"]:  src,
        })

    print(f"  [OK] {len(gsn)} GSN nodes created")


    # -----------------------------------------------------------------------
    # STEP 10  Evidence items
    # -----------------------------------------------------------------------
    print("\n-- Evidence items")

    ev = {}

    ev["EV001"] = create_node(client, nt["EVIDENCE"]["id"],
        "EV-001", "ATP System Hazard Log")
    ev["EV002"] = create_node(client, nt["EVIDENCE"]["id"],
        "EV-002", "Emergency Braking Integration Test Report")
    ev["EV003"] = create_node(client, nt["EVIDENCE"]["id"],
        "EV-003", "Speed Monitoring Subsystem SIL 4 Assessment")
    ev["EV004"] = create_node(client, nt["EVIDENCE"]["id"],
        "EV-004", "ATP System FMEA Report")
    ev["EV005"] = create_node(client, nt["EVIDENCE"]["id"],
        "EV-005", "SR-001 and SR-004 Verification Test Report")
    ev["EV006"] = create_node(client, nt["EVIDENCE"]["id"],
        "EV-006", "Brake Command Subsystem Design Specification")
    ev["EV007"] = create_node(client, nt["EVIDENCE"]["id"],
        "EV-007", "Track Interface Subsystem Validation Report")
    ev["EV008"] = create_node(client, nt["EVIDENCE"]["id"],
        "EV-008", "ATP Software V&V Report  EN 50128 Compliance")

    ev_props = {
        "EV001": ("ATP-HL-001",   "Analysis Report",  "2024-03-15", "Approved", "J. Smith"),
        "EV002": ("ATP-ITR-001",  "Test Report",      "2024-06-20", "Approved", "A. Jones"),
        "EV003": ("ATP-SIL-001",  "Analysis Report",  "2024-04-10", "In Review","T. Brown"),
        "EV004": ("ATP-FMEA-001", "Analysis Report",  "2024-02-28", "Approved", "J. Smith"),
        "EV005": ("ATP-VTR-001",  "Test Report",      "2024-07-05", "Approved", "A. Jones"),
        "EV006": ("ATP-DES-002",  "Design Document",  "2024-01-20", "Approved", "M. Davis"),
        "EV007": ("ATP-VAL-001",  "Test Report",      "2024-05-12", "Approved", "T. Brown"),
        "EV008": ("ATP-VV-001",   "Analysis Report",  "2024-08-01", "In Review","J. Smith"),
    }

    for key, (doc_ref, doc_type, ev_date, status, approved) in ev_props.items():
        set_properties(client, ev[key]["id"], {
            pd["IDENTIFIER"]["id"]:     ev[key]["node_identifier"],
            pd["DOC_REF"]["id"]:        doc_ref,
            pd["DOC_TYPE"]["id"]:       doc_type,
            pd["EVIDENCE_DATE"]["id"]:  ev_date,
            pd["STATUS"]["id"]:         status,
            pd["APPROVED_BY"]["id"]:    approved,
        })

    print(f"  [OK] {len(ev)} evidence items created")


    # -----------------------------------------------------------------------
    # STEP 11  Edges
    # -----------------------------------------------------------------------
    print("\n-- Edges")
    edge_count = 0

    # Architecture hierarchy
    arch_hier = [
        ("EB_FUNC",   "ATP_SYS",   "ATP-SYS-001 contains Emergency Braking Function"),
        ("SPEED_MON", "EB_FUNC",   "EB Function decomposes to Speed Monitoring"),
        ("BRAKE_CMD", "EB_FUNC",   "EB Function decomposes to Brake Command"),
        ("TRACK_INT", "EB_FUNC",   "EB Function decomposes to Track Interface"),
        ("SPEED_SENS","SPEED_MON", "Speed Monitoring contains Speed Sensor Assembly"),
        ("ATP_CPU",   "SPEED_MON", "Speed Monitoring contains ATP Processing Unit"),
        ("BRAKE_ACT", "BRAKE_CMD", "Brake Command contains Brake Actuator Interface"),
        ("WATCHDOG",  "ATP_CPU",   "ATP CPU includes Watchdog Timer"),
        ("BALISE_RDR","TRACK_INT", "Track Interface contains Balise Reader"),
    ]
    for src, tgt, name in arch_hier:
        create_edge(client, et["ALLOCATED_TO"]["id"],
            f"ARCH-{src}-{tgt}", name,
            arch[src]["id"], arch[tgt]["id"])
        edge_count += 1

    # Requirements allocated to architecture elements
    req_alloc = [
        ("SR001", "EB_FUNC",   "SR-001 allocated to Emergency Braking Function"),
        ("SR002", "BRAKE_CMD", "SR-002 allocated to Brake Command Subsystem"),
        ("SR003", "SPEED_MON", "SR-003 allocated to Speed Monitoring Subsystem"),
        ("SR004", "BRAKE_CMD", "SR-004 allocated to Brake Command Subsystem"),
        ("SR005", "SPEED_SENS","SR-005 allocated to Speed Sensor Assembly"),
        ("SR006", "ATP_CPU",   "SR-006 allocated to ATP Processing Unit"),
        ("SR007", "TRACK_INT", "SR-007 allocated to Track Interface Subsystem"),
        ("SR008", "ATP_CPU",   "SR-008 allocated to ATP Processing Unit"),
    ]
    for req_key, arch_key, name in req_alloc:
        create_edge(client, et["ALLOCATED_TO"]["id"],
            f"ALLOC-{req_key}-{arch_key}", name,
            req[req_key]["id"], arch[arch_key]["id"])
        edge_count += 1

    # Requirement derivation
    req_derived = [
        ("SR002", "SR001", "SR-002 derived from SR-001"),
        ("SR003", "SR001", "SR-003 derived from SR-001"),
        ("SR005", "SR003", "SR-005 derived from SR-003"),
        ("SR006", "SR001", "SR-006 derived from SR-001"),
        ("SR008", "SR002", "SR-008 derived from SR-002"),
    ]
    for child, parent, name in req_derived:
        create_edge(client, et["DERIVED_FROM"]["id"],
            f"DERIV-{child}-{parent}", name,
            req[child]["id"], req[parent]["id"])
        edge_count += 1

    # Hazard affects architecture elements
    haz_affects = [
        ("H001", "EB_FUNC",   "H-001 affects Emergency Braking Function"),
        ("H001", "BRAKE_CMD", "H-001 affects Brake Command Subsystem"),
        ("H002", "BRAKE_CMD", "H-002 affects Brake Command Subsystem"),
        ("H002", "ATP_CPU",   "H-002 affects ATP Processing Unit"),
        ("H003", "SPEED_SENS","H-003 affects Speed Sensor Assembly"),
        ("H003", "ATP_CPU",   "H-003 affects ATP Processing Unit"),
        ("H004", "TRACK_INT", "H-004 affects Track Interface Subsystem"),
        ("H004", "BALISE_RDR","H-004 affects Balise Reader"),
        ("H005", "ATP_CPU",   "H-005 affects ATP Processing Unit"),
        ("H006", "TRACK_INT", "H-006 affects Track Interface Subsystem"),
        ("H007", "BRAKE_CMD", "H-007 affects Brake Command Subsystem"),
    ]
    for haz_key, arch_key, name in haz_affects:
        create_edge(client, et["AFFECTS"]["id"],
            f"AFF-{haz_key}-{arch_key}", name,
            haz[haz_key]["id"], arch[arch_key]["id"])
        edge_count += 1

    # Hazard causal chain
    haz_causes = [
        ("H004", "H001", "H-004 can cause H-001"),
        ("H005", "H001", "H-005 can cause H-001"),
        ("H005", "H002", "H-005 can cause H-002"),
        ("H006", "H001", "H-006 can cause H-001"),
        ("H003", "H002", "H-003 can lead to delayed braking"),
    ]
    for src, tgt, name in haz_causes:
        create_edge(client, et["CAUSES"]["id"],
            f"CAUSE-{src}-{tgt}", name,
            haz[src]["id"], haz[tgt]["id"])
        edge_count += 1

    # Hazards mitigated by controls
    haz_mitigated = [
        ("H001", "C003", "H-001 mitigated by fail-safe brake output"),
        ("H001", "C002", "H-001 mitigated by watchdog timer"),
        ("H002", "C001", "H-002 mitigated by dual speed sensor channels"),
        ("H002", "C002", "H-002 mitigated by watchdog timer"),
        ("H003", "C001", "H-003 mitigated by dual channel cross-comparison"),
        ("H003", "C005", "H-003 mitigated by plausibility check"),
        ("H004", "C004", "H-004 mitigated by balise checksum validation"),
        ("H005", "C002", "H-005 mitigated by watchdog timer"),
        ("H005", "C003", "H-005 mitigated by fail-safe brake output"),
        ("H006", "C006", "H-006 mitigated by CRC integrity check on speed profile"),
        ("H007", "C007", "H-007 mitigated by brake release interlock"),
    ]
    for haz_key, ctrl_key, name in haz_mitigated:
        create_edge(client, et["MITIGATED_BY"]["id"],
            f"MIT-{haz_key}-{ctrl_key}", name,
            haz[haz_key]["id"], ctrl[ctrl_key]["id"])
        edge_count += 1

    # Controls implemented by architecture elements
    ctrl_impl = [
        ("C001", "SPEED_SENS", "C-001 implemented by Speed Sensor Assembly"),
        ("C002", "WATCHDOG",   "C-002 implemented by Watchdog Timer"),
        ("C003", "BRAKE_ACT",  "C-003 implemented by Brake Actuator Interface"),
        ("C004", "BALISE_RDR", "C-004 implemented by Balise Reader"),
        ("C005", "ATP_CPU",    "C-005 implemented by ATP Processing Unit"),
        ("C006", "ATP_CPU",    "C-006 implemented by ATP Processing Unit"),
        ("C007", "BRAKE_CMD",  "C-007 implemented by Brake Command Subsystem"),
    ]
    for ctrl_key, arch_key, name in ctrl_impl:
        create_edge(client, et["IMPLEMENTED_BY"]["id"],
            f"IMPL-{ctrl_key}-{arch_key}", name,
            ctrl[ctrl_key]["id"], arch[arch_key]["id"])
        edge_count += 1

    # GSN structure
    gsn_struct = [
        # G1 supported by S1 and S3, in context of C1 C2 C3
        ("G1",  "S1",  et["SUPPORTED_BY"]["id"],  "G1 supported by S1"),
        ("G1",  "G3",  et["SUPPORTED_BY"]["id"],  "G1 supported by G3"),
        ("G1",  "C1",  et["IN_CONTEXT_OF"]["id"], "G1 in context of system boundary"),
        ("G1",  "C2",  et["IN_CONTEXT_OF"]["id"], "G1 in context of applicable standards"),
        ("G1",  "C3",  et["IN_CONTEXT_OF"]["id"], "G1 in context of operating environment"),
        # S1 supported by G2, S2
        ("S1",  "G2",  et["SUPPORTED_BY"]["id"],  "S1 supported by G2"),
        ("S1",  "Sn1", et["SUPPORTED_BY"]["id"],  "S1 supported by hazard log solution"),
        # G2 supported by S2
        ("G2",  "S2",  et["SUPPORTED_BY"]["id"],  "G2 supported by S2"),
        # S2 supported by per-hazard goals
        ("S2",  "G4",  et["SUPPORTED_BY"]["id"],  "S2 supported by G4"),
        ("S2",  "G5",  et["SUPPORTED_BY"]["id"],  "S2 supported by G5"),
        # G4 supported by solutions
        ("G4",  "Sn2", et["SUPPORTED_BY"]["id"],  "G4 supported by H-001 risk assessment"),
        # G5 supported by solutions
        ("G5",  "Sn3", et["SUPPORTED_BY"]["id"],  "G5 supported by integration test"),
        # G3 supported by S3
        ("G3",  "S3",  et["SUPPORTED_BY"]["id"],  "G3 supported by S3"),
        # S3 supported by SIL and V&V solutions
        ("S3",  "G6",  et["SUPPORTED_BY"]["id"],  "S3 supported by G6"),
        ("S3",  "G7",  et["SUPPORTED_BY"]["id"],  "S3 supported by G7"),
        ("G6",  "Sn4", et["SUPPORTED_BY"]["id"],  "G6 supported by SIL assessment"),
        ("G7",  "Sn5", et["SUPPORTED_BY"]["id"],  "G7 supported by verification report"),
        ("G3",  "Sn6", et["SUPPORTED_BY"]["id"],  "G3 supported by FMEA"),
    ]
    for src, tgt, etype, name in gsn_struct:
        create_edge(client, etype,
            f"GSN-{src}-{tgt}", name,
            gsn[src]["id"], gsn[tgt]["id"])
        edge_count += 1

    # GSN solutions evidenced by evidence items
    gsn_evidence = [
        ("Sn1", "EV001", "Sn1 evidenced by hazard log"),
        ("Sn2", "EV001", "Sn2 evidenced by hazard log risk assessment"),
        ("Sn3", "EV002", "Sn3 evidenced by integration test report"),
        ("Sn4", "EV003", "Sn4 evidenced by SIL 4 assessment"),
        ("Sn5", "EV005", "Sn5 evidenced by verification test report"),
        ("Sn6", "EV004", "Sn6 evidenced by FMEA report"),
    ]
    for soln, evid, name in gsn_evidence:
        create_edge(client, et["EVIDENCED_BY"]["id"],
            f"EVID-{soln}-{evid}", name,
            gsn[soln]["id"], ev[evid]["id"])
        edge_count += 1

    # Requirements evidenced by evidence
    req_evidence = [
        ("SR001", "EV005", "SR-001 evidenced by verification test report"),
        ("SR002", "EV002", "SR-002 evidenced by integration test report"),
        ("SR003", "EV003", "SR-003 evidenced by SIL 4 assessment"),
        ("SR003", "EV008", "SR-003 evidenced by SW V&V report"),
        ("SR005", "EV004", "SR-005 evidenced by FMEA"),
        ("SR007", "EV007", "SR-007 evidenced by track interface validation"),
    ]
    for req_key, evid, name in req_evidence:
        create_edge(client, et["EVIDENCED_BY"]["id"],
            f"EVID-{req_key}-{evid}", name,
            req[req_key]["id"], ev[evid]["id"])
        edge_count += 1

    # Evidence references architecture elements
    ev_refs = [
        ("EV002", "EB_FUNC",   "Integration test covers Emergency Braking Function"),
        ("EV002", "BRAKE_CMD", "Integration test covers Brake Command Subsystem"),
        ("EV003", "SPEED_MON", "SIL assessment covers Speed Monitoring Subsystem"),
        ("EV003", "SPEED_SENS","SIL assessment covers Speed Sensor Assembly"),
        ("EV004", "ATP_CPU",   "FMEA covers ATP Processing Unit"),
        ("EV004", "WATCHDOG",  "FMEA covers Watchdog Timer"),
        ("EV005", "BRAKE_ACT", "Verification test covers Brake Actuator Interface"),
        ("EV006", "BRAKE_CMD", "Design spec covers Brake Command Subsystem"),
        ("EV007", "TRACK_INT", "Validation covers Track Interface Subsystem"),
        ("EV007", "BALISE_RDR","Validation covers Balise Reader"),
        ("EV008", "ATP_CPU",   "SW V&V covers ATP Processing Unit software"),
    ]
    for evid, arch_key, name in ev_refs:
        create_edge(client, et["REFERENCES"]["id"],
            f"REF-{evid}-{arch_key}", name,
            ev[evid]["id"], arch[arch_key]["id"])
        edge_count += 1

    print(f"  [OK] {edge_count} edges created")


    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    node_count = (len(arch) + len(req) + len(haz) +
                  len(ctrl) + len(gsn) + len(ev))

    print(f"""
========================================
  Seed complete

  Node types   : {len(nt)}
  Edge types   : {len(et)}
  Property defs: {len(pd)}

  Nodes created: {node_count}
    Architecture elements : {len(arch)}
    Safety requirements   : {len(req)}
    Hazards               : {len(haz)}
    Controls              : {len(ctrl)}
    GSN nodes             : {len(gsn)}
    Evidence items        : {len(ev)}

  Edges created: {edge_count}

  Open Tracer and explore the graph.
========================================
""")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Tracer with ATP test data")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--username", default=DEFAULT_USERNAME)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--clean", action="store_true",
                        help="Remove all existing data before seeding")
    args = parser.parse_args()

    print(f"\nTracer seed  ATP Emergency Braking dataset")
    print(f"Target: {args.base_url}\n")

    client = TracerClient(args.base_url, args.username, args.password)

    if args.clean:
        clean(client)

    seed(client)
