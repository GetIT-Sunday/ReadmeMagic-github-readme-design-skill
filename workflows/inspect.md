# Inspect stage

Input: project path and an optional README.

Collect package metadata, entry points, install and usage commands, tests, docs, license, visual assets, papers, and GitHub repository identity.

Output: project profile, evidence inventory, workflow kind (`optimize` when README.md
exists, `create` otherwise), and workflow state.

Completion gate: every generated claim has a repository source or is marked as missing
evidence. A missing README is a valid first-README workflow, not an error.
