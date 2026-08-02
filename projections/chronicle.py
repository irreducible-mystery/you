#!/usr/bin/env python3
"""
Chronicle projection — the accepted-state sequence F_0 -> F_1 -> ... as data.
============================================================================
Walks the FIRST-PARENT history of main (each merge/root commit IS an accepted
state, FIELD.md §1), reconstructs the field at every state, and derives the
transitions: elements/relations that appeared, statuses that changed,
origin-confirmations that arrived, observers that registered.

This is the field applying its own vocabulary to itself:
  - the state sequence x(t)            -> the list of accepted states
  - dx/dt                              -> per-transition diffs
  - memory (CLM-0004)                  -> git history as H_t
  - observation as participation
    (CLM-0020)                         -> this projection is itself part of
                                          the field it displays

A GENERATED PROJECTION, never primary reality (LIM-0001). It reads history;
it never writes it. Output: field/derived/chronicle.json
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))

def git(*args):
    out = subprocess.run(["git", *args], capture_output=True, text=True, cwd=REPO)
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {out.stderr.strip()}")
    return out.stdout

def mainline_ref():
    """Resolve the mainline ref robustly across measurement contexts.

    Locally, `main` exists as a branch. On pull_request CI checkouts the
    working tree is a detached merge commit and only `origin/main` is a
    visible ref. This difference in ref visibility is itself an instance of
    the projection inheriting the measurement geometry (REL-0028): the same
    accepted-state sequence, observed from different vantage points, is
    reachable under different names. We resolve the name, not the history.
    """
    for ref in ("main", "origin/main"):
        ok = subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref],
                            capture_output=True, text=True, cwd=REPO)
        if ok.returncode == 0:
            return ref
    return "HEAD"

def accepted_states():
    """First-parent commits on the mainline, oldest first. Each is an accepted state F_n."""
    lines = git("log", "--first-parent", "--reverse",
                "--format=%H|%cI|%s", mainline_ref()).strip().splitlines()
    states = []
    for n, line in enumerate(lines):
        sha, time, subject = line.split("|", 2)
        states.append({"index": n, "label": f"F{n}", "commit": sha,
                       "time": time, "subject": subject})
    return states

def field_at(commit):
    """Reconstruct elements/relations/observers as they were at a commit."""
    out = {"elements": {}, "relations": {}, "observers": {}}
    ls = git("ls-tree", "-r", "--name-only", commit).splitlines()
    for path in ls:
        for kind in ("elements", "relations", "observers"):
            if path.startswith(f"field/{kind}/") and path.endswith(".json"):
                raw = git("show", f"{commit}:{path}")
                try:
                    d = json.loads(raw)
                    out[kind][d.get("id", path)] = d
                except json.JSONDecodeError:
                    pass
    return out

def summarize(d, kind):
    """Small stable summary of an item for the chronicle."""
    if kind == "elements":
        return {"id": d["id"], "kind": d["kind"], "status": d["status"],
                "observer": d.get("observer"),
                "origin_confirmation": d.get("origin_confirmation"),
                "label": d["expression"]["original"][:120] +
                         ("…" if len(d["expression"]["original"]) > 120 else "")}
    if kind == "relations":
        return {"id": d["id"], "type": d["type"], "source": d["source"],
                "target": d["target"], "status": d.get("status")}
    return {"id": d["id"], "observer_class": d.get("observer_class"),
            "label": d.get("label")}

def diff_states(prev, cur):
    """Derive the transition prev -> cur."""
    delta = {"added": {"elements": [], "relations": [], "observers": []},
             "status_changes": [], "confirmation_changes": [], "removed": []}
    for kind in ("elements", "relations", "observers"):
        for id_, d in cur[kind].items():
            if id_ not in prev[kind]:
                delta["added"][kind].append(summarize(d, kind))
        for id_ in prev[kind]:
            if id_ not in cur[kind]:
                # append-preservation says this shouldn't happen for accepted
                # content; if it does, the chronicle must show it, not hide it.
                delta["removed"].append({"kind": kind, "id": id_})
    for id_, d in cur["elements"].items():
        p = prev["elements"].get(id_)
        if not p: continue
        if p.get("status") != d.get("status"):
            delta["status_changes"].append(
                {"id": id_, "from": p.get("status"), "to": d.get("status")})
        if p.get("origin_confirmation") != d.get("origin_confirmation"):
            delta["confirmation_changes"].append(
                {"id": id_, "from": p.get("origin_confirmation"),
                 "to": d.get("origin_confirmation")})
    for id_, d in cur["relations"].items():
        p = prev["relations"].get(id_)
        if p and p.get("status") != d.get("status"):
            delta["status_changes"].append(
                {"id": id_, "from": p.get("status"), "to": d.get("status")})
    return delta

def counts(state_field):
    els = state_field["elements"].values()
    return {"elements": len(state_field["elements"]),
            "relations": len(state_field["relations"]),
            "observers": len(state_field["observers"]),
            "unresolved": sum(1 for e in els if e.get("status") in
                              ("preserved-unresolved", "contested") or
                              (e.get("kind") == "tension" and
                               e.get("status") not in ("rejected", "superseded"))),
            "unconfirmed": sum(1 for e in els
                               if e.get("origin_confirmation") == "unconfirmed")}

def build(write=False):
    states = accepted_states()
    fields = [field_at(s["commit"]) for s in states]
    chronicle = {"note": "Derived projection of the accepted-state sequence. "
                         "Reads history; never writes it. Not primary reality (LIM-0001). "
                         "The chronicle observing the field is participation (CLM-0020).",
                 "states": [], "transitions": []}
    for s, f in zip(states, fields):
        entry = dict(s); entry["counts"] = counts(f)
        # per-state node/edge snapshot for the viewer
        entry["nodes"] = [summarize(d, "elements") for d in
                          sorted(f["elements"].values(), key=lambda x: x["id"])]
        entry["edges"] = [summarize(d, "relations") for d in
                          sorted(f["relations"].values(), key=lambda x: x["id"])]
        chronicle["states"].append(entry)
    for i in range(1, len(states)):
        d = diff_states(fields[i-1], fields[i])
        d["from"] = states[i-1]["label"]; d["to"] = states[i]["label"]
        d["commit"] = states[i]["commit"]; d["subject"] = states[i]["subject"]
        d["time"] = states[i]["time"]
        chronicle["transitions"].append(d)
    if write:
        out = os.path.join(REPO, "field", "derived", "chronicle.json")
        with open(out, "w") as f:
            json.dump(chronicle, f, indent=2); f.write("\n")
    return chronicle

if __name__ == "__main__":
    c = build(write=True)
    print(f"accepted states: {len(c['states'])}")
    for s in c["states"]:
        print(f"  {s['label']}  {s['commit'][:8]}  {s['counts']}  — {s['subject'][:60]}")
    for t in c["transitions"]:
        a = t["added"]
        print(f"  {t['from']}→{t['to']}: +{len(a['elements'])} elements, "
              f"+{len(a['relations'])} relations, "
              f"{len(t['status_changes'])} status changes, "
              f"{len(t['confirmation_changes'])} confirmations, "
              f"{len(t['removed'])} removals")
