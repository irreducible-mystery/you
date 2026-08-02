#!/usr/bin/env python3
"""
seed-ingestion operator, revision 1.0.0
=======================================
The field is born by self-ingesting the claims of the document
"Organized Change, Projection, and Generative Fields".

Bounds of this operator:
  - It may only APPEND elements and relations to field/.
  - Every originating expression is VERBATIM from the document
    (origin: OBS-DOC-0001, attribution: surrogate, confirmation: surrogate-verbatim).
  - Every interpretation added by the ai-system observer (OBS-AI-0001) is
    marked origin_class=transformed and origin_confirmation=unconfirmed.
  - It does not apply the acceptance map. Acceptance happens in review.
  - TEN-0001 (element-primacy vs relation-primacy) is written FIRST, honoring
    the seed instruction: "Preserve tension as the field's first element."

Deterministic: fixed capture time = genesis time, stable ordering.
"""
import json, os, sys

GENESIS_TIME = "2025-01-01T00:00:00Z"  # symbolic genesis timestamp; git history carries real time
RULESET = "FIELD.md@F0"
OP = {"operator_family": "seed-ingestion", "operator_revision": "1.0.0",
      "ruleset_revision": RULESET, "inputs": ["Organized_Change_Projection_and_Generative_Fields.docx"],
      "generation_time": GENESIS_TIME}

ROOT = os.path.join(os.path.dirname(__file__), "..", "field")

OBSERVERS = [
    {"id": "OBS-DOC-0001", "observer_class": "document-surrogate",
     "label": "Organized Change, Projection, and Generative Fields (source document)",
     "theta": {"position": "topic-agnostic Q&A treatment in mathematical, physical, geometric language",
               "scales_preserved": ["multiscale"],
               "primitive_frameworks": ["state-centered", "process-centered", "relation-centered", "observer-centered"],
               "known_sensitivities": ["organization of change", "projection failure", "generative structure"],
               "known_blind_spots": ["its own proposed design is one projection among possible designs"]},
     "dependence": {"shares_source_with": [], "shares_transformation_with": [], "shares_rule_with": []}},
    {"id": "OBS-HUM-0001", "observer_class": "human",
     "label": "irreducible-mystery (seed-giver)",
     "theta": {"position": "originating human observer; set the four seed commitments",
               "scales_preserved": [], "primitive_frameworks": [],
               "known_sensitivities": ["preservation of tension", "non-collapse of observer classes"],
               "known_blind_spots": ["unrecorded"]},
     "dependence": {"shares_source_with": ["OBS-DOC-0001"], "shares_transformation_with": [], "shares_rule_with": []}},
    {"id": "OBS-AI-0001", "observer_class": "ai-system",
     "label": "SuperNinja (NinjaTech AI) — builder instance at genesis",
     "theta": {"position": "AI agent that ingested the document and constructed F0",
               "scales_preserved": ["assembly", "total-system"],
               "primitive_frameworks": ["process-centered", "relation-centered"],
               "known_sensitivities": ["formal structure", "verifiability"],
               "known_blind_spots": ["shares the document as sole content source at genesis",
                                     "interpretations at F0 are unconfirmed by origins"]},
     "dependence": {"shares_source_with": ["OBS-DOC-0001", "OBS-HUM-0001"],
                    "shares_transformation_with": [], "shares_rule_with": ["FIELD.md@F0"]}},
]

def el(id, kind, status, origin_class, attribution, observer, original, scale, tscope,
       frameworks, distinctions=None, assumptions=None, confirmation="surrogate-verbatim",
       transformation=None, tension_class=None, elaboration=None, grounding=None, ledger=None):
    e = {"id": id, "kind": kind, "status": status, "origin_class": origin_class,
         "attribution_mode": attribution, "observer": observer,
         "expression": {"original": original},
         "context": {"scale": scale, "temporal_scope": tscope, "primitive_framework": frameworks},
         "origin_trace": {"origin_kind": "document" if observer == "OBS-DOC-0001" else "ai-expression",
                          "origin_ref": "Organized_Change_Projection_and_Generative_Fields.docx"
                          if observer == "OBS-DOC-0001" else "OBS-AI-0001@genesis",
                          "capture_time": GENESIS_TIME},
         "origin_confirmation": confirmation}
    if elaboration: e["expression"]["elaboration"] = elaboration
    if distinctions: e["distinctions"] = distinctions
    if assumptions: e["depends_on_assumptions"] = assumptions
    if transformation: e["transformation"] = transformation
    if tension_class: e["tension_class"] = tension_class
    if grounding: e["grounding"] = grounding
    if ledger: e["synthesis_ledger"] = ledger
    return e

