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

## Steering mechanism and source excitability

A real484-cell MaleCNS path context gives left-output PFL3→left DNa02 excitation
and right DNa02 hyperpolarization; right stimulation reverses the response.
Direct DNa02 mutual inhibition is not imposed. PFL2 coactivation initially
suppresses output because several PFL sources settle below spike threshold.
A20ms restart probe did not establish persistent recovery, so a simple
bistability explanation remains a hypothesis, not a confirmed mechanism.

Hand-changing the shared PFL2/PFL3 axon bias by+5pA (no target-curve fitting)
restores bilateral PFL2 recruitment and directional gain modulation. Under the
same adjusted parameters, left PFL3 alone gives DNa02 L/R22/0Hz, right alone
0/28Hz, bilateral PFL2 alone35/27Hz, and PFL2+left PFL3 gives44/0Hz. The off
control is silent. The coactivation direction is retained at dt0.00625ms,
though individual relay responses differ; full quantitative convergence is not
claimed. These are qualitative neuronal responses, not angular-velocity fits.

The3142-cell same-MaleCNS command context now includes verified type-level FG
(CB0890→GNG458), BB(DNg60), P9(DNp09), Fdg(CB0038→GNG588), MDN and BRK/BON1
candidates plus actual two-hop routes. The published identity XLSX is included.
BPN type1 CL210 remains unresolved and is not replaced by a different subtype.

P9 source activity fails under the initial network prior despite isolated-cell
firing. Raising current160→200pA does not fix it. Hand-reducing K density in
both P9 homologues by10%, then20%, raises steady-window source output from0
to9 then40Hz, but several expected DN outputs remain suppressed. These are
intermediate observations, not a successful stop/forward phenotype. Next manual
comparison halves the shared brain inhibitory conductance and checks both P9
and previously working steering responses before adoption.

The edge traversal was made event-based to allow more manual experiments.
Presynaptic row order and addition order are retained; three independent
continuous-HH protocols give bitwise identical spikes, voltage, Ca, synaptic
currents and conductances against revision6dda175. A first reference-loader
cache failure is retained in event-traversal-cache-failure.log; the loader was
fixed by disabling cache only for the immutable reference implementation.
Fifteen regression checks pass. This is execution acceleration, not a neural
approximation or parameter-selection algorithm.

## Manual checkpoint: shared candidate r4

The source identity table resolves BPN type 1 to the CL210_a family (10 MaleCNS
cells; exact experimental driver coverage remains uncertain). The revised
command context contains 3088 cells and 398481 signed-hypothesis edges. Only the
six publication-linked BRK cells receive BRK stimulation; other AN19A018 cells
are not silently treated as part of that driver.

Manual adjustments restore MDN recruitment of LBL40 and BRK recruitment of
BON1 in this larger context. Source-cell K conductance is reduced by 20%,
cholinergic DN followers share the same reduction and +5 pA axonal bias, and
DNg100/DNg97/DNge053 receive twice the effective excitatory gain. These remain
unmeasured candidate parameters, not identified biological channel densities.
The shared inhibitory prior is 0.006. Complete failed and intermediate runs are
retained beside the candidate; no scalar loss selected this bank.

Under the latest command-only profile BPN recruits DNg100 L/R 26/25 Hz;
adding FG gives 2/2 Hz, while adding BB gives 23/23 Hz. This difference agrees
with the paper's selective FG/BPN versus BB/P9 mechanism; forcing BB to suppress
BPN equally would be an erroneous target. Those DN-level paper coactivation
results include model predictions, distinct from the experimentally measured
behavioral interventions. MDN+FG and MDN+BB retain LBL40 output, but require a
same-profile baseline and pulse/recovery test before comparative claims.

The frozen r4 bank also includes the previously hand-tested PFL source bias.
Combining profiles can change network responses: earlier results are NOT
inherited as joint passes. pulse_neural_panel.py tests a fixed candidate with
command onset, a later halt pulse, and recovery, recording full neuronal traces
and input/code identities. It does not optimize or threshold endpoint losses.

