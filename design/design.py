"""Design (numerical, non-rigorous) of a chain of h-sets for the laser map P (one period, phase 0), m = 0.0608.
  A0..A5 : affine boxes at the period-6 saddle orbit p_i, frame (e^u_i, e^s_i) from the cocycle.
  C<n>   : affine boxes at x_n = P^n(x_0), x_0 on the local unstable direction of p_0 (homoclinic shooting, homo.json),
           n = NIN..NOUT; frame e^u pushed forward along the orbit, e^s pulled back from e^s_0 at x_{NOUT+1}.
Transitions (each one period P): A_i => A_{i+1}, A_5 => C_NIN, C_n => C_{n+1}, C_NOUT => A_0.
Writes design.txt (chart/set/trans format of the Ueda checker, plus the model parameters) after dense float checks.
usage: python design.py [out]
"""
import numpy as np, json, sys
from lasermap import P, PJ

d = json.load(open("orb6.json")); orb = [np.array(q) for q in d["orb"]]
eu = [np.array(e) for e in d["eu"]]; es = [np.array(e) for e in d["es"]]
lam, mu = d["lam"], d["mu"]
u0 = json.load(open("homo.json"))["u0"]
NIN, NOUT = 18, 35          # C boxes at x_18 .. x_35 ; x_36 lands in A0

# A sizes
WA0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.008
SIG = float(sys.argv[5]) if len(sys.argv) > 5 else 1.15
wA = [WA0]
sig = [SIG] * 5
for i in range(5): wA.append(lam[i] * wA[i] / sig[i])
bA = [0.004, 0.006, 0.0045, 0.0035, 0.0012, 0.0068]

# homoclinic pseudo-orbit and frames
xs = [orb[0] - u0 * eu[0]]
for n in range(NOUT + 1): xs.append(P(xs[-1]))
Js = [PJ(xs[n])[1] for n in range(NOUT + 1)]
tu = [eu[0].copy()]
for n in range(NOUT + 1): tu.append(Js[n] @ tu[-1])
lamC = [np.linalg.norm(tu[n + 1]) / np.linalg.norm(tu[n]) for n in range(NOUT + 1)]
tu = [t / np.linalg.norm(t) for t in tu]
ts = [None] * (NOUT + 2); ts[NOUT + 1] = es[0].copy(); muC = [0.0] * (NOUT + 1)
for n in range(NOUT, -1, -1):
    t = np.linalg.solve(Js[n], ts[n + 1]); muC[n] = np.linalg.norm(ts[n + 1]) / np.linalg.norm(t); ts[n] = t / np.linalg.norm(t)
for n in range(NIN, NOUT + 1):
    print(f"x{n:2d} = ({xs[n][0]:+.5f},{xs[n][1]:+.5f}) angle {np.degrees(np.arccos(abs(tu[n] @ ts[n]))):5.1f}  stretch {lamC[n]:7.3f} contr {muC[n]:.4f}")

RHO_U, RHO_S = float(sys.argv[2]) if len(sys.argv) > 2 else 2.5, float(sys.argv[3]) if len(sys.argv) > 3 else 2.5
RHO_END = 2.0
wC = {NOUT: RHO_END * wA[0] / lamC[NOUT]}
for n in range(NOUT - 1, NIN - 1, -1): wC[n] = RHO_U * wC[n + 1] / lamC[n]
bC = {NIN: RHO_S * mu[5] * bA[5] + 2e-5}
KAP = float(sys.argv[6]) if len(sys.argv) > 6 else 2.0
for n in range(NIN, NOUT): bC[n + 1] = RHO_S * muC[n] * bC[n] + KAP * wC[n] ** 2
print("wC", {k: "%.1e" % v for k, v in wC.items()})
print("bC", {k: "%.1e" % v for k, v in bC.items()})

