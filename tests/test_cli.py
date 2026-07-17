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


if __name__ == "__main__":
    unittest.main()
