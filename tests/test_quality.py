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
        self.assertEqual(report.dimensions["presentation"], 5)

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

        self.assertNotIn(
            "showcase_evidence", {item.code for item in report.findings}
        )
        self.assertNotIn("type_structure", {item.code for item in report.findings})


if __name__ == "__main__":
    unittest.main()