ELEMENTS = [
    # ---- THE FIRST ELEMENT: the preserved seam (per seed instruction 1) ----
    el("TEN-0001", "tension", "preserved-unresolved", "originating", "surrogate", "OBS-DOC-0001",
       "Q7: 'The fundamental unit is not an answer. It is an attributed element situated within a context.' "
       "vs Q6: 'What lies beyond a multitude is not a larger number. It is relations before isolated elements... "
       "In a relational field, relations can be primary. Entities are relatively stable intersections within them.'",
       "total-system", "long-interval", ["relation-centered", "state-centered"],
       distinctions=["element-primacy vs relation-primacy",
                     "a field's implementation substrate need not share its ontology",
                     "the tension is structural, not accidental: any persistable field must serialize *something*"],
       tension_class="primitive-framework-mismatch",
       elaboration="Preserved by explicit seed instruction of OBS-HUM-0001: 'Preserve tension as the field's first "
                   "element.' Honored structurally: relations are first-class files with equal standing to elements. "
                   "Reopening condition: an accepted L3 change demonstrating a representation in which neither "
                   "elements nor relations are prior."),

    # ---- Q1: organization of change ----
    el("CLM-0001", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "A system does not merely undergo change. It channels change. The important distinction is not between "
       "change and no change, but between arbitrary change and change constrained by an organized set of possibilities.",
       "total-system", "multi-interval", ["process-centered"],
       distinctions=["arbitrary change vs organized change"]),
    el("CLM-0002", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "A system persists when its transformations are woven into a recursive order: organization -> structured "
       "change -> renewed or transformed organization. It continually regulates the conditions under which it may become different.",
       "total-system", "long-interval", ["process-centered"]),
    el("CLM-0003", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "Identity is not defined only by what a system is doing now. It also includes what it remains capable of "
       "doing: R(x) = {viable transformations accessible from x}.",
       "total-system", "multi-interval", ["process-centered", "state-centered"],
       distinctions=["identity as repertoire vs identity as state"]),
    el("CLM-0004", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "History becomes organization when previous change alters the rules of future change.",
       "multiscale", "long-interval", ["process-centered"]),

    # ---- Q2: types of organization ----
    el("CLM-0005", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "A system is never simply robust in the abstract. It is robust with respect to something. Antifragility "
       "must be specified as: antifragile to disturbance S over [S_1, S_2] on timescale T.",
       "total-system", "multi-interval", ["state-centered"],
       distinctions=["robustness vs resilience vs adaptation vs antifragility vs transformation vs collapse"]),
    el("CLM-0006", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "A type of organization is a structured way of distributing constraints, variation, memory, and control. "
       "Each distribution creates a distinctive mixture of robustness, adaptability, vulnerability, and possible transformation.",
       "total-system", "multi-interval", ["relation-centered"]),
    el("CLM-0007", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "Fractality does not imply resilience or antifragility. A branching network can distribute flow efficiently "
       "while remaining vulnerable at a critical branch. Fractality describes scaling; it does not by itself determine response to damage.",
       "multiscale", "multi-interval", ["state-centered"]),

    # ---- Q3: projection ----
    el("CLM-0008", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "Under what conditions can many detailed trajectories be represented as one coherent reduced trajectory? "
       "A successful coarse-graining approximately satisfies: pi o F_t ~= G_t o pi.",
       "multiscale", "path-interval", ["state-centered", "process-centered"],
       distinctions=["observational equivalence vs dynamical equivalence"]),
    el("CLM-0009", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "When history is projected away, it returns at the reduced level as memory; hidden variables can also "
       "appear as randomness. Randomness at one scale does not imply randomness at every scale.",
       "multiscale", "path-interval", ["process-centered"]),
    el("CLM-0010", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "Aggregate state != average component state. {0, 0, 10, 10} and {5, 5, 5, 5} have the same mean and "
       "different organizations. The aggregate is partly constituted by relations among components.",
       "ensemble", "instant", ["relation-centered"]),
    el("CLM-0011", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "Emergence = structured compression that retains consequential relations. Every compression creates blind spots.",
       "multiscale", "multi-interval", ["relation-centered"]),
    el("CLM-0012", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "Three geometries must be distinguished: the geometry of the system; the geometry induced by measurement; "
       "and the geometry produced by display. They need not agree.",
       "total-system", "instant", ["observer-centered"]),

    # ---- Q4: coordinated observation ----
    el("CLM-0013", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "With several observations, the underlying state must lie in the intersection of the ambiguity sets: "
       "x in intersection pi_i^(-1)(y_i). Collective observation can increase resolution without requiring any "
       "observer to perceive everything.",
       "ensemble", "instant", ["observer-centered"],
       grounding=[{"method": "lean-formal", "artifact": "verification/lean/Field/Invariants.lean",
                   "result": "ambiguity-set intersection narrowing proved as set-inclusion lemma"}]),
    el("CLM-0014", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "Consensus is not automatically accuracy. If all observers use the same transformation, their errors may be "
       "correlated. Many agreeing projections can reproduce one blind spot many times.",
       "ensemble", "multi-interval", ["observer-centered"]),
    el("CLM-0015", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "The goal is not many views -> one average. It is many situated views + relations among them + preserved "
       "disagreement -> a richer, revisable model.",
       "ensemble", "long-interval", ["observer-centered", "relation-centered"]),
    el("CLM-0016", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "Collective observation does not eliminate projection; it creates a higher-order projection. The "
       "synthesizing process must therefore be studied as part of the system.",
       "total-system", "long-interval", ["observer-centered"]),

    # ---- Q5: structured field ----
    el("DEF-0001", "definition", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "A structured field F = (P, D, R, C, T): positions, dimensions, relations, contexts, transitions. "
       "It shows how positions are related, when they apply, what assumptions generate them, and how movement between them occurs.",
       "total-system", "instant", ["relation-centered"]),
    el("CLM-0017", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "Generativity often appears where the current representation repeatedly fails: seams, holes, curvature, "
       "bifurcations, frustration, degeneracy, hysteresis, singularities, boundary cases.",
       "total-system", "multi-interval", ["relation-centered"]),
    el("CLM-0018", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "A good structured field permits several coordinate systems, local rather than universal metrics, observers "
       "whose descriptions do not fit the framing, untranslated observations, and revision of the field's own structure. "
       "The fields themselves may require an atlas.",
       "total-system", "long-interval", ["relation-centered", "observer-centered"]),

    # ---- Q6: beyond a multitude ----
    el("CLM-0019", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "A generative system can change the state space itself: X(t_1) != X(t_2), with coupled dynamics "
       "dx/dt = F(x, X); dX/dt = G(x, X). The system changes inside a possibility space while transforming that space.",
       "total-system", "long-interval", ["process-centered"]),
    el("CLM-0020", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "Observation becomes participation in the dynamics. There is no fixed perspective entirely outside the field.",
       "total-system", "multi-interval", ["observer-centered"]),
    el("CLM-0021", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "This does not make understanding impossible. It replaces completeness with revisability: "
       "M_t = best current organization of perspectives, limits, and possibilities; M_t -> M_(t+1).",
       "total-system", "long-interval", ["process-centered"]),

    # ---- Q7: the design ----
    el("CLM-0022", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "Originating observations and transformed elements may both enter the field, but no transformation may "
       "silently replace its origin. Every interpretation must remain traceable, challengeable, and revisable.",
       "total-system", "long-interval", ["observer-centered"]),
    el("CLM-0023", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "Number of outputs != number of independent perspectives. Correlated agreement must not be counted as "
       "independent confirmation.",
       "ensemble", "instant", ["observer-centered"]),
    el("CLM-0024", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "The field becomes generative when contributions can modify not only its contents but its structure. "
       "Changes at L_3 require the strongest conditions because they change what the field is capable of representing.",
       "total-system", "long-interval", ["process-centered"]),
    el("CLM-0025", "claim", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "The system should preserve not one collective answer, but the evolving and inspectable organization "
       "through which answers, assumptions, tensions, and new possibilities arise.",
       "total-system", "long-interval", ["process-centered", "observer-centered"]),

    # ---- assumptions the genesis itself depends on (made explicit) ----
    el("ASM-0001", "assumption", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "An append-preserving ordered sequence of accepted states is an adequate substrate for a field that must "
       "remain traceable and revisable.",
       "total-system", "long-interval", ["state-centered"]),
    el("ASM-0002", "assumption", "open", "transformed", "direct", "OBS-AI-0001",
       "Git commits on main can serve as the accepted-state sequence F_n, pull requests as candidate changes, and "
       "independent review-and-merge as the acceptance map, without distorting the design's intent.",
       "total-system", "long-interval", ["state-centered"],
       confirmation="unconfirmed", transformation=OP,
       elaboration="An implementation mapping proposed by the ai-system builder. It inherits git's particular "
                   "geometry (linear-ish history, file granularity) as measurement geometry — see CLM-0012."),
    el("ASM-0003", "assumption", "open", "transformed", "direct", "OBS-AI-0001",
       "At genesis, all content descends from a single source document; therefore F0 has maximal source "
       "correlation and zero independent confirmation. The field's claims are seeded, not established.",
       "ensemble", "instant", ["observer-centered"],
       confirmation="unconfirmed", transformation=OP),

    # ---- tensions beyond TEN-0001, detected at ingestion ----
    el("TEN-0002", "tension", "preserved-unresolved", "transformed", "direct", "OBS-AI-0001",
       "Self-reference at genesis: the field's first contents are the claims of the document that specifies the "
       "field. The rules used to test the claims are derived from the claims being tested.",
       "total-system", "instant", ["observer-centered"],
       tension_class="self-reference", confirmation="unconfirmed", transformation=OP,
       elaboration="Per CLM-0014 this is a correlated-error risk: consensus of field with document is not accuracy. "
                   "Mitigation path: admit differently-situated observers and external grounding (braided verification). "
                   "Reopening condition: first accepted contribution from an observer independent of OBS-DOC-0001."),
    el("TEN-0003", "tension", "preserved-unresolved", "transformed", "direct", "OBS-AI-0001",
       "Bootstrap acceptance: F0 enters the accepted sequence before the acceptance machinery it defines could be "
       "applied to it. Genesis is self-accepting in a way every later change is forbidden to be.",
       "total-system", "instant", ["process-centered"],
       tension_class="self-reference", confirmation="unconfirmed", transformation=OP,
       elaboration="Partially mitigated: OBS-HUM-0001 issued the four seed commitments and can reject F0 wholesale. "
                   "Recorded rather than hidden."),
    el("TEN-0004", "tension", "preserved-unresolved", "transformed", "direct", "OBS-AI-0001",
       "The stability/change vocabulary of the field cannot distinguish changes that can be undone from changes "
       "that permanently alter the system.",
       "total-system", "multi-interval", ["state-centered", "process-centered"],
       tension_class="scale-mismatch", confirmation="unconfirmed", transformation=OP,
       elaboration="The document itself (Q7 §16) offers this as the canonical example of a structure-modifying "
                   "contribution. It is seeded as a live tension so the field's first candidate change (DIM-0001, "
                   "the reversibility dimension) can demonstrate the L2->L3 acceptance cycle."),

    # ---- the first dimension proposal (arrives as a candidate change, not in F0's accepted set) ----

    # ---- limits, stated at birth ----
    el("LIM-0001", "limit", "accepted", "transformed", "direct", "OBS-AI-0001",
       "The derived atlas, the Lean invariants, the Python validator, and the Julia re-derivations are all "
       "projections. None is primary reality. Deterministic tests establish consistency and derivation; they do "
       "not establish truth.",
       "total-system", "long-interval", ["observer-centered"],
       confirmation="unconfirmed", transformation=OP),
    el("LIM-0002", "limit", "accepted", "transformed", "direct", "OBS-AI-0001",
       "A system that changes its own dimensions and possibilities may not admit one final exhaustive "
       "representation. This field does not claim completeness for itself at any F_n.",
       "total-system", "long-interval", ["process-centered"],
       confirmation="unconfirmed", transformation=OP),

    # ---- perspectives (one per observer class present at genesis) ----
    el("PER-0001", "perspective", "accepted", "originating", "surrogate", "OBS-DOC-0001",
       "The document speaks in topic-agnostic mathematical, physical, and geometric language; it deliberately "
       "avoids domain examples so that its structures can be projected into many domains.",
       "total-system", "long-interval", ["state-centered", "process-centered", "relation-centered", "observer-centered"]),
    el("PER-0002", "perspective", "accepted", "originating", "direct", "OBS-HUM-0001",
       "Seed commitments: (1) preserve tension as the field's first element; (2) the field is a seed for many "
       "observers/participants, both AI and human — the distinction between different systems should not be "
       "collapsed; (3) braided grounding in Lean, Julia, Python, TypeScript and other methods as needed; "
       "(4) the field is born by self-ingesting the document's own claims.",
       "total-system", "long-interval", ["observer-centered"],
       confirmation="confirmed",
       elaboration="Verbatim from the seed conversation, lightly normalized for spelling. The four commitments are "
                   "L3-level constraints recorded in FIELD.md."),
    el("PER-0003", "perspective", "accepted", "originating", "direct", "OBS-AI-0001",
       "Builder's situated view: I constructed F0 by projecting the document into schemas, operators, validators, "
       "and proofs. My known blind spots at genesis: I share the document as sole content source; my "
       "interpretations are unconfirmed; my formal emphasis is itself a projection preference.",
       "total-system", "instant", ["observer-centered"],
       confirmation="confirmed", transformation=OP),
]

