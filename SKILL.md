---
name: readme-magic
description: Create visually polished, high-impact GitHub README.md files that clearly showcase a project's value, capabilities, screenshots or diagrams, and fastest path to first success. Inspect the actual repository, preserve useful content, score presentation and documentation quality, and produce a reviewable candidate before replacement. Use when users ask to improve, beautify, redesign, audit, rewrite, generate, translate, or fix a README; showcase or present a GitHub project; add screenshots, banners, feature grids, badges, demos, or quick starts; or invoke $readme-magic.
---

# ReadmeMagic

Turn repositories into compelling project pages. Optimize for visual hierarchy and project understanding while keeping every claim grounded in repository evidence.

## Workflow

1. Locate the project root and existing `README.md`.
2. Run `readme-magic inspect --project-path <path> --json` to identify the project type, confidence, evidence sources, and presentation gaps. From this repository, use `python -m readme_magic.cli inspect --project-path <path> --json`.
3. Inspect the files that define the product and its real usage. Prioritize package metadata, entry points, examples, tests, license, configuration, existing documentation, and reusable images under `assets/`, `docs/`, `images/`, or `screenshots/`.
4. Classify the repository conservatively as a product, library, CLI, AI, infrastructure, knowledge, personal, or generic project. Use the detected type and confidence to choose the information architecture; lower confidence means preserve more existing structure.
5. Define the first-screen story: project identity, concrete value, strongest available evidence, primary audience, and the first useful action.
6. Run `readme-magic optimize --project-path <path>` to create `README.optimized.md` without changing the original. Optimization also creates a project-aware visual asset manifest. By default it uses `prompt_only`, so users without an image API receive ready-to-use prompts under `artifacts/prompts/`.
7. Review the candidate against the repository. Correct generic text, remove unsupported claims, and preserve valuable examples or domain explanations from the original.
8. Use the automatically generated `README.preview.html` to compare the original and candidate in a GitHub-like layout. Review the score change, changed sections, preserved sections, line counts, and visual asset status.
9. Run the analyzer against the candidate or assess it with [references/readme-rubric.md](references/readme-rubric.md). Resolve every placeholder, require strong content and presentation dimensions, and target a score of at least 85.
10. Present the candidate, the preview path, the change summary, and remaining findings. Never recommend blind commit or push. Replace `README.md` only after explicit user confirmation; use `--apply` for a backed-up replacement, then ask the user to review the diff before commit/push.

## Content Rules

- Make the first screen function like a project landing page: project name, concrete value proposition, strongest available evidence, and the first useful action. Add 3-5 useful badges only when they provide verifiable context.
- Show the project before explaining every detail. Prefer real screenshots, output samples, demos, benchmarks, or architecture diagrams over generic decoration. A library or knowledge repository may use code output, taxonomy, or a study path instead of a screenshot.
- Present 3-6 differentiated capabilities in a two-column feature grid when the content supports it.
- Do not force a universal section list. Architecture is useful for complex systems, while a knowledge repository may need taxonomy and a CLI may need terminal examples instead.
- Keep every generated claim traceable to the inspection evidence. When evidence is missing, state the gap and recommend a specific repository asset or file instead of filling it with invented content.
- Derive installation and usage commands from repository files. Never invent commands, compatibility claims, benchmarks, integrations, or features.
- Preserve detailed sections whose content remains correct. Reorganize them when that improves scanning.
- Treat an existing README that already passes the 85-point quality gate and has a branded first screen as a project-owned design. Improve it surgically: fill evidenced gaps, but preserve its section titles, order, navigation, language switch, and back-to-top controls unless a specific defect requires changing them.
- A higher rubric score is not proof of a better README. Reject candidates that regress brand identity, visual hierarchy, readability, or useful navigation even when their numeric score increases.
- For an existing README scoring 95 or higher, allow a no-op candidate. Do not add a generic command section, discovered GIF, or decorative asset unless it fixes a concrete user-facing gap or the user explicitly requests it.
- For visual products, treat a missing screenshot as a blocking presentation gap. For infrastructure or libraries, use a real architecture or usage-flow diagram when it materially improves understanding.
- Keep badges limited to useful, verifiable signals. Do not use badge walls or decorative animation by default.
- Match the existing project language unless the user requests another language. For bilingual output, keep each section easy to scan rather than duplicating the entire document line by line.
- Keep the main README focused. Link to detailed documentation instead of copying it all into the front page.
- Do not expose secrets, local absolute paths, internal-only URLs, or private repository information.

## Safety

- Default to `README.optimized.md`; do not overwrite `README.md` implicitly.
- When applying, keep `README.md.bak` until the user confirms the result.
- Show or summarize the diff before applying substantial changes.
- Do not add external tracking images or services without a clear documentation purpose.
- Do not use generic stock images or fabricated screenshots as project evidence. Generated banners may establish identity but must not imply nonexistent product behavior.
- Treat visual generation as capability-gated. CLI GIFs require a runnable CLI, screenshots require a visual product, and benchmark figures require source data. Architecture, workflow, and overview visuals are planned for every project, but their content must come from repository or paper evidence.
- Support image generation modes `api`, `prompt_only`, and `disabled`. Store provider settings in `.readme-magic.json`; never print API keys or write them to manifests.
- Always provide a visual review artifact before application: `README.preview.html` by default, or the path selected with `--preview-output`. The review must place the original and candidate side by side and expose section-level changes.
- Keep prompt-only authoring artifacts under `artifacts/prompts/`; never show prompt paths or unfinished image instructions in the candidate README.
- Render the source README's supported HTML presentation blocks (`h1`-`h6`, `ul`/`ol`/`li`, tables, links, images, details, and inline emphasis) as HTML in the preview; never expose those tags as visible text.
- Preserve existing language switches such as `English | 中文` in the optimized first screen. Do not remove a valid navigation or language entry while rebuilding the hero.
- For CLI projects, prefer a real runnable command transcript or a verified GIF as the showcase evidence. Do not use a decorative chart, banner, or growth image as the primary CLI demo.
- A real runtime simulation is opt-in only: when the user provides `--demo-command`, run that explicit command in the project, capture its output, and label it as verified runtime evidence. Never execute an inferred or unknown command automatically.

## CLI

```bash
# Inspect project type and traceable evidence
readme-magic inspect --project-path .
readme-magic inspect --project-path . --json

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
