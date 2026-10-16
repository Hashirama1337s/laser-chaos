import numpy as np, json
from lasermap import *
d=json.load(open("orb6.json")); orb=[np.array(q) for q in d["orb"]]; eu=[np.array(e) for e in d["eu"]]; es=[np.array(e) for e in d["es"]]
Minv=[np.linalg.inv(np.column_stack([eu[i],es[i]])) for i in range(6)]
N=38
def aN(u0):
    x=orb[0]-u0*eu[0]
    for n in range(N): x=P(x)
    return (Minv[N%6]@(x-orb[N%6]))[0]
lo,hi=2.69e-5,2.712e-5
flo=aN(lo); fhi=aN(hi); print(flo,fhi)
for it in range(45):
    mid=(lo+hi)/2; fm=aN(mid)
    if np.sign(fm)==np.sign(flo): lo,flo=mid,fm
    else: hi,fhi=mid,fm
u0=(lo+hi)/2; print("u0*",repr(u0))
x=orb[0]-u0*eu[0]; xs=[x]
for n in range(46): xs.append(P(xs[-1]))
for n,x in enumerate(xs):
    a,b=Minv[n%6]@(x-orb[n%6]); print(n,n%6,"x=(%.6f,%.6f)"%tuple(x),"a=%+.3e b=%+.3e"%(a,b))
np.save("homo_orbit.npy",np.array(xs)); json.dump({"u0":u0},open("homo.json","w"))
