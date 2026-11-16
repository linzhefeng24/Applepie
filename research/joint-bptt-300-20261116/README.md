# Direct joint-trajectory BPTT: completion and300-update training

User request: complete differentiable physical/neural code, regularize changes from starting parameters, compare coefficients, and perform300 actual optimizer updates. Old u-fit updates do not count. Completion is false until300 joint-loss updates are saved and verified remotely.

This experiment keeps the original AB full initial state, native body/contacts/friction/adhesion, auxiliary controls and0.4s physical time. Existing neural-output timing convention is retained. Training starts at the pre-BPTT manually tuned UnifiedFlyModel858d1818 baseline; regularization and the±10% hard fractional bounds anchor to that same manual bank. Epoch123/1000 are comparisons only. This follows the user correction; zero updates had run when corrected. Shared types retain shared factors.

Implementation in progress: `patch_mjx.py` extends version-locked MJX3.3.2 with native BODY contact-gap adhesion and a masked scan with unchanged contact-solver stopping conditions and iteration budget. Original model has mixed condim1/3 elliptic contacts; the compatibility guard is removed only to exercise existing frictionless+elliptic paths, pending force/state/gradient parity tests. No claim of parity or completed training yet. Changes apply only to isolated `/workspace/physics-bptt-env`; original native AB and existing neural environments remain unchanged.

Upstream smooth source is copied unmodified from https://raw.githubusercontent.com/google-deepmind/mujoco/3.3.2/mjx/mujoco/mjx/_src/smooth.py ; its Apache2 license is at ../physics-bptt-20261116/source/LICENSE. Other original source files and hashes are preserved there. Every patch records before/after SHA256. All model-forward and gradient validations must pass before counting training updates.

Initial compatibility failure retained: unmodified MJX rejects BODY; after first BODY prototype conversion failed on condim1 with elliptic cones. Inspection found AB geom gap0.0005, so the first draft's zero-gap assumption was corrected before any physical training. No updates have run.

The contact buffer now stores64 candidate contacts per condim, ranked by distance minus native margin (including contact gap), rather than thousands of provably inactive rows. Adapter must abort if the retained valid-contact count reaches capacity; no training update may be counted after overflow. Native physical model/contact parameters are unchanged. The Newton Hessian is computed algebraically as Jᵀdiag(D*active)J plus cone block contributions, avoiding a dense nefc-by-nefc temporary. Capacity and parity must be validated before training.

Parameter-anchor correction: group raw=0 represents exactly the original manually tuned parameter bank. No fitted checkpoint parameters enter the starting point, drift penalty or hard bounds. Full model hash remains858d1818b8d8394c95bb62a6ce60474cb534a83b94265ef8615e367c110d262c.

Current derivative backend uses implicit differentiation of stationary contact equations, with the original native-budget/tolerance forward stopping loop unchanged. The initial masked-scan performance test was abandoned after an unresolved whole-step stall; no updates counted. JAX0.8 also stalled at isolated kinematics. The separate JAX0.5.3 environment executes the entire stage sequence; original environments remain intact. First force audit revealed spurious distant head/wing ellipsoid overlaps from upstream approximate SDFs. A conservative bounding-sphere rejection (which cannot reject any real contact) is being validated; initial failing force/state reports are retained. Training is gated on physical and derivative parity.

Neural training code is now expanded to all3988 cells and all485045 actual signed edges, using CSR sparse products. It no longer replays a frozen outer network. This full-network implementation still needs baseline spike/gradient verification before training. The original207 shared variables remain, with manual-bank raw0 as both initialization and drift anchor. All300 main updates must each cover the continuous0.4s joint trajectory.

Full-network manual-bank forward parity passed for1400ms: all12755 spike counts match the native baseline elementwise, with all3988 cells/485045 edges simulated (no boundary replay). Raw group factors start at0.

