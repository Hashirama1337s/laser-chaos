"""Print the saved numerical homoclinic orbit (homo_orbit.npy from homo.py) in the local frames of the period-6 orbit."""
import numpy as np, json
d = json.load(open("orb6.json")); orb = [np.array(q) for q in d["orb"]]
M = [np.linalg.inv(np.column_stack([d["eu"][i], d["es"][i]])) for i in range(6)]
for n, x in enumerate(np.load("homo_orbit.npy")):
    a, b = M[n % 6] @ (x - orb[n % 6]); print(f"{n:2d}  x=({x[0]:+.6f},{x[1]:+.6f})  a={a:+.3e}  b={b:+.3e}")
