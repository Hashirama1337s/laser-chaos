import numpy as np, pickle, sys
p,ev,V,U,S=pickle.load(open(sys.argv[1],"rb"))
def segs(sides):
    L=[]
    for si,side in enumerate(sides):
        for it,c in enumerate(side):
            for j in range(len(c)-1): L.append((c[j],c[j+1],si,it,j))
    return L
def inter(a,b,c,d):
    r=b-a; s=d-c; den=r[0]*s[1]-r[1]*s[0]
    if abs(den)<1e-18: return None
    q=c-a; t=(q[0]*s[1]-q[1]*s[0])/den; u=(q[0]*r[1]-q[1]*r[0])/den
    if 0<=t<=1 and 0<=u<=1:
        ang=abs(den)/(np.linalg.norm(r)*np.linalg.norm(s)); return a+t*r, ang
    return None
SU=segs(U); SS=segs(S)
# drop segments very close to p (local manifolds meet at p)
A=np.array([[*a,*b] for a,b,*_ in SU]); B=np.array([[*a,*b] for a,b,*_ in SS])
res=[]
for i,(a,b,si,it,j) in enumerate(SU):
    lo=np.minimum(a,b); hi=np.maximum(a,b)
    mask=(np.minimum(B[:,0],B[:,2])<=hi[0])&(np.maximum(B[:,0],B[:,2])>=lo[0])&(np.minimum(B[:,1],B[:,3])<=hi[1])&(np.maximum(B[:,1],B[:,3])>=lo[1])
    for k in np.where(mask)[0]:
        c,d,sj,jt,jj=SS[k]
        r=inter(a,b,c,d)
        if r and np.linalg.norm(r[0]-p)>1e-3: res.append((r[0],r[1],si,it,sj,jt))
seen=[]
for x,ang,si,it,sj,jt in res:
    if any(np.linalg.norm(x-y)<1e-4 for y in seen): continue
    seen.append(x); print("x=(%.5f,%.5f) sin(angle)=%.3f  U side %d iter %d | S side %d iter %d"%(x[0],x[1],ang,si,it,sj,jt))
print(len(seen),"distinct crossings")
