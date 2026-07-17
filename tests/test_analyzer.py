import json
from pathlib import Path
import tempfile
import unittest

from readme_magic.analyzer import inspect_project


class AnalyzerTests(unittest.TestCase):
    def test_inspects_python_cli_project(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo-cli"
            project.mkdir()
            (project / "pyproject.toml").write_text(
                """[project]
name = "demo-cli"
version = "1.2.3"
description = "A reliable demo command."
requires-python = ">=3.10"

[project.scripts]
demo = "demo.cli:main"
""",
                encoding="utf-8",
            )
            (project / "LICENSE").write_text("MIT License", encoding="utf-8")
            metadata = inspect_project(project)

            self.assertEqual(metadata.name, "demo-cli")
            self.assertEqual(metadata.version, "1.2.3")
            self.assertEqual(metadata.language, "Python")
            self.assertEqual(metadata.template, "cli-tool")
            self.assertEqual(metadata.project_type, "cli")
            self.assertGreaterEqual(metadata.type_confidence, 0.8)
            self.assertEqual(metadata.license, "MIT")
            self.assertEqual(metadata.usage_commands, ["demo --help"])
            self.assertEqual(
                metadata.evidence["usage_commands"][0].source, "pyproject.toml"
            )
            self.assertEqual(metadata.evidence["license"][0].source, "LICENSE")

    def test_inspects_node_project(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "demo-web"
            project.mkdir()
            (project / "package.json").write_text(
                json.dumps({
                    "name": "demo-web",
                    "version": "2.0.0",
                    "description": "A small web app.",
                    "scripts": {"dev": "vite"},
                    "engines": {"node": ">=20"},
                }),
                encoding="utf-8",
            )
            (project / "pnpm-lock.yaml").write_text("lockfileVersion: 9", encoding="utf-8")
            metadata = inspect_project(project)

            self.assertEqual(metadata.language, "JavaScript / TypeScript")
            self.assertEqual(metadata.project_type, "product")
            self.assertEqual(metadata.install_commands, ["pnpm install"])
            self.assertEqual(metadata.usage_commands, ["pnpm run dev"])

    def test_does_not_invent_missing_version_or_license(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "unknown"
            project.mkdir()
            metadata = inspect_project(project)

            self.assertEqual(metadata.version, "Not specified")
            self.assertEqual(metadata.license, "Not specified")

    def test_discovers_showcase_assets_in_priority_order(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "visual-app"
            (project / "assets").mkdir(parents=True)
            (project / "docs").mkdir()
            (project / "assets" / "logo.svg").write_text("<svg/>", encoding="utf-8")
            (project / "docs" / "product-screenshot.png").write_bytes(b"png")
            (project / "assets" / "build-badge.svg").write_text("<svg/>", encoding="utf-8")

            metadata = inspect_project(project)

            self.assertEqual(metadata.visual_assets[0], "docs/product-screenshot.png")
            self.assertIn("assets/logo.svg", metadata.visual_assets)
            self.assertNotIn("assets/build-badge.svg", metadata.visual_assets)
            self.assertEqual(
                metadata.evidence["screenshots"][0].value,
                "docs/product-screenshot.png",
            )
            self.assertEqual(metadata.evidence["brand_assets"][0].value, "assets/logo.svg")

    def test_classifies_knowledge_repository_without_installation_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "awesome-databases"
            project.mkdir()
            (project / "README.md").write_text(
                "# Awesome Databases\n\nA curated learning resources guide for databases.\n",
                encoding="utf-8",
            )

            metadata = inspect_project(project)

            self.assertEqual(metadata.project_type, "knowledge")
            self.assertEqual(metadata.evidence["installation_commands"], [])
            self.assertEqual(metadata.evidence["usage_commands"], [])

    def test_classifies_ai_library_and_keeps_evidence_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "model-kit"
            project.mkdir()
            (project / "pyproject.toml").write_text(
                """[project]
name = "model-kit"
description = "Utilities for transformer inference."
dependencies = ["transformers", "torch"]
""",
                encoding="utf-8",
            )

            metadata = inspect_project(project)

            self.assertEqual(metadata.project_type, "ai")
            self.assertEqual(metadata.template, "ai-project")
            self.assertEqual(
                metadata.evidence["installation_commands"][0].source,
                "pyproject.toml",
            )

    def test_classifies_library_from_manifest_without_application_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "math-kit"
            project.mkdir()
            (project / "Cargo.toml").write_text(
                """[package]
name = "math-kit"
version = "0.1.0"
description = "Reusable numeric helpers"
""",
                encoding="utf-8",
            )

            metadata = inspect_project(project)

            self.assertEqual(metadata.project_type, "library")
            self.assertEqual(metadata.template, "library")
            self.assertEqual(metadata.evidence["usage_commands"][0].source, "Cargo.toml")

    def test_does_not_classify_ai_from_unrelated_readme_prose(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "readme-agent-tools"
            project.mkdir()
            (project / "pyproject.toml").write_text(
                """[project]
name = "readme-agent-tools"
description = "A README documentation utility."
""",
                encoding="utf-8",
            )
            (project / "README.md").write_text(
                "# Documentation\n\nThis agent workflow improves repository docs.\n",
                encoding="utf-8",
            )

            metadata = inspect_project(project)

            self.assertNotEqual(metadata.project_type, "ai")


if __name__ == "__main__":
    unittest.main()
