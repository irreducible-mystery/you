# Bounded Transformation Operators — definitions, revision 1.0.0

Each operator is limited, inspectable, and versioned. Every output carries a
formal signature (operator family, operator revision, ruleset revision, inputs,
generation time, origin-confirmation state). No operator applies the acceptance
map to its own change. No operator alters FIELD.md directly.

An operator here is a *procedure definition*: it may be executed by a human,
an AI system, or a script — the executor is recorded as the element's observer,
and the operator family is recorded in the transformation signature. This keeps
the operator/executor distinction visible (observer classes are never collapsed).

---

## reflection @ 1.0.0

**Input:** one originating expression (element with `origin_class: originating`).
**Output:** a structured interpretation element (`origin_class: transformed`,
`origin_confirmation: unconfirmed`) restating the expression and listing what
the restatement omitted.

Bounds:
- MUST quote the original verbatim in `inputs`.
- MUST list omissions in `expression.elaboration`.
- The derived element CANNOT enter accepted status as origin-confirmed until
  the origin confirms, modifies, or rejects it. A rejected interpretation stays
  visible as `rejected`; it never reappears as confirmed.

## assumption-map @ 1.0.0

**Input:** one claim or synthesis.
**Output:** the chain `observation → interpretation → assumption → conclusion`
as separate elements (`ASM-*` for proposed assumptions), plus `depends-on`
relations.

Bounds:
- Proposed assumptions are marked as *proposed by the operator*, never asserted
  as held by the originating observer (`origin_confirmation: unconfirmed`).

## tension-classification @ 1.0.0

**Input:** two elements between which a mismatch is suspected.
**Output:** a tension element with a `tension_class` from:
`logical-contradiction | equivocation | scale-mismatch | temporal-mismatch |
primitive-framework-mismatch | measurement-disagreement | false-dichotomy |
self-reference | undecidability | uncomputability | irreducible-priority-conflict`
plus a `contradicts-under-conditions` or `remains-unresolved-with` relation
whose conditions are stated.

Bounds:
- MUST record whether the two elements share referent, definition, scale, and
  overlapping time before classifying anything as a contradiction (validator C7).
- MUST include reopening conditions in the elaboration if the tension is
  proposed for `preserved-unresolved` status.

## seed-ingestion @ 1.0.0 (genesis only)

Defined and bounded in `seed_ingestion.py`. Used once, to birth F₀ from the
source document. Its self-referential character is recorded as TEN-0002 and
TEN-0003 rather than hidden.

---

Adding a new operator family, or revising these definitions, is an **L3
change** (FIELD.md §10).
