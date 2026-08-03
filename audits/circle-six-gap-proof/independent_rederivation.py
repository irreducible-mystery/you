"""
Independent re-derivation of the circle-six-gap-proof claims.
Written from the mathematical definitions (group cohomology of G = Z/2 with
coefficients in an abelian group M, possibly with non-trivial G-action),
NOT copied from the artifact's compute/ scripts.

Auditor: SuperNinja (NinjaTech AI), independent of the artifact's authors.

Setting:
  G = Z/2 = {0,1} with xor as the operation.
  M = Z/n (written additively), G acts by a |-> (x -> k*x mod n), k^2 = 1 mod n.
  Inhomogeneous cochains: C^m = maps G^m -> M (unnormalised).
  Differential (standard inhomogeneous bar complex):
    (d f)(g1,...,g_{m+1}) = g1 . f(g2,...,g_{m+1})
       + sum_{i=1..m} (-1)^i f(g1,..., g_i g_{i+1}, ..., g_{m+1})
       + (-1)^{m+1} f(g1,...,g_m)

  For m=3:
    (d3 F)(a,b,c,d) = a.F(b,c,d) - F(a+b,c,d) + F(a,b+c,d) - F(a,b,c+d) + F(a,b,c)
  For m=2:
    (d2 g)(a,b,c) = a.g(b,c) - g(a+b,c) + g(a,b+c) - g(a,b)

These match the artifact's d3k/d2k, which I verify below is the standard complex
(d3 o d2 = 0 is checked independently as well).
"""
from itertools import product
import sys

OK = True
def check(name, cond):
    global OK
    status = "PASS" if cond else "FAIL"
    if not cond: OK = False
    print(f"  [{status}] {name}")

B = [0, 1]
K4 = list(product(B, repeat=4))
K3 = list(product(B, repeat=3))
K2 = list(product(B, repeat=2))

def make_complex(n, k):
    def act(a, x):
        return (k * x) % n if a else x % n
    def d3(F):
        # returns dict on K4
        return {(a,b,c,d): (act(a, F[(b,c,d)]) - F[(a^b,c,d)] + F[(a,b^c,d)]
                            - F[(a,b,c^d)] + F[(a,b,c)]) % n
                for a,b,c,d in K4}
    def d2(g):
        return {(a,b,c): (act(a, g[(b,c)]) - g[(a^b,c)] + g[(a,b^c)] - g[(a,b)]) % n
                for a,b,c in K3}
    return act, d2, d3

def is_zero(d): return all(v == 0 for v in d.values())

def top(n, u):
    return {t: (u if t == (1,1,1) else 0) for t in K3}

print("="*72)
print("SECTION A — sanity of the complex itself: d3 o d2 = 0 for all gauges")
print("="*72)
# If d3(d2(g)) != 0 for some g the 'complex' would not be a complex and
# 'cocycle/coboundary' language would be unjustified. Exhaustive over all
# 2-cochains for (n,k) in the cases used by the artifact.
for (n, k) in [(4,1),(4,3),(8,1),(8,3),(8,5),(8,7),(3,1),(3,2),(5,1),(5,4),(12,5),(12,7),(12,11)]:
    if (k*k) % n != 1 % n:
        check(f"(n={n},k={k}) k^2=1 mod n", False); continue
    act, d2, d3 = make_complex(n, k)
    good = all(is_zero(d3(d2(dict(zip(K2, v))))) for v in product(range(n), repeat=4))
    check(f"(n={n},k={k}): d3(d2(g)) == 0 for all {n}^4 gauges", good)

print()
print("="*72)
print("SECTION B — the mu_4 seal (C6_Twist / C6_Gap section 3)")
print("="*72)
# In multiplicative language Z[i]^x = {1, i, -1, -i} ~ Z/4 additively via
# i^u <-> u. conj(i^u) = i^{-u} = i^{3u}, i.e. k=3. Fermion = -1 = i^2 <-> u=2,
# sliceI = i <-> u=1.
act, d2, d3 = make_complex(4, 1)
check("mu4 trivial action: top(2) (fermion) IS a cocycle", is_zero(d3(top(4,2))))
check("mu4 trivial action: top(1) (i) is NOT a cocycle", not is_zero(d3(top(4,1))))

