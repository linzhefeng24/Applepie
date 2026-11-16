# Direct joint-trajectory BPTT: completion and300-update training

User request: complete differentiable physical/neural code, regularize changes from starting parameters, compare coefficients, and perform300 actual optimizer updates. Old u-fit updates do not count. Completion is false until300 joint-loss updates are saved and verified remotely.

This experiment keeps the original AB full initial state, native body/contacts/friction/adhesion, auxiliary controls and0.4s physical time. Existing neural-output timing convention is retained. Starting neural checkpoint will be the already validated epoch123; regularization anchors to that checkpoint rather than to the old untrained baseline. Shared types retain shared factors.

Implementation in progress: `patch_mjx.py` extends version-locked MJX3.3.2 with native BODY contact-gap adhesion and a masked scan with unchanged contact-solver stopping conditions and iteration budget. Original model has mixed condim1/3 elliptic contacts; the compatibility guard is removed only to exercise existing frictionless+elliptic paths, pending force/state/gradient parity tests. No claim of parity or completed training yet. Changes apply only to isolated `/workspace/physics-bptt-env`; original native AB and existing neural environments remain unchanged.

Upstream smooth source is copied unmodified from https://raw.githubusercontent.com/google-deepmind/mujoco/3.3.2/mjx/mujoco/mjx/_src/smooth.py ; its Apache2 license is at ../physics-bptt-20261116/source/LICENSE. Other original source files and hashes are preserved there. Every patch records before/after SHA256. All model-forward and gradient validations must pass before counting training updates.

Initial compatibility failure retained: unmodified MJX rejects BODY; after first BODY prototype conversion failed on condim1 with elliptic cones. Inspection found AB geom gap0.0005, so the first draft's zero-gap assumption was corrected before any physical training. No updates have run.
