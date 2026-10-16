import os
"""Red-team seat 2: independent check of covering relations in design_chain.txt.
Integrates Oppo Eq.(27) in ORIGINAL (I, W) variables with vectorized fixed-step RK4,
with step-halving error estimate, and cross-checks a subset with scipy DOP853 (rtol 1e-13).
Usage: python cover_check.py NU NS NSTEP
"""
import sys, numpy as np, time
from scipy.integrate import solve_ivp

MU, EPS, OM, M = 2.0, 0.04, 1.1, 0.0608
T = 2*np.pi/OM
CHAIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "proof", "design_chain.txt")

def rhs(t, I, W, m=M):
    c = np.cos(OM*t)
    return I*(W + (m/EPS)*c), MU - (1+EPS*W)*(1+I)

def rk4_map(I, W, N, m=M):
    h = T/N; t = 0.0
    I = I.copy(); W = W.copy()
    for k in range(N):
        t = k*h
        k1I, k1W = rhs(t, I, W, m)
        k2I, k2W = rhs(t+h/2, I+h/2*k1I, W+h/2*k1W, m)
        k3I, k3W = rhs(t+h/2, I+h/2*k2I, W+h/2*k2W, m)
        k4I, k4W = rhs(t+h, I+h*k3I, W+h*k3W, m)
        I = I + h/6*(k1I+2*k2I+2*k3I+k4I)
        W = W + h/6*(k1W+2*k2W+2*k3W+k4W)
    return I, W

def parse():
    charts, sets, trans = {}, {}, []
    for line in open(CHAIN):
        p = line.split()
        if not p or p[0].startswith('#'): continue
        if p[0] == 'chart':
            v = list(map(float, p[3:9]))
            charts[p[1]] = (np.array(v[0:2]), np.array(v[2:4]), np.array(v[4:6]))
        elif p[0] == 'set':
            sets[p[1]] = tuple(map(float, p[2:5]))
        elif p[0] == 'trans':
            trans.append((p[1], p[2], int(p[3])))
    return charts, sets, trans

def to_xy(ch, u, s):
    Q, U, S = ch
    return Q[0]+u*U[0]+s*S[0], Q[1]+u*U[1]+s*S[1]

def to_us(ch, y, W):
    Q, U, S = ch
    A = np.array([[U[0], S[0]], [U[1], S[1]]])
    Ai = np.linalg.inv(A)
    dy, dW = y-Q[0], W-Q[1]
    return Ai[0,0]*dy+Ai[0,1]*dW, Ai[1,0]*dy+Ai[1,1]*dW

if __name__ == '__main__':
    NU, NS, NSTEP = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    charts, sets, trans = parse()
    print(f"{len(charts)} charts, {len(sets)} sets, {len(trans)} transitions; T={T!r}")
    worst = []
    t0 = time.time()
    maxerr = 0
    for (src, dst, o) in trans:
        c, w, b = sets[src]; cd, wd, bd = sets[dst]
        uu = np.linspace(c-w, c+w, NU); ss = np.linspace(-b, b, NS)
        Ug, Sg = np.meshgrid(uu, ss, indexing='ij')
        y, W0 = to_xy(charts[src], Ug.ravel(), Sg.ravel())
        I1, W1 = rk4_map(np.exp(y), W0, NSTEP)
        I2, W2 = rk4_map(np.exp(y), W0, 2*NSTEP)
        u1, s1 = to_us(charts[dst], np.log(I1), W1)
        u2, s2 = to_us(charts[dst], np.log(I2), W2)
        err = max(np.abs(u1-u2).max(), np.abs(s1-s2).max())
        maxerr = max(maxerr, err)
        u2 = u2.reshape(NU, NS); s2 = s2.reshape(NU, NS)
        left, right = u2[0, :], u2[-1, :]
        if o == 1:
            mL = (cd-wd) - left.max()     # need left < cd-wd
            mR = right.min() - (cd+wd)    # need right > cd+wd
        else:
            mL = left.min() - (cd+wd)
            mR = (cd-wd) - right.max()
        mS = bd - np.abs(s2).max()
        # also full-grid u stretch: report min/max of image u
        worst.append((src, dst, o, mL/wd, mR/wd, mS/bd, mL, mR, mS, err))
        print(f"{src:>4}->{dst:<4} o={o:+d} margL={mL:+.3e} ({mL/wd:+.3f}w) margR={mR:+.3e} ({mR/wd:+.3f}w) "
              f"margS={mS:+.3e} ({mS/bd:+.3f}b) rk4err={err:.1e}", flush=True)
    print("max rk4 step-halving diff:", maxerr, " time", time.time()-t0)
    rel = [min(x[3], x[4], x[5]) for x in worst]
    i = int(np.argmin(rel))
    print("WORST relative margin:", worst[i][:3], rel[i])
    print("ANY VIOLATION:", any(min(x[6], x[7], x[8]) <= 0 for x in worst))
