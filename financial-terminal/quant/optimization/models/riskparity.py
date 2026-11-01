def objective(w,r,p):
    import numpy as np
    cov=np.atleast_2d(np.cov(r,rowvar=False));rc=w*(cov@w);variance=float(rc.sum())
    return float(np.sum((rc/max(variance,1e-16)-1/len(w))**2))
