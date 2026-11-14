# Persistent work and GitHub synchronization

The user explicitly requires all future work to be saved continuously to GitHub (`linzhefeng24/Applepie`). This is standing authorization to commit and push the user's project work; do not ask again for routine synchronization.

- Work in a clean branch/worktree based on current remote main; preserve unrelated work.
- At each completed meaningful step, save code, parameters, configuration, provenance, metrics, and the current state to the repository, then commit and push. Do this before finishing a turn and before lengthy next-stage experiments. Do not rely on chat-only reports or ephemeral `/workspace` paths as the sole copy.
- Use `research/` for these scientific experiments. Track input identities and immutable model/parameter hashes, software versions, seeds, commands, and incomplete/failed results. An experiment is not durably saved until a fresh remote read confirms the commit.
- Store large datasets/checkpoints/bundles as GitHub Release assets; commit a manifest with source URL, SHA-256, byte count, and the corresponding code revision. Existing Release assets may be referenced instead of duplicated.
- Never upload passwords, tokens, SSH keys, credential-bearing configuration, or unrelated private data. Review the actual staged files before every push.
- Distinguish user-pasted historical results, recovered artifacts, newly implemented substitutes, and independently rerun results. Do not mark missing code or parameters as restored merely because an old chat names them.
- If GitHub synchronization fails, retain a local checkpoint and report exactly what remains unpushed. Do not claim backup succeeded.
- Use ordinary fast-forward updates; never force-push, overwrite history, or include unrelated modifications.