# is top(2) a coboundary under trivial action? enumerate all gauges
covers = {tuple(d2(dict(zip(K2,v)))[t] for t in K3) for v in product(range(4), repeat=4)}
key_fermion = tuple(top(4,2)[t] for t in K3)
check("mu4 trivial action: fermion NOT a coboundary (class -1 nontrivial)",
      key_fermion not in covers)

act, d2t, d3t = make_complex(4, 3)
check("mu4 twisted (k=3): top(1) IS a cocycle", is_zero(d3t(top(4,1))))
check("mu4 twisted (k=3): top(2) IS a cocycle", is_zero(d3t(top(4,2))))
covers_t = {tuple(d2t(dict(zip(K2,v)))[t] for t in K3) for v in product(range(4), repeat=4)}
check("mu4 twisted: fermion (top 2) IS a coboundary (gauge-trivialised)",
      tuple(top(4,2)[t] for t in K3) in covers_t)
check("mu4 twisted: sliceI (top 1) NOT a coboundary (sigma-generator survives)",
      tuple(top(4,1)[t] for t in K3) not in covers_t)
# verify the artifact's explicit witness gauge gge4(3,3,1,2): g00=3,g01=3,g10=1,g11=2
gW = {(0,0):3, (0,1):3, (1,0):1, (1,1):2}
check("mu4 twisted: artifact witness gauge [3,3,1,2] hits the fermion",
      d2t(gW) == top(4,2))

print()
print("="*72)
print("SECTION C — full cochain-space counts, mu_4 (|Z3|, |B3|, |ker d2|)")
print("="*72)
# The artifact's kernel-decided counts: B3 = 16 untwisted / 32 twisted,
# ker d2 = 16 / 8. Also the NOT-kernel-decided ones: Z3 = 32 / 64, shared 8,
# and pentagon <-> untwisted cocycle. I re-derive Z3/B3 here independently.
for k, name in [(1, "untwisted"), (3, "twisted")]:
    act, d2, d3 = make_complex(4, k)
    Z3 = [v for v in product(range(4), repeat=8) if is_zero(d3(dict(zip(K3, v))))]
    B3 = {tuple(d2(dict(zip(K2, v)))[t] for t in K3) for v in product(range(4), repeat=4)}
    ker = [v for v in product(range(4), repeat=4) if is_zero(d2(dict(zip(K2, v))))]
    print(f"  mu4 {name} (k={k}): |Z3|={len(Z3)}  |B3|={len(B3)}  |ker d2|={len(ker)}  |H3|={len(Z3)//len(B3)}")
    if k == 1:
        check("|Z3| untwisted == 32", len(Z3) == 32)
        check("|B3| untwisted == 16", len(B3) == 16)
        check("|ker d2| untwisted == 16", len(ker) == 16)
        check("B3 subset Z3 (untwisted)", all(is_zero(d3(dict(zip(K3, b)))) for b in B3))
        Z3_untw = set(Z3)
    else:
        check("|Z3| twisted == 64", len(Z3) == 64)
        check("|B3| twisted == 32", len(B3) == 32)
        check("|ker d2| twisted == 8", len(ker) == 8)
        check("B3 subset Z3 (twisted)", all(is_zero(d3(dict(zip(K3, b)))) for b in B3))
        Z3_tw = set(Z3)
check("|Z3_untwisted ∩ Z3_twisted| == 8", len(Z3_untw & Z3_tw) == 8)

print()
print("="*72)
print("SECTION D — pentagon <-> untwisted cocycle (the NOT-kernel-decided identity)")
print("="*72)
# Multiplicative U(1)-subgroup {1,i,-1,-i} as Z/4 additive. Pentagon equation
# for a fusion-category-style F-symbol on Z/2 fusion rules reduces (per the
# artifact's own lhs/rhs_reduces, which I re-check numerically below via the
# seal's genPent formulas) to:
#   F(a,b,c) + F(a, b^c, d) + F(b,c,d) == F(a^b, c, d) + F(a,b,c^d)  (mod 4)
def pentagon_holds(F):
    return all((F[(a,b,c)] + F[(a, b^c, d)] + F[(b,c,d)]) % 4
               == (F[(a^b, c, d)] + F[(a,b,c^d)]) % 4
               for a,b,c,d in K4)
