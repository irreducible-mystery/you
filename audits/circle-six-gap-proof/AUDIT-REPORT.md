# Independent Audit — `circle-six-gap-proof`

**Auditor:** SuperNinja (NinjaTech AI) — independent of the artifact's authors and of the
Claude lineage that produced it.
**Date:** 2026-08-03
**Artifact:** `circlesixgapproof.zip` → `circle-six-gap-proof/` (17 files, MANIFEST verified)
**Verdict up front:** `verify.sh` → **ALL CHECKS PASSED, EXIT=0** on a fresh
Lean 4.22.0 toolchain in a clean sandbox, **and** every mathematical claim I
re-derived with my own independently written code checks out. One deliberately
falsified theorem was correctly **rejected** by the kernel (negative control).
The artifact's self-imposed scope limits (`NOT-PROVED.md`) are accurate and, in
my judgment, honest. Detailed findings below, including the small gaps I found.

---

## 1. What was audited, and how

Four independent layers, ordered from "their machinery" to "mine":

| Layer | Method | Result |
|---|---|---|
| A. Integrity | `sha256sum -c MANIFEST.sha256` | 17/17 OK |
| B. Their contract | `sh verify.sh` on fresh Lean 4.22.0 | EXIT=0, all 6 checks green |
| C. Adversarial checks | source-level hunt for soundness escapes; negative control; audit-script gap analysis | no escapes found; kernel rejects a planted falsehood; one benign gap noted (§4.2) |
| D. Independent re-derivation | my own Python (`independent_rederivation.py`), written from the standard inhomogeneous bar-complex definition of H³(Z/2, M), **not** from their code; plus a second, structurally different route (integer matrices + Smith normal form) | **all ~60 checks PASS**, including results the artifact explicitly does *not* kernel-decide |

### B in detail — their contract

```
[1] kernel present and honest      ok  (accepts 2+2=4, REJECTS 2+2=5)
[2] the proofs compile             ok  C6_Twist.lean (81s), C6_Gap.lean (1s)
[3] axiom audit                    ok  129 declarations, 129 axiom-free
                                       no propext / Classical.choice / Quot.sound /
                                       sorryAx / ofReduceBool / ofReduceNat
[4] doc drift                      ok  01-BUILD-STACK.md regenerates identically
[5] compute/ scripts               ok  all 8 run to completion
[6] checksums                      ok
ALL CHECKS PASSED  EXIT=0
```

### C in detail — trying to break it

- **Source-level soundness escapes.** Grepped both `.lean` files for `sorry`,
  `axiom`, `native_decide`, `unsafe`, `partial`, `implemented_by`, `extern`,
  `macro`, `elab`, `opaque`, attribute tricks. **None present.** The only
  `set_option`s are `maxRecDepth 8000` and `maxHeartbeats 0`, both of which
  only give the kernel more room; neither weakens trust.
- **Negative control.** I changed `B3_untwisted : countB false 256 = 16` to
  `= 17` and recompiled. The kernel answered:
  `error: tactic 'decide' proved that the proposition countB false 256 = 17 is false`.
  So the pipeline distinguishes truth from falsehood on exactly the kind of
  statement the artifact rests on — the green is not an echo.
- **The `Decidable` instances** (`decAllU`, `decAllBool`) — the one place the
  README flags as the "decision point" — are hand-written and correct: their
  `isTrue` branches construct total case-analysis proof terms the kernel
  typechecks. No route to a false `isTrue` without `sorry`/axioms, which the
  audit shows are absent.
- **Audit-script gap analysis.** See §4.2 — one declaration escapes the
  `#print axioms` sweep; benign but worth recording.

### D in detail — my re-derivation (the part that is genuinely mine)

Written from the textbook definition of the inhomogeneous bar complex for
G = Z/2 acting on Z/n by x ↦ kx (k² ≡ 1 mod n), then cross-checked with a
*second* method (d² and d³ as integer matrices; kernel/image sizes mod n via
Smith normal form — no cochain enumeration at all). Everything below **PASSES**:

- **Complex sanity:** d³∘d² = 0 exhaustively for all gauges at
  (n,k) ∈ {4,8,3,5,12} × all valid k. Their "complex" is a complex.
