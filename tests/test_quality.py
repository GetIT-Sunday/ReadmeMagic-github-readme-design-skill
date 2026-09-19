import unittest

from readme_magic.quality import analyze_readme


class QualityTests(unittest.TestCase):
    def test_complete_readme_scores_high(self):
        content = """# Demo

A concrete project description for new users.

![Demo](demo.png)

[Features](#features) · [Showcase](#showcase) · [Quick Start](#quick-start)

## Features
- Fast

## Installation
```bash
pip install demo
```

## Quick Start
```bash
demo --help
```

## Documentation
See docs.

## Project Structure
See source.

## Contributing
Pull requests welcome.

## License
MIT.
"""
        report = analyze_readme(content)
        self.assertEqual(report.score, 100)
        self.assertFalse(report.findings)

    def test_badges_do_not_count_as_project_visuals(self):
        content = """# Demo

A concrete description of this project and its audience.

![Version](https://img.shields.io/badge/version-1.0-blue)

[Features](#features) · [Showcase](#showcase) · [Quick Start](#quick-start)

## Features
- Fast
"""
        report = analyze_readme(content)

        self.assertIn("visual_story", {item.code for item in report.findings})
        self.assertLess(report.score, 100)

    def test_core_documentation_can_pass_without_showcase_assets(self):
        content = """# Data Tool

A command line tool for validating and transforming project data for new users.

## Features
- Validates input records
- Produces transformed output

## Command Reference
```console
$ data-tool run input.jsonl
validated 12 records
```

## Installation
```bash
pip install data-tool
```

## Quick Start
```bash
data-tool run input.jsonl
```

## Documentation
See the docs guide.

## Contributing
Run the test suite before opening a pull request.

## License
MIT.
"""
        report = analyze_readme(content, "cli")
        details = report.to_dict()
        self.assertGreaterEqual(details["core_score"], 56)
        self.assertTrue(details["core_quality_gate"])
        self.assertLess(details["presentation_score"], 30)
        self.assertFalse(details["strict_evidence_gate"])

    def test_placeholder_in_prose_fails_but_inline_example_does_not(self):
        failed = analyze_readme("# Demo\n\nThis README has {{ONE_LINER}} to finish.")
        self.assertIn("complete", {item.code for item in failed.findings})

        example = analyze_readme("# Demo\n\nUse `{{PLACEHOLDER}}` in your custom template.")
        self.assertNotIn("complete", {item.code for item in example.findings})

        gap = analyze_readme(
            "# Demo\n\nAdd representative command examples before publishing."
        )
        self.assertIn("complete", {item.code for item in gap.findings})

    def test_cli_banner_and_mermaid_do_not_replace_terminal_evidence(self):
        content = """# Demo CLI

A command line tool with a clear value proposition.

![Banner](assets/banner.png)

[Features](#features) · [Usage](#usage) · [Documentation](#documentation)

## Features
- Fast

## Showcase
```mermaid
flowchart LR
  A --> B
```

## Installation
```bash
pip install demo
```

## Usage
```bash
demo --help
```

## Documentation
See docs.

## Contributing
Pull requests welcome.

## License
MIT.
"""
        report = analyze_readme(content, "cli")
        codes = {item.code for item in report.findings}

        self.assertIn("showcase_evidence", codes)
        self.assertIn("type_structure", codes)
        self.assertLess(report.score, 100)

    def test_cli_terminal_transcript_counts_as_project_evidence(self):
        content = """# Demo CLI

A command line tool with a clear value proposition.

## Command Reference

```console
$ demo inspect .
Project: demo
Type: cli
```
"""
        report = analyze_readme(content, "cli")

        self.assertNotIn("showcase_evidence", {item.code for item in report.findings})
        self.assertIn("visual_story", {item.code for item in report.findings})
        self.assertNotIn("type_structure", {item.code for item in report.findings})

    def test_cli_transcript_accepts_project_specific_output(self):
        content = """# Demo CLI

A command line tool with a clear value proposition.

## Command Reference
```console
$ demo run
Verified runtime transcript
custom project result
[exit code: 0]
```
"""
        report = analyze_readme(content, "cli")
        self.assertIn("showcase_evidence", report.passed_checks)

    def test_cli_mermaid_and_help_text_do_not_count_as_excellent_showcase(self):
        content = """# Demo CLI

A command line tool for processing data.

![Star History](https://api.star-history.com/svg?repos=owner/demo&type=Date)

## Features
- Fast processing

## Architecture
```mermaid
flowchart LR
 A --> B
```

## Command Reference
```console
$ demo --help
usage: demo [-h]
```
"""
        report = analyze_readme(content, "cli")
        codes = {item.code for item in report.findings}
        self.assertIn("visual_story", codes)
        self.assertIn("showcase_evidence", codes)
        self.assertIn("architecture_quality", codes)
        self.assertIn("dynamic_demo", codes)

    def test_strict_evidence_gate_requires_visual_runtime_and_architecture_proof(self):
        content = """<p align="center"><img src="assets/project-overview.png" alt="Project overview"></p>

# Demo CLI

A command line tool for processing data.

[Highlights](#highlights) · [Architecture](#architecture) · [Quick Start](#quick-start)

## Highlights
- Processes data

## Architecture
<p align="center"><img src="assets/architecture.svg" alt="Architecture"></p>

## Command Reference
```console
$ demo run input.jsonl
Verified runtime transcript
Rendered 2 samples into outputs
[exit code: 0]
```

<p align="center"><img src="assets/cli-demo.gif" alt="CLI demo"></p>

## Installation
```bash
pip install demo
```

## Quick Start
```bash
demo run input.jsonl
```

## Documentation
See docs.

## Contributing
Pull requests welcome.

## License
MIT.
"""
        report = analyze_readme(content, "cli")
        self.assertEqual(report.score, 100)
        self.assertTrue(report.to_dict()["strict_evidence_gate"])
        self.assertEqual(report.to_dict()["tier"], "exceptional")


if __name__ == "__main__":
    unittest.main()
