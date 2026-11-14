# Latest completed motion stage

These are NEW simulations with shared annotated-type parameters, not Monday recovered artifacts.

The first9-trial activation/torque fit did not produce repeated knee movement under its declared criterion. A separate15-trial developmental physical-motion search tested causal NMJ filters and constant gains; all time dependence comes from actual HH spikes. Actual free-body runs retain native muscle equations and contact, disable adhesion, and use no applied rescue forces or resets.

Accepted short-window readout:20ms causal spike filter, constant per-channel gains from the training split, gain scale1. Shared Ti-flexor gating-rate factor0.85; Ti-extensor gating restored to1 rather than treating one residual neuron separately. One-second continuation uses new continuous neural output, not repetition of a0.4s pattern.

Right foreleg steady-window(0.4–1.0s) range:14.145deg,4 peaks/5 troughs. Matched constant-mean input range0.001799deg, no peaks/troughs. E2-lesion range0.048309deg, no peaks/troughs. Minimum body-up-z0.858 with dynamic input; no six-leg walking claim. Fine neural-step0.00625ms yields RF18.250deg, also4 peaks/5 troughs; mean0.002770deg and E2-lesion0.036216deg. Fine body-up minimum0.812. Qualitative motion survives refinement; amplitude is not tightly timestep-converged.

OnlyRF satisfies repeated-motion criteria after0.4s; other five knees do not. Same muscle-type MN parameters are shared across sides. Muscle readout gains are channel-specific fitted coefficients, so asymmetry is not asserted to arise from connectome alone.

Remaining issue: fine-step1454-cell induced graph still has one RH Ti-extensor MN with periodic activity after T1 E2 lesion. The new shared parameters preserve E2 cancellation in the full4604-cell T1 graph at the tested0.025ms step. These scopes must not be mixed. adaptation_probe.py tests one bounded shared-SK hypothesis; no positive result is assumed in this checkpoint.
