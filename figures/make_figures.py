"""Figures for the laser-chaos repository.

Usage:  python figures/make_figures.py <repo root>
Writes figures/*.svg next to this script. Every plotted number is read from files shipped in the repository:
  proof/design_chain.txt          the 24 proof boxes (charts, sizes) and the 25 links of the route map
  design/attr.npy                 simulated strobe points at m = 0.0608 (written by design/attractor.py)
  design/homo_orbit.npy           the numerical guide orbit (written by design/homo.py)
  design/sweep.txt                Lyapunov sweep in m (written by design/sweep.py)
  design/period16.txt             multipliers of the period-16 cycle (written by design/period16.py)
Nothing here is part of the proof; the boxes are drawn exactly as defined, everything else is a float illustration.
Checked copy (figure referee, 2026-11-17): hero title/legend mark the rhythm as simulation; sweep shows dots only.
"""
import os
import re
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon

BG, BORDER, GRID, AXC, TXT, ACC = "#1c2026", "#2f353d", "#22272e", "#9aa4ae", "#e8edf2", "#39ff14"
CAT = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#0ca30c", "#9085e9", "#e66767"]
NEUTRAL = "#5b636c"


def style():
    plt.rcParams.update({
        "svg.fonttype": "none", "svg.hashsalt": "laser-chaos-figures",
        "font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 14, "axes.titlesize": 15, "axes.labelsize": 14, "xtick.labelsize": 12.5, "ytick.labelsize": 12.5,
        "legend.fontsize": 12.5, "figure.facecolor": "none", "axes.facecolor": BG, "axes.edgecolor": AXC,
        "axes.labelcolor": TXT, "axes.titlecolor": TXT, "xtick.color": AXC, "ytick.color": AXC, "text.color": TXT,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.spines.top": False,
        "axes.spines.right": False, "legend.facecolor": BG, "legend.edgecolor": BORDER, "legend.labelcolor": TXT,
        "legend.framealpha": 1.0, "lines.linewidth": 2.0,
    })


def frame(fig):
    w, h = fig.get_size_inches()
    fig.patches.append(FancyBboxPatch((0.03, 0.03), w - 0.06, h - 0.06, boxstyle="round,pad=0,rounding_size=0.18",
                                      transform=fig.dpi_scale_trans, fc=BG, ec=BORDER, lw=1.5, zorder=-100))


def save(fig, name):
    here = os.path.dirname(os.path.abspath(__file__))
    out = here if os.path.basename(here) == "figures" else os.path.join(here, "figures")   # repo: figures/make_figures.py
    os.makedirs(out, exist_ok=True)
    fig.savefig(os.path.join(out, name), format="svg", metadata={"Date": None, "Creator": None})
    plt.close(fig)
    print("wrote figures/" + name)


def read_design(root):
    L = [l.split() for l in open(os.path.join(root, "proof", "design_chain.txt"), encoding="utf-8")
         if l.strip() and not l.startswith("#")]
    head = open(os.path.join(root, "proof", "design_chain.txt"), encoding="utf-8").readline()
    charts = {t[1]: np.array(list(map(float, t[3:9]))) for t in L if t[0] == "chart"}
    sets = {t[1]: tuple(map(float, t[2:5])) for t in L if t[0] == "set"}
    trans = [(t[1], t[2]) for t in L if t[0] == "trans"]
    m = re.search(r"m=(\d+)/(\d+)", head)
    return charts, sets, trans, (int(m.group(1)), int(m.group(2)))


def box_corners(chart, st):
    """Corners of an h-set: X = Q + u U + s S with |u - c| <= w, |s| <= b (as in design/fig_proof.py)."""
    Q, U, S = chart[:2], chart[2:4], chart[4:6]
    c, w, b = st
    return np.array([Q + (c + su * w) * U + sb * b * S for su, sb in [(-1, -1), (1, -1), (1, 1), (-1, 1)]])


def closed_routes(nodes, trans, nmax):
    """trace(G^n): the number of closed routes of length n in the route map (exact integers)."""
    idx = {n: i for i, n in enumerate(nodes)}
    G = [[0] * len(nodes) for _ in nodes]
    for a, b in trans:
        G[idx[a]][idx[b]] += 1
    M = [[int(i == j) for j in range(len(nodes))] for i in range(len(nodes))]
    out = []
    for _ in range(nmax):
        M = [[sum(M[i][k] * G[k][j] for k in range(len(nodes))) for j in range(len(nodes))] for i in range(len(nodes))]
        out.append(sum(M[i][i] for i in range(len(nodes))))
    return out, np.array(G, float)


