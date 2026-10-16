"""Numerical (non-rigorous): the period-16 cycle of P at m = 0.0608 and its multipliers (eigenvalues of DP^16)."""
import numpy as np
from lasermap import newton
y = np.load("attr.npy")[-1]              # a point on the simulated attractor (attractor.py)
y, res, J = newton(y, 16)
print("period-16 point (y, W) =", y, " residual", res)
print("multipliers of P^16:", np.linalg.eigvals(J))
