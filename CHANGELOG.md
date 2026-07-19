# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
