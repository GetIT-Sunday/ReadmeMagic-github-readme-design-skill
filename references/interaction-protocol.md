# ReadmeMagic interaction protocol

ReadmeMagic is an executable Agent workflow. A user should see evidence of work in the conversation, not a promise to work later.

## Required interaction sequence

1. Resolve the local path or GitHub URL and state the exact target branch/ref. The first assistant turn must perform this action; a future-tense promise is not a stage update. For a remote-only URL, clone the requested ref into an isolated temporary workspace when network access is available; otherwise emit `blocked_missing_checkout` instead of substituting the caller's current directory.
2. Run repository inspection and show a compact evidence summary. If native tool cards are available, expose the command/file operation as a tool event.
3. Score the source README on content/evidence and reading experience.
4. Generate a candidate without applying it. If no README exists, label the run as `create` and write `README.generated.md`; do not fabricate a baseline score.
5. Render and open the before/after preview when the host supports file panels. In Codex desktop this means calling `mcp__codex_app__open_in_codex` with the absolute preview path; a printed path or browser URL alone is not an open event. For a new README, render a clearly labeled single-candidate preview instead of an empty “original” column.
6. Show a status card with scores, changed sections, safe fixes, suggested fixes, and missing evidence.
7. Stop and request one review action.

The event stream should be emitted when the host supports tool-like progress UI:

```json
[
  {"stage":"inspect","status":"completed","label":"Collected repository evidence"},
  {"stage":"score","status":"completed","label":"Scored content and reading experience"},
  {"stage":"optimize","status":"completed","label":"Wrote candidate README","artifact":"/absolute/path/README.optimized.md"},
  {"stage":"preview","status":"completed","label":"Rendered before/after preview","artifact":"/absolute/path/README.preview.html"},
  {"stage":"review","status":"awaiting_user_review","label":"Waiting for user review","actions":["apply","revise","keep_original"]}
]
```

If native buttons are unavailable, render the same events as concise status lines and
keep the three review actions as explicit user-facing choices. Do not collapse the
events into a single progress paragraph.

The preview lifecycle is strict:

```text
preview_not_generated → generated_pending_open → opened → awaiting_user_review
```

Generating `README.preview.html` is not equivalent to showing it. The Agent must use the host
file/browser panel, then run `readme-magic preview --opened` (or call the equivalent state update)
and verify both state files. When the CLI reports `preview_pending_open`, it also emits a
`host_action` object naming the required open tool and acknowledgement command; hosts should
surface that action as an openable interaction instead of leaving it in plain text.

For architecture, workflow, and overview visuals, the default provider is the host's native
`image_generation` tool. API and prompt-only modes are explicit fallbacks; prompt-only output
must be labelled pending and must never be embedded as a completed README asset.

The visual review shell should follow the Apple-inspired `DESIGN.md` reference: neutral
canvas, SF Pro/system typography, one Action Blue accent, low-noise chrome, and generous
spacing. This styling applies to the dashboard shell; the source and candidate columns
must continue to render their Markdown/HTML faithfully.

## Status card schema

```json
{
  "module": "readme-magic",
  "version": "2.2.0",
  "stage": "review",
  "status": "awaiting_user_review",
  "target": "owner/repo@branch",
  "execution_mode": "hybrid",
  "scores": {
    "overall": 95,
    "core_documentation": 68,
    "showcase_enhancement": 27,
    "reading_experience": 92
  },
  "quality_tier": "excellent",
  "strict_evidence_gate": true,
  "score_kind": "automated_preflight",
  "findings": {"safe_fix": 2, "suggested_fix": 1, "needs_input": 0},
  "candidate": "/absolute/path/README.optimized.md",
  "preview": "/absolute/path/README.preview.html",
  "preview_status": "opened",
  "host_action": null,
  "visual_actions": [],
  "visual_capability_probe": {
    "status": "pending",
    "tool": "image_generation",
    "on_available": "generate requested visual assets and rerun optimize",
    "on_unavailable": "show complete prompt and save path under prompt_only"
  },
  "gap_plan": [
    {
      "id": "gap-1",
      "code": "architecture_quality",
      "problem": "The architecture explanation is not presented as a polished visual",
      "evidence": {"check": "architecture_quality", "source": "automated_preflight"},
      "impact": "Readers cannot map the README narrative to real modules and data flow",
      "recommendation": "Use a repository-grounded PNG/SVG architecture figure",
      "remediation": "suggested_fix",
      "question": "要现在补这张视觉资产吗？",
      "options": [
        {"id": "native_generate", "label": "让当前 Agent 直接生成"},
        {"id": "prompt_only", "label": "我用外部生图工具"},
        {"id": "skip", "label": "暂时跳过"}
      ],
      "visual_asset": {
        "key": "architecture",
        "status": "native_required",
        "prompt": "...",
        "prompt_path": "/absolute/path/artifacts/prompts/architecture.prompt.md",
        "save_to": "/absolute/path/assets/generated/architecture.png"
      }
    }
  ],
  "bilingual": {
    "enabled": true,
    "candidates": ["/absolute/path/README.optimized.md", "/absolute/path/README_ZH.optimized.md"],
    "language_switches": {"english": "README_ZH.md", "chinese": "README.md"}
  },
  "next_actions": ["apply", "revise", "keep_original"]
}
```

For a first-README run, the card additionally includes
`workflow_kind="create"`, `baseline_available=false`, and a `README.generated.md`
candidate. The review surface must show the absence of a baseline explicitly rather
than displaying a fabricated zero score.

`core_documentation` is scored out of 70 and is the required quality track;
`showcase_enhancement` is scored out of 30 and captures optional visual polish.
`strict_evidence_gate` means the optional showcase package is complete. A failed gate
should be shown as a showcase gap, not as proof that the README is unusable.

`gap_plan` is the interactive remediation surface. The Agent must show it after scoring,
answer the user's provider question for visual gaps, and wait for the selected actions
before applying optional changes. `visual_capability_probe.status` is `pending` until the
host confirms whether native `image_generation` is available; it must never be inferred
from the presence of the Python CLI.

## Review choices

- `应用候选 README`: run `--apply` only; do not commit or push.
- `继续修改候选稿`: keep `README.md` untouched and revise the named sections.
- `保留原 README`: end the run and preserve all source files.

Commit and push require separate explicit user requests after application review.