act, d2u, d3u = make_complex(4, 1)
pent = {v for v in product(range(4), repeat=8) if pentagon_holds(dict(zip(K3, v)))}
Z3u = {v for v in product(range(4), repeat=8) if is_zero(d3u(dict(zip(K3, v))))}
check("pentagon == untwisted-cocycle as SETS over all 65536 symbols", pent == Z3u)
print(f"  |pentagon solutions| = {len(pent)}")

# And the seal's genPentLhs/genPentRhs with guard, re-implemented from the
# 01-BUILD-STACK statement, as a cross-check of the reduction claim:
import cmath
UVAL = {0: 1, 1: 1j, 2: -1, 3: -1j}
def Fgen(F, a, b, c, d, x, y):
    if x == (a+b) % 2 and y == (b+c) % 2 and d == (a+b+c) % 2:
        return F[(a,b,c)]
    return 0  # GZ.zero
def genLhs(F, a, b, c, d):
    x=(a+b)%2; y=(x+c)%2; t=(y+d)%2; w=(c+d)%2; v=(b+w)%2; u=(b+c)%2
    return Fgen(F,a,b,c,y,x,u) * Fgen(F,a,u,d,t,y,v) * Fgen(F,b,c,d,v,u,w)
def genRhs(F, a, b, c, d):
    x=(a+b)%2; y=(x+c)%2; t=(y+d)%2; w=(c+d)%2; v=(b+w)%2
    return Fgen(F,x,c,d,t,y,w) * Fgen(F,a,b,w,t,x,v)
def seal_pentagon(Fadd):
    Fc = {t: UVAL[Fadd[t]] for t in K3}
    return all(genLhs(Fc,a,b,c,d) == genRhs(Fc,a,b,c,d) for a,b,c,d in K4)
seal_pent = {v for v in product(range(4), repeat=8) if seal_pentagon(dict(zip(K3, v)))}
check("seal's genPent (with guard, complex arithmetic) == reduced pentagon set",
      seal_pent == pent)

print()
print("="*72)
print("SECTION E — the pinch at mu_8 (C6_Gap section 4)")
print("="*72)
def audit_topcells(n, k):
    act, d2, d3 = make_complex(n, k)
    Bset = {tuple(d2(dict(zip(K2, v)))[t] for t in K3) for v in product(range(n), repeat=4)}
    rows = []
    for u in range(n):
        F = top(n, u)
        rows.append((u, is_zero(d3(F)), tuple(F[t] for t in K3) in Bset))
    return rows

rows83 = audit_topcells(8, 3)
check("mu8 k=3: odd top-cells are NOT cocycles",
      all(not cyc for (u, cyc, cob) in rows83 if u % 2 == 1))
check("mu8 k=3: even top-cells ARE cocycles AND coboundaries (the pinch)",
      all(cyc and cob for (u, cyc, cob) in rows83 if u % 2 == 0))

rows87 = audit_topcells(8, 7)
check("mu8 k=7 (inversion): top(1) is a cocycle", rows87[1][1])
check("mu8 k=7 (inversion): top(1) is NOT a coboundary (no pinch)", not rows87[1][2])

rows85 = audit_topcells(8, 5)
print(f"  mu8 k=5 top-cell table (u, cocycle, coboundary): {rows85}")

# artifact witness gauges at mu8 k=3
act, d28, d38 = make_complex(8, 3)
for u, g in [(0,(7,7,5,5)), (2,(7,7,5,6)), (4,(7,7,5,7)), (6,(7,7,5,4))]:
    gd = {(0,0):g[0], (0,1):g[1], (1,0):g[2], (1,1):g[3]}
    check(f"mu8 k=3 artifact witness gauge {list(g)} hits top({u})", d28(gd) == top(8, u))

print()
print("="*72)
print("SECTION F — sqrt(1) counts and odd-n total pinch (C6_Gap sections 5-6)")
print("="*72)
def sqrts_of_one(n): return [k for k in range(n) if (k*k) % n == 1 % n]
check("sqrtsOfOne(4) == [1,3]", sqrts_of_one(4) == [1,3])
check("sqrtsOfOne(8) == [1,3,5,7]", sqrts_of_one(8) == [1,3,5,7])
check("sqrtsOfOne(12) == [1,5,7,11]", sqrts_of_one(12) == [1,5,7,11])

