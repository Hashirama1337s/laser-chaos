import numpy as np, json, sys
from lasermap import *
from multiprocessing import Pool
d=json.load(open("orb6.json")); orb=[np.array(q) for q in d["orb"]]; eu=[np.array(e) for e in d["eu"]]; es=[np.array(e) for e in d["es"]]
Minv=[np.linalg.inv(np.column_stack([eu[i],es[i]])) for i in range(6)]
NMAX=60
def track(a):
    sgn,u0=a
    x=orb[0]+sgn*u0*eu[0]; out=[]
    for n in range(1,NMAX+1):
        x=P(x)
        if not (-10<x[0]<3 and -5<x[1]<5): out.append((np.nan,np.nan)); break
        i=n%6; out.append(tuple(Minv[i]@(x-orb[i])))
    out+= [(np.nan,np.nan)]*(NMAX-len(out))
    return out
if __name__=="__main__":
    delta=1e-5; lam=d["ev"][0]
    us=delta*np.exp(np.linspace(0,np.log(lam),3000))
    jobs=[(s,u) for s in (1,-1) for u in us]
    with Pool(16) as p: R=np.array(p.map(track,jobs,chunksize=20))
    np.save("shoot.npy",R); np.save("shoot_jobs.npy",np.array(jobs))
    # homoclinic candidates: at step n, a_n changes sign between neighbours while |a|,|b| small
    for si,s in enumerate((1,-1)):
        A=R[si*3000:(si+1)*3000]
        for n in range(12,NMAX):
            a=A[:,n-1,0]; b=A[:,n-1,1]
            idx=np.where((np.sign(a[:-1])!=np.sign(a[1:]))&(np.abs(b[:-1])<0.05)&(np.abs(a[:-1])<0.05))[0]
            if len(idx): print("sgn",s,"n",n,"roots at u0=",["%.6e"%us[k] for k in idx[:6]], "count",len(idx))
