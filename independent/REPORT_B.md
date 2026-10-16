# Checker B report

## In plain words

Checker B is a second, independently written program that checks the same 25 covering relations and the disjointness of
the 24 boxes. It was written by a separate "blind seat" from the specification [`SPEC.md`](SPEC.md) and the design file
only, without access to checker A. It verifies the proof and rejects all three of its negative controls. This report
was compiled by the main team from the blind seat's code, logs and written summary.

## Independence

- **Inputs.** SPEC.md (published here with local paths removed) and `proof/design_chain.txt`.
- **No access to checker A.** The blind seat reports that it did not open checker A, the design scripts, or the code of
  our earlier proofs.
- **A different program.** It differs from checker A at every main step:

| | Checker A | Checker B |
|---|---|---|
| Time | autonomous rotating pair (cos, sin) | explicit time variable, integrated to an interval enclosure of T; a guard requires the time component to contain T |
| Sets | CAPD C0 tripleton | CAPD C0Rect2Set doubleton, started as the exact parallelogram piece |
| Chart inverse | interval inverse of [U S], applied through the tripleton's affine transformation | adjugate formula in interval arithmetic; enclosures from the set structure and from the hull, intersected |
| Disjointness | chart-to-chart subdivision | separating-axis test with interval projections |
| Comparisons | CAPD interval comparisons ("certainly") | explicit bound comparisons |

## Code

- [`verify_b.cpp`](verify_b.cpp): CAPD 6.1, Taylor order 12, single thread.

## Results

| Run | Log | Result |
|---|---|---|
| The design | `run_B.log` | **ALL VERIFIED.** 25/25 transitions (E−, E+, S); 276/276 pairs disjoint; 5,200 integrations, 0 failures; 36 s |
| Order 14, finer grid | `run_B_order14.log` | **ALL VERIFIED** |
| Control 1: last link orientation flipped | `run_B_neg1_orient.log` | NOT VERIFIED (C35 → A0 exit edges fail with certainty) |
| Control 2: m = 0.0590 | `run_B_neg2_m0590.log` | NOT VERIFIED (all transitions fail with certainty) |
| Control 3: A0 with b = 0.0024 | `run_B_neg3_thinA0.log` | NOT VERIFIED (C35 → A0 band check undecided at the depth cap) |

- **Control 3 is a real violation.** `run_B_neg3_probe.log` shows a point of C35 whose image has s ≤ −0.003263, outside
  the thinned band |s| ≤ 0.0024. So the failure is not a resolution artefact.
- **Margins.** The smallest margins on the design are 1.25e-3 for the exit conditions and 4.1e-4 for the band condition.
