import numpy as np, sys
from lasermap import *
from multiprocessing import Pool
m=float(sys.argv[1]) if len(sys.argv)>1 else M
KS=[int(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else [1,2,3,4,5,6]
def inbox(y): return -9<y[0]<2.5 and -4<y[1]<4
def gnewton(y,k):
    y=np.array(y,float)
    for _ in range(25):
        if not inbox(y): return None
        z,J=PJ(y,k,m); F=z-y
        dy=np.linalg.solve(J-np.eye(2),-F)
        if np.linalg.norm(dy)>0.5: dy*=0.5/np.linalg.norm(dy)
        y=y+dy
        if np.linalg.norm(dy)<1e-12: break
    if not inbox(y): return None
    z,J=PJ(y,k,m)
    return (y,np.linalg.norm(z-y),J) if np.linalg.norm(z-y)<1e-9 else None
def job(a):
    k,y0=a
    try:
        r=gnewton(y0,k)
        if r: return (k,tuple(r[0]),tuple(np.linalg.eigvals(r[2])))
    except Exception: pass
    return None
if __name__=="__main__":
    # seeds: transient orbit points from several ICs (bounded, dynamically relevant)
    seeds=[]
    for y0 in [(-3,0),(0,2),(1,-2),(-6,1),(0.5,0)]:
        y=np.array(y0,float)
        for i in range(40): y=P(y,1,m); seeds.append(y.copy())
    seeds=seeds[::2]
    jobs=[(k,s) for k in KS for s in seeds]
    with Pool(16) as p: R=[r for r in p.map(job,jobs,chunksize=4) if r]
    out=[]
    for k,y,ev in R:
        z=np.array(y); per=k
        for d in range(1,k):
            if k%d==0 and np.linalg.norm(P(z,d,m)-z)<1e-7: per=d;break
        if per!=k: continue
        orb=[z]
        for i in range(k-1): orb.append(P(orb[-1],1,m))
        if any(kk==k and min(np.linalg.norm(o-np.array(yy)) for o in orb)<1e-6 for kk,yy,_ in out): continue
        out.append((k,y,ev))
    for k,y,ev in sorted(out):
        ev=np.array(ev); typ="saddle" if (abs(ev)>1).sum()==1 else ("sink" if (abs(ev)<1).all() else "source")
        print("period",k,"s=%.9f W=%.9f"%y,"eig",np.round(ev,5),typ)
