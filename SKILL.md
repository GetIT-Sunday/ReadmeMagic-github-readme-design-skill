---
name: readme-magic
metadata:
  version: "2.1.0"
description: Use ReadmeMagic as an executable README optimization agent. When a user asks in Chinese or English to optimize, beautify, redesign, audit, rewrite, or improve a README, or provides a GitHub repository URL, immediately resolve the target and run inspect → score → optimize → preview. Produce a candidate, visual comparison, evidence-backed findings, and a review choice; never stop at a prose plan or silently apply changes.
---

# ReadmeMagic

Turn repositories into compelling project pages. Optimize for visual hierarchy and project understanding while keeping every claim grounded in repository evidence.

## Activation and interaction contract

Activate when the request contains README/readme, GitHub repository URL, “优化/美化/重写/改进 README”, “optimize/redesign/rewrite README”, or `$readme-magic`. Do not answer with only an explanation of what ReadmeMagic could do.

For an optimization request, the first assistant turn must perform an observable ReadmeMagic
action (CLI invocation or equivalent repository inspection). A sentence such as “流程已经启动”
or “我会先……” is not a valid stage result. If execution is blocked, report the exact blocker
and still emit the structured `agent_only` status card; do not fabricate scores, paths, or a
completed optimization.

Resolve a local project path first. If the user supplies a GitHub URL, parse its `owner/repo` and branch or tree ref, then use the matching checkout when available. If no checkout exists and network/git access is available, clone the requested ref into a temporary workspace and run the same workflow there. If cloning is blocked, stop at a `blocked_missing_checkout` status card and ask for a local path or archive; do not silently analyze the current repository and do not present a baseline-only report as an optimization.

Emit a short stage update before each real action:

```text
🧭 ReadmeMagic · Inspecting repository evidence
📊 ReadmeMagic · Scoring content and reading experience
🛠️ ReadmeMagic · Building a reviewable candidate
🖼️ ReadmeMagic · Rendering the before/after preview
⏸️ ReadmeMagic · Waiting for your review
```

The user-facing result must contain a status card with project, target ref, execution mode (`hybrid` or `agent_only`), content score, reading-experience score, finding counts, candidate path, preview path, and next action. If the Codex app can open files, call `mcp__codex_app__open_in_codex` with the preview path immediately after generating it, then run `readme-magic preview --opened` (or the equivalent state update) and verify the card says `preview_status=opened`. Merely printing a `file://` URL or creating the HTML file does not count. If the host cannot open files, leave the card at `preview_pending_open` and report that exact blocker; never claim the review gate was reached.

The review dashboard is a product surface, not a debug dump. Use the repository's
`DESIGN.md` Apple-inspired tokens when styling the generated preview: restrained chrome,
SF Pro/system typography, Action Blue (`#0066cc`) as the single accent, soft neutral canvas,
generous spacing, and clear card hierarchy. Keep the README columns faithful to GitHub Markdown;
apply the visual system to the surrounding review UI rather than rewriting the source README's
design language.

When the host supports tool-like progress, emit one event per completed stage and a final
`awaiting_user_review` event. Do not compress the run into one generic paragraph. The
machine-readable event stream and status-card schema are defined in
[references/interaction-protocol.md](references/interaction-protocol.md).

At the review gate, offer exactly these actions in plain language: `应用候选 README`, `继续修改候选稿`, or `保留原 README`. Applying, committing, and pushing are separate actions.

Do not present a baseline-only score as the result of optimization. The minimum successful
optimization response includes a non-empty candidate path, a non-empty preview path, and a
review status of `awaiting_user_review`.

## Workflow

