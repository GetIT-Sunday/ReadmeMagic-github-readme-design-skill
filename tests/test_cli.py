import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from readme_magic.cli import main


class CliTests(unittest.TestCase):
    def test_inspect_json_exposes_profile_and_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo"
            project.mkdir()
            (project / "pyproject.toml").write_text(
                """[project]
name = "demo"
description = "A small command line demo."

[project.scripts]
demo = "demo:main"
""",
                encoding="utf-8",
            )
            output = io.StringIO()
            with patch("sys.argv", ["readme-magic", "inspect", "-p", str(project), "--json"]):
                with redirect_stdout(output):
                    main()

            payload = json.loads(output.getvalue())
            profile = payload["project"]
            self.assertEqual(profile["project_type"], "cli")
            self.assertEqual(
                profile["evidence"]["installation_commands"][0]["source"],
                "pyproject.toml",
            )

    def test_image_config_init_and_preview_compare(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo"
            project.mkdir()
            (project / "README.md").write_text("# Demo\n\nOriginal README.\n", encoding="utf-8")
            output = io.StringIO()
            with patch("sys.argv", ["readme-magic", "image-config", "-p", str(project), "--init"]):
                with redirect_stdout(output):
                    main()
            config = json.loads((project / ".readme-magic.json").read_text(encoding="utf-8"))
            self.assertEqual(config["image_generation"]["mode"], "prompt_only")

            (project / "README.optimized.md").write_text("# Demo\n\n## Highlights\n\nBetter.\n", encoding="utf-8")
            with patch("sys.argv", ["readme-magic", "preview", "-p", str(project), "-i", "README.md", "--compare", "README.optimized.md", "-o", "diff.html"]):
                with redirect_stdout(io.StringIO()):
                    main()
            preview = (project / "diff.html").read_text(encoding="utf-8")
            self.assertIn("comparison", preview)
            self.assertIn("README.optimized.md", preview)

    def test_optimize_creates_review_page_with_change_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo"
            project.mkdir()
            (project / "pyproject.toml").write_text(
                """[project]
name = "demo"
description = "A small command line demo."

[project.scripts]
demo = "demo:main"
""", encoding="utf-8"
            )
            (project / "README.md").write_text("# Demo\n\nOriginal description.\n", encoding="utf-8")
            with patch("sys.argv", ["readme-magic", "optimize", "-p", str(project), "--json"]):
                with redirect_stdout(io.StringIO()) as output:
                    main()
            result = json.loads(output.getvalue())
            preview_path = Path(result["preview"]["path"])
            self.assertTrue(preview_path.exists())
            preview = preview_path.read_text(encoding="utf-8")
            self.assertIn("What changed", preview)
            self.assertIn("README.md", preview)
            self.assertIn("README.optimized.md", preview)
            self.assertIn("Original content &amp; evidence", preview)
            self.assertIn("Candidate content &amp; evidence", preview)
            self.assertIn("Original reading experience", preview)
            self.assertIn("Candidate reading experience", preview)
            self.assertIn("Original · README.md · Back-to-top:", preview)
            self.assertIn("Optimized candidate · README.optimized.md · Back-to-top:", preview)
            self.assertIn("Concrete presentation changes", preview)
            self.assertIn("Back-to-top controls", preview)
            self.assertIn("Source verification", preview)
            self.assertIn("publish_ready", result)
            self.assertIn("before_experience", result)
            self.assertIn("after_experience", result)
            self.assertNotIn("From source", result["preview"]["summary"]["added_sections"])

    def test_preview_marks_mermaid_blocks_for_rendering(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo"
            project.mkdir()
            readme = project / "README.md"
            readme.write_text("# Demo\n\n```mermaid\nflowchart LR\n A --> B\n```\n", encoding="utf-8")
            with patch("sys.argv", ["readme-magic", "preview", "-p", str(project), "-i", "README.md", "-o", "preview.html"]):
                with redirect_stdout(io.StringIO()):
                    main()
            preview = (project / "preview.html").read_text(encoding="utf-8")
            self.assertIn('class="mermaid"', preview)
            self.assertIn("mermaid.initialize", preview)

    def test_preview_renders_readme_html_and_language_switch(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo"
            project.mkdir()
            readme = project / "README.md"
            readme.write_text(
                '<p align="center"><strong>English</strong> | '
                '<a href="README_ZH.md">中文</a></p>\n\n'
                '<table><tr><td><h3>Project-aware Analysis</h3>'
                '<ul><li>Verified evidence</li></ul></td></tr></table>\n',
                encoding="utf-8",
            )
            with patch("sys.argv", ["readme-magic", "preview", "-p", str(project), "-i", "README.md", "-o", "preview.html"]):
                with redirect_stdout(io.StringIO()):
                    main()
            preview = (project / "preview.html").read_text(encoding="utf-8")
            self.assertIn("<h3>Project-aware Analysis</h3>", preview)
            self.assertIn('<a href="README_ZH.md">中文</a>', preview)
            self.assertIn("<table>", preview)
            self.assertNotIn("&lt;h3&gt;", preview)


if __name__ == "__main__":
    unittest.main()
