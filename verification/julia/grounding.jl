#!/usr/bin/env julia
# Independent re-derivation of the grounding experiments (Julia projection, pi_julia).
# Same claims, independently coded dynamics. Agreement with pi_python is
# cross-perspectival invariance, not proof (CLM-0014: shared blind spots remain possible —
# both projections share the same experiment designs).
# Writes verification/results/julia.json

using Printf

function integrate(f, x0::Vector{Float64}, t::Float64; dt=1e-4)
    x = copy(x0)
    for _ in 1:Int(round(t/dt))
        x .+= dt .* f(x)
    end
    x
end

# G1: commutation (CLM-0008)
function g1()
    t = 1.0
    pi_(x) = x[1] + x[2]
    fa(x) = [-x[1], -x[2]]
    x0 = [0.7, 0.3]
    lhs = pi_(integrate(fa, x0, t))
    y = pi_(x0); dt = 1e-4
    for _ in 1:Int(round(t/dt)); y += dt * (-y); end
    good_gap = abs(lhs - y)
    fb(x) = [-x[1], -3x[2]]
    yA = pi_(integrate(fb, [1.0, 0.0], t))
    yB = pi_(integrate(fb, [0.0, 1.0], t))
    fiber_div = abs(yA - yB)
    Dict("claim"=>"CLM-0008", "commutation_gap_good"=>good_gap,
         "fiber_divergence_bad"=>fiber_div,
         "passes"=>(good_gap < 1e-3 && fiber_div > 0.1))
end

# G2: aggregate != average (CLM-0010)
function g2()
    A = [0.0, 0.0, 10.0, 10.0]; B = [5.0, 5.0, 5.0, 5.0]
    mA = sum(A)/4; mB = sum(B)/4
    vA = sum((A .- mA).^2)/4; vB = sum((B .- mB).^2)/4
    Dict("claim"=>"CLM-0010", "mean_A"=>mA, "mean_B"=>mB, "var_A"=>vA, "var_B"=>vB,
         "passes"=>(mA == mB && vA != vB))
end

# G3: hidden slow variable returns as memory (CLM-0004/CLM-0009)
function g3()
    eps = 0.05; dt = 1e-3; T = 20.0
    function run(x0, y0)
        x, y = x0, y0
        for _ in 1:Int(round(T/dt))
            x, y = x + dt*(-(x - y)), y + dt*(eps*x)
        end
        x
    end
    x1 = run(1.0, 0.0); x2 = run(1.0, 0.8)
    d = abs(x1 - x2)
    Dict("claim"=>"CLM-0004/CLM-0009", "x_end_hidden_y0_0.0"=>x1,
         "x_end_hidden_y0_0.8"=>x2, "observed_divergence"=>d, "passes"=>(d > 0.1))
end

# G4: ambiguity-set intersection (CLM-0013)
function g4()
    N = 20
    X = [(i, j) for i in 0:N-1 for j in 0:N-1]
    xt = (7, 13)
    p1(p) = div(p[1], 4); p2(p) = div(p[2], 4); p3(p) = div(p[1] + p[2], 5)
    f1 = filter(p -> p1(p) == p1(xt), X)
    f12 = filter(p -> p2(p) == p2(xt), f1)
    f123 = filter(p -> p3(p) == p3(xt), f12)
    f11 = filter(p -> p1(p) == p1(xt), f1)
    Dict("claim"=>"CLM-0013 (+CLM-0014 corollary)",
         "ambiguity_1_view"=>length(f1), "ambiguity_2_views"=>length(f12),
         "ambiguity_3_views"=>length(f123),
         "ambiguity_correlated_second_view"=>length(f11),
         "passes"=>(length(f1) > length(f12) > length(f123) && length(f11) == length(f1)))
end

function jsonval(v)
    v isa Dict ? jsonobj(v) :
    v isa Bool ? string(v) :
    v isa AbstractString ? "\"" * v * "\"" :
    v isa AbstractFloat ? @sprintf("%.12g", v) : string(v)
end
jsonobj(d) = "{" * join(["\"$k\": " * jsonval(v) for (k, v) in d], ", ") * "}"

results = Dict{String,Any}("G1"=>g1(), "G2"=>g2(), "G3"=>g3(), "G4"=>g4())
results["all_pass"] = all(results[k]["passes"] for k in ("G1","G2","G3","G4"))

outdir = joinpath(@__DIR__, "..", "results")
mkpath(outdir)
open(joinpath(outdir, "julia.json"), "w") do io
    write(io, jsonobj(results), "\n")
end

for k in ("G1","G2","G3","G4")
    println(k, " ", results[k]["passes"] ? "PASS" : "FAIL", " - ", results[k]["claim"])
end
println("ALL ", results["all_pass"] ? "PASS" : "FAIL")
exit(results["all_pass"] ? 0 : 1)
