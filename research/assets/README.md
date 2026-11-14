# Recovery assets

`flymimic-legacy-AB-twofile.zip` preserves the archived A/B muscle model: exactly simulation.py and parameters.yaml, including original mesh assets, model constants, initial states and complete A/B controls. Requires MuJoCo3.3.2. Source/provenance is in the YAML and prior model reports; it is the Flybody-based130-muscle+11auxiliary model, not a new claim of measured six-leg anatomy.

SHA-256 and byte count: ../conductance-rebuild-20261114/data/body-model-release.json.

The18MB bundle is stored in git because the separately authenticated Release-upload endpoint returned401. Do not claim a Release asset exists. Model sources: https://github.com/TuragaLab/flybody and https://github.com/gizemozd/FlyMimic ; source model hash is recorded in the YAML. The neural reimplementation and its native activation interface diagnostics reference this frozen bundle.
