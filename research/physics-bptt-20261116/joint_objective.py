"""Compose neural BPTT with joint-only physics loss and parameter drift penalty.
The backend must expose a differentiable scalar joint loss; the native reference
backend uses numerical local Jacobians and is NOT the final analytic backend.
This interface has not yet been used to train the full neural parameter set.
"""
import jax.numpy as j

def make_objective(neural_forward_u,physics_joint_loss,clock_indices,reference_raw,
                   relative_bound,regularization_lambda):
 """neural_forward_u(theta) returns the full ms-by-muscle u array.
 Shared group assignment and frozen cells stay in the original neural model.
 Penalize fractional parameter change from the chosen CURRENT checkpoint,
 rather than silently anchoring to the old untrained baseline.
 """
 reference_delta=relative_bound*j.tanh(reference_raw)
 def objective(raw):
  neural_u=neural_forward_u(raw)
  joint_loss=physics_joint_loss(neural_u[clock_indices])
  delta=relative_bound*j.tanh(raw)
  fractional_shift=(delta-reference_delta)/(1+reference_delta)
  penalty=regularization_lambda*j.mean(fractional_shift**2)
  return joint_loss+penalty,{'joint_loss':joint_loss,'parameter_regularization':penalty}
 return objective
