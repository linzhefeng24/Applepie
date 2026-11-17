# Physical-range joint BPTT restart

Start: lowest measured joint-MSE parent weights after update87 (MSE0.10746249083268701), not latest88 and not the manual bank. `initialization.json` preserves the exact original207-vector, immutable archive identity and converted log multipliers.

Regularization stays centered on the original manual bank: lambda10 times mean((exp(theta)-1)^2). Positive log scales replace both ±10% projection and ±20% tanh. Cell types still share23x9 variables. No new percentage limit; baseline zero mechanisms remain zero. Adam moments restart because coordinates changed; learning rate0.002 compensates for the old0.2 local scale derivative.

300 NEW actual updates, no coefficient pilots. Same full3988-cell graph, surrogate/200ms-truncated neural adjoint and native0.4s physical forward. Physical derivatives retain the documented piecewise implicit approximation and failed strict20ms random-direction test (max13.3% error); this is not an exact end-to-end derivative.

Run in a pinned isolated Python3.12 environment: install requirements, run the original single-model build.py, run patch_mjx.py here, then `python train_chunk.py --updates 10`. GitHub workflow handles immutable checkpoint restore, per-update Release uploads, fresh remote confirmation and continuation. Check `progress.json` for actual completed new updates.
