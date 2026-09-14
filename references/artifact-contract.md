# ReadmeMagic artifact contract

Each optimization run may create these reviewable artifacts under artifacts/:

| Artifact | Meaning |
|---|---|
| workflow-state.json | Current stage, execution mode, completed stages, scores, findings, and paths |
| asset-manifest.json | Visual assets, evidence sources, generation mode, and statuses |
| prompts/*.prompt.md | Authoring prompts when image mode is prompt_only |
| runtime/*.txt | Explicitly requested verified command transcripts |

The candidate README and preview remain at the project root by default. Missing optional artifacts must be reported as unavailable evidence, never represented by fabricated content.
