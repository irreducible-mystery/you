# FIELD.md — The Generating Rules (L3)

> This file is the field's constitution: its defining constraints, admissibility
> conditions, and acceptance rules. Changes to this file are **L3 changes** and
> require the strongest acceptance conditions (see §7). The field is
> **topic-agnostic**: it can hold observations about any subject. What it
> constrains is not *what* may be said, but *how* contributions enter, relate,
> transform, and become challengeable.

The field was born by self-ingesting the claims of the document
*Organized Change, Projection, and Generative Fields* (its origin surrogate is
observer `OBS-DOC-0001`). Its first accepted element is a **preserved tension**,
`TEN-0001`, and this is deliberate: the field begins from an unresolved seam,
not from a settled axiom.

---

## 1. What the field is

An ordered sequence of accepted states

```
F_0 → F_1 → F_2 → ...
```

where each state is a git commit on `main`, each **candidate change** is a pull
request, and the **acceptance map** is the review-and-merge act — which must be
independent of the transformation that proposed the change (§6).

The field is a structured graph of:

```
observations + claims + assumptions + relations + tensions + transformations
```

The fundamental unit is **not an answer**. It is an *attributed element situated
within a context* — while relations are stored as first-class citizens with
their own files and provenance, so that neither elements nor relations are
treated as conceptually prior. This double bookkeeping is the structural
honoring of `TEN-0001` and remains in force until an accepted L3 change revises
it.

## 2. Element kinds

`observation | claim | assumption | definition | perspective | tension |
bridge | test | dimension-proposal | synthesis | limit`

Every element carries (see `schemas/element.schema.json`):

- a stable reference (`id`), kind, and status
  (`open | accepted | contested | rejected | superseded | preserved-unresolved`);
- origin class (`originating | transformed | aggregate`) and attribution mode
  (`direct | surrogate | abstract`);
- the **original expression, verbatim** — a transformation may never silently
  replace its origin;
- context: scale, temporal scope, primitive framework
  (`state-centered | process-centered | relation-centered | observer-centered`);
- distinctions introduced, assumptions depended on;
- an origin trace (origin kind, origin reference, capture time);
- any transformation signature used (operator family, operator revision,
  rule-set revision, inputs, generation time);
- an origin-confirmation state
  (`confirmed | modified | rejected | unconfirmed | surrogate-verbatim`).

A derived element must never appear as unoriginated common truth. An
interpretation rejected by its origin remains historically visible **as
rejected**; it may not continue to appear as origin-confirmed.

## 3. Relations are first-class

Relations live in `field/relations/` with their own ids, provenance, and
transformation signatures. Admitted types:

`supports | challenges | contradicts-under-conditions |
compatible-under-conditions | complements | overlaps | contains | depends-on |
caused-by | correlated-with | translates-to | partially-translates-to |
loses-information-when-translated-to | applies-at-another-scale |
applies-at-another-time | transforms-into | counterexample-to |
shares-assumption-with | requires-new-dimension | remains-unresolved-with`

A `contradicts-under-conditions` relation **must state its conditions** (same
referent? same definition? same scale? overlapping time?). The field must not
manufacture opposition by stripping context.

## 4. Observers — the distinction is never collapsed

Observer classes: `human | ai-system | hybrid | document-surrogate`.

- Every element and relation names its contributing observer.
- Dependence profiles are mandatory in derived projections: outputs sharing a
  transformation definition, a common source, or a shared rule are marked, and
  **correlated agreement is never counted as independent confirmation**
  (`number of outputs ≠ number of independent perspectives`).
- No synthesis may present ai-system-derived and human-originated content as
  interchangeable. Provenance survives every projection.

## 5. Bounded transformation operators

Operators live in `operators/`, each limited, inspectable, and versioned.
Initial family: `reflection`, `assumption-map`, `tension-classification`.
Each operator:

- begins with an empty action set and receives only the mappings it needs;
- appends attributed derivatives; may propose a candidate change;
- **never applies the acceptance map to its own change**;
- never bypasses the consistency conditions (§6);
- never alters this file directly;
- signs every output (operator family, revision, rule-set revision, inputs,
  generation time, origin-confirmation state).

## 6. Deterministic consistency conditions

`verification/python/validate.py` is the canonical validator, run by CI on
every candidate change. It tests: formal well-formedness against the schemas;
completeness of the origin trace; validity of relation endpoints; links from
claims to assumptions; origin-confirmation states; operator attribution on all
transformed elements; conditions on every contradiction relation; presence of
the dependence profile; and successful regeneration of the derived atlas.

Grounding is **braided**, not singular:

- **Python** — canonical validator + numerical grounding experiments;
- **Julia** — independent re-derivation of the grounding experiments
  (a second projection π₂ of the same claims; agreement between Python and
  Julia is *cross-perspectival invariance*, not proof);
- **Lean 4** — machine-checked invariants of the field's own rules
  (no self-acceptance, origin-trace completeness, ambiguity-set narrowing);
- **TypeScript** — the derived atlas viewer; a generated projection, never
  primary reality.

Deterministic tests establish consistency and derivation. They do not
establish truth.

## 7. Acceptance and update control

- Every change to accepted state arrives as a visible candidate change (PR)
  showing both the structural diff and a readable explanation.
- CI (consistency conditions) must pass.
- At least one acceptance mapping **independent of the proposing
  transformation** must approve (a human or a differently-situated system; an
  operator never accepts its own output).
- L1 (new contributions) needs the above. L2 (new relations, interpretations)
  additionally requires relation-integrity checks. **L3** (changes to this
  file, the schemas, the operator definitions, or the validator) additionally
  requires explicit confirmation from at least one human observer, because L3
  changes alter what the field can represent.
- Acceptance of a synthesis means only: *adequately represented, traceable,
  and revisable* — not finally true, not agreed by every originating view.

## 8. Unresolved difference is preserved

Every synthesis element must list: supporting origins, partial supports,
opposing origins, counterstatement references, unresolved questions, and
explicit reopening conditions. The unresolved-tension set
(`field/derived/unresolved.json`) is regenerated with the atlas and may never
be emptied by convention — only by accepted elements that genuinely resolve or
supersede a tension, with the history retained.

Nothing is permanently settled. A later element can reopen any synthesis.

## 9. Origin control and restricted material

- Restricted first-order material is never placed in this public sequence.
- Removal of a current element may not erase its occurrence in earlier states
  (git history is append-preserving by construction).
- Exposed elements may use `direct`, `surrogate`, or `abstract` origin labels.
- Later transformation of restricted material requires an explicit
  authorization relation.

## 10. The three levels

| Level | Type of change | Acceptance strength |
|-------|----------------|---------------------|
| L1 | New contributions | CI + one independent acceptance |
| L2 | New relations and interpretations | CI + relation integrity + one independent acceptance |
| L3 | Changes to the field's generating rules | CI + independent acceptance + explicit human confirmation |

The field becomes generative when contributions can modify not only its
contents but its structure. This document expects to be changed.

---

*The system preserves not one collective answer, but the evolving and
inspectable organization through which answers, assumptions, tensions, and new
possibilities arise.*