Physical forward now uses original native MuJoCo callbacks with complete carried state and native contact primals; backward differentiates explicit muscle/rigid/contact equations at those native witnesses. Analytic convex active-feature geometry KKT replaces upstream approximate SDF derivatives. Initial gradient check is not yet valid (nonfinite gradient) and source inspection identified a missing native post-solver NoSlip stage: original AB runs5 sweeps, MJX omits them. Native warmstart stores acceleration before NoSlip, so confusing it with final acceleration caused the observed2342.8 acceleration discrepancy. A faithful differentiable NoSlip port is required before any update. Failures remain preserved; main updates still0/300.

## Current verified state

The manual R2 bank is the only initialization and regularization anchor. Epoch123/1000 archives are comparison metadata only; all207 shared factors start at multiplier1. No main optimizer updates have run (0/300).

The native NoSlip5-sweep stage and native inertia-box fluid terms are now reproduced in the white-box backward equations. At the audited initial step, muscle/actuator/constraint/passive-force errors are respectively1.25e-14,3.73e-16,2.31e-15,8.68e-19; acceleration error3.86e-10. These are numerical parity tests, not training results.

The inactive zero-width muscle-smoothing branch is protected against0/0 in reverse mode without changing its forward formula. The native-forward10-step (1ms) directional gradient check passes: maximum relative error0.002648 across three directions and two perturbation sizes. Full1400ms neural forward parity also passes. The longer200-step (20ms) physics gradient check is still pending; training remains gated. Current environment is isolated physics-bptt-053-env (JAX0.5.3); original AB model remains unchanged.

## Approximate-adjoint training acceptance

The strict20ms random directional test FAILED (maximum relative error13.28%). Reducing finite perturbations does not remove the discrepancy; this failure is preserved in whitebox-validation-200.json and direction-refinement-200.json. It must not be presented as a strict pass.

The practical training acceptance instead requires exact complete AB forward, exact full neural baseline, finite derivatives, force parity along the trajectory, the passed1ms strict test, and actual native loss descent along the negative physical gradient. All four20ms descent trials pass; actual/predicted improvement ratios0.99958,0.99894,0.99761,0.99296. This justifies exploratory approximate-gradient optimization, not a claim of exact differentiability of native contact/stopping decisions or validated400ms adjoint accuracy. Source hashes and limitations are in validation-report.json.

The manual bank is also verified by a runtime SHA256 check on the complete3988-cell parameter array. Configuration no longer contains misleading old123/1000 training-window or optimizer settings. A new workflow trains only this manual-anchor joint objective, saves and freshly re-downloads every update checkpoint, and continues automatically until300 actual main updates. Five updates for each of three coefficient trials are additional and do not count toward300. No main updates completed yet.

## Durable execution

Training source1847a4d706b8e73c09c9c25c6e92b4d74fdd3de5 is running in GitHub Actions run43848029276. Initial manual-anchor optimizer checkpoint was uploaded, downloaded and SHA256 verified; progress.json is independently readable on remote main. At this checkpoint the first coefficient trial has0 updates and main0/300: dispatch is not evidence of an optimizer update.

A separate completion workflow is gated on the remotely saved main count reaching300. It will evaluate manual/best/last neural outputs on identical free native AB dynamics, render a four-panel video including direct archived A, and publish a self-contained offline replay bundle with source, original model, optimizer and all parameter banks. It then commits fresh-download-verified manifests and metrics. This completion renderer is implemented and syntax checked, not yet executed; no completed-training video is claimed.

Independent full1400ms neural surrogate-adjoint diagnostic passed: finite207-parameter gradient, all23 shared groups nonzero, norm7005.38; runtime450.2s including first compilation. Objective was mean neural u squared solely to check derivative plumbing, not the joint-training loss. No optimizer update occurred and none is counted. This confirms the neural surrogate reverse path; it does not validate physical gradients or hard-spike finite differences. Full joint optimization remains in the independent GitHub run.
