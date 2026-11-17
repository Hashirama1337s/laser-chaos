# laser-chaos: figure captions and sources

All three figures are drawn by `figures/make_figures.py` (run: `python figures/make_figures.py .` from the repo root;
Python 3.11, numpy, matplotlib 3.11). Every plotted value is read from a shipped file; no number is typed into a plot.

## 1. `figures/laser-proof-boxes-and-rhythm.svg` (hero)

**Point.** The proved chaotic set and the steady rhythm the laser actually settles into sit side by side in the same
strobe picture: the chaos is real but hidden.

**Caption.** The laser seen once per wobble of its losses (log-intensity across, inversion up), at the review's
setting m = 76/1250. Blue diamonds and orange squares mark where the 24 proof boxes sit: 6 on the short loop A0-A5 and
18 on the long detour C18-C35. The boxes are far too small to see at this scale; the right panel shows two of them
(A0 and C18) at true size, drawn exactly as defined in `proof/design_chain.txt`. Green rings: the 16 strobe points of
the stable rhythm that long simulations settle into (a numerical result, not part of the theorem). The proof says
the boxes carry chaotic motions; it does not say which motion a simulation will show.

**Alt text.** Scatter plot of the laser's strobe plane. Twenty-four small square and diamond markers (the proof boxes)
spread along an arc from the upper left to the lower right; sixteen green rings (the simulated period-16 rhythm) sit
near but apart from them. A zoom panel shows two of the boxes as thin parallelograms.

**Sources.**
| element | file | field |
|---|---|---|
| box positions and shapes (24) | `proof/design_chain.txt` | `chart` lines (centre Q, directions U, S) and `set` lines (c, w, b); corners Q + (c ± w)U ± bS, as in `design/fig_proof.py` |
| counts 24, 6, 18 | `proof/design_chain.txt` | number of `set` lines starting with A / C (script asserts 24 sets and 25 `trans` lines) |
| m = 76/1250 | `proof/design_chain.txt` | header comment `m=76/1250` |
| 16 rhythm points (legend: "numerical, not proved") | `design/attr.npy` | last 16 rows; the script asserts they close up after 16 steps and not sooner |
| "rhythm is numerical, not proved" | README "Where the picture breaks"; TECHNICAL "Numerical note" | text |

## 2. `figures/laser-lyapunov-sweep.svg`

**Point.** The review's setting lies just below the depth where visible chaos begins in simulations, which is why
the proved chaos stays hidden.

**Caption.** Largest Lyapunov exponent (how fast nearby motions separate, per wobble) from long simulations, against
the wobble depth m (numerical, not proved). Below zero, nearby motions draw together and the laser settles into a
regular rhythm; above zero, they fly apart. At the proof's setting m = 0.0608 (dashed line) simulations settle into a
stable 16-wobble rhythm, with multipliers 0.640 and 0.00102. The exponent is negative up to m = 0.0606 and positive
from m = 0.0610, apart from one periodic window at m = 0.0638. Dots: the 18 sampled depths; nothing is drawn
between them.

**Alt text.** Dot chart of the Lyapunov exponent at 18 wobble depths from 0.0590 to 0.0658. Values sit near -0.2 up to
0.0606 (one point just below zero, -0.017, at 0.0602), jump above zero at 0.0610, stay around +0.25 except one dip to -0.23 at 0.0638. A dashed vertical line marks
0.0608.

**Sources.**
| element | file | field |
|---|---|---|
| 18 (m, exponent) points | `design/sweep.txt` | rows with `om=1.10` (`m=`, `lyap=`) |
| 0.0606 / 0.0610 / 0.0638 | `design/sweep.txt` | last negative, first positive, the dip |
| m = 76/1250 = 0.0608 | `proof/design_chain.txt` | header comment |
| multipliers 0.640, 0.00102 | `design/period16.txt` | `multipliers of P^16: [0.63977308 0.00101663]` (printed to 3 significant figures) |

## 3. `figures/laser-repeating-routes.svg`

**Point.** The proof gives repeating motions without end, and their number grows steadily with the length of the
repeat.

**Caption.** How many different box-routes close up after n wobbles, counted exactly from the route map of the proof
(log scale). Routes exist only when n is a multiple of 6, since the two loops last 6 and 24 wobbles. For every such
route the theorem gives an exact solution that repeats after n wobbles, and because the boxes do not overlap,
different routes give different starting states: 6 for n = 6, 30 for n = 24, 3,780 for n = 120 and 2,381,268 for n = 240.
In the long run the count grows by a factor of about 1.05518 per wobble, the largest root of x^24 = x^18 + 1; its
logarithm, about 0.0537, is the proved lower bound on the topological entropy.

**Alt text.** Dot chart on a log scale: the number of closed routes rises from 6 at n = 6 to about 2.4 million at
n = 240, almost along a straight line.

**Sources.**
| element | file | field |
|---|---|---|
| route map (24 nodes, 25 links) | `proof/design_chain.txt` | `trans` lines |
| counts 6, 30, 3,780, 2,381,268 | computed | trace of G^n for the 0/1 link matrix G, exact integers (script prints them) |
| 1.05518, 0.0537 | computed; matches README "How fast the patterns multiply" | spectral radius of G (script asserts r^24 = r^18 + 1); ln r = 0.053714 |
| "different routes give different starting states" | README Theorem items 1-2 ("every periodic one by a periodic orbit") and "pairwise disjoint h-sets" | text |

Dropped: a per-link margin chart (75 positive margins from `independent/run_B.log`). It is true but it reads as an
audit table rather than a picture of the discovery; the TECHNICAL table already shows it.
