# README Showcase Rubric

Evaluate a README as both documentation and the project's primary GitHub landing page.

## Scoring

The score remains 100 points, split into 70 points of required documentation quality
and 30 points of optional showcase enhancement. A README can be usable without a GIF,
custom architecture artwork, or a product screenshot; those assets improve the landing
page but must not overwhelm the score for a technically complete project.

| Dimension | Category | Weight | Passing evidence |
|---|---|---:|---|
| Content (core) | First-screen story | 12 | Project identity, audience, problem, and concrete value are clear without scrolling far |
| Content | Highlights | 8 | 3-6 differentiated, repository-supported capabilities are easy to scan |
| Content | Structure | 5 | A compact repository, architecture, or workflow map helps readers understand the project |
| Presentation (optional) | First-screen visual | 6 | A meaningful project visual appears before the first major section; badges, Star History, and generic banners do not count as product proof |
| Presentation (optional) | Verified showcase | 9 | A real runtime transcript, GIF, screenshot, output sample, benchmark, or runnable demo demonstrates the project in use |
| Presentation (optional) | Architecture quality | 6 | A repository-grounded PNG/SVG/figure explains architecture or workflow; Mermaid alone receives no credit for this category |
| Presentation (optional) | Dynamic demonstration | 3 | A real GIF/video or equivalent interactive evidence exists when the workflow benefits from motion; mark unavailable when it is not meaningful |
| Presentation (optional) | Visual identity | 3 | A coherent project-owned logo, banner, or visual system establishes identity; this is separate from runtime proof |
| Presentation (optional) | Navigation | 3 | Compact links connect the first screen to the most important sections |
| Onboarding (core) | Installation | 8 | Prerequisites and installation commands are verified and copy-pasteable |
| Onboarding (core) | First success | 10 | The shortest verified path produces a useful result with available example inputs |
| Onboarding (core) | Documentation | 7 | Readers can reach examples, API docs, guides, or deeper documentation |
| Trust (core) | Contribution | 5 | Issue, PR, and relevant validation guidance are present |
| Trust (core) | License | 3 | The license is named and linked to the actual file |
| Trust (core) | Completeness and evidence integrity | 12 | No placeholders, stale links, invented claims, missing sample inputs, or unverified runtime claims remain |

Core points total 70. Showcase points total 30. The CLI reports both subtotals as
`core_score` and `presentation_score` so a missing visual is not confused with missing
documentation.

## Quality Gate

- Require at least 56/70 core points before recommending replacement. The 30 showcase
  points are an enhancement track, not a hard prerequisite.
- Also require at least 80/100 in the independent [reading-experience rubric](reading-experience-rubric.md). Do not average the two scores.
- Report showcase completeness separately. The strict evidence gate indicates that the
  optional showcase package is complete; it must not block a technically usable README.
- A score of 100 is allowed only when the strict evidence gate passes: the first screen has a meaningful visual, runnable/visual projects show verified runtime evidence, and any claimed architecture/workflow has a non-Mermaid visual figure.
- Report a tier in addition to the number: `incomplete` (<60), `usable` (60-79), `strong` (80-89), `excellent` (90-94), or `exceptional` (95-100 with the strict evidence gate). Never describe a 100 that fails the evidence gate as exceptional.
- The CLI score is an automated preflight, not a design award. The `excellent` and `exceptional` tiers require host/agent visual review; the CLI must never present them as final approval without the preview gate.
- Treat inaccurate commands, unsupported claims, leaked secrets, broken local asset paths, and unresolved placeholders as blocking issues regardless of score.
- Treat a missing real screenshot as blocking for GUI applications, websites, games, and visual tools.
- Allow infrastructure, CLI, and library projects to substitute a real output sample, architecture diagram, or usage-flow figure.
- Treat Mermaid as a planning/backup representation. It may support structure, but it does not prove polished visual communication or actual runtime behavior.

## Visual Hierarchy

1. First screen: strongest visual, name, one-sentence value, useful badges, navigation.
2. Highlights: compact feature grid with concrete differentiators.
3. Showcase: screenshots, result examples, or architecture.
4. First success: installation plus the shortest working example.
5. Depth: documentation, project structure, contribution, and license.

Avoid badge walls, excessive emoji, decorative animations, repeated calls to action, and oversized sections that bury the first useful command.

## Review Questions

1. Can a visitor understand and remember the project after the first screen?
2. Does the README visibly demonstrate the product rather than merely describe it?
3. Are the most differentiated capabilities visually prioritized?
4. Can a new user reach first success using only verified commands?
5. Is the first screen visually legible before a reader scrolls into reference material?
6. Are every screenshot, GIF, link, command, version, and claim grounded in the repository?
7. If the README claims architecture or workflow, is the figure more informative than a basic Mermaid flowchart?

## High-Star README signals

The following patterns recur across strong, high-star repositories such as FastAPI,
Transformers, Supabase, Aider, Open WebUI, uv, and Ollama:

- a recognizable first-screen identity (logo/hero/product visual) rather than a text-only title;
- a concrete demo, output, screenshot, GIF, or benchmark near the top;
- a short value proposition followed by 3-6 differentiated capabilities;
- a copy-pasteable installation and shortest successful command;
- architecture or workflow visuals for multi-module systems, preferably as a maintained SVG/PNG;
- links to deeper docs, examples, tutorials, benchmarks, and contribution guidance;
- restrained badges and one coherent footer/community module;
- claims that are demonstrated by repository assets or reproducible commands.

These are quality signals, not a universal template. The optimizer should preserve a
project's own language and design while refusing to award full presentation credit to
empty placeholders, Mermaid-only diagrams, help-only snippets, or prompt-only assets.
