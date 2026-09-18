# ReadmeMagic interaction protocol

ReadmeMagic is an executable Agent workflow. A user should see evidence of work in the conversation, not a promise to work later.

## Required interaction sequence

1. Resolve the local path or GitHub URL and state the exact target branch/ref. The first assistant turn must perform this action; a future-tense promise is not a stage update. For a remote-only URL, clone the requested ref into an isolated temporary workspace when network access is available; otherwise emit `blocked_missing_checkout` instead of substituting the caller's current directory.
2. Run repository inspection and show a compact evidence summary. If native tool cards are available, expose the command/file operation as a tool event.
3. Score the source README on content/evidence and reading experience.
4. Generate a candidate without applying it.
5. Render and open the before/after preview when the host supports file panels.
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

The visual review shell should follow the Apple-inspired `DESIGN.md` reference: neutral
canvas, SF Pro/system typography, one Action Blue accent, low-noise chrome, and generous
spacing. This styling applies to the dashboard shell; the source and candidate columns
must continue to render their Markdown/HTML faithfully.

## Status card schema

```json
{
  "module": "readme-magic",
  "stage": "review",
  "status": "awaiting_user_review",
  "target": "owner/repo@branch",
  "execution_mode": "hybrid",
  "scores": {"content_evidence": 95, "reading_experience": 92},
  "findings": {"safe_fix": 2, "suggested_fix": 1, "needs_input": 0},
  "candidate": "/absolute/path/README.optimized.md",
  "preview": "/absolute/path/README.preview.html",
  "next_actions": ["apply", "revise", "keep_original"]
}
```

## Review choices

- `应用候选 README`: run `--apply` only; do not commit or push.
- `继续修改候选稿`: keep `README.md` untouched and revise the named sections.
- `保留原 README`: end the run and preserve all source files.

Commit and push require separate explicit user requests after application review.
