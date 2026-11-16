# Free-body comparison with direct target u(t)

Three new body simulations: epoch123 neural output, epoch1000 neural output, and direct replay of the exact old-A training target u(t). All use the same current 130-channel body YAML, free root, identical initial qpos/qvel/activation, native gravity/friction/contact, 1.4s physical duration and 5x slow playback. No root stabilization, resets, rescue forces or sensory feedback. Neural states are reused exactly from the verified full-network runs because this model has no body-to-neural feedback. They are not newly fitted or generated target signals.

Direct replay uses target_u (not target_a) with the same global training time mapping `(neural_ms-200)/3`, holds the last target after 1.2s body time, and applies all130 channels. The neural conditions retain 104 candidate-mapped channels plus26 mapping gaps. Target replay on this current model/initial state is not a reproduction of the older successful AB body simulation. This comparison does not establish free walking or experimentally correct alternation.

Run the existing single-model `build.py`, download `BPTT_Epoch123_1000_State.zip` into `cache/` from the existing public fixed-body Release, install the pinned runtime requirements with EGL, and run `python research/free-body-target-comparison-20261116/render.py`. Input hashes are enforced. Each case saves input u(t), initial state, body states, physical contacts, an MP4, and a report; the bundle and manifest include versions, code revision and immutable hashes. The GitHub workflow independently executes these commands and saves assets to the existing Release.

Generation pending.