The Feng source supplement identifies MF09=LUL130 and MF14=LUL152. MF14's
T1/T2 excitation versus T3 inhibition is an experimental constraint; an exact
EM identity is still missing. INXXX468 is a family-level LUL130 candidate, not
an established individual-cell identity. Current provisional responses do not
yet reproduce stronger T3 LUL130 recruitment. Missing mappings are not filled
with invented neurons. Large public raw source caches remain outside git;
source manifests mark their archive status explicitly.

## Frozen-bank pulse observations and next manual changes

Seventeen complete r4 pulse conditions now retain full traces, not just endpoint
samples. FG reversibly reduces BPN-driven DNg100 from approximately 27–29 Hz to
4.4 Hz bilaterally, while BB leaves about 24.4 Hz. P9+FG preserves substantial
DNa02 recruitment and reduces oDN1/DNg97, but BB's wider inhibition is too weak.
BRK recruits BON1 strongly but also incorrectly suppresses BPN-driven DNg100.
These mismatches are retained, not counted as completed experimental passes.
MDN-driven LBL40 persists during FG and BB pulses. Left/right PFL3 stimulation
still reverses the DNa02 response in the same shared bank; PFL2 addition boosts
the ipsilateral response but introduces some contralateral activity.

A shared INXXX468 Kx0.9 probe unexpectedly suppresses LBL40 during part of the
MDN response. Because these family candidates feed recurrent paths, this is not
a local isolated-cell change. The probe is NOT adopted. Family identity and
calcium interpretation remain uncertain; stronger T3 input/depolarization is
already present, whereas a strong segment-specific Ca contrast is not.

Actual BB source neurons fire about 71–73 Hz during the pulse, so source failure
is not the explanation. Input-event inspection identifies direct BB inhibition
of DNg97/DNa02, partly offset by recurrent disinhibition. The next hand test
raises the shared BB inhibitory release gain from 1 to 2, leaving all connection
counts and signs intact. BRK→BON1 direct input is strong; a separate shared BRK
release reduction tests whether BON1 recruitment can remain while reducing
unwanted ascending-network suppression. These are explicit unknown-release
hypotheses, not literature-measured conductance values or loss optimization.

## Recurrent context and target receptors

The new unified MaleCNS graph has3474 neurons and455231 signed-hypothesis edges.
Both previous graphs' signed AND unsigned induced submatrices match exactly.
Cross-context edges are re-extracted from the original significant-only table;
this remains a truncated graph, not the whole CNS. The same r5 parameter bank
is being tested in every condition, with full pulse and recovery records.

Unity changes the quantitative responses. PFL3 retains DNa02 directional
excitation/opponent hyperpolarization. BPN+FG suppresses DNg100 strongly, whereas
BB does not suppress it strongly. MDN→LBL40 survives FG/BB. BB's inhibition of
P9-driven oDN1 weakens in the expanded context: old isolated-context success
is not inherited as a new pass. Current reports distinguish neural directions,
behavioral proxies and paper-model predictions.

network.receptor_conductances adds an explicit target GABAA/GluCl response
hypothesis. Previously inhibitory_gain was solely PRESYNAPTIC release. The new
option multiplies effective event conductance on existing negative edges of the
specified transmitter and target type. Structural matrices are left untouched;
positive edges and other transmitters are unchanged. It does not represent
receptor subtype kinetics, chloride homeostasis or metabotropic signalling.
Namespace-qualified groups prevent transfer to an unrelated connectome.

Four tests verify transmitter selectivity, preserved structural weights,
namespace/bounds, and unchanged no-feedback source spikes with the expected
postsynaptic conductance scaling. Together22 regression checks pass. r6 is a
manual GABAA-responsex1.5 probe shared by DNa02 and DNg97 homologues, not an
adopted improvement. It must preserve directional steering and FG/BB differences.

All four large public raw inputs (606774958 bytes total) are now verified in a
GitHub draft Release; data/public-input-release-verified.json records fresh
GitHub asset SHA-256 digests, byte counts, source URLs and code revisions.
The first archive task failed by querying a draft through a published-tag
endpoint; the corrected task succeeded. No cloud environment was published.
