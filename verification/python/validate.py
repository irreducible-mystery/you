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
    # Keyed by id, so two files declaring the same id used to COLLAPSE: one
    # silently replaced the other in the validated view while both survived
    # into projections/atlas.py, which loads into a list. The two instruments
    # then disagreed about how many elements exist and nothing compared them.
    # A duplicate id is now a violation, not a merge.
    out = {}
    for path in sorted(glob.glob(pattern)):
        try:
            with open(path) as f:
                d = json.load(f)
        except Exception as e:
            V(f"unparseable JSON: {path}: {e}")
            continue
        key = d.get("id", os.path.basename(path))
        if key in out:
            V(f"C0 {key}: declared by two files ({out[key][1]} and {path}); "
              f"one would silently replace the other in every condition below")
            continue
        out[key] = (d, path)
    return out


def complement(subdir, loaded):
    # THE COMPLEMENT. glob('<dir>/*.json') is flat: a record one directory down,
    # or with another extension, was invisible rather than rejected — and the
    # intake instructions tell contributors to hand-add these files. An
    # enumeration that reports only what it reached cannot report what it
    # missed, so both numbers are produced and required to agree.
    root = os.path.join(FIELD, subdir)
    on_disk = [p for p in glob.glob(os.path.join(root, "**", "*"), recursive=True)
               if os.path.isfile(p)]
    stray = [p for p in on_disk if os.path.dirname(p) != root or not p.endswith(".json")]
    for p in sorted(stray):
        V(f"C0b {os.path.relpath(p, REPO)}: outside {subdir}/*.json, so no condition "
          f"below inspects it. Move it, or it is not in the field.")
    return len(on_disk), len(loaded) + len(stray)

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

    # ---- C12a: reflection skeletons may not hold accepted/preserved status ----
    for eid, (e, _) in elements.items():
        blob = json.dumps(e)
        if ("TODO-RESTATEMENT" in blob or "TODO-OMISSIONS" in blob) and \
           e.get("status") in ("accepted", "preserved-unresolved"):
            V(f"C12a {eid}: unfinished reflection skeleton cannot enter accepted state")

    # ---- C13: the verbatim origin is non-empty ----
    # FIELD.md §2 requires the original expression verbatim; Invariants.lean
    # PROVES origin_expression_preserved. Nothing established its hypothesis of
    # any real element, and operators/reflect.py staged one whose expression was
    # '\n\n  '. The theorem was true and about nothing. (issue #16, OBS-0020)
    for eid, (e, path) in elements.items():
        if not str(e.get("expression", {}).get("original", "")).strip():
            V(f"C13 {eid}: verbatim originating expression is empty or whitespace")

    # ---- C12: atlas regeneration succeeds ----
    sys.path.insert(0, os.path.join(REPO, "projections"))
    atlas_path = os.path.join(FIELD, "derived", "atlas.json")
    try:
        committed = json.load(open(atlas_path))
    except Exception as ex:
        committed = None
        V(f"C12: committed atlas unreadable: {ex}")
    try:
        import atlas as atlas_mod
        # write=False. THE VALIDATOR MUST NOT MUTATE WHAT IT VALIDATES.
        # This was build(write=True), which meant a corrupted atlas was silently
        # REPAIRED instead of refused: locally the edit vanished with no message,
        # and in CI the repair was discarded so a wrong committed atlas passed
        # green forever and was what the viewer served.
        #
        # The first version of THIS fix compared and then still wrote. It caught
        # the corruption on run one and destroyed the evidence, so run two passed
        # -- and any element added and removed between runs left the tree dirty.
        # A check that repairs is a check whose second run cannot fail.
        regenerated = atlas_mod.build(write=False)
    except Exception as ex:
        regenerated = None
        V(f"C12: atlas regeneration failed: {ex}")

    if committed is not None and regenerated is not None:
        # REGENERATION IS NOT AGREEMENT. C12 asserted only that the builder ran.
        if committed != regenerated:
            V("C12b: committed field/derived/atlas.json differs from a fresh "
              "regeneration. Run: python3 projections/atlas.py")
        rc = regenerated.get("counts", {}).get("elements")
        if rc is not None and rc != len(elements):
            V(f"C12c: pi_python counts {len(elements)} elements and pi_ts's source "
              f"artifact counts {rc}. The field holds that disagreement between "
              f"projections is information; here it is a defect.")

    # ---- report ----
    n = len(elements); m = len(relations); o = len(observers)
    # Manifest, not just verdict: what was on disk vs what was inspected. A
    # gate that reports PASS without its scope cannot say how much it looked at.
    scope = []
    for sub, loaded in (("elements", elements), ("relations", relations), ("observers", observers)):
        disk, seen = complement(sub, loaded)
        scope.append(f"{sub}={len(loaded)}/{disk}")
    print("inspected/on-disk: " + "  ".join(scope))
    print(f"elements={n} relations={m} observers={o}")
    if violations:
        print(f"\nINCONSISTENT — {len(violations)} violation(s):")
        for v in violations: print("  -", v)
        return 1
    print("CONSISTENT — all deterministic conditions passed (consistency, not truth).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