1. Locate the project root and existing `README.md`.
2. Verify the runtime before invoking the CLI. Skill discovery exposes `SKILL.md`, but does not install the Python package. From a checkout, run `./scripts/install.sh` or `python3 -m pip install -e <skill-repo-path>`, then `readme-magic check-install`. The module entry point `python3 -m readme_magic` is also supported.
3. Run `readme-magic inspect --project-path <path> --json` to identify the project type, confidence, evidence sources, and presentation gaps.
4. Inspect the files that define the product and its real usage. Prioritize package metadata, entry points, examples, tests, license, configuration, existing documentation, and reusable images under `assets/`, `docs/`, `images/`, or `screenshots/`.
5. Classify the repository conservatively as a product, library, CLI, AI, infrastructure, knowledge, personal, or generic project. Use the detected type and confidence to choose the information architecture; lower confidence means preserve more existing structure.
6. Define the first-screen story: project identity, concrete value, strongest available evidence, primary audience, and the first useful action.
7. Run `readme-magic optimize --project-path <path> --image-mode native`. If `README.md` exists, this creates `README.optimized.md` without changing the original; if it does not exist, this creates `README.generated.md` and enters the first-README creation flow. Do not pass `--no-preview` in an interactive user request. Optimization also creates a project-aware visual asset manifest. For architecture, workflow, and overview visuals, call the host `image_generation` tool once per `interaction.visual_actions` item with its repository-grounded prompt, save each returned image under `save_to`, then rerun `readme-magic optimize --image-mode native` so the now-available images are embedded in the candidate. If native generation is unavailable, explicitly fall back to `api` or `prompt_only` and report the fallback.
8. Review the candidate against the repository. Correct generic text, remove unsupported claims, and preserve valuable examples or domain explanations from the original.
9. Use the automatically generated `README.preview.html` to compare the original and candidate in a GitHub-like layout. For a repository without README.md, render a single clearly labeled generated candidate and do not invent an original score or before/after delta. Review both independent scores, section changes, remaining findings, line counts, and visual asset status. In Codex desktop, call `mcp__codex_app__open_in_codex` for this exact file before the final response; then mark it opened and verify `artifacts/interaction-card.json` has `status=awaiting_user_review` and `next_actions=["apply", "revise", "keep_original"]`.
10. Run the analyzer against the candidate. Assess the 70-point core documentation score and the 30-point showcase enhancement score with [references/readme-rubric.md](references/readme-rubric.md), then assess reading experience with [references/reading-experience-rubric.md](references/reading-experience-rubric.md). Require core documentation >= 56/70, reading experience >= 80, and no blocking finding for basic review readiness. Treat the strict evidence gate as an optional showcase-completeness signal; do not make screenshots, GIFs, or custom architecture art a universal hard gate.
11. Present the candidate, the preview path, the change summary, and remaining findings. Never recommend blind commit or push. Replace `README.md` only after explicit user confirmation; use `--apply` for a backed-up replacement, then ask the user to review the diff before commit/push.

For a user request that says “优化 README”, the completion point is the review gate with a visible candidate and preview. Do not claim completion when only a baseline score or a plan has been produced.

## Authorization levels

- “分析 / 评估 / 看看”：inspect and report only; generate no candidate unless requested.
- “优化 / 重写”：if README.md exists, generate `README.optimized.md`; otherwise generate `README.generated.md` and a single-candidate preview; do not modify `README.md`.
- “直接应用 / 替换”：after the candidate and preview are shown, `--apply` may replace `README.md` and create `README.md.bak`.
- “提交”：commit only after a separate explicit request.
- “推送 GitHub”：push only after a separate explicit request.

These permissions are independent: `apply ≠ commit ≠ push`. Never infer commit or push permission from an optimization request.

After generating a preview, open or render it, report its path, summarize the visual changes, and wait for user review before applying. The completion message must include the candidate, preview, scores, findings, and next authorization step. When the CLI returns `preview_pending_open`, treat `interaction.host_action` as mandatory: execute the specified host open action, then acknowledge it with `readme-magic preview --opened`.

## Agent execution model

Treat the workflow as staged execution: discover → inspect → score → plan → optimize → preview → review → apply. Each stage must leave a structured state and reviewable artifacts. Read the relevant guidance in `workflows/` and [references/artifact-contract.md](references/artifact-contract.md).

The CLI is an optional deterministic executor. Detect it at runtime and choose hybrid when available; otherwise use agent-only and report that deterministic CLI checks were unavailable. The user-facing result must have the same shape in both modes: project evidence, two scores, findings, candidate path, preview path, and apply status.

## Visual generation contract

Architecture, workflow, and overview visuals are first-class ReadmeMagic outputs. Use this
provider order:

