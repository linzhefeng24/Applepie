import numpy as np
def capped_simplex(values, cap):
    """Euclidean projection, avoiding infeasible optimizer starting points."""
    v=np.asarray(values); lo=float(v.min()-cap);hi=float(v.max())
    for _ in range(80):
        mid=(lo+hi)/2
        if np.clip(v-mid,0,cap).sum()>1: lo=mid
        else: hi=mid
    return np.clip(v-(lo+hi)/2,0,cap)
