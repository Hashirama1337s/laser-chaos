"""Independent integrators (scipy DOP853 / LSODA / Radau) at rtol 1e-9..1e-13, 5000 transient periods
from ICs in the Fig.15(a) region; then period detection over 200 periods + continuous-orbit extent."""
import numpy as np, time, itertools
from multiprocessing import Pool
from scipy.integrate import solve_ivp
MU, EPS, OM, M = 2.0, 0.04, 1.1, 0.0608
T = 2*np.pi/OM

def f(t, z):
    return [z[0]*(z[1]+(M/EPS)*np.cos(OM*t)), MU-(1+EPS*z[1])*(1+z[0])]

def job(args):
    (I0, W0), meth, rtol, ntr = args
    t0 = time.time()
    z = np.array([I0, W0])
    # integrate in chunks of 100 periods to keep memory small; restart at multiples of T (phase exact)
    for c in range(ntr//100):
        r = solve_ivp(f, (c*100*T, (c+1)*100*T), z, method=meth, rtol=rtol, atol=rtol*1e-3)
        z = r.y[:, -1]
    r = solve_ivp(f, (ntr*T, (ntr+200)*T), z, method=meth, rtol=rtol, atol=rtol*1e-3,
                  t_eval=ntr*T+T*np.arange(201), dense_output=False)
    P = r.y.T  # 201 strobe points
    per = -1
    for p in range(1, 129):
        if np.abs(P[-1-p]-P[-1]).max() < 1e-6: per = p; break
    rr = solve_ivp(f, (ntr*T, (ntr+32)*T), z, method=meth, rtol=rtol, atol=rtol*1e-3, max_step=0.01)
    return (I0, W0, meth, f"{rtol:g} ntr={ntr}", per, rr.y[0].max(), rr.y[1].min(), rr.y[1].max(), P[-1].tolist(), time.time()-t0)

if __name__ == '__main__':
    ics = [(0.05, 0.0), (5.0, 0.0), (1.0, 2.5), (1.0, -2.7), (3.0, 1.0), (0.3, -1.5)]
    cfg = [('DOP853', 1e-9, 5000), ('DOP853', 1e-11, 5000), ('DOP853', 1e-13, 2000), ('LSODA', 1e-11, 3000), ('Radau', 1e-10, 500)]
    jobs = [(ic, me, tol, n) for ic in ics for (me, tol, n) in cfg]
    with Pool(12) as p:
        for res in p.imap_unordered(job, jobs):
            I0, W0, me, tol, per, Imax, Wmin, Wmax, last, dt = res
            print(f"IC=({I0},{W0}) {me} rtol={tol}: period={per} orbit Imax={Imax:.3f} W in [{Wmin:.3f},{Wmax:.3f}] "
                  f"strobe=({last[0]:.8f},{last[1]:.8f}) [{dt:.0f}s]", flush=True)