1. `native`: call the host's native `image_generation` tool with the repository-grounded prompt
   and save the returned image under the project `assets/` directory;
2. `api`: call the configured image provider when native generation is unavailable;
3. `prompt_only`: write a complete prompt and mark the visual as pending when neither model is
   available.

The default Agent behavior is `native` for architecture/workflow diagrams. Never claim an image
was generated when only a prompt was written. Every generated asset must appear in
`artifacts/asset-manifest.json` with `native`, `generated`, `available`, or `prompt_ready` status.

## Content Rules

- Make the first screen function like a project landing page: project name, concrete value proposition, strongest available evidence, and the first useful action. Add 3-5 useful badges only when they provide verifiable context.
- Treat the first screen as a visual proof surface, not just a title and badges. A meaningful project-owned visual, real output, screenshot, GIF, or native-generated hero must appear before the first major section; Star History, badge walls, and generic banners do not satisfy this requirement.
- Show the project before explaining every detail. Prefer real screenshots, output samples, demos, benchmarks, or architecture diagrams over generic decoration. A library or knowledge repository may use code output, taxonomy, or a study path instead of a screenshot.
- Present 3-6 differentiated capabilities in a two-column feature grid when the content supports it.
- Do not force a universal section list. Architecture is useful for complex systems, while a knowledge repository may need taxonomy and a CLI may need terminal examples instead.
- Keep every generated claim traceable to the inspection evidence. When evidence is missing, state the gap and recommend a specific repository asset or file instead of filling it with invented content.
- Derive installation and usage commands from repository files. Never invent commands, compatibility claims, benchmarks, integrations, or features.
- Preserve detailed sections whose content remains correct. Reorganize them when that improves scanning.
- Treat an existing README that already passes the 85-point quality gate and has a branded first screen as a project-owned design. Improve it surgically: preserve its hero, useful section titles, navigation, and language switch; change only sections named by findings. Existing elements are not automatically good: remove or consolidate repeated navigation, calls to action, separators, and other diagnosed noise.
- A higher rubric score is not proof of a better README. Reject candidates that regress brand identity, visual hierarchy, readability, or useful navigation even when their numeric score increases.
- For an existing README scoring 95 or higher, allow a no-op only when its reading-experience score also passes and no actionable findings remain. Do not add a generic command section, discovered GIF, or decorative asset unless it fixes a concrete user-facing gap or the user explicitly requests it.
- Classify each reading-experience finding as `safe_fix`, `suggested_fix`, or `needs_input`. Apply deterministic safe fixes to the candidate; expose suggested changes in the preview for review; never fabricate missing evidence to clear a needs-input finding.
- Remove back-to-top controls from optimized candidates by default, regardless of README length. GitHub and browsers already provide native page navigation, so repeated manual controls are visual noise. Preserve them only when the user explicitly requests that design.
- When a public GitHub `owner/repo` is known, keep exactly one dynamic Star History SVG as the final visual module after Contributing, License, and optional Acknowledgments. It is community/footer content, never Showcase evidence. Correct repository mismatches, remove duplicates and static screenshots, and use `https://api.star-history.com/svg?repos=OWNER/REPO&type=Date`.
- For visual products, treat a missing screenshot as a blocking presentation gap. For infrastructure or libraries, use a real architecture or usage-flow diagram when it materially improves understanding.
- Keep badges limited to useful, verifiable signals. Do not use badge walls or decorative animation by default.
- Match the existing project language unless the user requests another language. For bilingual output, keep each section easy to scan rather than duplicating the entire document line by line.
- Keep the main README focused. Link to detailed documentation instead of copying it all into the front page.
- Do not expose secrets, local absolute paths, internal-only URLs, or private repository information.
- When both `README.md` and `README_ZH.md` exist, audit title, positioning, image paths, and important links for synchronization. Report `bilingual_asset_mismatch` or `bilingual_positioning_mismatch` instead of silently updating only one file.
- Compare the README's primary positioning with package metadata, entry points, active UI/plugin directories, demo assets, and recently tested workflows. Report `positioning_drift` when the story no longer matches the repository's current focus.

## Safety

