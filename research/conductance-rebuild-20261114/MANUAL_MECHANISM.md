# Manual mechanism inspection, not endpoint-loss selection

The user clarified: unknown parameters should be changed when physiology and
traces justify it; similar cells should preferably share parameters. Muscle
u(t) needs only approximate trends and asymmetric rhythmic recruitment. A shared
time rescaling is allowed. Actual walking and precise trajectory matching are
not acceptance requirements. Avoid globally synchronous leg recruitment, but
inspect propagation along the real circuit rather than optimizing a sparse
terminal penalty. Measured neuronal phenomena take priority.

The attempted joint-neural-fit loss ranking was stopped before completion.
Completed candidates are retained as exploratory diagnostics and are not
adopted. Its script now refuses normal execution. The newly downloaded BON1
source data remain useful for direct visual inspection. The published source
curve has 43 samples at6Hz from-2 to5s; stimulation is0–2s. The14MB unrelated
MOESM18 source is cached outside git and unused; original URL/hash are retained.

New HH instrumentation records chosen cells' soma/axon voltage, intracellular
Ca, excitatory and inhibitory conductances/currents, axial current and external
current. Optional time-dependent stimuli permit real pulse onset/offset
experiments. Old tonic protocols are tested for identical spike/voltage output;
record_time_ms and valid_record_count exclude trailing unused record padding.
No HH membrane equation is replaced by a phase oscillator or prescribed output.

A structural problem was identified in the earlier1454-cell muscle-readout
subgraph:19 of26 bilateral/segmental rhythm/DNg100 nodes were absent. This is a
boundary limitation, not proof that intrinsic parameters are the cause of
synchrony. A new2553-cell context retains all26 rhythm/DN nodes,329 candidate
muscle-linked MNs and direct/two-hop routes through actual source-matrix cells.
No inter-leg edges or phases are fabricated. Direct core→MN and expanded
context runs are compared, then manual parameter changes are made one at a
time based on currents and voltage. This is still a subgraph, not all VNC.

For each run: inspect DN→E1/E2→I1/I2→premotor→MN→candidate u traces per leg;
identify absent input, failure to spike, tonic saturation or excessive
inhibition; record the mechanism hypothesis, the exact shared parameter change,
and the complete response. Negative results are preserved. Plots and descriptive
statistics assist inspection; they do not automatically select a model.

## Observations and hand interventions

1. Direct core→MN context leaves Ti-flexor pools largely silent. Adding real
premotor paths recruits all six legs' flexor pools. The direct-vs-expanded
comparison is structural diagnosis, not a claim of a six-leg gait.
2. Expanded baseline has different leg rhythms, but right extensor pools are
overdriven. Example RH extensor10462:65.8Hz, soma mean-39.0mV, mean excitatory
current176.6pA and inhibitory current-109.0pA. This is sustained depolarization,
not a lack of structural reachability.
3. Increasing background/premotor inhibitory gain0.03→0.1 does not solve the
specific overdriven extensor and silences a previously active LH-flexor example.
Do not adopt that global change.
4. Halving Ti-extensor excitatory gain reduces RH overdrive but silences the
left front/middle extensor examples. Do not adopt a blanket extensor reduction.
These failed adjustments locate heterogeneity rather than justify changing
muscle targets or scoring only a terminal point. Muscle activation is retained
as a rough downstream readout, not a walking requirement.

The full public MaleCNS v1.0 annotation, neurotransmitter and significant-weight
sources have been downloaded again into an external cache. Source URLs, byte
counts and hashes are recorded; these large raw caches are not yet uploaded as
Release assets, and are not claimed as GitHub-backed copies. Versioned extracted
circuits are tracked. Steering extraction uses actual PFL3/PFL2→DNa03/LAL010→
DNa02 pathways and inhibitory relays; functional PFL output side is inferred
from its direct projection weights, not soma side. Unknown modulatory effects
are kept as a stated missing mechanism, not represented as fast excitation.
