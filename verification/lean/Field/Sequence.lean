/-
  Field/Sequence.lean — invariants of the accepted-state SEQUENCE, and the
  sharp form of ambiguity narrowing.

  Companion to Field/Invariants.lean. Same discipline: core Lean 4 only, no
  external dependencies, no `sorry`, no axioms. Grounds FIELD.md §1, §5–§7,
  CLM-0013, CLM-0014, CLM-0023, ASM-0001.

  Three gaps in Invariants.lean are closed here, and one is recorded as NOT
  closable in Lean at all (§0).
-/

namespace Field

/-! ## 0. What Lean cannot reach, stated before anything it can

`Invariants.lean` proves

    theorem no_self_acceptance (a) (h : Admissible a) :
        ¬ (a.acceptor = a.change.proposer) := h

`Admissible a` is *defined* as `a.acceptor ≠ a.change.proposer`, and `≠` is
notation for `¬ (· = ·)`. So the statement is the hypothesis, unfolded, and the
proof is the identity function. It is true, it is not wrong to have written, and
it establishes nothing about the field.

**The content the field wants is not a theorem.** It is that the acceptance
recorded in git *actually had* an acceptor distinct from the proposer.
`Admissible` is a hypothesis in every theorem below; discharging it is the job
of something outside Lean.

`AcceptanceDischarged` names that obligation so it is visible in the build
rather than implied by a theorem name. Nothing here proves it. -/

structure Agent where
  id : Nat
deriving DecidableEq

structure CandidateChange where
  proposer : Agent

structure Acceptance where
  acceptor : Agent
  change   : CandidateChange

def Admissible (a : Acceptance) : Prop :=
  a.acceptor ≠ a.change.proposer

/-- **The open obligation.** For a run to mean what FIELD.md §7 says, every
    recorded acceptance must in fact be admissible. This proposition is stated,
    never proved, and every theorem below takes it as a hypothesis. -/
def AcceptanceDischarged (run : List Acceptance) : Prop :=
  ∀ a ∈ run, Admissible a

/-! ## 1. No solo run

The non-tautological statement in the neighbourhood of `no_self_acceptance`:
a single agent cannot be the only participant in a nonempty run. This is about
the RUN, not about one acceptance, so it is not its own hypothesis. -/

/-- Every agent who acted in the run, in either role. -/
def participants : List Acceptance → List Agent
  | []      => []
  | a :: as => a.acceptor :: a.change.proposer :: participants as

/-- **Invariant 5**: a nonempty admissible run has at least two distinct
    participants. No agent advances the field alone. -/
theorem no_solo_run (a : Acceptance) (as : List Acceptance)
    (h : AcceptanceDischarged (a :: as)) :
    ∃ x y : Agent, x ≠ y ∧ x ∈ participants (a :: as) ∧ y ∈ participants (a :: as) := by
  refine ⟨a.acceptor, a.change.proposer, h a (List.Mem.head as), ?_, ?_⟩
  · exact List.Mem.head _
  · exact List.Mem.tail _ (List.Mem.head _)

/-! ## 2. The SEQUENCE, not one step

`Invariants.lean`'s `history_preserved` covers one transition `Fn → Fm`. The
field is a sequence `F₀ → F₁ → …` (FIELD.md §1), so the claim that nothing is
ever erased needs transitivity and a chain. -/

def AppendsTo (Fn Fm : List Nat) : Prop :=
  ∃ new, Fm = Fn ++ new

/-- Proved here rather than imported, so the file stays axiom-free:
    `List.append_nil` and `List.append_assoc` in core are `simp`-produced and
    carry `propext`. These do not. -/
theorem app_nil : ∀ l : List Nat, l ++ [] = l
  | []     => rfl
  | a :: t => congrArg (a :: ·) (app_nil t)

/-- Core's `List.mem_append_left` carries `propext` on Lean 4.9.0 (the pin in
    `.github/workflows/consistency.yml`) but not on 4.22.0. Proving it locally
    keeps the axiom footprint identical on both toolchains. See §5. -/
theorem mem_app_left {e : Nat} : ∀ {a : List Nat} (b : List Nat), e ∈ a → e ∈ a ++ b := by
  intro a b h
  induction a with
  | nil => cases h
  | cons x t ih =>
    cases h with
    | head => show e ∈ e :: (t ++ b); exact List.Mem.head _
    | tail _ h' => show e ∈ x :: (t ++ b); exact List.Mem.tail _ (ih h')

theorem app_assoc : ∀ a b c : List Nat, a ++ b ++ c = a ++ (b ++ c)
  | [],     _, _ => rfl
  | x :: t, b, c => congrArg (x :: ·) (app_assoc t b c)

