def objective(w,r,p):
    import numpy as np
    scale=max(float(r.std(axis=0,ddof=1).mean()),1e-8)
    z=(r@w)/scale;mean=float(z.mean());c=z-mean
    return -mean+p['riskAversion']*np.mean(c**2)/2-p['skewPreference']*np.mean(c**3)/6+p['kurtosisAversion']*np.mean(c**4)/24
