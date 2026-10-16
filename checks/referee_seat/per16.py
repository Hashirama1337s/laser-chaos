# red-team check: attractor period at m=0.0608 in original (I,W) variables, independent of lab code
import numpy as np, sys
from scipy.integrate import solve_ivp
mu,eps,om=2.0,0.04,1.1
T=2*np.pi/om
def run(m,x0,ntr,nrec,rtol,method='DOP853'):
    K=m/eps
    f=lambda t,x:[x[0]*(x[1]+K*np.cos(om*t)), mu-(1+eps*x[1])*(1+x[0])]
    x=np.array(x0,float); pts=[]
    for k in range(ntr+nrec):
        s=solve_ivp(f,(k*T,(k+1)*T),x,method=method,rtol=rtol,atol=rtol*1e-3)
        x=s.y[:,-1]
        if k>=ntr: pts.append(x.copy())
    return np.array(pts)
m=float(sys.argv[1]); rtol=float(sys.argv[2]); ntr=int(sys.argv[3]); meth=sys.argv[4] if len(sys.argv)>4 else 'DOP853'
rng=np.random.default_rng(1)
for ic in [(1.0,0.0),(0.5,1.0),(3.0,-1.0)]:
    p=run(m,ic,ntr,128,rtol,meth)
    d=[np.max(np.linalg.norm(p[q:]-p[:-q],axis=1)) for q in range(1,65)]
    best=int(np.argmin(d))+1
    print(f"m={m} rtol={rtol} {meth} ic={ic}: smallest-period-with-return<1e-6:",
          next((q for q in range(1,65) if d[q-1]<1e-6),None), " min dist",min(d),"at",best)