for n, kinv in [(3,2),(5,4)]:
    act, d2, d3 = make_complex(n, 1)
    only_zero = is_zero(d3(top(n,0))) and all(not is_zero(d3(top(n,u))) for u in range(1,n))
    check(f"mu{n} trivial action: only top(0) is a cocycle", only_zero)
    rows = audit_topcells(n, kinv)
    check(f"mu{n} inversion (k={kinv}): ALL top-cells are cocycles AND coboundaries (total pinch)",
          all(cyc and cob for (u, cyc, cob) in rows))

# H^3(Z/2, M) with M = Z/n: standard theory says for trivial action
# H^3 = H^1 = M[2]... actually for cyclic group G=Z/2, H^odd = ker(N)/im(g-1),
# H^even = M^G / N(M). For trivial action H^3(Z/2, Z/n) = Z/gcd(2,n).
# For n odd => trivial. Matches "total pinch" for odd n. For inversion action on
# Z/n (n odd), H^3 = 0 as well (|G| invertible). Theory concurs.
print("  (theory cross-check: |G|=2 invertible mod odd n => H^*=0; consistent)")

print()
print("="*72)
print("SECTION G — braiding sector / hexagon (C6_Twist final section)")
print("="*72)
# Independent hexagon check with complex numbers. Fusion rules Z/2; F-symbol
# F(a,b,c) = f if a=b=c=1 else 1; R-symbol R(x,y) = R if x=y=1 else 1.
# Hexagon (one of the two, per the seal's hexLhs/hexRhs shape):
def Fs(f, a, b, c):  # unguarded value (guards checked separately above)
    return f if (a==1 and b==1 and c==1) else 1
def Rsym(R, x, y):
    return R if (x==1 and y==1) else 1
def hex_holds(f, R):
    okk = True
    for a,b,c,d in K4:
        e=(a+b)%2; z=(a+c)%2; g=(b+c)%2
        if d != (e+c)%2 or d != (z+b)%2: continue
        lhs = Rsym(R,e,c) * Fs(f,c,a,b)
        rhs = Fs(f,a,b,c) * Rsym(R,b,c) * Fs(f,a,c,b) * Rsym(R,a,c)
        if lhs != rhs: okk = False
    return okk
check("boson (f=1): hexagon holds for R=+1 and R=-1", hex_holds(1,1) and hex_holds(1,-1))
check("boson (f=1): hexagon FAILS for R=+i and R=-i", not hex_holds(1,1j) and not hex_holds(1,-1j))
check("fermion (f=-1): hexagon holds for R=+i and R=-i", hex_holds(-1,1j) and hex_holds(-1,-1j))
check("fermion (f=-1): hexagon FAILS for R=+1 and R=-1", not hex_holds(-1,1) and not hex_holds(-1,-1))
check("conj swaps fermion braidings, fixes boson braidings",
      (1j).conjugate() == -1j and (1).conjugate() == 1)
check("SelfInverse: R=+-1 yes, R=+-i no",
      1*1 == 1 and (-1)*(-1) == 1 and (1j*1j) != 1 and ((-1j)*(-1j)) != 1)

print()
print("="*72)
print("SECTION H — H^3 formula cross-check: |H^3| = gcd(1+k,n)*gcd(k-1,n)/n")
print("="*72)
# The artifact's compute/absence4_pinch.py proposes this formula; standard
# theory for cyclic G=Z/2 acting on Z/n via k (k^2=1):
#   H^3 = H^1 = ker(N)/im(sigma-1) where N = 1+k (norm), sigma-1 = k-1.
#   |ker(N: Z/n -> Z/n)| = gcd(1+k, n); |im(k-1)| = n/gcd(k-1, n).
#   => |H^1| = gcd(1+k,n)*gcd(k-1,n)/n. Theory agrees with the formula.
#
# METHOD (independent of the artifact's brute force): d3 and d2 are Z-linear
# maps once k is fixed. Build their integer matrices, compute Smith normal
# form, and count |ker mod n| = prod gcd(d_i, n) * n^(cols - rank),
# |im mod n| = n^cols / |ker mod n|. Then |H3| = |ker d3| / |im d2|.
from math import gcd

