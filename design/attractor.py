import numpy as np, time
from lasermap import *
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
t0=time.time()
y=np.array([0.0,0.0])
for i in range(300): y=P(y)
pts=[]
for i in range(1500):
    y=P(y); pts.append(y.copy())
pts=np.array(pts); np.save("attr.npy",pts)
print("time",time.time()-t0, "s range",pts[:,0].min(),pts[:,0].max(),"W range",pts[:,1].min(),pts[:,1].max())
plt.figure(figsize=(6,5)); plt.plot(pts[:,0],pts[:,1],',k'); plt.xlabel('s=lnI'); plt.ylabel('W'); plt.savefig("attr.png",dpi=120)
# Lyapunov
y=pts[-1]; v=np.array([1.0,0]); L=0
for i in range(400):
    z,J=PJ(y); v=J@v; n=np.linalg.norm(v); L+=np.log(n); v/=n; y=z
print("lyap per period",L/400)
