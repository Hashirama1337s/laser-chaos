import numpy as np
from lasermap import *
from scipy.integrate import solve_ivp
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,5,figsize=(20,4))
for a,m in zip(ax,[0.044,0.048,0.0568,0.0584,0.0608]):
    y=np.array([0.,0.])
    for i in range(400): y=P(y,m=m)
    sol=solve_ivp(f,(0,60*T),y,method="DOP853",rtol=1e-10,atol=1e-12,args=(m,),dense_output=True)
    t=np.linspace(0,60*T,30000); Y=sol.sol(t)
    a.plot(np.exp(Y[0]),Y[1],lw=0.3); a.set_title(f"m={m}"); a.set_xlim(0,6); a.set_ylim(-3,3)
    # period estimate
    pts=[]; z=y
    for k in range(64): z=P(z,m=m); pts.append(z)
    pts=np.array(pts); d=np.linalg.norm(pts-pts[0],axis=1)
    print(m, "Imax %.2f W[%.2f %.2f]"%(np.exp(Y[0]).max(),Y[1].min(),Y[1].max()), "returns near start at k=",[k for k in range(1,64) if d[k]<1e-3][:4])
plt.savefig("../figures/model_check_fig14.png",dpi=80)