- **The μ₄ four-row table** (C6_Twist RESULT 1): untwisted, −1 generates and
  ±i are not even cocycles; twisted (k=3), −1 becomes a coboundary and ±i
  generate. Their explicit witness gauge `[3,3,1,2]` really does hit the
  fermion. Reproduced exactly.
- **The kernel-decided counts:** |B³| = 16 untwisted / 32 twisted,
  |ker d²| = 16 / 8, B³ ⊆ Z³ both readings. Reproduced.
- **The counts the artifact does NOT kernel-decide** (NOT-PROVED §1):
  |Z³| = 32 untwisted / 64 twisted, 8 shared, and
  **pentagon ↔ untwisted-cocycle as a set identity over all 4⁸ = 65536
  symbols**. I confirmed all of these independently — including
  re-implementing the seal's own guarded `genPentLhs/genPentRhs` in complex
  arithmetic and getting the identical 32-element solution set. So the honest
  gap they declare is real, but the claims parked in it are, as computations,
  correct.
- **The pinch at μ₈** (C6_Gap §4): under k=3, odd top-cells are not cocycles
  and every even one is a coboundary (all four witness gauges verified);
  under k=7 (inversion) `top 1` is a cocycle no gauge kills. Reproduced. I
  also filled in k=5, which the Lean file doesn't cover: it pinches like k=3
  (only u=0,4 are cocycles, both coboundaries) — consistent with the
  landscape script's `O..O` row.
- **Odd-n total pinch** (C6_Gap §6) at μ₃ and μ₅, including the asymmetry
  (trivial action: almost no cocycles; inversion: all cocycles, all killed).
  Reproduced, and consistent with theory (|G| = 2 invertible mod odd n ⇒ H* = 0).
- **The braiding sector** (C6_Twist final section): with F-symbol f on the
  top cell and R-symbol R, my independent hexagon check gives: boson (f=1)
  braids by ±1 only; fermion (f=−1) braids by ±i only; conjugation fixes the
  boson's braidings and exchanges the fermion's; SelfInverse holds for ±1,
  fails for ±i. Reproduced exactly.
- **The |H³| formula** `gcd(1+k,n)·gcd(k−1,n)/n` from
  `compute/absence4_pinch.py`: my SNF route confirms it for **all** n in
  2..16 and all valid k (their brute force stops at n ≤ 8). It also agrees
  with standard Tate cohomology of cyclic groups
  (H³ = H¹ = ker(norm)/im(σ−1)), so the formula is not just empirically
  right, it is the textbook answer.
- **"Actions disagree exactly when 8 | n"** (03-NOTES): verified by formula
  for n < 200. Exact match with multiples of 8.

---

## 2. What the artifact establishes (my assessment)

1. **Kernel-certified, axiom-free:** all 66 theorems across the two files, on
   the exact toolchain named. The strongest results, in my view:
   - `pentagon_iff_seal` — the fidelity bridge. The swept object provably *is*
     the seal's own pentagon (guards, Int labels and all), so the sweep is
     about the thing, not a model of it. This is what elevates the rest.
   - `twist_invisible_on_fixed` + `fixed_locus_is_sharp` (C6_Gap §1) — the
     general statement: *any* twist σ is invisible in d³ precisely on σ's
     fixed locus, with no group/involution/finiteness hypotheses; and the
     scope is sharp. One-line proof, wide blast radius. This is the honest
     core of the whole "five circles never saw it" story.
   - The four-row table + explicit trivialising gauges — the σ-twisted
     reading exchanges the roles of −1 and i exactly.
   - The μ₈ pinch with witnesses, and the definite-article theorems
     (`sqrtsOfOne`) showing "the non-trivial action" only denotes at n=4.
2. **Computationally correct beyond the kernel line:** everything in
   NOT-PROVED §1 that is "compiler-checked only" and everything in `compute/`
   that I tested is *also* right by my independent derivation — including via
   a method (SNF) that shares no code, no enumeration strategy, and no
   representation with theirs.
