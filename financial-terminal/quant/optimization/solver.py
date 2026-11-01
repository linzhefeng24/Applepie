import numpy as np
from scipy.optimize import minimize
from optimization.projection import capped_simplex
from optimization.objective import objective
def optimize(r,model,p):
    n=r.shape[1];cap=float(p['maxWeight']);equal=np.ones(n)/n
    if model=='equal': return dict(weights=equal.tolist(),converged=True,message='解析等权解',iterations=0,objective=0.)
    rng=np.random.default_rng(42)
    starts=[equal]+[capped_simplex(rng.dirichlet(np.ones(n)),cap) for _ in range(2)]
    solutions=[minimize(objective,w,args=(r,model,p),method='SLSQP',bounds=[(0,cap)]*n,constraints=[dict(type='eq',fun=lambda x: x.sum()-1)],options=dict(maxiter=250,ftol=1e-10)) for w in starts]
    feasible=[s for s in solutions if np.isfinite(s.fun) and abs(s.x.sum()-1)<1e-6 and s.x.min()>=-1e-7 and s.x.max()<=cap+1e-7]
    good=[s for s in feasible if s.success]
    if not good:
        return dict(weights=equal.tolist(),converged=False,message='求解未收敛，回退等权持仓',iterations=sum(int(s.nit) for s in solutions),objective=float(objective(equal,r,model,p)))
    best=min(good,key=lambda s:s.fun)
    weights=capped_simplex(best.x,cap)
    return dict(weights=weights.tolist(),converged=True,message=str(best.message),iterations=int(best.nit),objective=float(best.fun))
