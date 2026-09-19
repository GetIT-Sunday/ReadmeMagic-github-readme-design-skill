# ReadmeMagic artifact contract

Each optimization run may create these reviewable artifacts under artifacts/:

| Artifact | Meaning |
|---|---|
| workflow-state.json | Current stage, execution mode, completed stages, core/showcase scores, quality tier, strict evidence gate, findings, and paths |
| interaction-card.json | Compact status card, separate core documentation and showcase scores, review actions, and a `host_action` describing how the host must open the preview |
| preview lifecycle | `generated_pending_open` until the host opens the preview; only then `awaiting_user_review` |
| asset-manifest.json | Visual assets, evidence sources, generation mode, and statuses |
| prompts/*.prompt.md | Authoring prompts for `native` or `prompt_only` image modes |
| runtime/*.txt | Explicitly requested verified command transcripts |

The candidate README and preview remain at the project root by default. Missing optional artifacts must be reported as unavailable evidence, never represented by fabricated content.
