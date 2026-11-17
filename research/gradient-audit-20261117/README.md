# Independent gradient audit

Audits the physical-range restart source and frozen best16 replay. No running training state or numerical source is edited. `algebra.json` is independently rerun, not inherited validation. `audit.py physics` evaluates the full400ms native objective at best16, computes its physical VJP, and compares feasible interior-control directions at multiple perturbation sizes. The full400ms check completed; see physics.json. The strict5% gate failed, including a sign disagreement at one finite perturbation. precision.py tests smaller perturbations using the saved physical VJP. A strict failure must remain reported as failure.

Confirmed: smooth positive parameter mapping and manual-centered regularization agree with finite differences. The state cotangent clip is a nonlinear custom backward and violates VJP additivity. Hard spikes use an intentional surrogate, output saturation has a straight-through estimator, and200ms detach boundaries omit earlier temporal paths. Thus current full-network update is a heuristic truncated surrogate direction, not the exact derivative of the hard forward scalar objective. Finite/nonzero gradients or historical improvement alone cannot establish gradient correctness.

The physical custom root also ignores native solver stopping and contact topology decisions. Prior20ms strict random-direction checks reached13.3% error; this audit adds full400ms evidence at the actual best trajectory instead of relabeling those results passed. The free-body root trajectory/support height is not penalized by the present joint-angle-only objective.

Commands (isolated JAX0.5.3, MuJoCo3.3.2 environment):

```
python audit.py algebra
python ../joint-bptt-physical-bounds-20261117/patch_mjx.py
python audit.py physics --replay /path/to/Joint_BestUpdate16_Replay.zip
```
