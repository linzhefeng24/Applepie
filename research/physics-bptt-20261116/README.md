# Joint-trajectory BPTT: exact AB physics audit and derivative prototype

The objective is joint trajectory error, with gradients through neural→muscle→body/contact. Target muscle u is no longer the loss. Exact native AB model/initial state/warmstart/all11 auxiliary schedules remain unchanged.

## Source audit

Pinned upstream MuJoCo3.3.2 sources and Apache license are in `source/`, with URLs, SHA256 and byte counts in `source/manifest.json`.

- `engine_forward.c`: native activation derivative at lines343ff; muscle gain408ff and passive force453ff; muscle force to generalized force525ff; smooth acceleration560ff; constraint solve690ff; native Euler812ff.
- `engine_core_smooth.c:1348ff`: BODY adhesion transmission. Its moment is an average of active contact normal Jacobians, negated for adhesion. These six actuators cannot be deleted or replaced by joint torques while claiming the same AB environment.
- MJX `forward.py:120ff,153ff,162ff,218ff` implements native muscle activation/gain/bias and generalized actuator force. `types.py` explicitly excludes BODY transmission; the actual original AB `put_model` fails with BODY unsupported. See `mjx-compatibility.json`. No adhesion-free substitute is claimed to reproduce AB.
- `engine_derivative_fd.c:550ff`: the native transitionFD interface uses2*nv+na physical tangent state, without warmstart as an independent derivative input. The reference prototype therefore augments solver warmstart explicitly. Local finite differences are not an analytical/automatic gradient claim.

The force chain is L=L(q), v_L=J(q)v, adot=muscleDynamics(u,a), F=gain(L,v_L)*a+bias(L), tau_act=J^T F; M(q)qacc=tau_act+tau_passive−bias+tau_contact. Contact/friction solve, adhesion and the actual Euler step are part of the transition. Contact creation/removal and clipping are piecewise differentiable; a gradient can be locally valid and fail across a mode change.

The discrete adjoint is bar_x[t]=ell_x[t]+A[t]^T bar_x[t+1], bar_u[t]=B[t]^T bar_x[t+1]. `physics_adjoint.py` provides the unchanged native forward, full augmented local Jacobian reference backend, and a JAX custom-VJP callback for composition with the existing surrogate HH BPTT. Forward spike derivatives remain surrogates; the original HH training stage is local boundary replay, not full3988-cell end-to-end BPTT.

For a fully automatic white-box backend, port native BODY adhesion and verify its force/Jacobian/contact semantics in MJX, then check native versus MJX states/forces before fitting. Do not silently change contacts, friction, integrator, auxiliary controls or physics timestep for easier gradients.

## Current scope

Compatibility/source audit completed. The1ms native-adjoint directional check passed (maximum relative error2.92e-5); JAX custom-VJP composition matched the native adjoint to2.1e-25 absolute, and a joint-loss-only direction step reduced loss by2.29%. Native muscle force/activation derivative values and force AD derivatives were checked independently; refined muscle force-derivative relative error is below7.7e-6. The20ms strict probe failed: maximum directional relative error25.43%, despite a trial step reducing joint loss by1.77%. This failure is retained and must not be promoted to a validated training backend. No full joint-trajectory neural training,1000-update run, or improved gait has been claimed. The local finite-difference adjoint is a correctness reference and likely too expensive for1000 full-length updates.

Installation was isolated from the existing AB/neural environments. An unpinned MJX installation initially resolved MuJoCo4.0.1 and left incompatible plugins; those were removed and MuJoCo3.3.2/JAX0.8.0 were explicitly reinstalled. No model experiment used the incompatible installation.

## Reproduce derivative probes

Install explicit versions `mujoco==3.3.2 mujoco-mjx==3.3.2 jax==0.8.0 jaxlib==0.8.0 numpy==2.5.4 PyYAML==6.0.3` into a clean isolated environment. Run `python research/physics-bptt-20261116/check_gradients.py --steps 10 --tag refined` or `--steps 200 --tag 20ms --skip-callback`. These probes use interior controls derived from A to avoid claiming a unique gradient at clipping boundaries. They do not optimize saved checkpoint neural parameters. Seed42, exact input/target arrays, versions, source hashes, timing and all directional results are saved. The JAX bridge can be composed as `loss(neural_forward(theta)[clock_indices]) + regularization(theta)`; gradients then accumulate through the declared clock gather and existing neural surrogate BPTT. This composition has not yet been run on the full neural parameter set.

MJX3.3.2 also uses a dynamic `jax.lax.while_loop` in its constraint solver (`solver.py:572`), which requires a separately validated reverse-differentiation treatment (such as fixed-budget masked scan preserving stopping semantics, or implicit differentiation of the converged constraints). BODY support alone is not sufficient to claim a verified end-to-end reverse-mode backend.

## Final audit state for this experiment

- `forward-parity.json`: full original A and B,4000 physical steps each, qpos/qvel/all activations/warmstart/time are elementwise identical to native stepping. The augmented reference forward really preserves AB.
- `gradient-report-refined.json`:1ms derivative/component checks pass. `gradient-report-20ms.json` and corresponding exact inputs/gradients preserve the failed20ms probe, exit1 from the gradient assertion.
- `gradient-noise-diagnosis.json`: exact native muscle force formula error0, M*qacc force-balance relative residual7.31e-16. Across tested finite perturbations no contact-pair topology sample changed; this does not exclude friction/active-constraint branch changes. Some solver iteration counts changed, but that alone does not establish the cause. The discrepancy persists at several perturbation scales. Do not attribute it solely to topology or declare an arbitrary larger epsilon fixes it.
- `diagnostic-failure-initial.log` preserves an initial diagnostic interface error: the convenience strict control interface rejects some original auxiliary controls; the diagnostic was corrected to original raw ctrl plus native mj_step, without altering controls.
- `joint_objective.py` exposes the intended joint-only loss plus fractional drift regularization toward a chosen current checkpoint. Existing grouped neural factors stay bounded/shared. The full neural composition has not been trained or validated yet.

The planned fully white-box backend must preserve six adhesion actuator forces and their contact Jacobians, the native muscle/transmission/inertia terms, and handle the contact solver derivative (e.g. validated implicit differentiation of the converged contact equations). The finite-difference adjoint remains a correctness reference, not a substitute claimed to meet that final requirement. Forward time remains continuous; checkpointed reverse memory management must not reset body state between training segments. All current results and failures are indexed in `status.json`.