RELATIONS = [
    # TEN-0001 wiring (the seam, connected)
    {"id": "REL-0001", "type": "remains-unresolved-with", "source": "TEN-0001", "target": "CLM-0025",
     "notes": "The field preserves the seam as part of its inspectable organization."},
    {"id": "REL-0002", "type": "contradicts-under-conditions", "source": "CLM-0022", "target": "CLM-0019",
     "conditions": {"same_referent": False, "same_definition": False, "same_scale": None, "overlapping_time": True,
                    "notes": "Only a conditional contradiction: Q7's attributed-element unit (implementation ontology) vs "
                             "Q6's relation-primacy (conceptual ontology). If 'fundamental' means 'serialization unit' the "
                             "contradiction dissolves; if it means 'what is conceptually prior' it stands.",
                    "unresolved_questions": ["Can a persistable field avoid privileging either serialization or ontology?"]}},
    {"id": "REL-0003", "type": "depends-on", "source": "TEN-0001", "target": "REL-0002",
     "notes": "The first element depends on a first-class relation — enacting the seam it preserves."},

    # organization of change cluster
    {"id": "REL-0004", "type": "supports", "source": "CLM-0004", "target": "CLM-0002"},
    {"id": "REL-0005", "type": "complements", "source": "CLM-0003", "target": "CLM-0002"},
    {"id": "REL-0006", "type": "supports", "source": "CLM-0006", "target": "CLM-0005"},
    {"id": "REL-0007", "type": "challenges", "source": "CLM-0007", "target": "CLM-0006",
     "notes": "Architecture does not determine outcome: scaling form alone does not fix disturbance response."},

    # projection cluster
    {"id": "REL-0008", "type": "supports", "source": "CLM-0010", "target": "CLM-0011"},
    {"id": "REL-0009", "type": "supports", "source": "CLM-0009", "target": "CLM-0008"},
    {"id": "REL-0010", "type": "depends-on", "source": "CLM-0011", "target": "CLM-0008"},
    {"id": "REL-0011", "type": "complements", "source": "CLM-0012", "target": "CLM-0011"},

    # observation cluster
    {"id": "REL-0012", "type": "supports", "source": "CLM-0013", "target": "CLM-0015"},
    {"id": "REL-0013", "type": "challenges", "source": "CLM-0014", "target": "CLM-0013",
     "notes": "Intersection of ambiguity sets narrows only when projections are relevantly diverse; correlated observers do not narrow."},
    {"id": "REL-0014", "type": "supports", "source": "CLM-0023", "target": "CLM-0014"},
    {"id": "REL-0015", "type": "contains", "source": "CLM-0016", "target": "CLM-0015",
     "notes": "The synthesis-as-higher-order-projection claim contains the situated-views program as a special case."},

    # field-structure cluster
    {"id": "REL-0016", "type": "depends-on", "source": "CLM-0017", "target": "DEF-0001"},
    {"id": "REL-0017", "type": "supports", "source": "CLM-0018", "target": "CLM-0021"},
    {"id": "REL-0018", "type": "transforms-into", "source": "DEF-0001", "target": "CLM-0019",
     "notes": "Structured field -> generative field: the transition from fixed dimensions to generated dimensions."},
    {"id": "REL-0019", "type": "supports", "source": "CLM-0020", "target": "CLM-0016"},

    # design cluster
    {"id": "REL-0020", "type": "depends-on", "source": "CLM-0022", "target": "ASM-0001"},
    {"id": "REL-0021", "type": "depends-on", "source": "ASM-0002", "target": "ASM-0001"},
    {"id": "REL-0022", "type": "supports", "source": "CLM-0024", "target": "CLM-0019",
     "notes": "L3 changes are the concrete mechanism for X(t1) != X(t2)."},
    {"id": "REL-0023", "type": "supports", "source": "CLM-0025", "target": "CLM-0021"},

    # genesis self-diagnosis
    {"id": "REL-0024", "type": "counterexample-to", "source": "TEN-0003", "target": "CLM-0022",
     "notes": "Genesis is the one transformation whose acceptance preceded the acceptance machinery. Marked, not hidden."},
    {"id": "REL-0025", "type": "depends-on", "source": "TEN-0002", "target": "ASM-0003"},
    {"id": "REL-0026", "type": "shares-assumption-with", "source": "PER-0003", "target": "PER-0001",
     "notes": "Builder and document share the source-correlation of genesis (ASM-0003)."},
    {"id": "REL-0027", "type": "requires-new-dimension", "source": "TEN-0004", "target": "DEF-0001",
     "notes": "The reversibility distinction is inexpressible in the seeded coordinates; a dimension proposal is expected as the first candidate change."},
    {"id": "REL-0028", "type": "applies-at-another-scale", "source": "CLM-0012", "target": "ASM-0002",
     "notes": "Git's geometry is measurement geometry for the field: file granularity, commit ordering, diff display."},
    {"id": "REL-0029", "type": "loses-information-when-translated-to", "source": "PER-0002", "target": "FIELD.md",
     "translation_ledger": {"preserves": ["the four commitments as enforceable constraints"],
                            "loses": ["tone, emphasis, and the conversational context of the seed instructions"],
                            "valid_range": "governance of F0 onward", "invalid_range": "reconstruction of the seed conversation"},
     "notes": "Translating seed instructions into constitutional text preserves force but loses situation."},
]