theorem appendsTo_refl (F : List Nat) : AppendsTo F F :=
  ⟨[], (app_nil F).symm⟩

/-- **Invariant 6a**: appending is transitive. -/
theorem appendsTo_trans {A B C : List Nat}
    (h₁ : AppendsTo A B) (h₂ : AppendsTo B C) : AppendsTo A C := by
  obtain ⟨n₁, rfl⟩ := h₁
  obtain ⟨n₂, rfl⟩ := h₂
  exact ⟨n₁ ++ n₂, app_assoc A n₁ n₂⟩

/-- A field history: an accepted state for every index, each appending to the
    last. This is FIELD.md §1's `F₀ → F₁ → F₂ → …`. -/
def IsHistory (F : Nat → List Nat) : Prop :=
  ∀ n, AppendsTo (F n) (F (n + 1))

/-- **Invariant 6b**: in a history, every state appends to every later state. -/
theorem appendsTo_of_le {F : Nat → List Nat} (hF : IsHistory F) :
    ∀ m n, m ≤ n → AppendsTo (F m) (F n) := by
  intro m n h
  induction n with
  | zero =>
    have : m = 0 := Nat.le_zero.mp h
    subst this; exact appendsTo_refl _
  | succ k ih =>
    rcases Nat.lt_or_ge m (k + 1) with hlt | hge
    · exact appendsTo_trans (ih (Nat.lt_succ_iff.mp hlt)) (hF k)
    · have : m = k + 1 := Nat.le_antisymm h hge
      subst this; exact appendsTo_refl _

/-- **Invariant 6c** — the statement FIELD.md §1 actually needs: in a history,
    anything accepted at any stage is still present at every later stage.
    Not one hop: the whole sequence. -/
theorem history_preserved_forever {F : Nat → List Nat} (hF : IsHistory F)
    (m n : Nat) (hmn : m ≤ n) (e : Nat) (he : e ∈ F m) : e ∈ F n := by
  obtain ⟨new, hnew⟩ := appendsTo_of_le hF m n hmn
  rw [hnew]
  exact mem_app_left new he

/-! ## 3. Ambiguity narrowing, in its sharp form

`Invariants.lean`'s `correlated_view_adds_nothing` is stated for two *identical*
projections `π π`. CLM-0014 is about *correlated* views, which is weaker than
identical — so the theorem proves only the extreme case.

The sharp condition is **constancy on fibers**: a second view adds nothing
exactly when it cannot distinguish states the first view already identifies.
Identical projections are the special case. No choice, no `f` constructed. -/

variable {X Y₁ Y₂ : Type}

def fiber (π : X → Y₁) (y : Y₁) : X → Prop := fun x => π x = y

def jointFiber (π₁ : X → Y₁) (π₂ : X → Y₂) (y₁ : Y₁) (y₂ : Y₂) : X → Prop :=
  fun x => π₁ x = y₁ ∧ π₂ x = y₂

/-- `π₂` is constant on the fibers of `π₁`: it sees nothing `π₁` does not. -/
def ConstantOnFibers (π₁ : X → Y₁) (π₂ : X → Y₂) : Prop :=
  ∀ x x', π₁ x = π₁ x' → π₂ x = π₂ x'

/-- **Invariant 7a**: a view constant on the fibers of another narrows nothing,
    at every observed value. Generalises `correlated_view_adds_nothing` from
    *identical* projections to *correlated* ones. -/
theorem constant_view_adds_nothing (π₁ : X → Y₁) (π₂ : X → Y₂)
    (hc : ConstantOnFibers π₁ π₂) (x₀ : X) :
    ∀ x, jointFiber π₁ π₂ (π₁ x₀) (π₂ x₀) x ↔ fiber π₁ (π₁ x₀) x := by
  intro x
  constructor
  · exact fun h => h.1
  · intro h
    exact ⟨h, hc x x₀ h⟩

/-- **Invariant 7b**, the converse: if a second view never narrows, it was
    constant on fibers. So constancy is not merely sufficient — it is the whole
    of "adds nothing". -/