- Default to `README.optimized.md` for an existing README and `README.generated.md` for a first README; do not overwrite `README.md` implicitly.
- When applying, keep `README.md.bak` until the user confirms the result.
- Show or summarize the diff before applying substantial changes.
- Do not add external tracking images or services without a clear documentation purpose.
- Do not use generic stock images or fabricated screenshots as project evidence. Generated banners may establish identity but must not imply nonexistent product behavior.
- Treat visual generation as capability-gated. CLI GIFs require a runnable CLI, screenshots require a visual product, and benchmark figures require source data. Architecture, workflow, and overview visuals are planned for every project, but their content must come from repository or paper evidence.
- Support image generation modes `native`, `api`, `prompt_only`, and `disabled`. Store provider settings in `.readme-magic.json`; never print API keys or write them to manifests.
- Always provide a visual review artifact before application: `README.preview.html` by default, or the path selected with `--preview-output`. The review must place the original and candidate side by side, render supported GitHub Markdown/HTML faithfully, and expose section-level changes plus both scores and localized findings.
- The preview is a required user-facing review step. Generation alone is not enough: the workflow must transition through `generated_pending_open` and only become `awaiting_user_review` after the host opens the preview (or explicitly marks it opened). Do not describe an optimization as complete until the preview has been opened and its path and material changes have been reported. When the CLI returns `preview_pending_open`, execute its emitted host action and verify the state card before ending the turn.
- Keep prompt-only authoring artifacts under `artifacts/prompts/`; never show prompt paths or unfinished image instructions in the candidate README.
- Render the source README's supported HTML presentation blocks (`h1`-`h6`, `ul`/`ol`/`li`, tables, links, images, details, and inline emphasis) as HTML in the preview; never expose those tags as visible text.
- Preserve existing language switches such as `English | 中文` in the optimized first screen. Do not remove a valid navigation or language entry while rebuilding the hero.
- For CLI projects, prefer a real runnable command transcript or a verified GIF as the showcase evidence. Do not use a decorative chart, banner, or growth image as the primary CLI demo.
- For CLI, AI, and visual-product projects, help-only snippets and descriptive prose are not runtime evidence. Require a captured output marker, exit status, generated artifact, screenshot, or verified GIF/video. Do not infer that a command was run merely because it appears in a fenced code block.
- Mermaid may explain a rough flow, but it does not receive full architecture credit. When the repository has multiple modules or the README claims an architecture/workflow, request a maintained PNG/SVG/figure with readable labels and a traceable relationship to real modules.
- Use the quality tier, core score, showcase score, and strict evidence gate from the analyzer. A numeric 100 with a failed strict evidence gate must be reported as incomplete showcase evidence, never as an exceptional README. A README with strong core documentation may still be review-ready without passing the optional showcase gate.
- Treat the CLI score as `automated_preflight`. Never call it “excellent” or “100-point quality” without inspecting the rendered preview and verifying that every visual asset, runtime transcript, and architecture claim is real.
- A real runtime simulation is opt-in only: when the user provides `--demo-command`, run that explicit command in the project, capture its output, and label it as verified runtime evidence. Never execute an inferred or unknown command automatically.

## CLI

```bash
# Inspect project type and traceable evidence
readme-magic inspect --project-path .
readme-magic inspect --project-path . --json
readme-magic check-install
python3 -m readme_magic check-install
readme-magic workflow --project-path . --json

# Diagnose the current README
readme-magic analyze --project-path .

# Produce a safe candidate
readme-magic optimize --project-path .

# Force English or Chinese
readme-magic optimize --project-path . --lang en
readme-magic optimize --project-path . --lang zh

# Plan or generate project-aware visual assets
readme-magic image-config --project-path . --init
readme-magic preview --project-path . --input README.optimized.md
readme-magic preview --project-path . --input README.md --compare README.optimized.md

# Customize or skip the automatic review page
readme-magic optimize --project-path . --preview-output README.review.html
readme-magic optimize --project-path . --no-preview
readme-magic optimize --project-path . --demo-command "python3 -m readme_magic.cli inspect --project-path ."

# Apply after review; creates README.md.bak
readme-magic optimize --project-path . --apply
```

Use `generate` only when a project has no README or the user explicitly wants a template-first document. Use `optimize` for existing projects.