def smith_diagonal(Ain):
    """Elementary divisors (diagonal of SNF) of integer matrix A (list of rows)."""
    A = [row[:] for row in Ain]
    m = len(A); c = len(A[0]) if m else 0
    diag = []
    r = 0
    while r < min(m, c):
        # find non-zero pivot with smallest |value|
        best = None
        for i in range(r, m):
            for j in range(r, c):
                if A[i][j] != 0 and (best is None or abs(A[i][j]) < abs(A[best[0]][best[1]])):
                    best = (i, j)
        if best is None:
            break
        i0, j0 = best
        A[r], A[i0] = A[i0], A[r]
        for row in A:
            row[r], row[j0] = row[j0], row[r]
        # reduce column and row
        done = False
        while not done:
            done = True
            for i in range(r+1, m):
                if A[i][r] % A[r][r] != 0 or A[i][r] != 0:
                    q = A[i][r] // A[r][r]
                    A[i] = [A[i][j] - q*A[r][j] for j in range(c)]
                    if A[i][r] != 0:  # remainder nonzero => swap and repeat
                        A[r], A[i] = A[i], A[r]
                        done = False
            for j in range(r+1, c):
                if A[r][j] != 0:
                    q = A[r][j] // A[r][r]
                    for i in range(m):
                        A[i][j] -= q * A[i][r]
                    if A[r][j] != 0:
                        for i in range(m):
                            A[i][r], A[i][j] = A[i][j], A[i][r]
                        done = False
        diag.append(abs(A[r][r]))
        r += 1
    return diag  # length = rank over Q

def ker_size_mod(Aint, n, cols):
    d = smith_diagonal(Aint)
    r = len(d)
    s = 1
    for di in d:
        s *= gcd(di, n)
    return s * n**(cols - r)

def d3_matrix(k, n):
    """16x8 integer matrix of d3 acting on F indexed by K3, rows indexed by K4.
       Entries use representative action multiplier k (integer)."""
    idx3 = {t: i for i, t in enumerate(K3)}
    rows = []
    for a,b,c,d in K4:
        row = [0]*8
        row[idx3[(b,c,d)]]   += (k if a else 1)
        row[idx3[(a^b,c,d)]] -= 1
        row[idx3[(a,b^c,d)]] += 1
        row[idx3[(a,b,c^d)]] -= 1
        row[idx3[(a,b,c)]]   += 1
        rows.append(row)
    return rows

def d2_matrix(k, n):
    idx2 = {t: i for i, t in enumerate(K2)}
    rows = []
    for a,b,c in K3:
        row = [0]*4
        row[idx2[(b,c)]]   += (k if a else 1)
        row[idx2[(a^b,c)]] -= 1
        row[idx2[(a,b^c)]] += 1
        row[idx2[(a,b)]]   -= 1
        rows.append(row)
    return rows

# validate SNF machinery against brute force where cheap (n=4, n=5, all k)
for n in [3, 4, 5]:
    for k in sqrts_of_one(n):
        act, d2, d3 = make_complex(n, k)
        Zbf = sum(1 for v in product(range(n), repeat=8) if is_zero(d3(dict(zip(K3, v)))))
        Bbf = len({tuple(d2(dict(zip(K2, v)))[t] for t in K3) for v in product(range(n), repeat=4)})
        Zsnf = ker_size_mod(d3_matrix(k, n), n, 8)
        Bsnf = n**4 // ker_size_mod(d2_matrix(k, n), n, 4)
        check(f"SNF matches brute force at n={n},k={k}: Z3 {Zbf}=={Zsnf}, B3 {Bbf}=={Bsnf}",
              Zbf == Zsnf and Bbf == Bsnf)

all_match = True
print(f"  {'n':>3} {'k':>3} {'|Z3|':>7} {'|B3|':>7} {'|H3|':>5} {'formula':>8}")
for n in range(2, 17):
    for k in sqrts_of_one(n):
        Z = ker_size_mod(d3_matrix(k, n), n, 8)
        Bc = n**4 // ker_size_mod(d2_matrix(k, n), n, 4)
        H = Z // Bc
        f = gcd(1+k, n) * gcd(k-1, n) // n
        m = (H == f)
        if not m: all_match = False
        print(f"  {n:>3} {k:>3} {Z:>7} {Bc:>7} {H:>5} {f:>8}  {'OK' if m else 'MISMATCH'}")
check("SNF-derived |H3| == gcd formula for all n in 2..16, all valid k", all_match)

print()
print("="*72)
print(f"OVERALL: {'ALL INDEPENDENT CHECKS PASS' if OK else 'SOME CHECKS FAILED'}")
print("="*72)
sys.exit(0 if OK else 1)
