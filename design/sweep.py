import numpy as np, sys
from lasermap import *
import lasermap
from multiprocessing import Pool
from scipy.integrate import solve_ivp
def Pg(y,m,om):
    Tg=2*np.pi/om
    return solve_ivp(f,(0,Tg),y,method="DOP853",rtol=1e-11,atol=1e-12,args=(m,MU,EPS,om)).y[:,-1]
def PJg(y,m,om):
    Tg=2*np.pi/om
    s=solve_ivp(fv,(0,Tg),list(y)+[1,0,0,1],method="DOP853",rtol=1e-11,atol=1e-12,args=(m,MU,EPS,om)).y[:,-1]
    return s[:2],s[2:].reshape(2,2)
def run(a):
    m,om=a
    y=np.array([0.,0.])
    for i in range(500): y=Pg(y,m,om)
    v=np.array([1.,.3]); L=0
    for i in range(300):
        z,J=PJg(y,m,om); v=J@v; n=np.linalg.norm(v); L+=np.log(n); v/=n; y=z
    return m,om,L/300
if __name__=="__main__":
    args=[(m,1.1) for m in np.round(np.arange(0.0590,0.0660,0.0004),5)]+[(0.080,0.47),(0.078,0.47),(0.082,0.47)]
    with Pool(14) as p:
        for r in p.map(run,args): print("m=%.4f om=%.2f lyap=%+.4f"%r)
