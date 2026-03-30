# Key Concepts

This page explains the core concepts behind Tracer. Understanding these will make the rest of the documentation — and the tool itself — much clearer.

---

## Property graphs

A **property graph** is a data model consisting of nodes and edges, where both nodes and edges can carry named properties.

- **Nodes** represent entities — in Tracer, these are safety case artefacts like hazards, requirements, GSN goals, and built assets
- **Edges** represent directed relationships between nodes — `CAUSES`, `SUPPORTED_BY`, `ALLOCATED_TO`, `EVIDENCED_BY`
- **Properties** are key-value pairs attached to nodes or edges — a hazard has a `system_state`, a requirement has a `sil_target`

This is different from a relational database, where relationships are expressed through foreign keys and joins. In a property graph, relationships are first-class data that can be traversed directly. "What are all the hazards reachable from this loss?" is a single traversal query, not a multi-table join.

Tracer uses a **configurable** property graph — the node types, edge types, and property definitions are themselves stored as data in the system rather than being fixed in the database schema. This means the safety case schema can evolve without database migrations.

---

## The three-layer model

Tracer organises safety case artefacts into three layers, each grounded in an established framework:

### Description layer — Uniclass 2015

<div class="layer-block uniclass" markdown>
**What the system is.** The description layer models the physical and functional architecture of the built asset using Uniclass 2015 classification codes. It answers: what exists, how it is structured, and how its parts relate to each other.
</div>

Uniclass 2015 is a classification system for the built environment published by the Construction Industry Council. Tracer uses seven of its tables as node types:

| Node type | Uniclass table | Examples |
|---|---|---|
| `COMPLEX` | Co — Complexes | Rail network, hospital campus, water treatment facility |
| `ENTITY` | En — Entities | Station building, pump house, signal box |
| `SPACE` | Sp — Spaces | Platform area, control room, equipment room |
| `ELEMENT` | EF — Elements | Structural frame, external wall, roof |
| `SYSTEM` | Ss — Systems | Fire detection system, access control system, signalling system |
| `PRODUCT` | Pr — Products | Smoke detector, door controller, relay |
| `ACTIVITY` | Ac — Activities | Normal operation, maintenance, emergency evacuation |

The description layer is the anchor for the rest of the safety case. Systems are the controllers and controlled processes in STPA. Safety requirements are allocated to systems. Evidence documents reference systems.

### Analysis layer — STPA

<div class="layer-block stpa" markdown>
**What can go wrong.** The analysis layer models the results of a System-Theoretic Process Analysis. It answers: what losses are we trying to prevent, what system states could lead to those losses, what control actions could be unsafe, and what constraints on controller behaviour would prevent unsafe actions.
</div>

STPA (System-Theoretic Process Analysis) is a hazard analysis method developed by Nancy Leveson at MIT. Unlike failure-based methods (FMEA, FTA), STPA starts from control structure: it identifies how controllers — human or automated — interact with controlled processes through control actions and feedback, and analyses what happens when those control actions are unsafe.

The STPA node types in Tracer form a chain:

```
LOSS → HAZARD → UNSAFE_CONTROL_ACTION → LOSS_SCENARIO
                       ↓
              CONTROL_CONSTRAINT → SAFETY_REQUIREMENT
```

### Argument layer — GSN / ISO 15026-2

<div class="layer-block gsn" markdown>
**Why it is safe.** The argument layer models the structured safety argument using Goal Structuring Notation (GSN). It answers: what is the top-level safety claim, how is that claim decomposed and argued, and what evidence supports the leaf nodes of the argument.
</div>

GSN (Goal Structuring Notation) is a graphical notation for expressing safety arguments. An argument is a hierarchy of goals decomposed through strategies into sub-goals and solutions, with contexts and assumptions scoping each node.

In Tracer, GSN goals address STPA hazards and losses. GSN solutions point to evidence that verifies safety requirements. The argument layer is the integrating layer — it draws on everything else to make the case that the system is safe.

---

## Configurable schema

Most safety governance tools have a fixed data model. Tracer's schema is configurable: the node types, edge types, and property definitions are data that can be created and modified through the Admin interface and API.

This means Tracer can be adapted to different:

- **Domains** — a rail project and a building project may use different node types or different property sets
- **Standards regimes** — different regulatory environments may require different hazard analysis approaches
- **Project scales** — a small project may use a simpler schema than a large multi-system programme

The configurable schema is implemented as three layers in the database:

1. **Type registry** — `NodeType` and `EdgeType` tables define what types exist
2. **Schema layer** — `NodePropertyDefinition`, `EdgePropertyDefinition`, and the assignment tables define what properties each type carries
3. **Instance layer** — `Node`, `Edge`, and the property value tables store the actual data

---

## Lifecycle states

Every artefact in Tracer carries a `status` property that tracks where it is in its governance lifecycle:

| Status | Meaning |
|---|---|
| `Draft` | Being created or edited, not yet ready for review |
| `Proposed` | Ready for review, formally submitted |
| `Under Review` | Currently being reviewed |
| `Approved` | Review complete, approved for use |
| `Baselined` | Locked to a specific configuration — cannot be changed without a new revision |
| `Superseded` | Replaced by a newer version, retained for traceability |
| `Withdrawn` | Removed from use, not replaced |
| `Closed` | Lifecycle complete |

The lifecycle states matter for querying: "show me all requirements that are Approved or Baselined and have no verified evidence" is a meaningful governance query.

---

## Edge direction convention

All edges in Tracer are directed. The convention is **top-down** — edges point from parent to child, from more abstract to more concrete:

- `COMPLEX` –CONTAINS→ `ENTITY` –CONTAINS→ `SYSTEM`
- `GSN_GOAL` –SUPPORTED_BY→ `GSN_STRATEGY` –SUPPORTED_BY→ `GSN_SOLUTION`
- `HAZARD` –CAUSES→ `LOSS`

This convention supports graph traversal from a root node outward — starting from a top-level goal or a high-level system and following edges to find everything connected to it.

For non-GSN relationships, **reverse edge types** are provided for practitioners who prefer bottom-up conventions (common in SysML/UML):

| Canonical (top-down) | Reverse (bottom-up) |
|---|---|
| `CONTAINS` | `PART_OF` |
| `ALLOCATED_TO` | `IMPLEMENTS` |
| `MITIGATED_BY` | `MITIGATES` |

!!! warning "Avoid duplicates"
    Do not create both the canonical and reverse edges for the same relationship. By convention, use one direction consistently within a project.

---

## Multi-project architecture

Tracer is designed for multiple projects sharing a common type library. The node types, edge types, and property definitions are shared across all projects. Individual project instances then populate nodes against that shared schema.

A `PROJECT` node type anchors all artefacts to a specific project via `BELONGS_TO` edges. This makes it possible to filter the graph to a single project, or to query across projects for artefacts of a given type or status.
