import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
L=[l.split() for l in open("../proof/design_chain.txt") if l.strip() and not l.startswith("#")]
ch={t[1]:np.array(list(map(float,t[3:9]))) for t in L if t[0]=="chart"}
st={t[1]:tuple(map(float,t[2:5])) for t in L if t[0]=="set"}
attr=np.load("attr.npy"); hom=np.load("homo_orbit.npy")
fig,ax=plt.subplots(1,2,figsize=(13,5.5))
for a,zoom in zip(ax,[False,True]):
    a.plot(hom[18:37,0],hom[18:37,1],'o',mfc='none',color='0.5',ms=5,zorder=1,label='homoclinic orbit x18..x36')
    a.plot(attr[:,0],attr[:,1],'k.',ms=3,label='attractor (period 16)',zorder=2)
    for nm,(c,w,b) in st.items():
        Q,U,S=ch[nm][:2],ch[nm][2:4],ch[nm][4:6]
        cs=np.array([Q+(c+su*w)*U+sb*b*S for su,sb in [(-1,-1),(1,-1),(1,1),(-1,1),(-1,-1)]])
        a.fill(cs[:,0],cs[:,1],color='tab:red' if nm[0]=='A' else 'tab:blue',alpha=0.6,zorder=3)
    a.set_xlabel('y = ln I'); a.set_ylabel('W')
    if zoom: a.set_xlim(-5.3,-4.8); a.set_ylim(1.05,1.45); a.set_title('zoom near A0 (red: period-6 boxes, blue: chain)')
    else: a.set_title('m = 0.0608: 24 boxes of the covering chain')
ax[0].legend(loc='lower left',fontsize=8)
plt.tight_layout(); plt.savefig("../figures/proof_chain.png",dpi=110)
