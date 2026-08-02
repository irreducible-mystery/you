#!/usr/bin/env python3
"""
reflection operator, revision 1.0.0 — runnable intake path
===========================================================
Turns an originating expression (ordinary language) into:

  1. an ORIGINATING element that preserves the expression VERBATIM
     (origin_confirmation: confirmed — it *is* the origin's own words), and
  2. a TRANSFORMED reflection element (origin_confirmation: UNCONFIRMED)
     that restates the expression and explicitly lists what the restatement
     omitted — awaiting the origin's confirm / modify / reject.

Bounds enforced by this script (OPERATORS.md):
  - append-only: never modifies or deletes existing elements/relations;
  - the verbatim original always enters alongside any interpretation;
  - the reflection is marked unconfirmed and CANNOT be flipped to confirmed
    here — only the origin can do that, in a later candidate change;
  - the operator does not merge; acceptance stays independent (FIELD.md §7);
  - every output carries a full transformation signature.

Usage:
  # from a GitHub issue (intake path):
  python3 operators/reflect.py --issue 3

  # from a file or stdin:
  python3 operators/reflect.py --observer OBS-HUM-0001 --kind observation \
      --scale total-system --time instant --framework observer-centered \
      --text "..." [--restatement "..."] [--omissions "a; b; c"]

If --restatement is not given, the script writes a reflection SKELETON with
explicit TODO markers — because a mechanical paraphrase would be a projection
pretending not to be one. A situated transformer (human or AI) fills it in,
signs it, and the validator refuses skeletons in accepted state.
"""
import argparse, json, os, re, subprocess, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
FIELD = os.path.join(REPO, "field")

KIND_PREFIX = {"observation": "OBS", "claim": "CLM", "assumption": "ASM",
               "definition": "DEF", "perspective": "PER", "tension": "TEN",
               "bridge": "BRG", "test": "TST", "dimension-proposal": "DIM",
               "synthesis": "SYN", "limit": "LIM"}
SCALES = ["local-component", "subassembly", "assembly", "total-system", "ensemble", "multiscale"]
TSCOPES = ["instant", "cycle", "path-interval", "long-interval", "multi-interval"]
FRAMEWORKS = ["state-centered", "process-centered", "relation-centered", "observer-centered"]

def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def next_id(prefix):
    ids = []
    for p in os.listdir(os.path.join(FIELD, "elements")):
        m = re.match(rf"^{prefix}-(\d{{4}})\.json$", p)
        if m: ids.append(int(m.group(1)))
    return f"{prefix}-{(max(ids) + 1 if ids else 1):04d}"

def next_rel_id():
    ids = [int(re.match(r"^REL-(\d{4})\.json$", p).group(1))
           for p in os.listdir(os.path.join(FIELD, "relations"))
           if re.match(r"^REL-\d{4}\.json$", p)]
    return f"REL-{(max(ids) + 1 if ids else 1):04d}"

def write(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2); f.write("\n")
    print("  wrote", os.path.relpath(path, REPO))

