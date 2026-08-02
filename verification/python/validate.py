#!/usr/bin/env python3
"""
Deterministic consistency conditions (FIELD.md §6).
Run by CI on every candidate change. Exit 0 = consistent, 1 = violations.

These tests establish consistency, graph construction, and derivation.
They do NOT establish truth (LIM-0001).
"""
import json, os, sys, glob, re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
FIELD = os.path.join(REPO, "field")

ELEMENT_ID = re.compile(r"^(OBS|CLM|ASM|DEF|PER|TEN|BRG|TST|DIM|SYN|LIM)-\d{4}$")
OBSERVER_ID = re.compile(r"^OBS-(HUM|AI|HYB|DOC)-\d{4}$")
RELATION_ID = re.compile(r"^REL-\d{4}$")

KIND_PREFIX = {"observation": "OBS", "claim": "CLM", "assumption": "ASM", "definition": "DEF",
               "perspective": "PER", "tension": "TEN", "bridge": "BRG", "test": "TST",
               "dimension-proposal": "DIM", "synthesis": "SYN", "limit": "LIM"}
STATUSES = {"open", "accepted", "contested", "rejected", "superseded", "preserved-unresolved"}
ORIGIN_CLASSES = {"originating", "transformed", "aggregate"}
ATTRIBUTION = {"direct", "surrogate", "abstract"}
CONFIRMATIONS = {"confirmed", "modified", "rejected", "unconfirmed", "surrogate-verbatim"}
REL_TYPES = {"supports", "challenges", "contradicts-under-conditions", "compatible-under-conditions",
             "complements", "overlaps", "contains", "depends-on", "caused-by", "correlated-with",
             "translates-to", "partially-translates-to", "loses-information-when-translated-to",
             "applies-at-another-scale", "applies-at-another-time", "transforms-into",
             "counterexample-to", "shares-assumption-with", "requires-new-dimension",
             "remains-unresolved-with"}
SCALES = {"local-component", "subassembly", "assembly", "total-system", "ensemble", "multiscale"}
TSCOPES = {"instant", "cycle", "path-interval", "long-interval", "multi-interval"}
FRAMEWORKS = {"state-centered", "process-centered", "relation-centered", "observer-centered"}
OBSERVER_CLASSES = {"human", "ai-system", "hybrid", "document-surrogate"}

violations = []
def V(msg): violations.append(msg)

def load(pattern):
    out = {}
    for path in sorted(glob.glob(pattern)):
        try:
            with open(path) as f:
                d = json.load(f)
            out[d.get("id", os.path.basename(path))] = (d, path)
        except Exception as e:
            V(f"unparseable JSON: {path}: {e}")
    return out

