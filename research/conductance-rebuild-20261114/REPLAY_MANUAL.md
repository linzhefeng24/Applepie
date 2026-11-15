# Replay the manual neural experiments

This directory contains newly implemented/re-run research. Historical Monday
chat numbers (8/8 perturbations,0.446 trajectory error) are not inherited as
results of this implementation. The original scoped audit remains separate.

Use Python3.12 with `pip install -r requirements.txt`. Source re-extraction also
requires `pip install -r source-data-requirements.txt`. Replays use the tracked
extracted graphs; they do not require downloading the entire original dataset.

From this directory:

```bash
OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=1 python -m pytest test_receptors.py test_grouped.py test_temporal_protocol.py test_scientific_checks.py -q
OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=1 python pulse_neural_panel.py P9+FG configs/manual-neural-bank-r8.json unified-r8 results/mcns-unified
OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=1 python pulse_neural_panel.py BRK2s configs/manual-neural-bank-r8.json unified-r8 results/mcns-unified
python inspect_pulse_panel.py P9+FG unified-r8
python report_manual_progress.py unified-r8
```

Use a different output tag in place of `unified-r8` to preserve the original
saved output. The runner otherwise writes that condition's output files anew.
Every condition records actual input body IDs, parameter bank hash, full runtime
parameters, graph and code hashes, software versions, source activity, target
voltages, calcium, synaptic conductance and currents. Recent runs also record
the exact command and effective runtime-parameter hash. Simulations are
deterministic; there is no stochastic seed or loss-selected solution.

All18 r8 conditions: BPN, BPN+FG, BPN+BB, BPN+BRK, P9, P9+FG, P9+BB, P9+BRK,
MDN, MDN+FG, MDN+BB, MDN+BRK, PFL3L, PFL3R, PFL2, PFL3L+PFL2, control, BRK2s.
Source input is200–1500ms; the later halt pulse is450–950ms. BRK2s instead uses
2000–4000ms in a7001ms simulation. These are engineering current stimuli, not
calibrated optical dose. MF calcium recordings used20s stimulation, so short
MDN probes only address response direction, not their full experimental trace.

For raw inputs, see `data/public-input-release-verified.json`. The draft GitHub
Release `public-neural-inputs-20261115` contains all four hash-pinned public raw
sources (606774958 bytes). Draft access requires repository authorization.
`research/public-input-archive` and its workflow document download/verification.

This model is reduced two-compartment HH/Ca/SK dynamics with unmeasured active
channel and synapse priors. Adult MN leak calibration does not establish adult
cell-specific active kinetics. Glutamate-inhibitory sign is a receptor hypothesis;
monoaminergic signalling and presynaptic sensory gating remain unimplemented.
