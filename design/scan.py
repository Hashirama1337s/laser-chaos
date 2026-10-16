import numpy as np
from lasermap import *
from multiprocessing import Pool
def run(y0):
    y=np.array(y0,float)
    for i in range(250): y=P(y)
    pts=[]
    for i in range(60): y=P(y); pts.append(y.copy())
    pts=np.array(pts)
    v=np.array([1.0,0.3]); L=0
    for i in range(150):
        z,J=PJ(y); v=J@v; n=np.linalg.norm(v); L+=np.log(n); v/=n; y=z
    I=np.exp(pts[:,0])
    return y0, L/150, I.max(), pts[:,1].min(), pts[:,1].max()
if __name__=="__main__":
    ics=[(np.log(I0),W0) for I0 in [0.05,0.3,1,2,4] for W0 in [-2.5,-1,0,1,2.5]]
    with Pool(12) as p:
        for r in p.map(run,ics): print("IC I=%.2f W=%.1f  lyap=%.4f  Imax=%.2f W[%.2f,%.2f]"%(np.exp(r[0][0]),r[0][1],r[1],r[2],r[3],r[4]))
