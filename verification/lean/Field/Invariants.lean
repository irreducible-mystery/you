/-
  Field/Invariants.lean — machine-checked invariants of the field's rules.
  Grounds: FIELD.md §5–§7, CLM-0013, CLM-0022, CLM-0023.

  These proofs establish properties of the RULES, not truth of the CONTENTS
  (LIM-0001). Uses only core Lean 4 — no external dependencies.
-/

namespace Field

/-! ### 1. No self-acceptance (FIELD.md §5, §7)

A candidate change carries its proposer. An acceptance map is *admissible*
only if the acceptor differs from the proposer. We prove that under any
admissible acceptance relation, no operator accepts its own change. -/

structure Agent where
  id : Nat
deriving DecidableEq

structure CandidateChange where
  proposer : Agent

structure Acceptance where
  acceptor : Agent
  change   : CandidateChange

/-- Admissibility: the acceptor is independent of the proposer. -/
def Admissible (a : Acceptance) : Prop :=
  a.acceptor ≠ a.change.proposer

/-- **Invariant 1**: an admissible acceptance is never a self-acceptance. -/
theorem no_self_acceptance (a : Acceptance) (h : Admissible a) :
    ¬ (a.acceptor = a.change.proposer) := h

/-- Corollary: the act "operator X accepts the change X proposed" is
    inadmissible by construction. -/
theorem self_acceptance_inadmissible (x : Agent) (c : CandidateChange)
    (hx : c.proposer = x) : ¬ Admissible ⟨x, c⟩ := by
  intro h
  exact h hx.symm

/-! ### 2. Origin-trace completeness (CLM-0022)

A transformed element without a transformation signature cannot be
well-formed. Hence every well-formed transformed element is traceable:
no transformation silently replaces its origin. -/

inductive OriginClass | originating | transformed | aggregate
deriving DecidableEq

structure Signature where
  operatorFamily : String
  inputs : List Nat   -- references to input elements

structure Element where
  originClass : OriginClass
  signature   : Option Signature
  originalExpression : String

/-- Well-formedness per the deterministic conditions (validator C5/C6). -/
def WellFormed (e : Element) : Prop :=
  (e.originClass = OriginClass.transformed → e.signature.isSome) ∧
  e.originalExpression ≠ ""

/-- **Invariant 2**: a well-formed transformed element always carries a
    transformation signature — it is traceable, never unoriginated. -/
theorem transformed_is_traceable (e : Element) (hw : WellFormed e)
    (ht : e.originClass = OriginClass.transformed) :
    e.signature.isSome := hw.1 ht

/-- **Invariant 2b**: a well-formed element never loses its verbatim
    originating expression. -/
theorem origin_expression_preserved (e : Element) (hw : WellFormed e) :
    e.originalExpression ≠ "" := hw.2

/-! ### 3. Ambiguity sets under coordinated observation (CLM-0013, CLM-0014)

Observation i is a projection πᵢ : X → Yᵢ. The ambiguity set (fiber) of an
observation is πᵢ⁻¹(yᵢ). We prove:
  (a) the true state lies in every fiber, hence in their intersection;
  (b) adding a view never enlarges the ambiguity set (monotone narrowing);
  (c) a *correlated* second view (same projection) adds nothing —
      the formal core of "consensus is not automatically accuracy". -/

variable {X Y₁ Y₂ : Type}

/-- Fiber (ambiguity set) of an observation. -/
def fiber (π : X → Y₁) (y : Y₁) : X → Prop := fun x => π x = y

/-- Joint ambiguity set of two observations. -/
def jointFiber (π₁ : X → Y₁) (π₂ : X → Y₂) (y₁ : Y₁) (y₂ : Y₂) : X → Prop :=
  fun x => π₁ x = y₁ ∧ π₂ x = y₂

/-- **Invariant 3a**: the true state is in the joint ambiguity set. -/
theorem true_state_in_intersection (π₁ : X → Y₁) (π₂ : X → Y₂) (x : X) :
    jointFiber π₁ π₂ (π₁ x) (π₂ x) x := ⟨rfl, rfl⟩

/-- **Invariant 3b**: adding a second view never enlarges ambiguity —
    the joint fiber is contained in the single fiber. -/
theorem intersection_narrows (π₁ : X → Y₁) (π₂ : X → Y₂) (y₁ : Y₁) (y₂ : Y₂) :
    ∀ x, jointFiber π₁ π₂ y₁ y₂ x → fiber π₁ y₁ x :=
  fun _ h => h.1

/-- **Invariant 3c**: a correlated second view (identical projection) leaves
    the ambiguity set exactly unchanged. Many agreeing projections can
    reproduce one blind spot many times (CLM-0014, CLM-0023). -/
theorem correlated_view_adds_nothing (π : X → Y₁) (y : Y₁) :
    ∀ x, jointFiber π π y y x ↔ fiber π y x := by
  intro x
  constructor
  · exact fun h => h.1
  · exact fun h => ⟨h, h⟩

/-! ### 4. Append-preservation of the accepted-state sequence (ASM-0001)

Modeled minimally: a state is a list of element ids; a transition may only
append. We prove membership is monotone — nothing accepted is ever erased. -/

def AppendsTo (Fn Fm : List Nat) : Prop :=
  ∃ new, Fm = Fn ++ new

/-- **Invariant 4**: under append-only transitions, every element of an
    earlier accepted state remains in every later state. -/
theorem history_preserved (Fn Fm : List Nat) (h : AppendsTo Fn Fm)
    (e : Nat) (he : e ∈ Fn) : e ∈ Fm := by
  obtain ⟨new, rfl⟩ := h
  exact List.mem_append_left new he

end Field
