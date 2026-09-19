import json
from pathlib import Path
import tempfile
import unittest

from readme_magic.analyzer import inspect_project
from readme_magic.assets import extract_paper_context, load_image_config, materialize_assets, plan_assets


class AssetTests(unittest.TestCase):
    def _project(self, root: str) -> Path:
        project = Path(root) / "demo"
        project.mkdir()
        (project / "pyproject.toml").write_text(
            """[project]
name = "demo"
description = "A small reusable project."
""", encoding="utf-8"
        )
        return project

    def test_config_file_and_overrides(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            (project / ".readme-magic.json").write_text(json.dumps({
                "image_generation": {"mode": "disabled", "provider": "custom", "model": "x"}
            }), encoding="utf-8")
            configured = load_image_config(project)
            self.assertEqual(configured.mode, "disabled")
            overridden = load_image_config(project, overrides={"mode": "prompt_only", "model": "y"})
            self.assertEqual(overridden.mode, "prompt_only")
            self.assertEqual(overridden.model, "y")

    def test_prompt_only_writes_prompts_and_manifest_without_images(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            metadata = inspect_project(project)
            config = load_image_config(project, overrides={"mode": "prompt_only"})
            manifest = materialize_assets(project, plan_assets(metadata, config), config)
            self.assertEqual({asset.status for asset in manifest.assets}, {"prompt_ready"})
            self.assertTrue((project / "artifacts" / "prompts" / "architecture.prompt.md").exists())
            self.assertTrue((project / "artifacts" / "asset-manifest.json").exists())
            self.assertFalse((project / "assets" / "generated" / "architecture.png").exists())
            self.assertEqual(manifest.optional_skills["cli-demo"], False)

    def test_prompt_only_reuses_user_supplied_image(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            image = project / "assets" / "generated" / "architecture.png"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"png")
            metadata = inspect_project(project)
            config = load_image_config(project, overrides={"mode": "prompt_only"})
            manifest = materialize_assets(project, plan_assets(metadata, config), config)
            architecture = next(asset for asset in manifest.assets if asset.key == "architecture")
            self.assertEqual(architecture.status, "available")
            self.assertEqual(architecture.path, "assets/generated/architecture.png")

    def test_disabled_mode_only_plans_mandatory_visuals(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            metadata = inspect_project(project)
            config = load_image_config(project, overrides={"mode": "disabled"})
            manifest = materialize_assets(project, plan_assets(metadata, config), config)
            self.assertEqual(len(manifest.assets), 3)
            self.assertTrue(all(asset.status == "disabled" for asset in manifest.assets))

    def test_native_mode_records_host_generation_request_without_fabricating_image(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            metadata = inspect_project(project)
            config = load_image_config(project, overrides={"mode": "native"})
            manifest = materialize_assets(project, plan_assets(metadata, config), config)
            self.assertEqual({asset.status for asset in manifest.assets}, {"native_required"})
            self.assertTrue((project / "artifacts" / "prompts" / "architecture.prompt.md").exists())
            self.assertFalse((project / "assets" / "generated" / "architecture.png").exists())

    def test_rejects_output_directory_outside_project(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            metadata = inspect_project(project)
            config = load_image_config(project, overrides={"output_dir": "/tmp/generated"})
            with self.assertRaises(ValueError):
                plan_assets(metadata, config)

    def test_extracts_latex_title_abstract_and_captions(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self._project(directory)
            (project / "paper.tex").write_text(
                r"""\title{A Grounded README Agent}
\begin{abstract}
We generate repository-aware documentation.
\end{abstract}
\caption{Evidence planning pipeline}
""", encoding="utf-8")
            context = extract_paper_context(project, ["paper.tex"])
            self.assertEqual(context["title"], "A Grounded README Agent")
            self.assertIn("repository-aware", context["abstract"])
            self.assertEqual(context["figure_captions"], "Evidence planning pipeline")


if __name__ == "__main__":
    unittest.main()
