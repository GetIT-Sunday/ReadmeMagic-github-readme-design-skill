# Optimize stage

Apply only changes supported by score findings and repository evidence. Preserve project-owned design, language switches, useful examples, and valid sections. Apply deterministic safe fixes automatically; leave editorial suggestions visible for review.

Output: `README.optimized.md` when a README exists, or `README.generated.md` for a
repository without a README, plus an asset manifest and updated workflow state.

The first-README path is a creation workflow, not an optimization diff: do not invent a
baseline score or render an empty original column. Apply remains a separate, explicit action.
