import tempfile
import unittest
from pathlib import Path

from readme_magic.analyzer import inspect_project
from readme_magic.experience import (
    analyze_experience,
    apply_safe_experience_fixes,
    audit_repository_consistency,
)


class ExperienceTests(unittest.TestCase):
    def test_reports_localized_findings_with_fix_classes(self):
        readme = """# Demo

<p align="center"><a href="#missing">Missing</a></p>

## Usage

Text.

<div align="right"><a href="#demo">↑ back to top</a></div>

## Usage

More text.

<div align="right"><a href="#demo">↑ back to top</a></div>
"""
        report = analyze_experience(readme)
        findings = {finding.code: finding for finding in report.findings}
        self.assertIn("duplicate_sections", findings)
        self.assertEqual(findings["duplicate_sections"].section, "global")
        self.assertEqual(findings["duplicate_sections"].remediation, "suggested_fix")
        self.assertIn("broken_navigation_anchor", findings)
        self.assertEqual(findings["broken_navigation_anchor"].remediation, "safe_fix")
        self.assertIn("repeated_back_to_top", findings)
        self.assertTrue(findings["repeated_back_to_top"].auto_fix)

    def test_safe_fix_limits_navigation_and_normalizes_star_history(self):
        padding = "\n".join(f"line {index}" for index in range(260))
        back = '<div align="right"><a href="#demo">↑ back to top</a></div>'
        readme = (
            '<a name="demo"></a>\n# Demo\n\n## One\n' + padding + "\n" + back
            + "\n\n## Two\n" + padding + "\n" + back
            + "\n\n## Three\n" + padding + "\n" + back
            + "\n\n## Four\n" + padding + "\n" + back
            + '\n\n<p align="center"><a href="https://star-history.com/#wrong/repo&Date">'
              '<img src="assets/star-history.png" alt="Star History"></a></p>'
            + "\n\n## License\nMIT\n" + back + "\n"
        )
        fixed = apply_safe_experience_fixes(readme, "owner/demo")
        self.assertEqual(fixed.lower().count("back to top"), 0)
        self.assertNotIn("wrong/repo", fixed)
        self.assertNotIn("assets/star-history.png", fixed)
        self.assertEqual(fixed.count("api.star-history.com/svg?repos=owner/demo&type=Date"), 1)
        self.assertTrue(fixed.rstrip().endswith("</p>"))

    def test_safe_fix_reduces_rules_and_repeated_ctas(self):
        readme = """# Demo

---
## One
Please consider giving this project a star ⭐.
---
## Two
Text.
---
## Three
Text.
---
## Four
If Demo saved you time, consider giving it a ⭐.
"""
        fixed = apply_safe_experience_fixes(readme)
        self.assertLessEqual(fixed.count("\n---\n"), 2)
        report = analyze_experience(fixed)
        self.assertNotIn("repeated_call_to_action", {finding.code for finding in report.findings})

    def test_safe_fix_removes_only_broken_header_navigation(self):
        readme = """# Demo

<p align="center"><a href="#usage">Usage</a> · <a href="#examples">Examples</a></p>

## Usage

Text.
"""
        fixed = apply_safe_experience_fixes(readme)
        self.assertIn('href="#usage"', fixed)
        self.assertNotIn('href="#examples"', fixed)

    def test_star_history_is_not_required_without_known_repo(self):
        report = analyze_experience("# Local\n\n## Usage\n\nText.\n")
        self.assertNotIn("community_star_history", {finding.code for finding in report.findings})

    def test_bilingual_language_switch_is_not_reported_as_asset_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "README.md").write_text(
                '<p align="center"><a href="README_ZH.md">中文</a></p>\n'
                '<p align="center"><img src="assets/banner.png" alt="banner"></p>\n',
                encoding="utf-8",
            )
            (project / "README_ZH.md").write_text(
                '<p align="center"><a href="README.md">English</a></p>\n'
                '<p align="center"><img src="assets/banner.png" alt="banner"></p>\n',
                encoding="utf-8",
            )
            metadata = inspect_project(project)
            findings = audit_repository_consistency(project, metadata)
            self.assertNotIn("bilingual_asset_mismatch", {item.code for item in findings})


if __name__ == "__main__":
    unittest.main()
