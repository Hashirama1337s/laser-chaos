import numpy as np, json
from lasermap import *
p0=np.array([-5.132864839,1.365421594])
y,res,J6=newton(p0,6); print("res",res)
orb=[y]
for i in range(5): orb.append(P(orb[-1]))
Js=[PJ(q)[1] for q in orb]
# unstable dir at p0 of P^6
ev,V=np.linalg.eig(J6); ev=np.real(ev); V=np.real(V); iu=np.argmax(abs(ev))
eu=[V[:,iu]/np.linalg.norm(V[:,iu])]; lam=[]
for i in range(6):
    t=Js[i]@eu[-1]; lam.append(np.linalg.norm(t)); eu.append(t/np.linalg.norm(t))
# stable dir at p0
es=[None]*7; es[6]=V[:,1-iu]/np.linalg.norm(V[:,1-iu]); mu=[0]*6
for i in (5,4,3,2,1,0):
    t=np.linalg.solve(Js[i],es[i+1]); mu[i]=1/np.linalg.norm(t); es[i]=t/np.linalg.norm(t)
for i in range(6):
    ang=np.degrees(np.arccos(abs(eu[i]@es[i])))
    print(i,"p=(%.9f,%.9f)"%tuple(orb[i]),"I=%.4f"%np.exp(orb[i][0]),"angle %.1f"%ang,"stretch %.3f contr %.4f"%(lam[i],mu[i]))
print("prod stretch",np.prod(lam),"prod contr",np.prod(mu), "eig",ev, "eu6 vs eu0",eu[6]@eu[0])
json.dump({"orb":[list(q) for q in orb],"eu":[list(e) for e in eu[:6]],"es":[list(e) for e in es[:6]],"lam":lam,"mu":mu,"ev":list(ev)},open("orb6.json","w"),indent=1)
