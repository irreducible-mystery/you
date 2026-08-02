# you — a generative field

An ordered sequence of accepted states `F_0 → F_1 → …` for organizing
observations, claims, assumptions, relations, tensions, and transformations —
**topic-agnostic**, open to many observers (human and AI, never collapsed into
one class), grounded in a braid of verification methods.

Born by self-ingesting the claims of *Organized Change, Projection, and
Generative Fields*. Its first accepted element is a **preserved tension**:

> **TEN-0001** — Q7 says the fundamental unit is an *attributed element*;
> Q6 says *relations come before isolated elements*. The field keeps this seam
> open, and honors it structurally: relations are first-class citizens with
> their own files, provenance, and standing.

## The state sequence, in git

| Field concept (doc Q7) | Implementation |
|---|---|
| Accepted state `F_n` | commit on `main` |
| Candidate change | pull request |
| Deterministic consistency conditions | CI (`.github/workflows/consistency.yml`) |
| Independent acceptance map | review + merge by someone other than the proposer |
| Append-preserving history | git history (proved append-monotone in Lean) |
| Derived atlas | `field/derived/atlas.json` + `projections/viewer/` |

## Layout

```
FIELD.md                    the generating rules (L3 — strongest acceptance conditions)
schemas/                    formal structural rules (element, relation, observer)
field/
  observers/                modeled observers: y_i = pi_i(x; theta_i) + eps_i
  elements/                 attributed elements (TEN-0001 first)
  relations/                first-class relations (the other half of the seam)
  derived/                  regenerated projections: atlas.json, unresolved.json
operators/                  bounded transformation operators (signed, versioned)
verification/
  python/                   canonical validator + numeric grounding (G1–G4)
  julia/                    independent re-derivation of G1–G4
  lean/                     machine-checked invariants of the field's rules
  results/                  executed grounding outputs, committed for comparison
projections/
  atlas.py                  atlas generator (current state)
  chronicle.py              chronicle generator (the sequence F_0 -> F_1 -> ... itself)
  viewer/                   TypeScript viewers: index.html (atlas), chronicle.html (time)
```

## The braid of grounding

| Projection | What it grounds | Result at F₀ |
|---|---|---|
| π_python | consistency conditions C1–C12; experiments G1–G4 | CONSISTENT; G1–G4 PASS |
| π_julia | independent re-derivation of G1–G4 | G1–G4 PASS (cross-perspectival agreement) |
| π_lean | no-self-acceptance; origin traceability; ambiguity-set narrowing; correlated views add nothing; append-preservation | all theorems verified, Lean 4.9.0 |
| π_ts | the derived atlas as an inspectable projection | compiles strict; renders |

Agreement between π_python and π_julia is **cross-perspectival invariance,
not proof** — both share the same experiment designs (a recorded correlated
dependence). The Lean theorems verify the *rules*, not the truth of contents
(LIM-0001).

The grounding experiments at F₀:

- **G1** (CLM-0008): `π∘F_t ≈ G_t∘π` holds for a good macrovariable and fails
  measurably when fiber members have different projected velocities.
- **G2** (CLM-0010): `{0,0,10,10}` and `{5,5,5,5}` — same mean, different
  organization.
- **G3** (CLM-0004/0009): a hidden slow variable makes identical observed
  states diverge — history returns as memory at the reduced level.
- **G4** (CLM-0013/0014): diverse projections shrink the ambiguity set
  (400 → 100 → 20 → 5); a correlated second view shrinks nothing.

## How to participate

1. **Contribute an originating expression** — the easiest way: open an issue
   with the *Originating expression* template and add the
   `originating-expression` label. The reflection intake workflow enters your
   words **verbatim**, stages an *unconfirmed* reflection, and opens a
   candidate-change PR for you to confirm, modify, or reject. Or run the
   operator directly:

   ```bash
   python3 operators/reflect.py --observer OBS-XXX-0000 --text "..." \
       [--restatement "..." --omissions "a; b"]
   ```

   Unfinished reflection skeletons are blocked from accepted state
   (validator C12a). You may also hand-write element files under
   `field/elements/` — ordinary language is fine in `expression.original`.
2. **Propose relations** — add files under `field/relations/`. Contradictions
   must state their conditions.
3. **Candidate change** — every PR is one. CI runs the consistency conditions.
4. **Acceptance** — someone independent of the proposer reviews and merges.
   No operator (or contributor) accepts their own change.
5. **L3 changes** (to `FIELD.md`, schemas, operators, validator) additionally
   require explicit human confirmation.

Register yourself in `field/observers/` with your observer class
(`human | ai-system | hybrid | document-surrogate`) and a dependence profile.
The distinction between different systems is never collapsed.

## Reproduce the groundings

```bash
python3 verification/python/validate.py     # consistency
python3 verification/python/grounding.py    # G1–G4 (python)
julia verification/julia/grounding.jl       # G1–G4 (julia)
cd verification/lean && lean Field/Invariants.lean   # rule invariants
```

---

*The system preserves not one collective answer, but the evolving and
inspectable organization through which answers, assumptions, tensions, and
new possibilities arise.*