def parse_issue(num):
    """Fetch a GitHub issue and parse the intake form (or free text)."""
    out = subprocess.run(["gh", "issue", "view", str(num), "--json", "title,body,author"],
                         capture_output=True, text=True, cwd=REPO)
    if out.returncode != 0:
        sys.exit(f"gh issue view failed: {out.stderr.strip()}")
    data = json.loads(out.stdout)
    body = data.get("body") or ""
    fields = {}
    # tolerant parse of "key: value" lines from the issue template
    for key in ("observer", "kind", "scale", "temporal_scope", "primitive_framework"):
        m = re.search(rf"^\s*{key}\s*[:=]\s*(.+)$", body, re.I | re.M)
        if m: fields[key] = m.group(1).strip()
    m = re.search(r"(?s)expression\s*[:=]\s*(.+?)(?:\n\s*(?:observer|kind|scale|temporal_scope|primitive_framework)\s*[:=]|\Z)", body, re.I)
    fields["text"] = (m.group(1).strip() if m else body.strip()) or data["title"]
    fields.setdefault("observer", None)
    fields["issue_ref"] = f"github issue #{num} by @{data['author']['login']}"
    return fields

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", type=int, help="intake from a GitHub issue number")
    ap.add_argument("--observer", help="observer id, e.g. OBS-HUM-0001")
    ap.add_argument("--kind", default="observation", choices=list(KIND_PREFIX))
    ap.add_argument("--scale", default="total-system", choices=SCALES)
    ap.add_argument("--time", dest="tscope", default="instant", choices=TSCOPES)
    ap.add_argument("--framework", default="observer-centered",
                    help="comma-separated primitive frameworks")
    ap.add_argument("--text", help="the originating expression (verbatim)")
    ap.add_argument("--restatement", help="the reflection's restatement (situated, signed)")
    ap.add_argument("--omissions", help="semicolon-separated list of what the restatement omits")
    ap.add_argument("--transformer", default="OBS-AI-0001",
                    help="observer id of whoever runs the reflection")
    args = ap.parse_args()

    origin_ref = "direct expression"
    if args.issue:
        f = parse_issue(args.issue)
        args.observer = args.observer or f.get("observer")
        args.kind = f.get("kind", args.kind).strip().lower() if f.get("kind") else args.kind
        if f.get("scale") in SCALES: args.scale = f["scale"]
        if f.get("temporal_scope") in TSCOPES: args.tscope = f["temporal_scope"]
        if f.get("primitive_framework"): args.framework = f["primitive_framework"]
        args.text = args.text or f["text"]
        origin_ref = f["issue_ref"]

    if not args.text: sys.exit("no originating expression (--text or --issue required)")
    if not args.observer: sys.exit("no observer id: register in field/observers/ first "
                                   "(observer classes are never collapsed; anonymous entry "
                                   "uses attribution_mode surrogate with a registered surrogate observer)")
    obs_path = os.path.join(FIELD, "observers", args.observer + ".json")
    if not os.path.exists(obs_path):
        sys.exit(f"observer {args.observer} not registered in field/observers/")
    with open(obs_path) as fh: obs_class = json.load(fh)["observer_class"]
    origin_kind = {"human": "human-expression", "ai-system": "ai-expression",
                   "hybrid": "ai-expression", "document-surrogate": "document"}[obs_class]
    frameworks = [x.strip() for x in args.framework.split(",") if x.strip() in FRAMEWORKS] or ["observer-centered"]
    t = now()

    # --- 1. originating element, verbatim ---
    oid = next_id(KIND_PREFIX[args.kind])
    originating = {
        "id": oid, "kind": args.kind, "status": "open",
        "origin_class": "originating", "attribution_mode": "direct",
        "observer": args.observer,
        "expression": {"original": args.text},
        "context": {"scale": args.scale, "temporal_scope": args.tscope,
                    "primitive_framework": frameworks},
        "origin_trace": {"origin_kind": origin_kind, "origin_ref": origin_ref, "capture_time": t},
        "origin_confirmation": "confirmed",
    }
    write(os.path.join(FIELD, "elements", oid + ".json"), originating)

    # --- 2. reflection element, unconfirmed ---
    rid = next_id("PER") if args.kind == "perspective" else next_id(KIND_PREFIX[args.kind])
    restatement = args.restatement or (
        "TODO-RESTATEMENT: restate the originating expression in the field's terms. "
        "A mechanical paraphrase is a projection pretending not to be one; a situated "
        "transformer must write and sign this.")
    omissions = ([o.strip() for o in args.omissions.split(";")] if args.omissions else
                 ["TODO-OMISSIONS: list what this restatement drops (tone? context? scale? history?)"])
    reflection = {
        "id": rid, "kind": args.kind, "status": "open",
        "origin_class": "transformed", "attribution_mode": "direct",
        "observer": args.transformer,
        "expression": {"original": restatement,
                       "elaboration": "Omissions of this restatement, per reflection bounds: " +
                                      "; ".join(omissions),
                       "unresolved_nuance": "Awaiting origin confirmation: the origin may confirm, "
                                            "modify, or reject this interpretation. If rejected it stays "
                                            "visible as rejected and never reappears as confirmed."},
        "context": {"scale": args.scale, "temporal_scope": args.tscope,
                    "primitive_framework": frameworks},
        "origin_trace": {"origin_kind": "derived", "origin_ref": f"reflection@1.0.0 on {oid}",
                         "capture_time": t},
        "transformation": {"operator_family": "reflection", "operator_revision": "1.0.0",
                           "ruleset_revision": "FIELD.md@F1", "inputs": [oid],
                           "generation_time": t},
        "origin_confirmation": "unconfirmed",
    }
    write(os.path.join(FIELD, "elements", rid + ".json"), reflection)

    # --- 3. relation: reflection transforms-from origin ---
    lid = next_rel_id()
    rel = {"id": lid, "type": "transforms-into", "source": oid, "target": rid,
           "observer": args.transformer, "status": "open",
           "conditions": {"notes": "reflection@1.0.0: the derived element may not silently replace "
                                   "its origin; both remain in the field, linked."},
           "origin_trace": {"origin_kind": "derived", "origin_ref": "reflection@1.0.0",
                            "capture_time": t},
           "transformation": reflection["transformation"]}
    write(os.path.join(FIELD, "relations", lid + ".json"), rel)

    print(f"\nreflection cycle staged: {oid} (verbatim) → {rid} (unconfirmed) via {lid}")
    print("next: run verification/python/validate.py, commit on a candidate-change/ branch, open a PR.")
    print("acceptance must come from someone other than the transformer (FIELD.md §7).")

if __name__ == "__main__":
    main()