def main():
    observers = load(os.path.join(FIELD, "observers", "*.json"))
    elements = load(os.path.join(FIELD, "elements", "*.json"))
    relations = load(os.path.join(FIELD, "relations", "*.json"))

    # ---- C1: formal well-formedness ----
    for oid, (o, p) in observers.items():
        if not OBSERVER_ID.match(o.get("id", "")): V(f"C1 {p}: bad observer id")
        if o.get("observer_class") not in OBSERVER_CLASSES: V(f"C1 {oid}: bad observer_class")
        # non-collapse: class must match id infix
        infix = o["id"].split("-")[1] if OBSERVER_ID.match(o.get("id", "")) else ""
        expect = {"HUM": "human", "AI": "ai-system", "HYB": "hybrid", "DOC": "document-surrogate"}.get(infix)
        if expect and o.get("observer_class") != expect:
            V(f"C1 {oid}: observer class '{o.get('observer_class')}' collapses distinction encoded in id (expected {expect})")

    for eid, (e, p) in elements.items():
        if not ELEMENT_ID.match(e.get("id", "")): V(f"C1 {p}: bad element id"); continue
        if e.get("kind") not in KIND_PREFIX: V(f"C1 {eid}: unknown kind"); continue
        if not e["id"].startswith(KIND_PREFIX[e["kind"]]): V(f"C1 {eid}: id prefix does not match kind {e['kind']}")
        if e.get("status") not in STATUSES: V(f"C1 {eid}: bad status")
        if e.get("origin_class") not in ORIGIN_CLASSES: V(f"C1 {eid}: bad origin_class")
        if e.get("attribution_mode") not in ATTRIBUTION: V(f"C1 {eid}: bad attribution_mode")
        if e.get("origin_confirmation") not in CONFIRMATIONS: V(f"C1 {eid}: bad origin_confirmation")
        if not e.get("expression", {}).get("original"): V(f"C1 {eid}: missing verbatim original expression")
        ctx = e.get("context", {})
        if ctx.get("scale") not in SCALES: V(f"C1 {eid}: bad context.scale")
        if ctx.get("temporal_scope") not in TSCOPES: V(f"C1 {eid}: bad context.temporal_scope")
        if not set(ctx.get("primitive_framework", [])) <= FRAMEWORKS or not ctx.get("primitive_framework"):
            V(f"C1 {eid}: bad context.primitive_framework")

    for rid, (r, p) in relations.items():
        if not RELATION_ID.match(r.get("id", "")): V(f"C1 {p}: bad relation id")
        if r.get("type") not in REL_TYPES: V(f"C1 {rid}: unknown relation type")

    # ---- C2: completeness of origin trace ----
    for eid, (e, _) in elements.items():
        ot = e.get("origin_trace", {})
        for k in ("origin_kind", "origin_ref", "capture_time"):
            if not ot.get(k): V(f"C2 {eid}: origin_trace missing {k}")
    for rid, (r, _) in relations.items():
        ot = r.get("origin_trace", {})
        for k in ("origin_kind", "origin_ref", "capture_time"):
            if not ot.get(k): V(f"C2 {rid}: origin_trace missing {k}")

    # ---- C3: validity of relation endpoints ----
    known = set(elements) | set(relations) | {"FIELD.md"}
    for rid, (r, _) in relations.items():
        for end in ("source", "target"):
            v = r.get(end)
            if v not in known: V(f"C3 {rid}: {end} '{v}' does not exist")

    # ---- C4: claims link to assumptions where declared; assumption refs valid ----
    for eid, (e, _) in elements.items():
        for a in e.get("depends_on_assumptions", []):
            if a not in elements: V(f"C4 {eid}: depends on missing assumption {a}")
            elif elements[a][0]["kind"] != "assumption": V(f"C4 {eid}: {a} is not an assumption")

    # ---- C5: origin-confirmation discipline ----
    for eid, (e, _) in elements.items():
        if e.get("origin_class") == "transformed":
            if "transformation" not in e:
                V(f"C5 {eid}: transformed element lacks transformation signature")
            if e.get("origin_confirmation") == "surrogate-verbatim":
                V(f"C5 {eid}: transformed element cannot claim surrogate-verbatim confirmation")
        if e.get("origin_confirmation") == "rejected" and e.get("status") == "accepted":
            V(f"C5 {eid}: origin-rejected interpretation may not hold accepted status")

    # ---- C6: operator attribution completeness ----
    for eid, (e, _) in elements.items():
        t = e.get("transformation")
        if t:
            for k in ("operator_family", "operator_revision", "ruleset_revision", "inputs", "generation_time"):
                if k not in t: V(f"C6 {eid}: transformation signature missing {k}")

    # ---- C7: contradictions must state conditions ----
    for rid, (r, _) in relations.items():
        if r["type"] in ("contradicts-under-conditions", "compatible-under-conditions"):
            c = r.get("conditions", {})
            if not any(k in c for k in ("same_referent", "same_definition", "same_scale", "overlapping_time")):
                V(f"C7 {rid}: contradiction/compatibility relation lacks explicit conditions")
        if r["type"] in ("translates-to", "partially-translates-to", "loses-information-when-translated-to"):
            tl = r.get("translation_ledger", {})
            if not tl.get("preserves") or not tl.get("loses"):
                V(f"C7 {rid}: translation relation must state what it preserves and loses")

    # ---- C8: observer references and dependence profile ----
    for eid, (e, _) in elements.items():
        if e.get("observer") not in observers: V(f"C8 {eid}: unknown observer {e.get('observer')}")
    for rid, (r, _) in relations.items():
        if r.get("observer") not in observers: V(f"C8 {rid}: unknown observer {r.get('observer')}")
    for oid, (o, _) in observers.items():
        if "dependence" not in o: V(f"C8 {oid}: missing dependence profile")

    # ---- C9: preserved tensions must carry reopening/elaboration; TEN-0001 must exist ----
    if "TEN-0001" not in elements:
        V("C9: TEN-0001 (the field's first element, per seed instruction) is missing")
    else:
        t1 = elements["TEN-0001"][0]
        if t1.get("status") != "preserved-unresolved":
            V("C9 TEN-0001: the first element must remain preserved-unresolved unless superseded by an accepted L3 change")
    for eid, (e, _) in elements.items():
        if e["kind"] == "tension" and e.get("status") == "preserved-unresolved":
            if not e.get("expression", {}).get("elaboration"):
                V(f"C9 {eid}: preserved tension lacks elaboration with reopening conditions")
            if not e.get("tension_class"): V(f"C9 {eid}: preserved tension lacks tension_class")

    # ---- C10: syntheses must carry the unresolved-difference ledger ----
    for eid, (e, _) in elements.items():
        if e["kind"] == "synthesis":
            sl = e.get("synthesis_ledger", {})
            for k in ("supporting", "opposing", "unresolved_questions", "reopening_conditions"):
                if k not in sl: V(f"C10 {eid}: synthesis ledger missing {k}")

    # ---- C11: dependence — flag derived-agreement loops (duplicated observers counted twice) ----
    # If two elements share observer, transformation family AND identical expression, that's duplication.
    seen = {}
    for eid, (e, _) in elements.items():
        key = (e.get("observer"), e.get("expression", {}).get("original", ""))
        if key in seen: V(f"C11 {eid}: duplicate expression of {seen[key]} by same observer (correlated agreement)")
        else: seen[key] = eid

    # ---- C12: atlas regeneration succeeds ----
    sys.path.insert(0, os.path.join(REPO, "projections"))
    try:
        import atlas as atlas_mod
        atlas_mod.build(write=True)
    except Exception as ex:
        V(f"C12: atlas regeneration failed: {ex}")

    # ---- report ----
    n = len(elements); m = len(relations); o = len(observers)
    print(f"elements={n} relations={m} observers={o}")
    if violations:
        print(f"\nINCONSISTENT — {len(violations)} violation(s):")
        for v in violations: print("  -", v)
        return 1
    print("CONSISTENT — all deterministic conditions passed (consistency, not truth).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
