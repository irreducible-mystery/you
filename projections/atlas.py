#!/usr/bin/env python3
"""
Derived geometric atlas (FIELD.md §6, doc Q7 §15).
A GENERATED PROJECTION, never primary reality (LIM-0001).
Regenerates field/derived/atlas.json and field/derived/unresolved.json
from accepted elements and relations, with a dependence profile.
"""
import json, os, glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
FIELD = os.path.join(REPO, "field")
DERIVED = os.path.join(FIELD, "derived")

def _load(sub):
    out = []
    for p in sorted(glob.glob(os.path.join(FIELD, sub, "*.json"))):
        with open(p) as f:
            out.append(json.load(f))
    return out

def build(write=False):
    elements = _load("elements")
    relations = _load("relations")
    observers = _load("observers")

    nodes = []
    for e in elements:
        nodes.append({
            "id": e["id"], "kind": e["kind"], "status": e["status"],
            "observer": e["observer"],
            "observer_class": next((o["observer_class"] for o in observers if o["id"] == e["observer"]), None),
            "origin_class": e["origin_class"],
            "origin_confirmation": e["origin_confirmation"],
            "scale": e["context"]["scale"],
            "temporal_scope": e["context"]["temporal_scope"],
            "primitive_framework": e["context"]["primitive_framework"],
            "label": e["expression"]["original"][:140] + ("…" if len(e["expression"]["original"]) > 140 else ""),
            "expression": e["expression"],
            "tension_class": e.get("tension_class"),
            "grounding": e.get("grounding", []),
            "transformed": "transformation" in e,
        })

    edges = []
    for r in relations:
        edges.append({
            "id": r["id"], "type": r["type"], "source": r["source"], "target": r["target"],
            "observer": r["observer"], "status": r["status"],
            "conditions": r.get("conditions"), "translation_ledger": r.get("translation_ledger"),
        })

    # dependence profile: which outputs share a transformation definition / source / rule
    dep = {"shared_transformation": {}, "shared_source": {}, "note":
           "number of outputs != number of independent perspectives (CLM-0023)"}
    for e in elements:
        t = e.get("transformation")
        if t:
            k = f"{t['operator_family']}@{t['operator_revision']}"
            dep["shared_transformation"].setdefault(k, []).append(e["id"])
        src = e["origin_trace"]["origin_ref"]
        dep["shared_source"].setdefault(src, []).append(e["id"])

    unresolved = [n["id"] for n in nodes if n["status"] in ("preserved-unresolved", "contested")
                  or (n["kind"] == "tension" and n["status"] not in ("rejected", "superseded"))]

    atlas = {
        "note": "Derived projection. Traceable to accepted elements and transformations. Not primary reality.",
        "counts": {"elements": len(nodes), "relations": len(edges), "observers": len(observers),
                   "unresolved_tensions": len(unresolved)},
        "observers": observers,
        "nodes": nodes,
        "edges": edges,
        "dependence_profile": dep,
        "filters": {
            "scale": ["local-component", "subassembly", "assembly", "total-system", "ensemble", "multiscale"],
            "time": ["instant", "cycle", "path-interval", "long-interval", "multi-interval"],
            "primitive_framework": ["state-centered", "process-centered", "relation-centered", "observer-centered"],
            "contribution_class": ["originating", "transformed", "aggregate"],
            "status": ["open", "accepted", "contested", "rejected", "superseded", "preserved-unresolved"],
        },
    }

    if write:
        os.makedirs(DERIVED, exist_ok=True)
        with open(os.path.join(DERIVED, "atlas.json"), "w") as f:
            json.dump(atlas, f, indent=2); f.write("\n")
        with open(os.path.join(DERIVED, "unresolved.json"), "w") as f:
            json.dump({"note": "The unresolved-tension set. May never be emptied by convention (FIELD.md §8).",
                       "unresolved": unresolved}, f, indent=2); f.write("\n")
    return atlas

if __name__ == "__main__":
    a = build(write=True)
    print(json.dumps(a["counts"], indent=2))
