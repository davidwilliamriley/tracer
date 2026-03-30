# What is Tracer

## The problem

Safety cases for built environment assets are complex, multi-disciplinary documents. A safety case for a rail system, a high-rise building, or a water treatment facility must demonstrate — through structured argument and objective evidence — that the system is acceptably safe to operate under defined conditions.

In practice, a safety case draws on:

- Hazard analyses identifying what can go wrong and how likely it is
- Safety requirements specifying what the system must do to prevent those hazards
- An architectural description of the system that implements those requirements
- Evidence — test reports, analyses, design documents — that the requirements are met
- A formal argument structure connecting evidence to top-level safety claims

These artefacts are created by different disciplines at different stages of a project lifecycle. They reference each other constantly: a requirement addresses a hazard, a test report verifies a requirement, an argument node is supported by evidence. **Maintaining that traceability manually — across Word documents, Excel registers, and disconnected tools — is the fundamental challenge of safety governance.**

When a hazard is revised, which requirements are affected? When a test report is superseded, which argument nodes become undischarged? When a subsystem changes, which safety functions need revalidation? These questions require traversing a network of relationships. Flat documents cannot answer them efficiently.

---

## The solution

Tracer models a safety case as a **property graph**: artefacts are nodes, relationships are edges. The graph can be traversed, filtered, and visualised in ways that document-based approaches cannot support.

This approach provides:

**Traceability by design.** Relationships between artefacts are first-class data, not text references in documents. A query like "show me all hazards that are not addressed by an approved safety requirement" is a graph traversal, not a manual audit.

**Configurable schema.** The node types, edge types, and property definitions that constitute the safety case schema are themselves data in the system. Tracer can be configured for different domains, different standards regimes, and different project contexts without changing the underlying codebase.

**Lifecycle governance.** Every artefact carries a lifecycle status — Draft, Proposed, Under Review, Approved, Baselined, Superseded, Withdrawn, Closed. The graph makes it possible to query the status of any artefact and understand what depends on it.

**Standards alignment.** Tracer's domain model is grounded in three established frameworks — Uniclass 2015, STPA, and GSN — rather than a bespoke ontology. This means artefacts in Tracer can be connected to BIM models, asset registers, and other tools that use the same classification systems.

---

## Who Tracer is for

Tracer is designed for safety engineers, safety managers, and the teams they work with on safety-critical built environment projects. It is particularly suited to:

- Projects where multiple disciplines contribute to the safety case and traceability between their outputs is critical
- Long-lifecycle assets where the safety case must be maintained and updated over time
- Organisations that manage multiple projects and want a consistent, governed approach to safety case artefacts
- Projects subject to formal safety submissions where the argument structure and evidence base must be auditable

---

## What Tracer is not

Tracer is not a document management system. It stores references to documents and the relationships between them, not the documents themselves. Evidence nodes in Tracer carry a document reference and revision — the document lives in your existing DMS.

Tracer is not a hazard analysis tool. It stores the outputs of hazard analyses — losses, hazards, unsafe control actions, control constraints — but it does not perform the analysis. The analysis is done by safety engineers using appropriate methods (STPA, HAZOP, FMEA) and the results are recorded in Tracer.

Tracer is not a requirements management tool in the traditional sense. It stores safety requirements and their relationships to hazards, architecture, and evidence. General functional requirements that are not safety-related are out of scope.

---

## The built environment focus

Tracer is designed for the built environment broadly — buildings, infrastructure, transport systems, utilities — not for a single sector. The Uniclass 2015 classification system provides a shared vocabulary that works across these domains, from a rail station (a Complex containing Entities containing Systems) to a water treatment plant or a hospital.

This breadth is intentional. The safety engineering challenges across built environment sectors are more similar than different: complex sociotechnical systems, long lifecycles, multiple stakeholders, regulatory oversight, and the fundamental challenge of demonstrating safety without being able to test every failure mode.