def fig_hero(root, charts, sets, mfrac):
    attr = np.load(os.path.join(root, "design", "attr.npy"))
    cyc = attr[-16:]
    # the last 16 strobe points close up after 16 wobbles (a stable period-16 cycle; numerical)
    assert np.max(np.abs(attr[-1] - attr[-17])) < 1e-6, "attr.npy tail is not a 16-cycle"
    assert np.min([np.max(np.abs(attr[-1] - attr[-1 - k])) for k in range(1, 16)]) > 1e-3
    A = [n for n in sets if n.startswith("A")]
    C = [n for n in sets if n.startswith("C")]
    cen = {n: box_corners(charts[n], sets[n]).mean(0) for n in sets}

    fig = plt.figure(figsize=(12.5, 6.8))
    frame(fig)
    ax = fig.add_axes([0.075, 0.11, 0.54, 0.68])
    az = fig.add_axes([0.70, 0.11, 0.27, 0.68])
    fig.text(0.03, 0.94, "Proved chaos hides beside the steady rhythm seen in simulations", fontsize=17, weight="bold")
    fig.text(0.03, 0.845, "One mark per wobble of the losses (strobe view), m = %d/%d.\nSquares and diamonds show "
             "where the proof boxes sit; the boxes themselves are tiny (right)." % mfrac, fontsize=13, color=AXC,
             linespacing=1.4)

    ax.plot(cyc[:, 0], cyc[:, 1], "o", ms=10, mfc="none", mec=CAT[2], mew=2.2, ls="none",
            label="rhythm seen in simulations: 16 rings (numerical, not proved)")
    ax.plot([cen[n][0] for n in C], [cen[n][1] for n in C], "s", ms=8, color=CAT[1], ls="none",
            label="18 proof boxes on the long detour (C18-C35)")
    ax.plot([cen[n][0] for n in A], [cen[n][1] for n in A], "D", ms=8, color=CAT[0], ls="none",
            label="6 proof boxes on the short loop (A0-A5)")
    ax.text(cen["A0"][0] + 0.12, cen["A0"][1] + 0.07, "A0", color=CAT[0], fontsize=12.5, ha="left", va="bottom",
            weight="bold")
    ax.set_xlabel("log-intensity  y = ln I")
    ax.set_ylabel("inversion  W")
    ax.set_xlim(-5.9, 2.1)
    ax.set_ylim(-2.05, 2.25)
    zx, zy = (-5.17, -5.115), (1.352, 1.373)
    ax.add_patch(Rectangle((zx[0], zy[0]), zx[1] - zx[0], zy[1] - zy[0], fill=False, ec=TXT, lw=1.2, zorder=5))
    ax.annotate("zoom", xy=(zx[1], zy[0]), xytext=(-4.75, 0.75), color=TXT, fontsize=12.5,
                arrowprops=dict(arrowstyle="-", color=TXT, lw=1))
    ax.legend(loc="lower left", frameon=True, fontsize=12, markerscale=0.9, borderpad=0.6)

    for n in sets:
        P = box_corners(charts[n], sets[n])
        col = CAT[0] if n.startswith("A") else CAT[1]
        az.add_patch(Polygon(P, closed=True, fc=col, ec=col, alpha=0.35, lw=0, zorder=3))
        az.add_patch(Polygon(P, closed=True, fill=False, ec=col, lw=1.2, zorder=4))
    for n in ("A0", "C18"):
        x, y = cen[n]
        az.text(x, y + 0.0045 if n == "A0" else y - 0.0050, n, color=CAT[0] if n == "A0" else CAT[1],
                ha="center", va="bottom" if n == "A0" else "top", fontsize=13, weight="bold")
    az.set_xlim(*zx)
    az.set_ylim(*zy)
    az.set_title("two boxes at true size", fontsize=13.5, color=TXT, loc="left")
    az.set_xlabel("y = ln I")
    az.set_ylabel("W")
    az.locator_params(axis="x", nbins=3)
    for s in az.spines.values():
        s.set_visible(True)
        s.set_color(TXT)
    save(fig, "laser-proof-boxes-and-rhythm.svg")