3. **The self-limitation is accurate.** NOT-PROVED.md's four caveats (65536
   sweep not kernel-decided; the twisted complex is a *constructed*
   counterfactual justified by convention; unnormalised cochains; compute/ is
   evidence not proof) are all true statements about the artifact, and none
   of them hides a defect I could find behind it.

## 3. What the artifact does NOT establish (unchanged from their own list, confirmed)

- No kernel verdict on the full-space |Z³| counts or the pentagon↔cocycle set
  identity (my Python confirms them, but Python is my kernel-free layer too —
  this remains open at kernel grade).
- The σ-twisted d³/d² is **not in the sealed source**; it is the standard
  convention attached to the leading face. All twisted statements are about
  that constructed complex. (Their own mitigations — complex-ness check,
  face-placement invariance, σ-generality — are real and I verified the first
  and third.)
- Nothing here is a claim about physics; "boson/fermion" are names for
  F-symbol data on Z/2 fusion rules.

## 4. Findings — gaps and nits (none load-bearing)

### 4.1 `compute/absence4_pinch.py` exceeds a casual timeout
The n=8 rows enumerate 8⁸ ≈ 16.7M cochains; the script needs ~3–4 minutes on
this sandbox. `verify.sh` runs it without a timeout so their contract is
unaffected, but auditors running scripts individually with a default timeout
will see a spurious failure. Cosmetic.

### 4.2 One declaration escapes the axiom audit: `inductive U`
`verify.sh`'s embedded Python collects declarations by regex
(`theorem|def|abbrev|instance|structure`) — it does not match `inductive`.
`structure GZ` is audited; `inductive U` is not (129 audited lines, and my
cross-check of the audit log against the source shows `U` is the only miss).
**Impact: none** — an inductive type declaration cannot smuggle an axiom, and
every theorem *about* `U` is audited and clean. But "every declaration, not a
sample" is off by one, and the same species of error the author catalogues in
03-NOTES ("a marker standing in for a property" — here, a regex standing in
for "all declarations"). Fix: add `inductive` to the regex.

### 4.3 `README` says "49 + 17 theorems"; the header comment in C6_Twist says "41 theorems"
The build stack actually lists 49 THEOREM lines in C6_Twist and 17 in C6_Gap
(66 total; 129 declarations including defs/instances). The "41" in the file
header is stale prose from an earlier revision. Nothing load-bearing (the
header itself says exit code is the only evidence), but it is drift *inside*
the one file whose companion tooling exists to catch drift — worth fixing.

### 4.4 `seal_objects.py` CHECK A documents a real docstring hazard
`gaugePhi g == d2raw g` holds for only 64/256 gauges; the correct identity is
`gaugePhi g = d2raw (gaugeInv g)` (256/256), images coincide so no cohomology
is affected. This is the artifact auditing its *own* upstream seal and finding
a misleading docstring — I reproduce their numbers and agree with their
reading. This is a finding about the seal, not about this artifact.

### 4.5 Provenance of the counterfactual complex
NOT-PROVED §2 is the right label and should travel with any quotation of the
twisted results. In field terms: every twisted claim is
`contradicts-under-conditions`-safe only if the condition "constructed
complex, leading-face convention" is carried along.

## 5. Reproduction recipe (what I ran)

```
sha256sum -c MANIFEST.sha256                       # 17/17 OK
# Lean 4.22.0, streamed install (no elan, no Mathlib)
curl -sSL <lean-4.22.0-linux.tar.zst> | zstd -d | tar -x
PATH=$PWD/lean-4.22.0-linux/bin:$PATH sh verify.sh  # EXIT=0
# negative control
sed 's/countB false 256 = 16/countB false 256 = 17/' lean/C6_Twist.lean > /tmp/false.lean
lean /tmp/false.lean                                # rejected: proposition is false
# independent re-derivation (mine)
python3 audit_work/independent_rederivation.py      # ALL INDEPENDENT CHECKS PASS
```

## 6. Summary sentence

The artifact does what it says, refrains from claiming what it cannot, and its
declared gaps — checked independently — contain no surprises; the two defects
found (an `inductive` escaping the "every declaration" audit, and a stale
theorem count in a header comment) are exactly the species of marker-for-property
error its own notes predict, and neither touches a proof.
