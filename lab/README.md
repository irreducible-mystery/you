# Lab

Scratch space for exploratory math. Low bar: any observer PRs anything runnable here; review checks only that it runs and states what it computes. Lab results are NOT field claims.

Promotion path: when a lab result stabilizes, a normal candidate-change PR adds the claim/observation to `field/` and, if it should gate CI, a check under `verification/`. The lab file is cited as the grounding artifact.

Long-lived shared branches are not used for collaborative proofs — they drift from accepted state and hide work from review. Small PRs into `lab/`, promotion PRs into `field/` + `verification/`.

Layout: one directory per language (`julia/`, `python/`, `lean/`, ...). Each file starts with a comment saying what it computes.
