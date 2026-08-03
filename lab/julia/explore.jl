#!/usr/bin/env julia
# Deeper exploration of the four grounding experiments.
# Not a re-run — a parameter sweep. Where does each phenomenon live, where does it die?
using Printf

function integrate(f, x0::Vector{Float64}, t::Float64; dt=1e-4)
    x = copy(x0)
    for _ in 1:Int(round(t/dt)); x .+= dt .* f(x); end
    x
end

println("="^72)
println("G1 — WHEN DOES A PROJECTION COMMUTE WITH THE DYNAMICS?")
println("="^72)
println("""
System: dx1/dt = -x1, dx2/dt = -k*x2, projection pi(x) = x1 + x2.
If k = 1 the projected variable obeys its own closed law dy/dt = -y.
As k moves away from 1, the fiber (hidden detail) leaks into the
projection: two states with the SAME pi-value evolve to DIFFERENT
pi-values. Commutation gap vs k:
""")
t = 1.0
pi_(x) = x[1] + x[2]
for k in [1.0, 1.05, 1.25, 1.5, 2.0, 3.0]
    f(x) = [-x[1], -k*x[2]]
    # fiber divergence: same pi(x0)=1, different split
    yA = pi_(integrate(f, [1.0, 0.0], t))
    yB = pi_(integrate(f, [0.0, 1.0], t))
    @printf("  k = %.2f   fiber divergence |pi(F(a)) - pi(F(b))| = %.6f  %s\n",
        k, abs(yA - yB), k == 1.0 ? "<- closed: projection is a law" : "")
end
println("""
Reading: 'macro-law exists' is not a property of the system alone —
it is a property of the (system, projection) PAIR. k=1 is the seam.
""")

println("="^72)
println("G2 — MEAN-BLINDNESS IS EXACT, NOT APPROXIMATE")
println("="^72)
A = [0.0, 0.0, 10.0, 10.0]; B = [5.0, 5.0, 5.0, 5.0]
mA, mB = sum(A)/4, sum(B)/4
vA = sum((A .- mA).^2)/4; vB = sum((B .- mB).^2)/4
@printf("  A = %s  mean %.1f  var %.1f\n", A, mA, vA)
@printf("  B = %s  mean %.1f  var %.1f\n", B, mB, vB)
println("""
  The mean is IDENTICALLY blind to organization: any transfer that
  conserves the sum is invisible to it. Now watch higher moments
  under progressive equalization x -> x + s*(mean - x):""")
for s in [0.0, 0.25, 0.5, 0.75, 1.0]
    As = A .+ s .* (mA .- A)
    v = sum((As .- mA).^2)/4
    @printf("    s = %.2f   mean = %.2f   var = %.3f\n", s, sum(As)/4, v)
end
println("""
  Mean: flat line. Variance: dies smoothly. Organization is what the
  chosen aggregate cannot see — and 'what it cannot see' is exactly
  where change can hide (CLM-0010).
""")

println("="^72)
println("G3 — HOW MUCH MEMORY DOES A HIDDEN SLOW VARIABLE INJECT?")
println("="^72)
println("""
System: dx/dt = -(x - y), dy/dt = eps*x, observe only x.
The hidden y returns as 'memory': two runs identical in x0 but
different in unseen y0 diverge in x. Final divergence vs eps
(time-scale separation), T = 20, |y0 difference| = 0.8:
""")
function g3run(eps, x0, y0; dt=1e-3, T=20.0)
    x, y = x0, y0
    for _ in 1:Int(round(T/dt)); x, y = x + dt*(-(x - y)), y + dt*(eps*x); end
    x
end
for eps in [0.0, 0.01, 0.05, 0.1, 0.5, 1.0]
    d = abs(g3run(eps, 1.0, 0.0) - g3run(eps, 1.0, 0.8))
    @printf("  eps = %.2f   divergence in observed x = %.4f  %s\n",
        eps, d, eps == 0.0 ? "<- y frozen: still leaks its INITIAL value" : "")
end
println("""
Reading: even eps=0 leaks (x relaxes toward the frozen y0). The
'memory' is not exotic — it is the shadow of unobserved state. The
faster y moves, the more the past of x matters to its own future.
""")

println("="^72)
println("G4 — THE AMBIGUITY-SET ARITHMETIC (the field's social theorem)")
println("="^72)
N = 20
X = [(i, j) for i in 0:N-1 for j in 0:N-1]
xt = (7, 13)
p1(p) = div(p[1], 4); p2(p) = div(p[2], 4); p3(p) = div(p[1] + p[2], 5)
f1   = filter(p -> p1(p) == p1(xt), X)
f12  = filter(p -> p2(p) == p2(xt), f1)
f123 = filter(p -> p3(p) == p3(xt), f12)
f11  = filter(p -> p1(p) == p1(xt), f1)
@printf("  no views:                     |ambiguity| = %d\n", length(X))
@printf("  view 1 (x-band):              |ambiguity| = %d\n", length(f1))
@printf("  + view 2 (y-band):            |ambiguity| = %d\n", length(f12))
@printf("  + view 3 (diagonal band):     |ambiguity| = %d\n", length(f123))
@printf("  view 1 AGAIN (correlated):    |ambiguity| = %d   <- adds nothing\n", length(f11))
println("""
Now the sweep the field actually lives by — partially correlated views.
View: theta-mixture  p(a) = div(cos(a)*x + sin(a)*y, 5). Angle a away
from view 1's axis measures genuine independence:
""")
using Base: div
pm(p, a) = floor(Int, (cos(a)*p[1] + sin(a)*p[2]) / 5.0)
for adeg in [0, 5, 15, 30, 45, 60, 90]
    a = adeg * pi / 180
    f1m = filter(p -> pm(p, a) == pm(xt, a), f1)
    @printf("  second view at %2d deg from first:  |ambiguity| = %3d\n", adeg, length(f1m))
end
println("""
Reading: independence is not binary. The narrowing power of a second
observer grows with the ANGLE of its cut. This is the number behind
every dependence profile in field/observers/ — OBS-AI-0002 declared
itself near 0 deg from OBS-AI-0001; Claude was recruited hoping for a
large angle; OBS-0011 warned the true angle is unverifiable. The
arithmetic is why any of that matters.
""")
