"""Numerical (non-rigorous) tools for the class-B laser with modulated losses, Oppo arXiv:2510.18472 Eq. (27):
    dI/dt = I (W + (m/eps) cos(w t)),   dW/dt = mu - (1 + eps W)(1 + I)
in log-intensity s = ln I:
    ds/dt = W + (m/eps) cos(w t),       dW/dt = mu - (1 + eps W)(1 + exp(s))
P = stroboscopic (time 2*pi/w) map of (s, W) starting at phase t = 0.
"""
import numpy as np
from scipy.integrate import solve_ivp

MU, EPS, OM, M = 2.0, 0.04, 1.1, 0.0608
T = 2 * np.pi / OM


def f(t, y, m=M, mu=MU, eps=EPS, om=OM):
    s, W = y[0], y[1]
    e = np.exp(s)
    return [W + (m / eps) * np.cos(om * t), mu - (1 + eps * W) * (1 + e)]


def fv(t, y, m=M, mu=MU, eps=EPS, om=OM):
    s, W = y[0], y[1]
    e = np.exp(s)
    J = np.array([[0.0, 1.0], [-(1 + eps * W) * e, -eps * (1 + e)]])
    V = y[2:].reshape(2, 2)
    dV = J @ V
    return [W + (m / eps) * np.cos(om * t), mu - (1 + eps * W) * (1 + e)] + list(dV.ravel())


def P(y, k=1, m=M, t0=0.0):
    sol = solve_ivp(f, (t0, t0 + k * T), y, method="DOP853", rtol=1e-12, atol=1e-12, args=(m,))
    return sol.y[:, -1]


def PJ(y, k=1, m=M):
    y0 = list(y) + [1.0, 0.0, 0.0, 1.0]
    sol = solve_ivp(fv, (0, k * T), y0, method="DOP853", rtol=1e-12, atol=1e-12, args=(m,))
    return sol.y[:2, -1], sol.y[2:, -1].reshape(2, 2)


def newton(y, k=1, m=M, it=40):
    y = np.array(y, float)
    for _ in range(it):
        z, J = PJ(y, k, m)
        F = z - y
        dy = np.linalg.solve(J - np.eye(2), -F)
        y = y + dy
        if np.linalg.norm(dy) < 1e-13:
            break
    z, J = PJ(y, k, m)
    return y, np.linalg.norm(z - y), J
