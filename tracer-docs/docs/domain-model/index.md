# Domain Model

The Tracer domain model defines the types of artefacts a safety case contains and the relationships between them. It is grounded in three established frameworks — Uniclass 2015, STPA, and GSN — rather than a bespoke ontology.

---

## The three layers

```
┌─────────────────────────────────────────────────────────┐
│  ARGUMENT LAYER — GSN / ISO 15026-2                     │
│  GSN_GOAL · GSN_STRATEGY · GSN_SOLUTION                 │
│  GSN_CONTEXT · GSN_ASSUMPTION · EVIDENCE                │
└──────────────────────┬──────────────────────────────────┘
                       │ ADDRESSES · EVIDENCED_BY · VERIFIED_BY
┌──────────────────────▼──────────────────────────────────┐
│  ANALYSIS LAYER — STPA + Safety Requirements            │
│  LOSS · HAZARD · CONTROL_ACTION                         │
│  UNSAFE_CONTROL_ACTION · LOSS_SCENARIO                  │
│  CONTROL_CONSTRAINT · SAFETY_REQUIREMENT                │
└──────────────────────┬──────────────────────────────────┘
                       │ CONTROLS · ALLOCATED_TO · ENABLES_HAZARD
┌──────────────────────▼──────────────────────────────────┐
│  DESCRIPTION LAYER — Uniclass 2015                      │
│  COMPLEX · ENTITY · SPACE · ELEMENT                     │
│  SYSTEM · PRODUCT · ACTIVITY                            │
└─────────────────────────────────────────────────────────┘
```

The layers are not isolated — edges cross between them. STPA analysis references Uniclass nodes as controllers and controlled processes. GSN goals address STPA hazards. GSN solutions point to evidence that verifies requirements allocated to Uniclass systems. This cross-layer connectivity is what makes the graph useful for governance queries.

---

## Node type summary

### Description layer

| Node type | Code | Framework | Description |
|---|---|---|---|
| `COMPLEX` | Co | Uniclass | Networks, campuses, whole systems |
| `ENTITY` | En | Uniclass | Discrete built assets — buildings, structures |
| `SPACE` | Sp | Uniclass | Rooms, zones, volumes within entities |
| `ELEMENT` | EF | Uniclass | Functional parts of entities |
| `SYSTEM` | Ss | Uniclass | Technical systems — fire, access control, signalling |
| `PRODUCT` | Pr | Uniclass | Physical components and products |
| `ACTIVITY` | Ac | Uniclass | Operations, processes, events |

### Analysis layer

| Node type | Code | Framework | Description |
|---|---|---|---|
| `LOSS` | L | STPA | Top-level consequence to prevent |
| `HAZARD` | H | STPA | System state that can lead to a loss |
| `CONTROL_ACTION` | CA | STPA | A control action between controller and controlled process |
| `UNSAFE_CONTROL_ACTION` | UCA | STPA | A control action that is unsafe in context |
| `LOSS_SCENARIO` | LS | STPA | Causal mechanism from UCA to hazard |
| `CONTROL_CONSTRAINT` | CC | STPA | Constraint on controller behaviour preventing the UCA |
| `SAFETY_REQUIREMENT` | SR | — | Formally stated requirement derived from control constraints |

### Argument layer

| Node type | Code | Framework | Description |
|---|---|---|---|
| `GSN_GOAL` | G | GSN | A claim to be argued |
| `GSN_STRATEGY` | S | GSN | An argument pattern decomposing a goal |
| `GSN_SOLUTION` | Sn | GSN | A leaf node pointing to evidence |
| `GSN_CONTEXT` | C | GSN | Contextual information scoping a goal or strategy |
| `GSN_ASSUMPTION` | A | GSN / ISO 15026-2 | A claim taken as given without proof |
| `EVIDENCE` | EV | — | A document providing objective evidence |

---

## Edge type summary

### Description layer edges

| Edge | From | To | Reverse |
|---|---|---|---|
| `CONTAINS` | Co/En/Ss | En/Sp/EF/Ss/Pr | `PART_OF` |

### STPA analysis edges

| Edge | From | To | Notes |
|---|---|---|---|
| `CONTROLS` | Ss / En | CA | Uniclass node acts as controller |
| `RECEIVES` | CA | Ss / En | Uniclass node is controlled process |
| `PROVIDES_FEEDBACK` | Ss / En | Ss / En | Feedback loop in control structure |
| `BECOMES_UNSAFE_AS` | CA | UCA | A control action has an unsafe form |
| `LEADS_TO` | UCA | H | UCA leads to a hazard |
| `EXPLAINED_BY` | UCA | LS | Loss scenario explains the UCA |
| `CAUSES` | H | L | Hazard causes a loss |
| `MITIGATED_BY` | H | CC | Hazard is mitigated by a constraint | 
| `INFORMS` | CC | SR | Constraint informs a requirement |
| `ENABLES_HAZARD` | AC | H | Activity creates conditions for hazard |

### Requirements edges

| Edge | From | To | Reverse |
|---|---|---|---|
| `ALLOCATED_TO` | SR | Ss / En | `IMPLEMENTS` |
| `DERIVED_FROM` | SR | SR | — |
| `VERIFIED_BY` | SR | EV | — |

### GSN argument edges

| Edge | From | To | Notes |
|---|---|---|---|
| `SUPPORTED_BY` | G / S | S / G / Sn | Top-down, parent to child |
| `IN_CONTEXT_OF` | G / S | C | — |
| `IN_ASSUMPTION_OF` | G / S | A | — |
| `EVIDENCED_BY` | Sn | EV | Solution points to evidence |

### Cross-layer edges

| Edge | From | To | Notes |
|---|---|---|---|
| `ADDRESSES` | G | H / L | GSN goal addresses a hazard or loss |
| `REFERENCES` | EV | Ss / En / EF | Evidence references an architectural element |

---

## Shared properties

Every node type carries these properties regardless of its layer:

| Property | Type | Description |
|---|---|---|
| `status` | enum | Lifecycle status — see [Lifecycle States](lifecycle-states.md) |
| `notes` | text | Free text annotation |

Every Uniclass node type additionally carries:

| Property | Type | Description |
|---|---|---|
| `uniclass_code` | string | Uniclass 2015 classification code e.g. `Ss_65_70_47` |
| `uniclass_name` | string | Uniclass name for that code |

---

## Further reading

The domain model is documented in detail across the following pages:

- [Description Layer — Uniclass](uniclass.md)
- [Analysis Layer — STPA](stpa.md)
- [Argument Layer — GSN](gsn.md)
- [Edge Types](edge-types.md)
- [Lifecycle States](lifecycle-states.md)
