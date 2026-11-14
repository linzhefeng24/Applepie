# Shared cell parameters and asymmetric muscle-driven movement

This is a newly implemented and independently simulated model, not restoration of the missing Monday checkpoint. The minimum single-leg motion goal is supported within the model; six-leg walking is not validated.

The 1454-cell induced MANC graph retains its edges and transmitter signs. Similar annotated types share parameters; the selected neural change is Ti-flexor MN gate speed ×0.85. No individual cell is muted to manufacture the result. Type annotations do not establish identical adult physiology; verified subtypes are separated when available. Parameter bounds are engineering priors, not measured confidence intervals.

Spikes drive a causal 20 ms filter, fixed nonnegative fitted channel gains, and the archived AB muscle activation law. Gains were fitted to the first 0.24 s of the old A trajectory. Thus channel-specific gains contribute to the asymmetry; it cannot be attributed exclusively to the connectome. There is no imposed periodic activation trace or sinusoidal joint command.

## Actual physical results

Continuous neural time 400–1400 ms drives a 1 s free-body simulation without repeating the short program. Adhesion is off, there are no rescue forces or intermediate resets. Archived head/abdomen controls are used for 0.4 s and then held at their last value. Native muscle activation matches decoded activation exactly in the saved runs.

The analysis window is body time 0.4–1.0 s. Repetition requires ≥5° range, ≥2 peaks and ≥2 troughs with 2° prominence, and body-up ≥0.8.

| Neural input | RF angle range | Peaks / troughs | Body-up minimum |
|---|---:|---:|---:|
| Selected shared parameters |14.145°|4 / 5|0.858|
| Constant mean input |0.0018°|0 / 0|0.895|
| E2 ablation |0.0483°|0 / 0|0.348|
| Finer neural step (0.00625 ms) |18.250°|4 / 5|0.812|
| Finer mean control |0.0028°|0 / 0|0.885|
| Finer E2 ablation |0.0362°|0 / 0|0.346|

Only RF passes the full motion criterion. Mean controls remain upright without RF cycles, helping distinguish rhythmic actuation from passive drift. E2 controls lose upright posture, so their absence of movement alone is not sufficient proof. Finer-step results preserve the qualitative effect, but the amplitude change means precise numerical convergence has not been established.

## Failed and unresolved tests

Nine initial shared-parameter trials with a reference-torque fitting objective did not yield accepted repeated body motion. A subsequent frozen 15-candidate filter/gain grid identified a physical-motion candidate. Its original extensor modification was removed because E2 ablation left residual activity. All trials remain saved, including failures.

The selected grouped model gives zero periodic MN after E2 ablation in the full T1 graph at the coarse step. The all-leg induced graph at the finer step retains one periodic RH Ti-extensor MN (10462). A further bounded test halving the shared Ti-extensor SK conductance still leaves one residual MN (baseline 42); it is rejected as a solution to that constraint. These outcomes must not be substituted for one another.

Full 130-channel trajectory recovery, six-leg coordinated walking, monotonic drive–frequency response, and the many steering/stopping/feedback observations in brain.json remain incomplete. An evidence entry is not a passed test.

## Files and reproduction

`configs/asymmetry-guarded.json` records the selected neural parameters. `results/asymmetry/` contains raw spikes, fixed readout gains, decoded inputs, actual body states, matched controls, all trial outcomes, and summary.json. The video `asymmetry-vs-mean-slow.mp4` shows the short candidate comparison; it is not the complete 1 s guarded validation. The 1 s guarded runs are shown in asymmetry-validation.png and retained as long-body-guarded*.npz.

Run `finalize_asymmetry.py` to rebuild the report plot from saved physical trajectories. The experiments are implemented in asymmetry_refinement.py, motion_readouts.py, motion_body_grid.py, asymmetry_guard_refine.py, guarded_motion_inputs.py, guarded_fine.py, and long_motion_validation.py. Native body replay requires body-requirements.txt; neural simulation uses requirements.txt. The body helper verifies the archived bundle hash before loading it. Inputs, software versions, and earlier baseline protocols remain documented in README.md and the data manifests.
