# README Reading Experience Rubric

Score reading experience independently from content/evidence completeness. Do not average the two scores: a complete README can still be repetitive, tiring, or unsafe to publish.

## Scoring

| Dimension | Weight | Passing evidence |
|---|---:|---|
| Information hierarchy | 20 | Each topic has one clear home; section order supports understanding before reference depth |
| Scanability | 20 | Headings, short paragraphs, tables, lists, and code blocks reveal the useful path quickly |
| Density and rhythm | 15 | Spacing and major transitions create rhythm without a separator after every section |
| Repetition and noise | 15 | Calls to action, badges, navigation, and back-to-top controls are restrained and non-repetitive |
| Navigation and consistency | 15 | Navigation targets resolve, labels are consistent, and bilingual entry points remain available |
| Visual evidence layout | 15 | Visuals appear near the claim they prove; community visuals remain in the footer |

## Quality Gate

- Require at least 80/100.
- Also require content/evidence >= 85/100; never average the scores.
- Block publication for broken primary navigation, repository-mismatched community assets, invalid local visuals, or severe duplicate structure.
- Fix only the section or presentation layer named by a finding. Preserve strong, unrelated project-owned design.

## Finding Classes

- `safe_fix`: deterministic and low-risk, such as limiting repeated back-to-top links or normalizing one Star History footer.
- `suggested_fix`: requires editorial judgment and must be reviewed in the before/after preview, such as splitting an oversized Usage section.
- `needs_input`: requires a real screenshot, runnable command, source data, image provider, or user decision.

## Deterministic Checks

Check duplicate H2 sections, broken navigation anchors, oversized sections, excessive horizontal rules, repeated calls to action, repeated back-to-top controls, and Star History placement/integrity. Report concrete evidence such as counts, section names, broken targets, and recommended maxima.

For back-to-top controls: optimized candidates should contain none by default, regardless of document length. Preserve them only when the user explicitly requests that design.

For a known public GitHub repository, Star History must be one dynamic SVG, point to the detected `owner/repo` in both URLs, and be the final visual module. It belongs to Community/Footer and never counts as product Showcase evidence.