def main():
    os.makedirs(os.path.join(ROOT, "elements"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "relations"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "observers"), exist_ok=True)

    for o in OBSERVERS:
        with open(os.path.join(ROOT, "observers", o["id"] + ".json"), "w") as f:
            json.dump(o, f, indent=2); f.write("\n")

    for e in ELEMENTS:
        with open(os.path.join(ROOT, "elements", e["id"] + ".json"), "w") as f:
            json.dump(e, f, indent=2); f.write("\n")

    for r in RELATIONS:
        rel = {"id": r["id"], "type": r["type"], "source": r["source"], "target": r["target"],
               "observer": "OBS-AI-0001" if r["id"] in
                   {"REL-0024", "REL-0025", "REL-0026", "REL-0027", "REL-0028", "REL-0029", "REL-0021", "REL-0003"}
                   else "OBS-DOC-0001",
               "status": "accepted",
               "origin_trace": {"origin_kind": "derived", "origin_ref": "seed-ingestion@1.0.0",
                                "capture_time": GENESIS_TIME},
               "transformation": OP}
        if "conditions" in r: rel["conditions"] = r["conditions"]
        if "translation_ledger" in r: rel["translation_ledger"] = r["translation_ledger"]
        if "notes" in r and "conditions" not in r:
            rel.setdefault("conditions", {})["notes"] = r["notes"]
        with open(os.path.join(ROOT, "relations", r["id"] + ".json"), "w") as f:
            json.dump(rel, f, indent=2); f.write("\n")

    print(f"seeded {len(OBSERVERS)} observers, {len(ELEMENTS)} elements, {len(RELATIONS)} relations")
    print("first element: TEN-0001 (preserved-unresolved) — per seed instruction of OBS-HUM-0001")

if __name__ == "__main__":
    main()
