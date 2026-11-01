def objective(w,r,p):
    import numpy as np
    cov=np.atleast_2d(np.cov(r,rowvar=False))
    return float(w@cov@w*252)
