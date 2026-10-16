"""Check pairwise disjointness of the 24 h-set parallelograms in (y=lnI, W), via separating-axis test,
and report minimal separation gap (lower bound via SAT max-separation)."""
import numpy as np, itertools
from cover_check import parse, to_xy

charts, sets, trans = parse()
polys = {}
for n, (c, w, b) in sets.items():
    pts = [to_xy(charts[n], c+su*w, ss*b) for su, ss in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    polys[n] = np.array(pts)

def sat_gap(P, Q):
    gap = -np.inf
    for poly in (P, Q):
        for i in range(4):
            e = poly[(i+1)%4]-poly[i]; nrm = np.array([-e[1], e[0]]); nrm /= np.linalg.norm(nrm)
            a, b = P@nrm, Q@nrm
            g = max(b.min()-a.max(), a.min()-b.max())
            gap = max(gap, g)
    return gap  # >0 => disjoint, value = separating distance along best axis

res = []
for a, b in itertools.combinations(polys, 2):
    res.append((sat_gap(polys[a], polys[b]), a, b))
res.sort()
print("closest pairs (gap>0 means disjoint):")
for r in res[:8]: print("  %.4e  %s %s" % r)
print("ALL DISJOINT:", all(r[0] > 0 for r in res))
# also check chart frames non-degenerate
for n,(Q,U,S) in charts.items():
    d = U[0]*S[1]-U[1]*S[0]
    if abs(d) < 0.05: print("near-degenerate chart", n, d)
