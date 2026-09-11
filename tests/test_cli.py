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


if __name__ == "__main__":
    unittest.main()
