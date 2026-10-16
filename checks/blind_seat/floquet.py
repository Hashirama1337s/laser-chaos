"""Locate the period-k orbit at m=0.0608 by Newton on P^k with DOP853 (rtol 1e-13) + variational eqs,
in (I,W); report Floquet multipliers of P^k and LE = ln|lambda_max|/(kT).
Also repeat the multiplier computation with Radau and LSODA at rtol 1e-11 as a cross-check."""
import sys, numpy as np
from scipy.integrate import solve_ivp
MU, EPS, OM = 2.0, 0.04, 1.1
T = 2*np.pi/OM
m = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0608
k = int(sys.argv[2]) if len(sys.argv) > 2 else 16

def f(t, z):
    I, W, a, b, c, d = z
    cc = (m/EPS)*np.cos(OM*t)
    J = np.array([[W+cc, I], [-(1+EPS*W), -EPS*(1+I)]])
    V = J @ np.array([[a, c], [b, d]])
    return [I*(W+cc), MU-(1+EPS*W)*(1+I), V[0,0], V[1,0], V[0,1], V[1,1]]

def Pk(x, method='DOP853', rtol=1e-13):
    z = [x[0], x[1], 1, 0, 0, 1]
    r = solve_ivp(f, (0, k*T), z, method=method, rtol=rtol, atol=rtol*1e-2)
    z = r.y[:, -1]
    return z[:2], np.array([[z[2], z[4]], [z[3], z[5]]])

# start from an attractor point: integrate 1500 periods from a generic IC
r = solve_ivp(lambda t, z: f(t, list(z)+[1,0,0,1])[:2], (0, 1500*T), [1.0, 0.0], method='DOP853',
              rtol=1e-11, atol=1e-13)
x = r.y[:, -1]
for it in range(12):
    y, J = Pk(x)
    F = y - x
    print(f"newton {it}: |P^k x - x| = {np.abs(F).max():.3e}")
    if np.abs(F).max() < 1e-12: break
    x = x - np.linalg.solve(J - np.eye(2), F)
y, J = Pk(x)
ev = np.linalg.eigvals(J)
print("periodic point (I,W):", x, " residual", np.abs(y-x).max())
print("Floquet multipliers of P^%d (DOP853 1e-13):" % k, ev, "|.|", np.abs(ev))
print("det check exp(trace integral) -> det J =", np.linalg.det(J))
print("LE per tau = %.6e ; per period = %.6e" % (np.log(np.abs(ev).max())/(k*T), np.log(np.abs(ev).max())/k))
# minimal period check
for p in range(1, k+1):
    z = x.copy()
    rr = solve_ivp(lambda t, z: f(t, list(z)+[1,0,0,1])[:2], (0, p*T), x, method='DOP853', rtol=1e-13, atol=1e-15)
    if np.abs(rr.y[:, -1]-x).max() < 1e-8:
        print("minimal period:", p); break
for meth, tol in [('Radau', 1e-11), ('LSODA', 1e-11), ('DOP853', 1e-9)]:
    y2, J2 = Pk(x, meth, tol)
    print(f"{meth} rtol={tol}: multipliers", np.linalg.eigvals(J2), " |P^k x - x| =", np.abs(y2-x).max())
