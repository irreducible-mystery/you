#!/usr/bin/env julia
# Honest version of the angle sweep: average ambiguity over ALL possible
# hidden truths, not one cherry-picked point. Separates the geometry
# (angle between cuts) from single-point aliasing artifacts.
using Printf

N = 20
X = [(i, j) for i in 0:N-1 for j in 0:N-1]
p1(p) = div(p[1], 4)                                 # view 1: x-band
pm(p, a) = floor(Int, (cos(a)*p[1] + sin(a)*p[2]) / 5.0)  # view 2 at angle a

println("Second view at angle a from view 1 — ambiguity AVERAGED over all 400 truths:")
println("(and worst-case truth, because averages can hide fragility)\n")
@printf("  %6s  %12s  %10s\n", "angle", "mean |amb|", "worst |amb|")
for adeg in [0, 5, 10, 15, 22, 30, 45, 60, 75, 90]
    a = adeg * pi / 180
    tot = 0; worst = 0
    for xt in X
        f1  = filter(p -> p1(p) == p1(xt), X)
        f1m = filter(p -> pm(p, a) == pm(xt, a), f1)
        tot += length(f1m); worst = max(worst, length(f1m))
    end
    @printf("  %4d°   %10.2f   %8d\n", adeg, tot/length(X), worst)
end

println("""

And the pure two-view baseline for reference:""")
tot1 = sum(length(filter(p -> p1(p) == p1(xt), X)) for xt in X)
@printf("  view 1 alone:  mean |amb| = %.2f\n", tot1/length(X))
