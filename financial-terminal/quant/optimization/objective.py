from optimization.models import minvariance,meanvariance,riskparity,mvsk
OBJECTIVES={'minvariance':minvariance.objective,'meanvariance':meanvariance.objective,'riskparity':riskparity.objective,'mvsk':mvsk.objective}
def objective(w,r,model,p):
    return OBJECTIVES[model](w,r,p)