frames, sets = {}, {}
for i in range(6): frames[f"A{i}"] = (orb[i], eu[i], es[i]); sets[f"A{i}"] = (0.0, wA[i], bA[i])
for n in range(NIN, NOUT + 1): frames[f"C{n}"] = (xs[n], tu[n], ts[n]); sets[f"C{n}"] = (0.0, wC[n], bC[n])
trans = [(f"A{i}", f"A{(i + 1) % 6}") for i in range(6)] + [("A5", f"C{NIN}")]
trans += [(f"C{n}", f"C{n + 1}") for n in range(NIN, NOUT)] + [(f"C{NOUT}", "A0")]


def chart(nm, u, s):
    Q, U, S = frames[nm]; return Q[None, :] + u[:, None] * U[None, :] + s[:, None] * S[None, :]


def unc(nm, X):
    Q, U, S = frames[nm]; M = np.linalg.inv(np.column_stack([U, S])); r = (X - Q[None, :]) @ M.T; return r[:, 0], r[:, 1]


def Pmany(X): return np.array([P(x) for x in X])


allok, orient = True, {}
for src, dst in trans:
    c, w, b = sets[src]; c2, w2, b2 = sets[dst]
    sg = np.linspace(-b, b, 41)
    L = unc(dst, Pmany(chart(src, np.full_like(sg, c - w), sg)))
    R = unc(dst, Pmany(chart(src, np.full_like(sg, c + w), sg)))
    U, Sg = np.meshgrid(np.linspace(c - w, c + w, 15), np.linspace(-b, b, 15))
    Wi = unc(dst, Pmany(chart(src, U.ravel(), Sg.ravel())))
    o = 1 if L[0].mean() < R[0].mean() else -1
    lo, hi = (L, R) if o > 0 else (R, L)
    m1 = (c2 - w2) - lo[0].max(); m2 = hi[0].min() - (c2 + w2); m3 = b2 - np.abs(Wi[1]).max()
    ok = m1 > 0 and m2 > 0 and m3 > 0; allok &= ok; orient[(src, dst)] = o
    print(f"{src:>3} => {dst:<3} o {o:+d}: exit margins {m1 / w2:+.2f} {m2 / w2:+.2f} (x w2={w2:.1e}); entry margin {m3 / b2:+.2f} (x b2={b2:.1e}) {'OK' if ok else 'FAIL'}")


# disjointness: sample boundary-free check via chart coordinates of corner-dense grids
def inside(nm, X):
    u, s = unc(nm, X); c, w, b = sets[nm]; return (np.abs(u - c) <= w) & (np.abs(s) <= b)


names = list(sets); dis_ok = True
for i, a in enumerate(names):
    c, w, b = sets[a]; U, Sg = np.meshgrid(np.linspace(c - w, c + w, 60), np.linspace(-b, b, 60))
    X = chart(a, U.ravel(), Sg.ravel())
    for bnm in names[i + 1:]:
        if inside(bnm, X).any(): print("OVERLAP", a, bnm); dis_ok = False
print("ALL OK (floating point)" if allok and dis_ok else "SOME FAIL")
out = sys.argv[1] if len(sys.argv) > 1 else "design.txt"
lines = ["# laser map (Oppo Eq. 27 in s = ln I), mu=2 eps=1/25 omega=11/10 m=76/1250; period-6 cycle A0..A5 + homoclinic chain",
         "m 1", "p 1 0.0"]
for nm, (Q, U, S) in frames.items():
    lines.append("chart %s affine %r %r %r %r %r %r" % ((nm,) + tuple(float(v) for v in (Q[0], Q[1], U[0], U[1], S[0], S[1]))))
for nm, (c, w, b) in sets.items(): lines.append("set %s %r %r %r" % (nm, float(c), float(w), float(b)))
for s_, d_ in trans: lines.append(f"trans {s_} {d_} {orient[(s_, d_)]}")
open(out, "w", newline="\n").write("\n".join(lines) + "\n")
print("wrote", out)