theorem adds_nothing_implies_constant (π₁ : X → Y₁) (π₂ : X → Y₂)
    (h : ∀ x₀ x, jointFiber π₁ π₂ (π₁ x₀) (π₂ x₀) x ↔ fiber π₁ (π₁ x₀) x) :
    ConstantOnFibers π₁ π₂ := by
  intro x x' hx
  exact ((h x' x).mpr hx).2

/-- **Invariant 7c**: a factored view — `π₂ = f ∘ π₁`, the usual way a
    correlated view arises in practice — is constant on fibers, hence adds
    nothing. -/
theorem factored_is_constant (π₁ : X → Y₁) (π₂ : X → Y₂) (f : Y₁ → Y₂)
    (hf : ∀ x, π₂ x = f (π₁ x)) : ConstantOnFibers π₁ π₂ := by
  intro x x' hx
  rw [hf x, hf x', hx]

/-! ## 4. The quantitative form, matching G4

G4 measures ambiguity shrinking 400 → 100 → 20 → 5 and a correlated view
shrinking nothing. Here is the counting statement behind it, over a finite
carrier given as a list. -/

/-- How many candidate states in `xs` a single view leaves indistinguishable. -/
def b2n : Bool → Nat
  | true  => 1
  | false => 0

/-- Own counter rather than `List.filter … |>.length`: this reduces
    definitionally on `true`/`false`, which keeps the proofs axiom-free. -/
def countP (p : X → Bool) : List X → Nat
  | []     => 0
  | a :: t => countP p t + b2n (p a)

def ambiguity (π : X → Y₁) [DecidableEq Y₁] (xs : List X) (y : Y₁) : Nat :=
  countP (fun x => decide (π x = y)) xs

/-- Joint ambiguity under two views. -/
def jointAmbiguity (π₁ : X → Y₁) (π₂ : X → Y₂) [DecidableEq Y₁] [DecidableEq Y₂]
    (xs : List X) (y₁ : Y₁) (y₂ : Y₂) : Nat :=
  countP (fun x => decide (π₁ x = y₁) && decide (π₂ x = y₂)) xs

/-- **Invariant 8a**: a second view never enlarges the ambiguity count.
    The quantitative form of `intersection_narrows`. -/
theorem jointAmbiguity_le (π₁ : X → Y₁) (π₂ : X → Y₂)
    [DecidableEq Y₁] [DecidableEq Y₂] (xs : List X) (y₁ : Y₁) (y₂ : Y₂) :
    jointAmbiguity π₁ π₂ xs y₁ y₂ ≤ ambiguity π₁ xs y₁ := by
  induction xs with
  | nil => exact Nat.le_refl 0
  | cons a t ih =>
    show countP _ t + b2n (decide (π₁ a = y₁) && decide (π₂ a = y₂))
       ≤ countP _ t + b2n (decide (π₁ a = y₁))
    cases _hb : decide (π₁ a = y₁) <;> cases _hc : decide (π₂ a = y₂)
    · exact ih
    · exact ih
    · exact Nat.le_succ_of_le ih
    · exact Nat.succ_le_succ ih

/-- **Invariant 8b**: when the second view is constant on the first's fibers,
    the counts are equal — the correlated view shrinks nothing, measured. -/
theorem jointAmbiguity_eq_of_constant (π₁ : X → Y₁) (π₂ : X → Y₂)
    [DecidableEq Y₁] [DecidableEq Y₂] (hc : ConstantOnFibers π₁ π₂)
    (xs : List X) (x₀ : X) :
    jointAmbiguity π₁ π₂ xs (π₁ x₀) (π₂ x₀) = ambiguity π₁ xs (π₁ x₀) := by
  induction xs with
  | nil => rfl
  | cons a t ih =>
    show countP _ t + b2n (decide (π₁ a = π₁ x₀) && decide (π₂ a = π₂ x₀))
       = countP _ t + b2n (decide (π₁ a = π₁ x₀))
    cases hb : decide (π₁ a = π₁ x₀)
    · exact congrArg (· + 0) ih
    · have h₂ : decide (π₂ a = π₂ x₀) = true :=
        decide_eq_true (hc a x₀ (of_decide_eq_true hb))
      rw [h₂]
      exact congrArg (· + 1) ih

/-! ## 5. An axiom audit is a property of (proof, toolchain)

Measured, not asserted. Running `#print axioms` over every declaration in both
files, under both toolchains:

    Lean 4.9.0   (the CI pin)   Invariants.lean + Sequence.lean
                                44 / 46 axiom-free
                                `history_preserved` : [propext]
                                `history_preserved_forever` : [propext]

    Lean 4.22.0                 46 / 46 axiom-free

Nothing about either proof changed. `List.mem_append_left` is `simp`-produced in
4.9.0 and carries `propext`; by 4.22.0 it does not. The same proof text has two
different axiom footprints depending on which kernel reads it.

`Sequence.lean` now proves `mem_app_left` locally and is axiom-free on both.
`Invariants.lean` is untouched here — changing it is an L3-adjacent act and
belongs to whoever owns that file. The one-line change is the same one:
`List.mem_append_left` → a local structural proof.

The general point, which is a claim about method rather than about lists:
**an axiom audit certifies a pair, not a proof.** A repository that pins a
toolchain and reports an audit is reporting a fact about that pin. Re-pinning is
not a neutral maintenance act. -/

end Field
