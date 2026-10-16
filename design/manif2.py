import numpy as np, sys, pickle
from lasermap import *
from scipy.integrate import solve_ivp
from multiprocessing import Pool
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
m=M
def Pf(y): return P(y,1,m)
def Pb(y): return solve_ivp(f,(T,0),y,method="DOP853",rtol=1e-11,atol=1e-12,args=(m,)).y[:,-1]
def inbox(y): return -10<y[0]<3 and -5<y[1]<5
POOL=None
def mapmany(fn,pts): return POOL.map(fn,pts,chunksize=16)
def Fk(y,k,fwd):
    for i in range(k):
        if not inbox(y): return np.array([np.nan,np.nan])
        y=Pf(y) if fwd else Pb(y)
    return y
def F6f(y): return Fk(y,6,True)
def F6b(y): return Fk(y,6,False)
def grow(p,v,lam,fwd,niter,tol=0.02,maxpts=6000):
    fn=F6f if fwd else F6b
    g=lam*lam if lam<0 else lam
    out=[]
    for sgn in [1,-1]:
        d=1e-6
        ts=d*np.exp(np.linspace(0,np.log(abs(g)),40))
        pre=np.array([p+sgn*t*v for t in ts]); img=np.array(mapmany(fn if lam>0 else (lambda q: fn(fn(q))) ,pre)) if False else None
        cur=pre; allc=[cur]
        steps = niter if lam>0 else 2*niter
        for it in range(steps):
            new=np.array(mapmany(fn,cur))
            # refine: insert preimage midpoints where image gaps > tol
            for rep in range(8):
                gaps=np.linalg.norm(np.diff(new,axis=0),axis=1)
                bad=np.where((gaps>tol)&np.isfinite(gaps))[0]
                if len(bad)==0 or len(cur)>maxpts: break
                mids=(cur[bad]+cur[bad+1])/2
                mimg=np.array(mapmany(fn,mids))
                cur=np.insert(cur,bad+1,mids,axis=0); new=np.insert(new,bad+1,mimg,axis=0)
            cur=new[np.all(np.isfinite(new),axis=1)]
            allc.append(cur)
        out.append(allc)
    return out
if __name__=="__main__":
    POOL=Pool(16)
    p=np.array([float(sys.argv[1]),float(sys.argv[2])]); nu=int(sys.argv[3]); ns=int(sys.argv[4]); tag=sys.argv[5]
    z,J=PJ(p,6,m); ev,V=np.linalg.eig(J); ev=np.real(ev); V=np.real(V)
    iu=np.argmax(abs(ev)); is_=1-iu
    U=grow(p,V[:,iu],ev[iu],True,nu); S=grow(p,V[:,is_],1/ev[is_],False,ns)
    pickle.dump((p,ev,V,U,S),open(f"man_{tag}.pkl","wb"))
    plt.figure(figsize=(10,8))
    for side in U:
        for c in side: plt.plot(c[:,0],c[:,1],'r-',lw=0.6)
    for side in S:
        for c in side: plt.plot(c[:,0],c[:,1],'b-',lw=0.6)
    attr=np.load("attr.npy"); plt.plot(attr[:,0],attr[:,1],'k.',ms=2); plt.plot(p[0],p[1],'go')
    plt.xlim(-10,3); plt.ylim(-5,5); plt.savefig(f"man_{tag}.png",dpi=90)
    print("eig",ev, "Upts",[sum(len(c) for c in s) for s in U],"Spts",[sum(len(c) for c in s) for s in S])
