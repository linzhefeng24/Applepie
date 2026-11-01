def objective(w,r,p):
    import numpy as np
    mu=r.mean(axis=0);cov=np.atleast_2d(np.cov(r,rowvar=False))
    return float(-w@mu*252+p['riskAversion']*(w@cov@w)*252/2)
