# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- First-README creation flow: repositories without `README.md` now produce a
  reviewable `README.generated.md` candidate without a fabricated baseline score.
- Installation verification now checks the package import, module entrypoint,
  Markdown renderer, and optional shell entrypoint separately.
- Explainable project profiles with type, confidence, and classification reasons.
- Traceable evidence items for commands, visuals, documentation, license, contribution, and security files.
- `readme-magic inspect` with human-readable and JSON output.
- Project-type coverage for CLI, product, library, AI, infrastructure, knowledge, and generic repositories.
- Type-aware quality scoring that separates brand visuals from real project evidence.
- Preservation of unmanaged README sections and stable generated anchors.
- A real CLI transcript GIF for the self-test repository example.

## [2.0.0] - 2026-07-16

### Added

- Project-aware inspection for Python, Node.js, Rust, and Go repositories.
- `readme-magic analyze` with a deterministic 100-point quality report.
- `readme-magic optimize` with safe candidate output and backed-up `--apply`.
- Codex-compatible Skill metadata, UI metadata, and a README quality rubric.
- Unit tests for analyzers, quality checks, optimization, and backup behavior.
- Showcase-oriented rendering with first-screen hierarchy, feature grids, asset discovery, and screenshot/demo sections.
- Separate content, presentation, onboarding, and trust dimensions in the README score.

### Changed

- The interactive workflow now distinguishes `optimize` and `create` runs while
  keeping the same simple review actions and preview lifecycle.
- Showcase evidence remains an optional enhancement track; missing visuals do not
  make a technically usable README look like an unfinished document.

- Packaged templates inside `readme_magic/templates` so wheels include them.
- Synchronized the package and CLI version at 2.0.0.
- Updated English and Chinese documentation for the agent-first workflow.

## [1.3.0] - 2026-07-15

### Added

- ✨ `--banner PATH_OR_URL` flag: embed an existing local image or remote URL as a full-width banner at the top of the generated README.
- ✨ `--gen-banner` flag: auto-generate a banner via GPT Image (requires `gpt_image.py`, available in the dodo AI Agent sandbox) and embed it automatically.
- 🔧 `{{BANNER}}` placeholder support in templates — place it anywhere in a template to control exact banner position; falls back to prepending at the top when the placeholder is absent.

## [1.2.0] - 2026-07-14

### Fixed

- 🐛 `library` and `personal` templates were listed in docs/CHANGELOG but the actual template files (`en/zh/bilingual`) were missing from `templates/`, causing `readme-magic generate --template library|personal` to fail with "Template not found". Added all 6 missing files.

## [1.0.0] - 2024-01-01

### Added

- 🎉 Initial release
- ✨ Standard template for general projects
- ✨ AI/ML project template
- ✨ CLI tool template
- ✨ Library/Framework template
- ✨ Personal project template
- 🎨 Custom color themes
- 📊 Star History integration
- 🏷️ Badge system with shields.io
- 📝 Example READMEs for different project types
- 📖 Comprehensive documentation
- 🧪 Test suite
- 🔧 CLI interface

### Features

- Generate professional READMEs in seconds
- Multiple pre-built templates
- Customizable color themes
- Dynamic badge generation
- Star History chart integration
- Project structure visualization
- Responsive design

### Templates

- **Standard Template** - For general open source projects
- **AI/ML Project Template** - Optimized for machine learning projects
- **CLI Tool Template** - For command line tools
- **Library/Framework Template** - For reusable components
- **Personal Project Template** - For portfolio projects

### Tools Integrated

- shields.io - Badge generation
- star-history.com - Star History charts
- contrib.rocks - Contributor avatars
- GitHub Readme Stats - Dynamic stats cards

## [0.9.0] - 2023-12-15

### Added

- Beta version for testing
- Basic template system
- Badge generation

### Fixed

- Initial bug fixes

## [0.8.0] - 2023-12-01

### Added

- Project kickoff
- Initial design
- Research phase

---

## Version History

- **1.0.0** - First stable release
- **0.9.0** - Beta release for testing
- **0.8.0** - Project kickoff

## Upgrade Guide

### From 0.9.0 to 1.0.0

1. Update installation
2. Check for breaking changes
3. Update custom templates if any

## Roadmap

### 1.1.0 (Planned)

- [ ] Add more templates
- [ ] Custom theme builder
- [ ] CLI improvements
- [ ] More integrations

### 1.2.0 (Planned)

- [ ] Web interface
- [ ] API access
- [ ] More examples
- [ ] Performance improvements

### 2.0.0 (Future)

- [ ] AI-powered generation
- [ ] Real-time preview
- [ ] Collaborative editing
- [ ] Plugin system

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
## Unreleased

- Add opt-in `--demo-command` runtime simulation that captures real command output for CLI Showcase sections.
- Prefer verified CLI transcripts over existing GIFs when an explicit demo command is supplied.
- Recognize arbitrary project-specific output as valid terminal evidence.
- Fix GitHub-like preview rendering for README HTML grids, headings, and lists.
- Preserve existing English/Chinese language switches during hero rebuilding.
- Keep decorative growth charts out of CLI Showcase sections.
- Render Mermaid blocks in the local GitHub-like review page when the browser can load the Mermaid runtime.
- Make `optimize` generate a GitHub-like before/after review page with scores, line counts, section changes, and asset status.
- Require the review artifact in the Skill workflow before apply, commit, or push.
- Add project-aware visual asset planning for overview, architecture, and workflow visuals.
- Add `api`, `prompt_only`, and `disabled` image generation modes with `.readme-magic.json` configuration.
- Add lightweight LaTeX paper context extraction and optional-skill capability detection.
- Add asset prompts and manifests to the optimization workflow without creating broken image links.
- Add side-by-side GitHub-like README preview support with `preview --compare`.
