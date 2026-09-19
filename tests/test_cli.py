import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from readme_magic import __version__
from readme_magic.cli import main


class CliTests(unittest.TestCase):
    def test_version_is_reported_by_cli_and_install_check(self):
        output = io.StringIO()
        with patch("sys.argv", ["readme-magic", "--version"]):
            with self.assertRaises(SystemExit) as exit_info:
                with redirect_stdout(output):
                    main()
        self.assertEqual(exit_info.exception.code, 0)
        self.assertEqual(output.getvalue().strip(), f"ReadmeMagic {__version__}")

        output = io.StringIO()
        with patch("sys.argv", ["readme-magic", "check-install"]):
            with redirect_stdout(output):
                main()
        self.assertIn(f"ReadmeMagic installation (v{__version__})", output.getvalue())

    def test_workflow_writes_state_and_reports_execution_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo"
            project.mkdir()
            output = io.StringIO()
            with patch("sys.argv", ["readme-magic", "workflow", "-p", str(project), "--json"]):
                with redirect_stdout(output):
                    main()
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["stage"], "discover")
            self.assertEqual(payload["readme_magic_version"], __version__)
            self.assertIn(payload["execution_mode"], ("hybrid", "agent_only"))
            self.assertTrue((project / "artifacts" / "workflow-state.json").exists())

    def test_optimize_result_exposes_independent_authorization_levels(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo"
            project.mkdir()
            (project / "README.md").write_text("# Demo\n\nA CLI tool.\n", encoding="utf-8")
            with patch("sys.argv", ["readme-magic", "optimize", "-p", str(project), "--no-preview", "--json"]):
                with redirect_stdout(io.StringIO()) as output:
                    main()
            result = json.loads(output.getvalue())
            self.assertEqual(result["readme_magic_version"], __version__)
            self.assertFalse(result["authorization"]["apply"])
            self.assertFalse(result["authorization"]["commit"])
            self.assertFalse(result["authorization"]["push"])
            self.assertEqual(result["interaction"]["module"], "readme-magic")
            self.assertEqual(result["interaction"]["version"], __version__)
            self.assertEqual(result["interaction"]["status"], "awaiting_user_review")
            self.assertIn("revise", result["interaction"]["next_actions"])
            self.assertEqual(result["interaction"]["events"][-1]["status"], "awaiting_user_review")
            self.assertTrue(Path(result["interaction_card"]).exists())

    def test_optimize_missing_readme_uses_creation_workflow_and_no_baseline(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo"
            project.mkdir()
            (project / "pyproject.toml").write_text(
                """[project]
name = "demo"
version = "0.1.0"
description = "A small command line demo."

[project.scripts]
demo = "demo:main"
""",
                encoding="utf-8",
            )
            with patch("sys.argv", ["readme-magic", "optimize", "-p", str(project), "--json"]):
                with redirect_stdout(io.StringIO()) as output:
                    main()
            result = json.loads(output.getvalue())

            self.assertEqual(result["workflow_kind"], "create")
            self.assertFalse(result["baseline_available"])
            self.assertIsNone(result["before"])
            self.assertTrue(result["output"].endswith("README.generated.md"))
            self.assertEqual(result["interaction"]["workflow_kind"], "create")
            self.assertFalse(result["interaction"]["baseline_available"])
            self.assertTrue(Path(result["preview"]["path"]).exists())
            self.assertFalse((project / "README.md").exists())

    def test_preview_lifecycle_requires_open_event(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo"
            project.mkdir()
            (project / "README.md").write_text("# Demo\n\nOriginal.\n", encoding="utf-8")
            with patch("sys.argv", ["readme-magic", "optimize", "-p", str(project), "--json"]):
                with redirect_stdout(io.StringIO()) as output:
                    main()
            result = json.loads(output.getvalue())
            self.assertEqual(result["interaction"]["status"], "preview_pending_open")
            with patch("sys.argv", ["readme-magic", "preview", "-p", str(project), "-i", "README.md", "--compare", "README.optimized.md", "--output", "opened.html", "--opened"]):
                with redirect_stdout(io.StringIO()):
                    main()
            state = json.loads((project / "artifacts" / "workflow-state.json").read_text(encoding="utf-8"))
            card = json.loads((project / "artifacts" / "interaction-card.json").read_text(encoding="utf-8"))
            self.assertEqual(state["preview_status"], "opened")
            self.assertEqual(state["status"], "awaiting_user_review")
            self.assertEqual(state["next_actions"], ["apply", "revise", "keep_original"])
            self.assertEqual(card["status"], "awaiting_user_review")
            self.assertIn("apply", card["next_actions"])

    def test_optimize_exposes_host_action_until_preview_is_opened(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo"
            project.mkdir()
            (project / "README.md").write_text("# Demo\n\nOriginal.\n", encoding="utf-8")
            with patch("sys.argv", ["readme-magic", "optimize", "-p", str(project), "--json"]):
                with redirect_stdout(io.StringIO()) as output:
                    main()
            result = json.loads(output.getvalue())
            action = result["interaction"]["host_action"]
            self.assertEqual(action["type"], "open_file")
            self.assertEqual(action["tool"], "mcp__codex_app__open_in_codex")
            self.assertIn("--opened", action["then"])

    def test_native_visuals_expose_generation_actions_without_fabricating_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo"
            project.mkdir()
            (project / "README.md").write_text("# Demo\n\nOriginal.\n", encoding="utf-8")
            with patch("sys.argv", ["readme-magic", "optimize", "-p", str(project), "--image-mode", "native", "--json"]):
                with redirect_stdout(io.StringIO()) as output:
                    main()
            result = json.loads(output.getvalue())
            actions = result["interaction"]["visual_actions"]
            self.assertEqual(len(actions), 3)
            self.assertTrue(all(item["tool"] == "image_generation" for item in actions))
            self.assertTrue(all(item["save_to"].startswith(str(project.resolve())) for item in actions))
            self.assertEqual(
                {asset["status"] for asset in result["asset_manifest"]["assets"]},
                {"native_required"},
            )

    def test_module_entrypoint_and_check_install_are_available(self):
        from readme_magic import __main__ as module_entry
        self.assertTrue(callable(module_entry.main))

        output = io.StringIO()
        with patch("sys.argv", ["readme-magic", "check-install"]):
            with redirect_stdout(output):
                main()
        self.assertIn("CLI: ready", output.getvalue())

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
            self.assertIn("SF Pro Text", preview)
            self.assertIn("review-header", preview)
            self.assertIn("publish_ready", result)
            self.assertIn("before_experience", result)
            self.assertIn("after_experience", result)
            self.assertEqual(result["interaction"]["events"][-1]["stage"], "review")
            self.assertEqual(result["interaction"]["target"].split("@", 1)[0], "demo")
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
