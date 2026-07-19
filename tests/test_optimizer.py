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
