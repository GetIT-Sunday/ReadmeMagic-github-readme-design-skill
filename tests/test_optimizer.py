from pathlib import Path
import tempfile
import unittest

from readme_magic.analyzer import inspect_project
from readme_magic.optimizer import optimize_project, render_optimized_readme


class OptimizerTests(unittest.TestCase):
    def _project(self, root: str) -> Path:
        project = Path(root) / "hello"
        project.mkdir()
        (project / "pyproject.toml").write_text(
            """[project]
name = "hello"
version = "1.0.0"
description = "Greets users from the command line."
requires-python = ">=3.9"

[project.scripts]
hello = "hello:main"
""", encoding="utf-8")
        return project

    def test_default_writes_candidate_without_replacing_original(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            original = "# Hello\n\nOriginal details.\n"
            (project / "README.md").write_text(original, encoding="utf-8")

            destination, before, after, _ = optimize_project(project, lang="en")

            self.assertEqual(destination.name, "README.optimized.md")
            self.assertEqual((project / "README.md").read_text(encoding="utf-8"), original)
            self.assertGreater(after.score, before.score)
            self.assertLess(after.score, 100)
            self.assertIn(
                "showcase_evidence", {finding.code for finding in after.findings}
            )

    def test_apply_backs_up_original(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            readme = project / "README.md"
            readme.write_text("# Old\n", encoding="utf-8")

            destination, _, _, _ = optimize_project(project, apply=True, lang="en")

            self.assertEqual(destination, readme.resolve())
            self.assertEqual((project / "README.md.bak").read_text(encoding="utf-8"), "# Old\n")
            self.assertIn("<h1>hello</h1>", readme.read_text(encoding="utf-8"))

    def test_relative_custom_output_stays_inside_project(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            destination, _, _, _ = optimize_project(
                project, output=Path("docs/README.next.md"), lang="en"
            )

            self.assertEqual(destination, project.resolve() / "docs/README.next.md")
            self.assertTrue(destination.exists())

    def test_chinese_output_localizes_inferred_features_and_preserves_banner(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            (project / "tests").mkdir()
            metadata = inspect_project(project)
            existing = (
                '# hello\n\n<p align="center">\n'
                '  <img src="assets/banner.png" alt="Banner">\n</p>\n'
            )

            content = render_optimized_readme(metadata, existing, lang="zh")

            self.assertIn('src="assets/banner.png"', content)
            self.assertIn("包含自动化测试套件", content)
            self.assertNotIn("Includes an automated test suite", content)

    def test_uses_discovered_screenshot_as_first_screen_visual(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            (project / "screenshots").mkdir()
            (project / "screenshots" / "demo.png").write_bytes(b"png")

            metadata = inspect_project(project)
            content = render_optimized_readme(metadata, lang="en")

            self.assertIn('src="screenshots/demo.png"', content)
            self.assertIn("## 🖼️ Showcase", content)
            self.assertIn("## ✨ Highlights", content)
            self.assertIn("<table>", content)

    def test_default_optimization_adds_prompt_slots_without_broken_images(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            destination, _, _, _ = optimize_project(project, lang="en")
            content = destination.read_text(encoding="utf-8")
            self.assertTrue((project / "artifacts" / "prompts" / "architecture.prompt.md").exists())
            self.assertNotIn("Image prompt ready", content)
            self.assertNotIn('src="assets/generated/architecture.png"', content)

    def test_preserves_polished_existing_hero_instead_of_rebuilding_it(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            existing = """<p align=\"center\"><img src=\"assets/banner.png\" alt=\"Original banner\"></p>

<p align=\"center\"><h1>Original Brand</h1><em>Original Chinese tagline</em></p>

<p align=\"center\"><strong>English</strong> | <a href=\"README_ZH.md\">中文</a></p>
"""
            content = render_optimized_readme(inspect_project(project), existing, lang="en")
            self.assertIn("Original Brand", content)
            self.assertIn("Original Chinese tagline", content)
            self.assertIn('README_ZH.md">中文</a>', content)
            self.assertEqual(content.count("Original banner"), 1)
            self.assertNotIn("img.shields.io/badge/version", content)

    def test_very_high_quality_readme_is_allowed_to_be_a_noop(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            (project / "assets").mkdir()
            (project / "assets" / "banner.png").write_bytes(b"png")
            (project / "assets" / "cli-demo.gif").write_bytes(b"GIF89a")
            existing = """<p align="center"><img src="assets/banner.png" alt="Brand"></p>

# Original Brand

<p align="center"><strong>English</strong> | <a href="README_ZH.md">中文</a></p>

<p align="center"><a href="#features">Features</a> · <a href="#showcase">Showcase</a> · <a href="#usage">Usage</a> · <a href="#documentation">Documentation</a></p>

## Features
- Repository-aware analysis
- Safe candidate generation
- Visual review

## Showcase
```mermaid
flowchart LR
  A --> B
```

<p align="center"><img src="assets/cli-demo.gif" alt="CLI demo"></p>

## Installation
```bash
pip install -e .
```

## Usage
```bash
hello --help
```

## Documentation
See `docs/` for details.

## Contributing
Issues and pull requests are welcome.

## License
MIT
"""
            content = render_optimized_readme(inspect_project(project), existing, lang="en")
            self.assertEqual(content, existing)

    def test_high_quality_readme_only_repairs_reading_experience_defects(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            (project / "assets").mkdir()
            (project / "assets" / "banner.png").write_bytes(b"png")
            (project / "assets" / "cli-demo.gif").write_bytes(b"GIF89a")
            back = '<div align="right"><a href="#brand">↑ back to top</a></div>'
            sections = [
                ("Features", "- Repository-aware analysis\n- Safe candidate generation\n- Visual review"),
                ("Showcase", '<p align="center"><img src="assets/cli-demo.gif" alt="CLI demo"></p>'),
                ("Installation", "    pip install -e ."),
                ("Usage", "    hello --help"),
                ("Documentation", "See docs for details."),
                ("Contributing", "Issues and pull requests are welcome."),
                ("License", "MIT"),
            ]
            body = "\n\n".join(f"## {title}\n{section_body}\n{back}" for title, section_body in sections)
            existing = (
                '<a name="brand"></a>\n<p align="center"><img src="assets/banner.png" alt="Brand"></p>\n\n'
                '# Original Brand\n\n'
                '<p align="center"><strong>English</strong> | <a href="README_ZH.md">中文</a></p>\n\n'
                '<p align="center"><a href="#features">Features</a> · <a href="#showcase">Showcase</a> · '
                '<a href="#usage">Usage</a> · <a href="#documentation">Documentation</a></p>\n\n'
                + body + "\n"
            )
            content = render_optimized_readme(inspect_project(project), existing, lang="en")
            self.assertIn("Original Brand", content)
            self.assertIn('README_ZH.md">中文</a>', content)
            self.assertIn("Repository-aware analysis", content)
            self.assertNotIn("back to top", content.lower())

    def test_cli_gets_a_grounded_command_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            metadata = inspect_project(project)
            content = render_optimized_readme(metadata, lang="en")
            self.assertIn("## 🧭 Command Reference", content)
            self.assertIn("hello --help", content)

    def test_existing_star_history_block_is_moved_to_document_end(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            existing = """# hello

## Acknowledgments

Thanks.

<p align="center">
  <sub>If hello saved you time, consider giving it a ⭐ — it helps others discover it too.</sub>
</p>
<p align="center">
  <a href="https://star-history.com/#owner/hello&Date">
    <img src="https://api.star-history.com/svg?repos=owner/hello&type=Date" alt="Star History Chart" width="600">
  </a>
</p>

## Contributing

Please contribute.
"""
            content = render_optimized_readme(inspect_project(project), existing, lang="en")
            self.assertGreater(content.rfind("api.star-history.com"), content.rfind("## 📄 License"))

    def test_opt_in_runtime_demo_is_added_to_showcase(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            destination, _, after, _ = optimize_project(
                project, lang="en", demo_command="python3 -c 'print(\"verified output\")'"
            )
            content = destination.read_text(encoding="utf-8")
            self.assertIn("Verified runtime transcript", content)
            self.assertIn("verified output", content)
            self.assertIn("showcase_evidence", after.passed_checks)
            showcase = content[content.index("## 🖼️ Showcase"):content.index("## 📦 Installation")]
            self.assertNotIn("readme-magic-cli-demo.gif", showcase)

    def test_star_history_asset_is_not_added_to_showcase(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            (project / "assets").mkdir()
            (project / "assets" / "star-history.png").write_bytes(b"png")
            metadata = inspect_project(project)
            content = render_optimized_readme(metadata, lang="en")
            showcase_start = content.index("## 🖼️ Showcase")
            showcase_end = content.index("## 📦 Installation")
            showcase = content[showcase_start:showcase_end]
            self.assertNotIn("star-history.png", showcase)

    def test_preserves_existing_language_switch_in_hero(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            existing = '<p align="center">\n  <strong>English</strong> | <a href="README_ZH.md">中文</a>\n</p>\n'
            content = render_optimized_readme(inspect_project(project), existing, lang="en")
            self.assertIn('<a href="README_ZH.md">中文</a>', content)

    def test_preserves_unmanaged_sections_and_adds_stable_anchors(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            metadata = inspect_project(project)
            existing = """# hello

Useful project description.

## Features
- Fast

## Language Support
English and Chinese are supported.

## Development
Run the tests before submitting changes.
"""

            content = render_optimized_readme(metadata, existing, lang="en")

            self.assertIn('<a name="highlights"></a>', content)
            self.assertIn("Language Support", content)
            self.assertIn("English and Chinese are supported.", content)
            self.assertIn("Development", content)

    def test_adds_cli_gif_when_existing_showcase_is_only_a_diagram(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            (project / "assets").mkdir()
            (project / "assets" / "cli-demo.gif").write_bytes(b"GIF89a")
            metadata = inspect_project(project)
            existing = """# hello

## Showcase
```mermaid
flowchart LR
  A --> B
```
"""

            content = render_optimized_readme(metadata, existing, lang="en")

            self.assertIn("assets/cli-demo.gif", content)


if __name__ == "__main__":
    unittest.main()
