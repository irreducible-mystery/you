#!/usr/bin/env python3
"""Axiom audit for every Lean declaration in verification/lean/Field/.

Not a sample: every theorem, def, structure, inductive and abbrev is carried
through `#print axioms`. Exits non-zero if any declaration depends on `sorryAx`
or on the native-evaluation axioms, and reports (without failing) any dependence
on the three standard sound axioms.

Run from the repository root:  python3 verification/lean/audit_axioms.py
"""
import re, subprocess, sys, os, tempfile, glob

HERE = os.path.dirname(os.path.abspath(__file__))
FATAL = ("sorryAx", "Lean.ofReduceBool", "Lean.ofReduceNat")
NOTED = ("propext", "Classical.choice", "Quot.sound")

def decls(src):
    top = re.findall(r'^(?:theorem|def|abbrev|instance|structure|inductive)\s+([A-Za-z_][A-Za-z_0-9\']*)', src, re.M)
    ns = re.search(r'^namespace\s+(\S+)', src, re.M)
    pre = (ns.group(1) + ".") if ns else ""
    seen, out = set(), []
    for d in top:
        if d not in seen:
            seen.add(d); out.append(pre + d)
    return out

def main():
    files = sorted(glob.glob(os.path.join(HERE, "Field", "*.lean")))
    if not files:
        print("no Lean files found"); return 1
    total = clean = 0
    fatal_hits, noted_hits = [], []
    for f in files:
        src = open(f).read()
        names = decls(src)
        with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False, dir=HERE) as t:
            t.write(src + "\n\n" + "\n".join(f"#print axioms {n}" for n in names) + "\n")
            tmp = t.name
        try:
            r = subprocess.run(["lean", tmp], capture_output=True, text=True)
        finally:
            os.unlink(tmp)
        if r.returncode != 0:
            print(f"FAIL {os.path.basename(f)}: did not compile")
            print(r.stdout[:2000] or r.stderr[:2000]); return 1
        lines = [l for l in r.stdout.splitlines() if l.strip()]
        total += len(lines)
        for l in lines:
            if "does not depend on any axioms" in l:
                clean += 1
            else:
                if any(a in l for a in FATAL):  fatal_hits.append(l)
                elif any(a in l for a in NOTED): noted_hits.append(l)
        print(f"  {os.path.basename(f):<20} {len(names):>3} declarations")
    print(f"\naudited {total} declarations; {clean} depend on no axiom")
    for l in noted_hits:
        print(f"  NOTE  {l}   (standard sound axiom; recorded, not fatal)")
    for l in fatal_hits:
        print(f"  FATAL {l}")
    if fatal_hits:
        print("\nAUDIT FAILED: a declaration rests on sorry or on native evaluation.")
        return 1
    print("\nAUDIT PASSED — no sorryAx, no native_decide.")
    print("Note: an axiom footprint is a property of (proof, toolchain). See CLM-0026.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
