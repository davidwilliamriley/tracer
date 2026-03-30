# Tracer

**Property graph database for systems safety governance in the built environment.**

Tracer provides a structured, queryable model of the relationships between built assets, safety analyses, requirements, and the arguments that demonstrate a system is acceptably safe. It is built on three established frameworks — Uniclass 2015, STPA, and GSN — grounded in a configurable property graph architecture that adapts to the scope and complexity of any project.

---

## Who this documentation is for

<div class="grid cards" markdown>

-   :material-account-hard-hat: **Safety Engineers**

    ---

    Understand the domain model and how to navigate Tracer's graph to manage hazard analyses, safety requirements, and GSN arguments across a project lifecycle.

    [:octicons-arrow-right-24: Domain Model](domain-model/index.md)
    [:octicons-arrow-right-24: User Guide](user-guide/navigation.md)

-   :material-briefcase-outline: **Project Managers & Clients**

    ---

    Understand what Tracer does, what problem it solves, and how it supports the delivery and governance of safety cases in the built environment.

    [:octicons-arrow-right-24: What is Tracer](overview/what-is-tracer.md)
    [:octicons-arrow-right-24: Key Concepts](overview/key-concepts.md)

-   :material-code-braces: **Developers**

    ---

    Extend Tracer's API, configure the schema, or adapt the codebase for a specific domain or deployment context.

    [:octicons-arrow-right-24: Developer Guide](developer-guide/codebase-structure.md)
    [:octicons-arrow-right-24: API Reference](api-reference/index.md)

</div>

---

## What Tracer does

A safety case for a built environment asset — a building, a rail network, a tunnel, an infrastructure system — is a structured argument that the asset is acceptably safe to operate. That argument draws on dozens or hundreds of interconnected artefacts: hazard analyses, safety requirements, architectural descriptions, control measures, test evidence, and formal argument structures.

In practice, these artefacts live in disconnected documents, spreadsheets, and tools. Traceability — knowing which requirements address which hazards, which evidence discharges which argument nodes, which subsystems implement which safety functions — is maintained manually and breaks down as projects evolve.

Tracer models these artefacts and their relationships as a **property graph**: nodes are artefacts, edges are the relationships between them. The graph can be traversed, queried, and visualised in ways that a document management system cannot support.

---

## The three-layer model

Tracer's domain model is structured around three layers, each grounded in an established framework:

| Layer | Framework | Purpose |
|---|---|---|
| **Description** | Uniclass 2015 | What the system is — assets, spaces, systems, products, activities |
| **Analysis** | STPA | What can go wrong — losses, hazards, control actions, unsafe control actions, requirements |
| **Argument** | GSN / ISO 15026-2 | Why it is safe — goals, strategies, solutions, evidence |

These layers are connected: STPA analysis references Uniclass nodes as controllers and controlled processes. GSN goals address STPA hazards. GSN solutions point to evidence that verifies safety requirements allocated to Uniclass systems.

[:octicons-arrow-right-24: Read the domain model in full](domain-model/index.md)

---

## Technology stack

| Component | Technology |
|---|---|
| Backend API | Python · FastAPI · SQLAlchemy · SQLite (→ PostgreSQL) |
| Authentication | JWT · python-jose · passlib |
| Migrations | Alembic |
| Frontend | React · Vite · Tailwind CSS |
| Graph canvas | Cytoscape.js · cytoscape-dagre |
| State management | Zustand |

---

## Current status

Tracer is under active development. The backend API is production-ready with a comprehensive passing test suite. The frontend provides a working graph canvas and admin interface. The domain schema (GSN + STPA + Uniclass) is the current focus of development.

!!! note "Version"
    This documentation describes the current development version. The schema and API are subject to change as the domain model is refined.
