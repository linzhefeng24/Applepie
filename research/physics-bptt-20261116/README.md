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

Compatibility/source audit completed. Native-adjoint and muscle analytic derivative checks pending. No full joint-trajectory neural training,1000-update run, or improved gait has been claimed. The local finite-difference adjoint is a correctness reference and likely too expensive for1000 full-length updates.

Installation was isolated from the existing AB/neural environments. An unpinned MJX installation initially resolved MuJoCo4.0.1 and left incompatible plugins; those were removed and MuJoCo3.3.2/JAX0.8.0 were explicitly reinstalled. No model experiment used the incompatible installation.
