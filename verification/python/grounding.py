#!/usr/bin/env python3
"""
Numeric grounding experiments (Python projection, pi_python).
Each experiment grounds a seeded claim in executable dynamics.
Julia re-derives the same experiments independently (pi_julia).
Agreement between the two is cross-perspectival invariance, not proof.

G1 -> CLM-0008  commutation test: pi o F_t vs G_t o pi
G2 -> CLM-0010  aggregate != average component
G3 -> CLM-0004/CLM-0009  fast-slow dynamics: history becomes organization / hidden variable returns as memory
G4 -> CLM-0013  ambiguity-set intersection shrinks with diverse projections
Writes verification/results/python.json
"""
import json, math, os, random

random.seed(20250101)
RESULTS = {}

# ---------- G1: commutation of coarse-graining (CLM-0008) ----------
# Detailed system: x = (x1, x2), dx1/dt = -x1, dx2/dt = -x2  (symmetric decay)
# Projection pi(x) = x1 + x2. Reduced rule G(y) = -y.
# pi o F_t == G_t o pi holds exactly here (good macrovariable).
# Counterexample: dx1/dt = -x1, dx2/dt = -3*x2 with same pi -> commutation fails
# (fiber members evolve at different projected velocities: same y, different futures).
def integrate(f, x0, t, dt=1e-4):
    x = list(x0); steps = int(t / dt)
    for _ in range(steps):
        d = f(x)
        x = [xi + dt * di for xi, di in zip(x, d)]
    return x

def g1():
    t = 1.0
    pi = lambda x: x[0] + x[1]
    # good projection
    fa = lambda x: [-x[0], -x[1]]
    Ga = lambda y: -y
    x0 = [0.7, 0.3]
    lhs = pi(integrate(fa, x0, t))
    y = pi(x0); dt = 1e-4
    for _ in range(int(t/dt)): y += dt * Ga(y)
    rhs = y
    good_gap = abs(lhs - rhs)
    # bad projection: two fiber members, same y0, different futures
    fb = lambda x: [-x[0], -3*x[1]]
    xA = [1.0, 0.0]; xB = [0.0, 1.0]   # pi(xA)=pi(xB)=1
    yA = pi(integrate(fb, xA, t)); yB = pi(integrate(fb, xB, t))
    fiber_divergence = abs(yA - yB)
    return {"claim": "CLM-0008", "commutation_gap_good": good_gap,
            "fiber_divergence_bad": fiber_divergence,
            "passes": good_gap < 1e-3 and fiber_divergence > 0.1}

# ---------- G2: aggregate != average component (CLM-0010) ----------
def g2():
    A = [0, 0, 10, 10]; B = [5, 5, 5, 5]
    meanA = sum(A)/len(A); meanB = sum(B)/len(B)
    varA = sum((a-meanA)**2 for a in A)/len(A)
    varB = sum((b-meanB)**2 for b in B)/len(B)
    return {"claim": "CLM-0010", "mean_A": meanA, "mean_B": meanB,
            "var_A": varA, "var_B": varB,
            "passes": meanA == meanB and varA != varB}

# ---------- G3: fast-slow dynamics; hidden slow variable returns as memory ----------
# dx/dt = -(x - y); dy/dt = eps * x. Observe only x. Two runs with identical x(0)
# but different hidden y(0) diverge in observed x — path dependence at the reduced level.
def g3():
    eps = 0.05; dt = 1e-3; T = 20.0
    def run(x0, y0):
        x, y = x0, y0; traj = []
        for i in range(int(T/dt)):
            x, y = x + dt * (-(x - y)), y + dt * (eps * x)
            if i % 1000 == 0: traj.append(x)
        return x, traj
    x_end_1, _ = run(1.0, 0.0)
    x_end_2, _ = run(1.0, 0.8)   # same observed x(0), different hidden y(0)
    divergence = abs(x_end_1 - x_end_2)
    return {"claim": "CLM-0004/CLM-0009", "x_end_hidden_y0_0.0": x_end_1,
            "x_end_hidden_y0_0.8": x_end_2, "observed_divergence": divergence,
            "passes": divergence > 0.1}

# ---------- G4: ambiguity-set intersection (CLM-0013) ----------
# X = 20x20 grid. pi_1 = row band, pi_2 = column band, pi_3 = diagonal band.
# |fiber| shrinks under intersection of diverse projections;
# correlated observers (same pi) do NOT shrink it (CLM-0014).
def g4():
    N = 20
    X = [(i, j) for i in range(N) for j in range(N)]
    x_true = (7, 13)
    pi1 = lambda p: p[0] // 4          # row band
    pi2 = lambda p: p[1] // 4          # column band
    pi3 = lambda p: (p[0] + p[1]) // 5 # diagonal band
    f1 = [p for p in X if pi1(p) == pi1(x_true)]
    f12 = [p for p in f1 if pi2(p) == pi2(x_true)]
    f123 = [p for p in f12 if pi3(p) == pi3(x_true)]
    f11 = [p for p in f1 if pi1(p) == pi1(x_true)]  # correlated observer: same projection again
    return {"claim": "CLM-0013 (+CLM-0014 corollary)",
            "ambiguity_1_view": len(f1), "ambiguity_2_views": len(f12),
            "ambiguity_3_views": len(f123),
            "ambiguity_correlated_second_view": len(f11),
            "passes": len(f1) > len(f12) > len(f123) and len(f11) == len(f1)}

def main():
    RESULTS["G1"] = g1(); RESULTS["G2"] = g2(); RESULTS["G3"] = g3(); RESULTS["G4"] = g4()
    RESULTS["all_pass"] = all(RESULTS[k]["passes"] for k in ("G1", "G2", "G3", "G4"))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "python.json"), "w") as f:
        json.dump(RESULTS, f, indent=2); f.write("\n")
    for k in ("G1", "G2", "G3", "G4"):
        print(k, "PASS" if RESULTS[k]["passes"] else "FAIL", "-", RESULTS[k]["claim"])
    print("ALL", "PASS" if RESULTS["all_pass"] else "FAIL")
    return 0 if RESULTS["all_pass"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
