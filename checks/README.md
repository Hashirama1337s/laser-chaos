# Review seats' numerical cross-checks (not rigorous)

In plain words: two review seats checked the claims with their own
floating-point code, in the original (I, W) variables. Nothing here is part of the proof.

- `blind_seat/cover_check.py` -> `cover_dense.txt`: every link sampled on a 301 x 301 grid; no violation.
- `blind_seat/disjoint.py` -> `disjoint.txt`: the 24 boxes are pairwise disjoint.
- `blind_seat/longrun.py` -> `longrun.txt`: period 16 for several integrators, tolerances and transients.
- `blind_seat/floquet.py` -> `floquet.txt`: multipliers of the period-16 cycle.
- `referee_seat/per16.py` -> `per16_out.txt`: period 16 at relative tolerance 1e-6; no period up to 64 at 1e-3.