def fig_sweep(root, mfrac):
    rows = []
    for line in open(os.path.join(root, "design", "sweep.txt"), encoding="utf-8"):
        g = re.match(r"m=([\d.]+) om=([\d.]+) lyap=([+-][\d.]+)", line.strip())
        if g and g.group(2) == "1.10":
            rows.append((float(g.group(1)), float(g.group(3))))
    rows = np.array(sorted(rows))
    mult = re.search(r"multipliers[^\[]*\[\s*([\d.e+-]+)\s+([\d.e+-]+)\s*\]",
                     open(os.path.join(root, "design", "period16.txt"), encoding="utf-8").read())
    m0 = mfrac[0] / mfrac[1]

    fig = plt.figure(figsize=(12.5, 5.6))
    frame(fig)
    ax = fig.add_axes([0.09, 0.14, 0.86, 0.66])
    fig.text(0.03, 0.92, "The proof's setting sits just below where visible chaos begins", fontsize=17, weight="bold")
    fig.text(0.03, 0.865, "Largest Lyapunov exponent from long simulations (numerical, not proved). "
             "Dots: the %d sampled depths; nothing is drawn between them." % len(rows),
             fontsize=13, color=AXC)
    ax.axhline(0, color=AXC, lw=1.2, zorder=1)
    ax.axvline(m0, color=TXT, lw=1.2, ls=(0, (4, 3)), zorder=1)
    ax.plot(rows[:, 0], rows[:, 1], "o", ms=8, color=ACC, zorder=3)
    ax.text(m0 - 0.00008, 0.375, "m = %d/%d = %.4f:\nthe review's value,\nwhere the chaos is proved" % (mfrac[0], mfrac[1], m0),
            ha="right", va="top", fontsize=12.5, color=TXT)
    ax.text(m0 - 0.00008, 0.17, "there, simulations settle into\na stable 16-wobble rhythm\n(multipliers %.3f and %.5f)"
            % (float(mult.group(1)), float(mult.group(2))), ha="right", va="top", fontsize=12.5, color=AXC)
    ax.text(0.0658, 0.03, "above 0: nearby motions\nfly apart (visible chaos)", ha="right", va="bottom",
            fontsize=12.5, color=TXT)
    ax.text(0.0658, -0.03, "below 0: nearby motions\ndraw together", ha="right", va="top", fontsize=12.5, color=TXT)
    ax.set_xlabel("wobble depth m (modulation depth of the cavity losses)")
    ax.set_ylabel("exponent per wobble")
    ax.set_xlim(0.0586, 0.0662)
    ax.set_ylim(-0.30, 0.40)
    save(fig, "laser-lyapunov-sweep.svg")


def fig_count(sets, trans):
    nodes = list(sets)
    N = 240
    cnt, G = closed_routes(nodes, trans, N)
    r = max(abs(np.linalg.eigvals(G)))
    assert abs(r ** 24 - r ** 18 - 1) < 1e-9, "growth rate is not the root of x^24 = x^18 + 1"
    n = np.arange(1, N + 1)
    keep = np.array(cnt) > 0
    assert all(k % 6 == 0 for k in n[keep]), "closed routes exist only at multiples of 6"
    fig = plt.figure(figsize=(12.5, 5.6))
    frame(fig)
    ax = fig.add_axes([0.10, 0.14, 0.85, 0.66])
    fig.text(0.03, 0.92, "Repeating motions without end: the count keeps growing", fontsize=17, weight="bold")
    fig.text(0.03, 0.865, "Different box-routes that close up after n wobbles, counted exactly from the route map "
             "(log scale)", fontsize=13, color=AXC)
    ax.semilogy(n[keep], np.array(cnt, float)[keep], "o", ms=8, color=ACC, zorder=3)
    for k in (6, 24, 120, 240):
        c = cnt[k - 1]
        ax.annotate("{:,}".format(c), (k, c), xytext=(0, 10), textcoords="offset points", ha="center",
                    fontsize=12.5, color=TXT)
    ax.text(130, 30, "long-run growth: a factor of about %.5f per wobble\n(largest root of x^24 = x^18 + 1)" % r,
            fontsize=12.5, color=AXC, ha="left", va="center")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, p: "{:,.0f}".format(v)))
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("n (wobbles until the motion repeats; routes exist only for multiples of 6)")
    ax.set_ylabel("number of routes")
    ax.set_xlim(0, N + 8)
    save(fig, "laser-repeating-routes.svg")
    return cnt, r


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), ".."))
    style()
    charts, sets, trans, mfrac = read_design(root)
    assert len(sets) == 24 and len(trans) == 25
    fig_hero(root, charts, sets, mfrac)
    fig_sweep(root, mfrac)
    cnt, r = fig_count(sets, trans)
    print("routes n=6,24,120,240:", cnt[5], cnt[23], cnt[119], cnt[239], " r=%.6f ln r=%.6f" % (r, np.log(r)))


if __name__ == "__main__":
    main()
