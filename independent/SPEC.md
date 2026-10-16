*(Local paths removed for publication; otherwise as given to the blind seat.)*

# Checker B specification (blind): verify a chain of covering relations for the modulated class-B laser map

You are writing an INDEPENDENT rigorous verifier. Do not look for, open or copy any other verifier code. In particular
open nothing under ../proof/, ../design/ or the code of our earlier proofs.
Work only from this specification and design_chain.txt in this folder.

## 1. The map
- Class-B laser with modulated losses (Oppo, arXiv:2510.18472, Eq. 27):
  dI/dt = I (W + (m/eps) cos(omega t)),  dW/dt = mu - (1 + eps W)(1 + I).
- Parameters, exact: mu = 2, eps = 1/25, omega = 11/10, m = 76/1250 (= 0.0608). Use interval enclosures of 1/25, 11/10,
  76/1250 and pi.
- State (y, W) with y = ln I:  dy/dt = W + (m/eps) cos(omega t),  dW/dt = mu - (1 + eps W)(1 + exp(y)).
- P: R^2 -> R^2 is the time-T map, T = 2*pi/omega, started at t = 0 (stroboscopic map at phase 0), in (y, W).

## 2. Charts (all coordinates below are doubles read from design_chain.txt; treat them as exact numbers)
- The "p" line (polynomial) is present for format compatibility; this design uses only affine charts. Reject the file
  if any chart is not affine.
- `chart NAME affine Qy QW Uy UW Sy SW`: X(u, s) = Q + u U + s S.
- Inverse: (u, s) = [U S]^(-1) (X - Q), where [U S] is the 2x2 matrix with columns U and S.
- The "m 1" line means one exit direction.

## 3. h-sets
- `set NAME c w b`: N = {X(u, s) : |u - c| <= w, |s| <= b} in chart NAME.
- Exit direction u, entry direction s.
- Left exit edge u = c - w; right exit edge u = c + w (each for |s| <= b).

## 4. What to prove
For every line `trans SRC DST o` (o = +1 or -1), with N = SRC and M = DST in their own charts:
- **(E-)** for every point of N's left edge, P(point) in M's chart has u < cM - wM if o = +1, or u > cM + wM if o = -1.
- **(E+)** for every point of N's right edge, the opposite inequality (u > cM + wM if o = +1, u < cM - wM if o = -1).
- **(S)** for every point of N, P(point) in M's chart has |s| < bM.

Also prove:
- **(D)** all h-sets are pairwise disjoint.

Every inequality must be established with rigorous interval arithmetic (outward rounding) and a validated ODE
integrator, for ALL points of the edges/sets (cover them by finitely many boxes and enclose each box's image).

## 5. Tools
You may use CAPD 6.1 (built locally).
- Build flags: the Cflags and Libs lines of CAPD's build/bin/capd.pc
  (g++ <Cflags> file.cpp <Libs> -o out).
- Or any other rigorous method you implement yourself (e.g. your own interval Taylor integrator).

**Independence matters more than speed.** Make your own choices for:
- how you handle the time dependence (e.g. explicit time variable vs. an autonomous (cos, sin) pair);
- the set representation (e.g. doubleton/rect set vs. tripleton);
- subdivision strategy;
- the inverse-chart computation.

**Known CAPD pitfalls:**
- Do NOT use multithreading with CAPD (not thread-safe).
- Moderate Taylor orders (about 10-14) are reliable.
- Every run must finish in under 30 minutes; the reference run takes seconds.

## 6. Deliverables (write in this folder only)
- **verify_b.cpp** (or .py): the verifier.
- **run_b.log:** the full output of a run on design_chain.txt, with per-transition and per-edge results and a final line
  ALL VERIFIED / NOT VERIFIED.
- **Negative controls, each must report NOT VERIFIED (write each as a modified copy of the design in this folder):**
  1. the last transition's orientation flipped (`trans C35 A0 1`);
  2. m = 0.0590 instead of 76/1250 (a command-line or compile-time switch is fine);
  3. h-set A0 with b = 0.0024 instead of its listed value (a box too thin to receive C35's image).
- **REPORT_B.md:** method, choices, results, run times, anything that looked suspicious in the design or this spec.

Stop after these deliverables; do not modify anything outside this folder.
