"""ReadmeMagic CLI - One spell, beautiful README"""
import argparse
import difflib
import hashlib
import html as html_lib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from markdown_it import MarkdownIt

from . import __version__
from .analyzer import inspect_project
from .assets import DEFAULT_CONFIG, IMAGE_MODES, load_image_config
from .experience import analyze_experience, audit_repository_consistency
from .optimizer import optimize_project
from .quality import analyze_readme
from .workflow import STAGES, create_state, mark_preview_opened, save_state

TEMPLATES_DIR = Path(__file__).parent / "templates"

TEMPLATE_CHOICES = ["standard", "ai-project", "cli-tool", "library", "personal"]
LANG_CHOICES = ["en", "zh", "bilingual"]

TEMPLATE_DESCRIPTIONS = {
    "en": {
        "standard":   "General open-source projects",
        "ai-project": "AI / ML / deep learning projects",
        "cli-tool":   "Command-line tools",
        "library":    "Reusable libraries and frameworks",
        "personal":   "Personal portfolio projects",
    },
    "zh": {
        "standard":   "通用开源项目",
        "ai-project": "AI / 机器学习 / 深度学习项目",
        "cli-tool":   "命令行工具",
        "library":    "可复用库 / 框架",
        "personal":   "个人作品集项目",
    },
}


def _print_report(report, experience=None) -> None:
    report_dict = report.to_dict()
    print(f"Core Documentation: {report_dict['core_score']}/{report_dict['core_max_score']}")
    print(f"Showcase Enhancement: {report_dict['presentation_score']}/{report_dict['presentation_max_score']}")
    print(f"Overall README score: {report.score}/{report.max_score}")
    if experience is not None:
        print(f"Reading Experience: {experience.score}/{experience.max_score}")
        ready = report_dict["core_quality_gate"] and experience.score >= 80 and not any(
            finding.severity == "high" for finding in report.findings + experience.findings
        )
        print(f"Publish readiness: {'Ready for review' if ready else 'Not ready'}")
        print(f"Quality tier: {report_dict['tier']} | Showcase completeness: {'PASS' if report_dict['strict_evidence_gate'] else 'OPTIONAL GAPS'}")
    print("Dimensions: " + " | ".join(
        f"{name} {value}" for name, value in report.dimensions.items()
    ))
    if not report.findings:
        print("No quality issues found.")
        return
    for finding in report.findings:
        print(f"- [{finding.severity}] {finding.message}")
        print(f"  {finding.recommendation}")
    if experience is not None:
        for finding in experience.findings:
            print(f"- [{finding.severity}] {finding.code} ({finding.section}): {finding.message}")
            print(f"  {finding.recommendation}")


def _print_inspection(metadata) -> None:
    """Print the evidence inventory used by the README planner."""
    print(f"Project: {metadata.name}")
    print(f"Type: {metadata.project_type} (confidence {metadata.type_confidence:.0%})")
    print(f"Language: {metadata.language}")
    print(f"README: {'present' if metadata.readme_path else 'missing (first-README flow)'}")
    if metadata.type_reasons:
        print("Why: " + "; ".join(metadata.type_reasons))
    labels = {
        "installation_commands": "Installation",
        "usage_commands": "Usage",
        "screenshots": "Screenshots",
        "demos": "Demos / outputs",
        "benchmarks": "Benchmarks",
        "architecture_assets": "Architecture assets",
        "documentation_links": "Documentation",
        "contribution_guide": "Contribution guide",
        "security_policy": "Security policy",
        "license": "License",
    }
    print("Evidence:")
    for key, label in labels.items():
        items = metadata.evidence.get(key, [])
        if items:
            values = ", ".join(item.value for item in items[:4])
            suffix = " ..." if len(items) > 4 else ""
            print(f"- {label}: {values}{suffix}")
        else:
            print(f"- {label}: missing")


def _git_ref(project: Path) -> str:
    """Return the current branch when the target is a local checkout."""
    try:
        result = subprocess.run(
            ["git", "-C", str(project), "branch", "--show-current"],
            capture_output=True, text=True, check=False,
        )
        return result.stdout.strip()
    except OSError:
        return ""


def _interaction_events(
    target: str,
    execution_mode: str,
    candidate: str,
    preview: str = "",
    actions=None,
    review_status: str = "awaiting_user_review",
    workflow_kind: str = "optimize",
) -> list:
    """Return a compact event stream that hosts can render as tool-like progress."""
    events = [
        {"stage": "discover", "status": "completed", "label": "Resolved target repository"},
        {"stage": "inspect", "status": "completed", "label": "Collected repository evidence"},
        {"stage": "score", "status": "completed", "label": "Scored content and reading experience"},
        {"stage": "plan", "status": "completed", "label": "Classified safe fixes and review items"},
        {"stage": "optimize", "status": "completed",
         "label": "Wrote first README candidate" if workflow_kind == "create" else "Wrote candidate README",
         "artifact": candidate},
    ]
    if preview:
        events.append({"stage": "preview", "status": "completed", "label": "Rendered before/after preview", "artifact": preview})
    events.append({
        "stage": "review",
        "status": review_status,
        "label": "Waiting for preview to be opened" if review_status == "preview_pending_open" else "Waiting for user review",
        "target": target,
        "execution_mode": execution_mode,
        "actions": actions or ["apply", "revise", "keep_original"],
    })
    return events


def _template_path(template: str, lang: str) -> Path:
    """Return the path to a template file, falling back to 'en' if not found."""
    path = TEMPLATES_DIR / lang / f"{template}.md"
    if not path.exists():
        # Fallback: try the root templates/ directory (legacy location)
        fallback = TEMPLATES_DIR / f"{template}.md"
        if fallback.exists():
            return fallback
        # Final fallback: English variant
        en_path = TEMPLATES_DIR / "en" / f"{template}.md"
        if en_path.exists():
            return en_path
        return path  # will raise a clear error on open()
    return path


def _load_template(template: str, lang: str) -> str:
    path = _template_path(template, lang)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"❌ Template not found: {path}", file=sys.stderr)
        print(f"   Run 'readme-magic templates' to list available templates.", file=sys.stderr)
        sys.exit(1)


def _banner_prompt(project_name: str) -> str:
    return (
        f"A wide horizontal GitHub repository banner image for a project called "
        f"'{project_name}'. Dark background (#0d1117 GitHub dark theme). "
        f"Modern, minimal design with subtle gradient and geometric accents. "
        f"Project name in large, clean sans-serif white text. "
        f"No logos of real companies or people. No text other than the project name."
    )


def _generate_banner_via_openai(project_name: str, banner_path: Path, api_key: str) -> bool:
    """Call OpenAI Images API directly using requests (no openai package required)."""
    import base64 as _b64
    import json as _json
    import urllib.request as _req
    import urllib.error as _uerr

    prompt = _banner_prompt(project_name)
    payload = _json.dumps({
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "1536x1024",
        "output_format": "png",
        "quality": "standard",
    }).encode()

    request = _req.Request(
        "https://api.openai.com/v1/images/generations",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with _req.urlopen(request, timeout=60) as resp:
            data = _json.loads(resp.read())
        b64_data = data["data"][0].get("b64_json")
        if not b64_data:
            # Some models return a URL instead
            url = data["data"][0].get("url")
            if url:
                with _req.urlopen(url, timeout=30) as img_resp:
                    banner_path.write_bytes(img_resp.read())
                return True
            return False
        banner_path.write_bytes(_b64.b64decode(b64_data))
        return True
    except _uerr.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"⚠️  OpenAI API error {e.code}: {body[:200]}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"⚠️  Banner generation error: {e}", file=sys.stderr)
        return False


def _generate_banner_via_dodo(project_name: str, banner_path: Path) -> bool:
    """Call gpt_image.py from the dodo sandbox environment."""
    # Try both the skill directory and the known dodo sandbox path
    candidates = [
        Path(__file__).parent.parent / "gpt_image.py",
        Path("/home/gem/workspace/.claude/skills/gpt-image/scripts/gpt_image.py"),
    ]
    gpt_image_script = next((p for p in candidates if p.exists()), None)
    if not gpt_image_script:
        return False

    prompt = _banner_prompt(project_name)
    result = subprocess.run(
        [sys.executable, str(gpt_image_script),
         "--prompt", prompt,
         "--output", str(banner_path),
         "--size", "1536x1024"],
        capture_output=True, text=True,
    )
    return result.returncode == 0 and banner_path.exists()


def _generate_banner(repo: str, project_name: str, output_dir: Path) -> str:
    """Generate a banner image and return the local relative path, or '' on failure.

    Resolution order:
    1. OPENAI_API_KEY env var → call OpenAI Images API directly (works everywhere)
    2. dodo sandbox gpt_image.py helper → call it via subprocess
    3. Neither available → print guidance and return ''
    """
    banner_path = output_dir / "assets" / "banner.png"
    banner_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"🎨 Generating banner → {banner_path}")

    # ── Strategy 1: OPENAI_API_KEY ────────────────────────────────────────────
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if api_key:
        print("   Using OPENAI_API_KEY …")
        if _generate_banner_via_openai(project_name, banner_path, api_key):
            print(f"✅ Banner saved → {banner_path}")
            return "assets/banner.png"
        print("⚠️  OpenAI generation failed, trying dodo sandbox …", file=sys.stderr)

    # ── Strategy 2: dodo sandbox gpt_image.py ────────────────────────────────
    if _generate_banner_via_dodo(project_name, banner_path):
        print(f"✅ Banner saved → {banner_path}")
        return "assets/banner.png"

    # ── Strategy 3: give up with helpful message ──────────────────────────────
    print(
        "\n⚠️  --gen-banner could not auto-generate a banner.\n"
        "   To enable auto-generation, choose one of:\n"
        "     A) Set OPENAI_API_KEY environment variable (works anywhere)\n"
        "        export OPENAI_API_KEY=sk-...\n"
        "     B) Run inside the dodo AI sandbox (gpt_image.py is available there)\n"
        "\n"
        "   Alternatively, create a banner manually and use:\n"
        "        --banner assets/banner.png",
        file=sys.stderr,
    )
    return ""


def _build_banner(banner_path: str, project_name: str) -> str:
    """Return the Markdown/HTML block to embed a banner at the top of a README."""
    if not banner_path:
        return ""
    return (
        f'<a name="{project_name.lower().replace(" ", "-")}"></a>\n'
        f'<p align="center">\n'
        f'  <img src="{banner_path}" alt="{project_name} banner" width="100%">\n'
        f'</p>\n'
    )

def _generate_readme(args) -> str:
    """Load the selected template and substitute known placeholders."""
    content = _load_template(args.template, args.lang)

    # Determine project name from path
    project_path = Path(args.project_path).resolve()
    project_name = project_path.name if project_path.exists() else args.project_path

    # Banner block
    banner_md = ""
    if args.banner:
        # User supplied an existing path/URL directly
        banner_md = _build_banner(args.banner, project_name)
    elif args.gen_banner:
        output_dir = Path(args.output).parent.resolve()
        banner_local = _generate_banner(
            args.repo or f"owner/{project_name}", project_name, output_dir
        )
        banner_md = _build_banner(banner_local, project_name)

    # Basic placeholder substitutions
    substitutions = {
        "{{PROJECT_NAME}}": project_name,
        "{{PRIMARY_COLOR}}": args.primary_color,
        "{{SECONDARY_COLOR}}": args.secondary_color,
        "{{BANNER}}": banner_md,
    }

    # Badge block
    if args.badges:
        badge_list = [b.strip() for b in args.badges.split(",")]
        badge_md = _build_badges(badge_list, args.repo or f"owner/{project_name}")
        substitutions["{{BADGES}}"] = badge_md

    # Star History
    if args.star_history and args.repo:
        substitutions["{{STAR_HISTORY}}"] = _build_star_history(args.repo)

    for key, value in substitutions.items():
        content = content.replace(key, value)

    # Prepend banner before first line if template has no {{BANNER}} placeholder
    if banner_md and "{{BANNER}}" not in _load_template(args.template, args.lang):
        content = banner_md + "\n" + content

    return content



def _build_badges(badge_names: list, repo: str) -> str:
    mapping = {
        "version": f'<img src="https://img.shields.io/badge/version-{__version__}-blue?style=flat-square" alt="Version">',
        "license": f'<img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">',
        "python":  f'<img src="https://img.shields.io/badge/python-3.8+-yellow?style=flat-square" alt="Python">',
        "stars":   f'<img src="https://img.shields.io/github/stars/{repo}?style=social" alt="Stars">',
        "forks":   f'<img src="https://img.shields.io/github/forks/{repo}?style=social" alt="Forks">',
        "issues":  f'<img src="https://img.shields.io/github/issues/{repo}" alt="Issues">',
    }
    badges = [mapping[b] for b in badge_names if b in mapping]
    if not badges:
        return ""
    return '<p align="center">\n  ' + "\n  ".join(badges) + "\n</p>"


def _build_star_history(repo: str) -> str:
    return (
        f'<p align="center">\n'
        f'  <a href="https://star-history.com/#{repo}&Date">\n'
        f'    <img src="https://api.star-history.com/svg?repos={repo}&type=Date" '
        f'alt="Star History Chart" width="600">\n'
        f'  </a>\n'
        f'</p>'
    )


def _markdown_to_html(markdown: str) -> str:
    """Render GitHub-like Markdown while preserving README presentation HTML."""
    renderer = MarkdownIt("commonmark", {"html": True}).enable(["table", "strikethrough"])
    rendered = renderer.render(markdown)
    # Mermaid needs a div for the browser-side Mermaid runtime rather than a
    # normal fenced-code block.
    return re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        r'<div class="mermaid">\1</div>',
        rendered,
        flags=re.S,
    )


def _heading_titles(markdown: str) -> list:
    # Ignore fenced examples so shell comments are not reported as README sections.
    markdown = re.sub(r"(?ms)^```[^\n]*\n.*?^```\s*$", "", markdown)
    return [
        re.sub(r"[`*_]", "", match.group(2)).strip()
        for match in re.finditer(r"(?m)^(#{1,6})\s+(.+?)\s*$", markdown)
    ]


def _preview_summary(
    before: str,
    after: str,
    before_score=None,
    after_score=None,
    before_experience=None,
    after_experience=None,
    after_report=None,
) -> dict:
    before_titles = _heading_titles(before)
    after_titles = _heading_titles(after)
    before_set = set(before_titles)
    after_set = set(after_titles)
    ratio = difflib.SequenceMatcher(None, before, after).ratio()
    summary = {
        "before_lines": len(before.splitlines()),
        "after_lines": len(after.splitlines()),
        "similarity": round(ratio, 3),
        "added_sections": [title for title in after_titles if title not in before_set],
        "removed_sections": [title for title in before_titles if title not in after_set],
        "preserved_sections": [title for title in after_titles if title in before_set],
        "before_sha256": hashlib.sha256(before.encode("utf-8")).hexdigest()[:12],
        "after_sha256": hashlib.sha256(after.encode("utf-8")).hexdigest()[:12],
        "presentation_changes": {
            "back_to_top": {
                "before": len(re.findall(r"(?i)back\s+to\s+top|返回顶部|回到顶部", before)),
                "after": len(re.findall(r"(?i)back\s+to\s+top|返回顶部|回到顶部", after)),
            },
            "horizontal_rules": {
                "before": len(re.findall(r"(?m)^\s*---+\s*$", before)),
                "after": len(re.findall(r"(?m)^\s*---+\s*$", after)),
            },
            "star_history": {
                "before": len(re.findall(r"api\.star-history\.com/svg\?repos=", before, re.I)),
                "after": len(re.findall(r"api\.star-history\.com/svg\?repos=", after, re.I)),
            },
        },
    }
    if before_score is not None:
        summary["before_score"] = before_score
    if after_score is not None:
        summary["after_score"] = after_score
    if after_report is not None:
        report = after_report.to_dict()
        summary["after_quality_tier"] = report["tier"]
        summary["strict_evidence_gate"] = report["strict_evidence_gate"]
        summary["evidence_findings"] = [
            {"code": finding.code, "severity": finding.severity, "message": finding.message}
            for finding in after_report.findings
            if finding.code in {"visual_story", "showcase_evidence", "architecture_quality", "dynamic_demo"}
        ]
    if before_experience is not None:
        summary["before_experience_score"] = before_experience.score
    if after_experience is not None:
        summary["after_experience_score"] = after_experience.score
        summary["experience_findings"] = [
            {
                "code": finding.code,
                "section": finding.section,
                "severity": finding.severity,
                "message": finding.message,
                "remediation": finding.remediation,
            }
            for finding in after_experience.findings
        ]
        summary["remediation_counts"] = after_experience.to_dict()["remediation_counts"]
        after_report_dict = after_report.to_dict() if after_report is not None else {}
        summary["core_score"] = after_report_dict.get("core_score", 0)
        summary["core_max_score"] = after_report_dict.get("core_max_score", 70)
        summary["presentation_score"] = after_report_dict.get("presentation_score", 0)
        summary["presentation_max_score"] = after_report_dict.get("presentation_max_score", 30)
        summary["publish_ready"] = bool(
            after_report_dict.get("core_quality_gate", False)
            and after_experience.score >= 80
            and not any(finding.severity == "high" for finding in after_experience.findings)
        )
    return summary


def _summary_panel(summary: dict) -> str:
    if not summary:
        return ""
    baseline_available = summary.get("baseline_available", True)
    before_score = summary.get("before_score", "-") if baseline_available else "—"
    after_score = summary.get("after_score", "-")
    before_experience = summary.get("before_experience_score", "-") if baseline_available else "—"
    after_experience = summary.get("after_experience_score", "-")
    similarity = "{:.0%}".format(summary.get("similarity", 0)) if baseline_available else "—"

    def items(values, empty="None"):
        return "".join(f"<li>{html_lib.escape(value)}</li>" for value in values) or f"<li class=\"muted\">{empty}</li>"

    asset_statuses = summary.get("asset_statuses", {})
    asset_text = ", ".join(f"{key}: {value}" for key, value in sorted(asset_statuses.items())) or "Not generated"
    readiness = "Ready for review" if summary.get("publish_ready") else "Not ready"
    tier = summary.get("after_quality_tier", "-")
    evidence_gate = "PASS" if summary.get("strict_evidence_gate") else "OPTIONAL GAPS"
    review_status = "AWAITING USER REVIEW"
    workflow_label = "OPTIMIZE EXISTING README" if baseline_available else "CREATE FIRST README"
    remediation = summary.get("remediation_counts", {})
    experience_items = "".join(
        f'<li><code>{html_lib.escape(item["code"])}</code> · {html_lib.escape(item["section"])} · '
        f'{html_lib.escape(item["message"])}</li>'
        for item in summary.get("experience_findings", [])
    ) or '<li class="muted">No remaining reading-experience findings</li>'
    presentation = summary.get("presentation_changes", {})

    def delta_card(key, label):
        values = presentation.get(key, {})
        before = values.get("before", "-")
        after = values.get("after", "-")
        changed = before != after
        css = "delta changed" if changed else "delta"
        return (
            f'<div class="{css}"><strong>{html_lib.escape(str(before))} → '
            f'{html_lib.escape(str(after))}</strong><span>{html_lib.escape(label)}</span></div>'
        )

    return (
        '<aside class="audit-panel">'
        '<div class="review-header">'
        f'<div class="review-eyebrow">README REVIEW · READMEMAGIC · {workflow_label}</div>'
        '<h1>Make the project easier to understand.</h1>'
        f'<p>{"Evidence-backed before/after review for a more useful GitHub landing page." if baseline_available else "Evidence-backed first README draft for a more useful GitHub landing page."}</p>'
        '</div>'
        f'<div class="review-banner">{review_status}<span>{"Choose apply, revise, or keep the original after inspecting both columns." if baseline_available else "Review the generated candidate, then choose apply, revise, or keep the project without a README."}</span></div>'
        '<h2>What changed</h2>'
        '<div class="metrics">'
        f'<div><strong>{html_lib.escape(str(before_score))}</strong><span>{"Original content &amp; evidence" if baseline_available else "No baseline README"}</span></div>'
        f'<div><strong>{html_lib.escape(str(after_score))}</strong><span>Candidate content &amp; evidence</span></div>'
        f'<div><strong>{html_lib.escape(str(summary.get("core_score", "-")))}/{html_lib.escape(str(summary.get("core_max_score", 70)))}</strong><span>Core documentation</span></div>'
        f'<div><strong>{html_lib.escape(str(summary.get("presentation_score", "-")))}/{html_lib.escape(str(summary.get("presentation_max_score", 30)))}</strong><span>Showcase enhancement</span></div>'
        f'<div><strong>{html_lib.escape(str(before_experience))}</strong><span>{"Original reading experience" if baseline_available else "No baseline experience"}</span></div>'
        f'<div><strong>{html_lib.escape(str(after_experience))}</strong><span>Candidate reading experience</span></div>'
        f'<div><strong>{readiness}</strong><span>Publish readiness</span></div>'
        f'<div><strong>{html_lib.escape(str(tier))}</strong><span>Quality tier</span></div>'
        f'<div><strong>{evidence_gate}</strong><span>Showcase completeness</span></div>'
        f'<div><strong>{html_lib.escape(str(summary.get("before_lines", 0) if baseline_available else "—"))}</strong><span>{"Original lines" if baseline_available else "Baseline lines"}</span></div>'
        f'<div><strong>{html_lib.escape(str(summary.get("after_lines", 0)))}</strong><span>Candidate lines</span></div>'
        f'<div><strong>{similarity}</strong><span>Text similarity</span></div>'
        '</div>'
        '<h3 class="audit-subtitle">Concrete presentation changes</h3>'
        '<div class="metrics deltas">'
        f'{delta_card("back_to_top", "Back-to-top controls")}'
        f'{delta_card("horizontal_rules", "Horizontal rules")}'
        f'{delta_card("star_history", "Dynamic Star History charts")}'
        '</div>'
        f'<p class="source-fingerprints"><strong>Source verification:</strong> Original '
        f'<code>{html_lib.escape(summary.get("before_sha256", "-"))}</code> · Candidate '
        f'<code>{html_lib.escape(summary.get("after_sha256", "-"))}</code></p>'
        '<div class="change-columns">'
        f'<div><h3>Added sections ({len(summary.get("added_sections", []))})</h3><ul>{items(summary.get("added_sections", []))}</ul></div>'
        f'<div><h3>Removed sections ({len(summary.get("removed_sections", []))})</h3><ul>{items(summary.get("removed_sections", []))}</ul></div>'
        f'<div><h3>Preserved sections ({len(summary.get("preserved_sections", []))})</h3><ul>{items(summary.get("preserved_sections", []))}</ul></div>'
        '</div>'
        f'<div class="experience-findings"><h3>Reading-experience findings</h3><ul>{experience_items}</ul>'
        f'<p class="muted">Safe fixes: {remediation.get("safe_fix", 0)} · Suggested fixes: {remediation.get("suggested_fix", 0)} · Needs input: {remediation.get("needs_input", 0)}</p></div>'
        f'<div class="experience-findings"><h3>Evidence findings</h3><ul>{items([item["code"] + " · " + item["message"] for item in summary.get("evidence_findings", [])], "Strict evidence checks passed")}</ul></div>'
        f'<p class="audit-note"><strong>Visual assets:</strong> {html_lib.escape(asset_text)}<br>Review the candidate and this change summary before applying or pushing it.</p>'
        '</aside>'
    )


def _preview_html(
    primary: str,
    primary_name: str,
    comparison: str = "",
    comparison_name: str = "",
    summary: dict = None,
) -> str:
    primary_html = _markdown_to_html(primary)
    panel = _summary_panel(summary or {})
    if comparison:
        comparison_html = _markdown_to_html(comparison)
        presentation = (summary or {}).get("presentation_changes", {})
        original_back = presentation.get("back_to_top", {}).get("before", "-")
        candidate_back = presentation.get("back_to_top", {}).get("after", "-")
        body = (
            '<main class="comparison-wrap">'
            f'{panel}<div class="comparison">'
            f'<section class="github-markdown original"><div class="file-label original-label">Original · {html_lib.escape(primary_name)} · Back-to-top: {original_back}</div>{primary_html}</section>'
            f'<section class="github-markdown candidate"><div class="file-label candidate-label">Optimized candidate · {html_lib.escape(comparison_name)} · Back-to-top: {candidate_back}</div>{comparison_html}</section>'
            '</div></main>'
        )
    else:
        label = "Generated candidate · " + primary_name if (summary or {}).get("workflow_kind") == "create" else primary_name
        body = f'<main class="single-wrap">{panel}<section class="github-markdown"><div class="file-label">{html_lib.escape(label)}</div>{primary_html}</section></main>'
    return """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"><meta http-equiv="Pragma" content="no-cache"><meta http-equiv="Expires" content="0"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ReadmeMagic GitHub README preview</title>
<style>
:root{color-scheme:light}*{box-sizing:border-box}body{font-family:"SF Pro Text",-apple-system,BlinkMacSystemFont,"Helvetica Neue",sans-serif;line-height:1.55;margin:0;background:#f5f5f7;color:#1d1d1f;-webkit-font-smoothing:antialiased}.comparison-wrap,.single-wrap{max-width:1540px;margin:0 auto;padding:48px 36px 72px}.comparison{display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:start}.github-markdown{background:#fff;border:0;border-radius:18px;padding:38px;min-width:0;box-shadow:0 12px 40px rgba(0,0,0,.06)}.github-markdown.original{border-top:0}.github-markdown.candidate{border-top:0;box-shadow:0 16px 48px rgba(0,102,204,.12)}.file-label{position:sticky;top:16px;z-index:20;font:600 12px "SF Pro Text",-apple-system,sans-serif;letter-spacing:.02em;text-transform:uppercase;color:#6e6e73;background:rgba(245,245,247,.88);backdrop-filter:blur(16px);border:0;margin:-22px -22px 28px;padding:12px 16px;border-radius:9999px;box-shadow:0 4px 16px rgba(0,0,0,.06)}.original-label{color:#6e6e73}.candidate-label{color:#0066cc;background:#e8f1fb}.review-banner{display:flex;justify-content:space-between;gap:24px;align-items:center;background:#f5f5f7;border:0;color:#1d1d1f;border-radius:14px;padding:16px 18px;margin-bottom:20px;font-weight:600}.review-banner span{font-size:13px;color:#6e6e73;font-weight:400}.review-header{padding:8px 4px 28px}.review-eyebrow{font-size:11px;font-weight:600;letter-spacing:.14em;color:#0066cc;margin-bottom:12px}.review-header h1{font:600 clamp(30px,4vw,52px)/1.07 "SF Pro Display","SF Pro Text",-apple-system,sans-serif;letter-spacing:-.03em;margin:0 0 12px;color:#1d1d1f}.review-header p{font-size:19px;line-height:1.45;color:#6e6e73;max-width:720px;margin:0}.github-markdown h1,.github-markdown h2,.github-markdown h3{line-height:1.15;border-bottom:0;padding-bottom:0;letter-spacing:-.02em}.github-markdown h1{font-size:2.15em}.github-markdown h2{font-size:1.65em;margin-top:32px}.github-markdown h3{font-size:1.2em}.github-markdown img{max-width:100%;height:auto;border-radius:12px}.github-markdown pre{overflow:auto;background:#1d1d1f;color:#f5f5f7;padding:18px;border-radius:12px}.github-markdown code{font-family:"SF Mono",ui-monospace,SFMono-Regular,monospace;background:#f5f5f7;padding:.18em .38em;border-radius:6px;color:#1d1d1f}.github-markdown pre code{background:transparent;color:inherit;padding:0}.github-markdown table{border-collapse:separate;border-spacing:0;width:100%;display:table;overflow:hidden;border:1px solid #e5e5ea;border-radius:12px}.github-markdown td,.github-markdown th{border-right:1px solid #e5e5ea;border-bottom:1px solid #e5e5ea;padding:10px 14px}.github-markdown tr:last-child td,.github-markdown tr:last-child th{border-bottom:0}.github-markdown td:last-child,.github-markdown th:last-child{border-right:0}.audit-panel{background:rgba(255,255,255,.9);border:0;border-radius:22px;padding:30px;margin-bottom:24px;box-shadow:0 12px 40px rgba(0,0,0,.06)}.audit-panel h2{margin:0 0 14px;font-size:26px;letter-spacing:-.02em}.audit-subtitle{font-size:13px;color:#6e6e73;margin:28px 0 10px;text-transform:uppercase;letter-spacing:.08em}.metrics{display:flex;flex-wrap:wrap;gap:10px}.metrics div{min-width:124px;padding:15px 16px;background:#f5f5f7;border-radius:12px}.metrics .delta.changed{background:#e8f1fb;border:0;color:#0066cc}.metrics strong,.metrics span{display:block}.metrics strong{font-size:22px;letter-spacing:-.02em}.metrics span{font-size:12px;color:#6e6e73}.source-fingerprints{font-size:12px;color:#6e6e73;margin:14px 0}.change-columns{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:24px}.change-columns h3{font-size:13px;margin-bottom:4px}.change-columns ul{margin-top:4px;padding-left:20px}.muted,.audit-note{color:#6e6e73}.audit-note{font-size:13px;margin:22px 0 0}.single-wrap{max-width:1060px}@media(max-width:900px){.comparison-wrap,.single-wrap{padding:28px 18px 48px}.comparison{display:block}.github-markdown+ .github-markdown{margin-top:20px}.change-columns{grid-template-columns:1fr}.review-banner{display:block}.review-banner span{display:block;margin-top:6px}}
</style><script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script><script>if(window.mermaid){mermaid.initialize({startOnLoad:true,theme:'base'});}</script></head><body>""" + body + "</body></html>"


def main():
    parser = argparse.ArgumentParser(
        prog="readme-magic",
        description="✨ ReadmeMagic - One spell, beautiful README",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  readme-magic inspect --project-path ./my-project
  readme-magic analyze --project-path ./my-project
  readme-magic optimize --project-path ./my-project
  readme-magic optimize --project-path ./my-project --apply
  readme-magic generate --project-path ./my-project
  readme-magic generate --template ai-project --lang zh
  readme-magic generate --template standard --lang bilingual
  readme-magic preview --output preview.html
  readme-magic templates
  readme-magic templates --lang zh
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # ── generate ──────────────────────────────────────────────────────────────
    gen = subparsers.add_parser("generate", help="Generate a beautiful README")
    gen.add_argument("--project-path", "-p", default=".", help="Path to project (default: current directory)")
    gen.add_argument("--template", "-t", default="standard", choices=TEMPLATE_CHOICES,
                     help="Template to use (default: standard)")
    gen.add_argument("--lang", "-l", default="en", choices=LANG_CHOICES,
                     help="Output language: en (English), zh (Chinese), bilingual (default: en)")
    gen.add_argument("--output", "-o", default="README.md", help="Output file (default: README.md)")
    gen.add_argument("--primary-color", default="#667eea", help="Primary badge color (default: #667eea)")
    gen.add_argument("--secondary-color", default="#764ba2", help="Secondary badge color (default: #764ba2)")
    gen.add_argument("--badges", help="Comma-separated badge names: version,license,python,stars,forks,issues")
    gen.add_argument("--star-history", action="store_true", help="Add Star History chart")
    gen.add_argument("--repo", help="GitHub repo (owner/repo) for badges and Star History")
    gen.add_argument(
        "--banner",
        metavar="PATH_OR_URL",
        help="Path or URL to an existing banner image to embed at the top of the README",
    )
    gen.add_argument(
        "--gen-banner",
        action="store_true",
        help=(
            "Auto-generate a banner image via GPT Image and embed it at the top. "
            "Requires gpt_image.py in the skill directory (available in the dodo AI sandbox)."
        ),
    )

    # -- inspect --------------------------------------------------------------
    inspect = subparsers.add_parser(
        "inspect", help="Detect project type and inventory README evidence"
    )
    inspect.add_argument("--project-path", "-p", default=".",
                         help="Path to project (default: current directory)")
    inspect.add_argument("--json", action="store_true",
                         help="Print a machine-readable project profile")

    subparsers.add_parser(
        "check-install", help="Verify the Python package and CLI dependencies"
    )
    workflow = subparsers.add_parser("workflow", help="Show the staged Agent workflow and artifact contract")
    workflow.add_argument("--project-path", "-p", default=".")
    workflow.add_argument("--stage", choices=STAGES, default="discover")
    workflow.add_argument("--json", action="store_true")

    # -- analyze --------------------------------------------------------------
    analyze = subparsers.add_parser("analyze", help="Score a README and suggest improvements")
    analyze.add_argument("--project-path", "-p", default=".",
                         help="Path to project (default: current directory)")
    analyze.add_argument("--json", action="store_true", help="Print a machine-readable JSON report")

    # -- optimize -------------------------------------------------------------
    optimize = subparsers.add_parser(
        "optimize", help="Create a grounded, improved README candidate"
    )
    optimize.add_argument("--project-path", "-p", default=".",
                          help="Path to project (default: current directory)")
    optimize.add_argument("--output", "-o",
                          help="Candidate path (default: README.optimized.md, or README.generated.md when missing)")
    optimize.add_argument("--lang", "-l", default="auto", choices=["auto", "en", "zh"],
                          help="Output language; auto preserves the current README language")
    optimize.add_argument(
        "--apply",
        action="store_true",
        help="Replace README.md after saving README.md.bak (default: candidate only)",
    )
    optimize.add_argument("--image-mode", choices=IMAGE_MODES, default=None,
                          help="Visual asset mode: native, api, prompt_only, or disabled")
    optimize.add_argument("--image-provider", default=None,
                          help="Image provider name (default: configured provider)")
    optimize.add_argument("--image-model", default=None,
                          help="Image model name (default: configured model)")
    optimize.add_argument("--image-config", default=None,
                          help="Path to a JSON image-generation config")
    optimize.add_argument("--preview-output", default="README.preview.html",
                          help="HTML review path (default: <project>/README.preview.html)")
    optimize.add_argument("--no-preview", action="store_true",
                          help="Skip automatic before/after HTML review generation")
    optimize.add_argument("--demo-command", default=None,
                          help="Opt-in command to run in the project and embed as verified Showcase evidence")
    optimize.add_argument("--json", action="store_true", help="Print a machine-readable result")

    # ── preview ───────────────────────────────────────────────────────────────
    preview = subparsers.add_parser("preview", help="Preview README as HTML")
    preview.add_argument("--project-path", "-p", default=".", help="Project path (default: current directory)")
    preview.add_argument("--input", "-i", default="README.md", help="Input README file (default: README.md)")
    preview.add_argument("--output", "-o", default="preview.html", help="Output HTML file (default: preview.html)")
    preview.add_argument("--compare", help="Optional second README to show beside the input")
    preview.add_argument("--opened", action="store_true", help="Mark the generated preview as opened by the host UI")

    # -- image-config --------------------------------------------------------
    image_config = subparsers.add_parser("image-config", help="Inspect or initialize image generation settings")
    image_config.add_argument("--project-path", "-p", default=".", help="Project path (default: current directory)")
    image_config.add_argument("--file", help="Config file path (default: <project>/.readme-magic.json)")
    image_config.add_argument("--init", action="store_true", help="Write a commented-free default JSON config")
    image_config.add_argument("--json", action="store_true", help="Print the effective config as JSON")

    # ── templates ─────────────────────────────────────────────────────────────
    tmpl = subparsers.add_parser("templates", help="List available templates")
    tmpl.add_argument("--lang", "-l", default="en", choices=LANG_CHOICES,
                      help="Language for descriptions (default: en)")

    # ── version ───────────────────────────────────────────────────────────────
    parser.add_argument("--version", "-v", action="version", version=f"ReadmeMagic {__version__}")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # -- handle inspect -------------------------------------------------------
    if args.command == "inspect":
        try:
            metadata = inspect_project(Path(args.project_path))
        except ValueError as exc:
            parser.error(str(exc))
        if args.json:
            print(json.dumps({"project": metadata.to_dict()}, ensure_ascii=False, indent=2))
        else:
            _print_inspection(metadata)

    # -- handle check-install -----------------------------------------------
    elif args.command == "check-install":
        import importlib.util
        import shutil
        import platform
        package_ok = importlib.util.find_spec("readme_magic") is not None
        markdown_ok = importlib.util.find_spec("markdown_it") is not None
        module_entry_ok = importlib.util.find_spec("readme_magic.__main__") is not None
        executable = shutil.which("readme-magic")
        print(f"ReadmeMagic installation (v{__version__})")
        print(f"- Python: {sys.executable}")
        print(f"- Python version: {platform.python_version()}")
        print(f"- Package import: {'ok' if package_ok else 'missing'}")
        print(f"- markdown-it-py: {'ok' if markdown_ok else 'missing'}")
        print(f"- Module entrypoint: {'ok' if module_entry_ok else 'missing'}")
        print(f"- Shell entrypoint: {executable or 'not on PATH (module entrypoint remains available)'}")
        if not package_ok or not markdown_ok or not module_entry_ok:
            print("Install from the repository with: python3 -m pip install -e .")
            print("Or run: ./scripts/install.sh")
            raise SystemExit(1)
        print("- CLI: ready")
        print("- Preview renderer: ready")
        print("- Image generation: optional (native, API, or prompt-only)")

    elif args.command == "workflow":
        state = create_state(Path(args.project_path), args.stage)
        state.artifacts["workflow_state"] = str(Path(args.project_path).resolve() / "artifacts" / "workflow-state.json")
        state_path = save_state(state, Path(args.project_path))
        if args.json:
            print(json.dumps(state.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"Workflow stage: {state.stage}")
            print(f"ReadmeMagic version: {__version__}")
            print(f"Execution mode: {state.execution_mode}")
            print(f"CLI available: {'yes' if state.cli_available else 'no (Agent fallback)'}")
            print(f"State artifact: {state_path}")

    # -- handle analyze -------------------------------------------------------
    elif args.command == "analyze":
        try:
            metadata = inspect_project(Path(args.project_path))
        except ValueError as exc:
            parser.error(str(exc))
        content = ""
        if metadata.readme_path:
            content = Path(metadata.readme_path).read_text(encoding="utf-8")
        report = analyze_readme(content, metadata.project_type)
        experience = analyze_experience(content, metadata.repo)
        consistency_findings = audit_repository_consistency(Path(metadata.path), metadata)
        experience.findings.extend(consistency_findings)
        if consistency_findings:
            for finding in consistency_findings:
                experience.dimensions["navigation_consistency"] = max(
                    0, experience.dimensions["navigation_consistency"] - 3
                )
            experience.score = sum(experience.dimensions.values())
        if args.json:
            print(json.dumps({"project": metadata.to_dict(),
                              "readme_present": bool(metadata.readme_path),
                              "baseline_available": bool(metadata.readme_path),
                              "report": report.to_dict() if metadata.readme_path else None,
                              "experience": experience.to_dict() if metadata.readme_path else None},
                             ensure_ascii=False, indent=2))
        else:
            print(f"Project: {metadata.name}")
            print(f"Detected: {metadata.language} | template: {metadata.template}")
            if not metadata.readme_path:
                print("README: missing")
                print("No baseline score is available. Run `readme-magic optimize` to create a reviewable README candidate.")
            else:
                _print_report(report, experience)

    # -- handle optimize ------------------------------------------------------
    elif args.command == "optimize":
        output = Path(args.output).expanduser() if args.output else None
        try:
            destination, before, after, metadata = optimize_project(
                Path(args.project_path), output=output, apply=args.apply, lang=args.lang,
                image_mode=args.image_mode,
                image_provider=args.image_provider,
                image_model=args.image_model,
                image_config_path=Path(args.image_config).expanduser() if args.image_config else None,
                demo_command=args.demo_command,
            )
        except ValueError as exc:
            parser.error(str(exc))
        has_readme = bool(metadata.readme_path and Path(metadata.readme_path).is_file())
        workflow_kind = "optimize" if has_readme else "create"
        result = {
            "readme_magic_version": __version__,
            "project": metadata.to_dict(),
            "output": str(destination.resolve()),
            "applied": args.apply,
            "workflow_kind": workflow_kind,
            "baseline_available": has_readme,
            "before": before.to_dict() if has_readme else None,
            "after": after.to_dict(),
        }
        project = Path(metadata.path)
        workflow_state = create_state(project, "apply" if args.apply else "review")
        workflow_state.preview_status = "not_generated"
        branch = _git_ref(project)
        workflow_state.target = f"{metadata.repo}@{branch}" if metadata.repo and branch else (metadata.repo or metadata.name)
        workflow_state.completed_stages = ["discover", "inspect", "score", "plan", "optimize"]
        if not args.no_preview:
            workflow_state.completed_stages.append("preview")
        workflow_state.artifacts = {
            "candidate": str(destination.resolve()),
        }
        if not args.no_preview:
            workflow_state.artifacts["preview"] = (
                str((project / args.preview_output).resolve())
                if not Path(args.preview_output).is_absolute()
                else str(Path(args.preview_output).resolve())
            )
        workflow_state.scores = {
            "baseline_available": has_readme,
            "content_before": before.score if has_readme else None,
            "content_after": after.score,
            "core_documentation_after": after.to_dict()["core_score"],
            "showcase_enhancement_after": after.to_dict()["presentation_score"],
        }
        workflow_state_path = save_state(workflow_state, project)
        result["workflow_state"] = str(workflow_state_path.resolve())
        if not has_readme:
            before_source = None
        elif args.apply and (project / "README.md.bak").exists():
            before_source = project / "README.md.bak"
        else:
            before_source = Path(metadata.readme_path) if metadata.readme_path else project / "README.md"
        before_experience = analyze_experience(
            before_source.read_text(encoding="utf-8") if before_source and before_source.exists() else "", metadata.repo
        )
        after_experience = analyze_experience(destination.read_text(encoding="utf-8"), metadata.repo)
        consistency_findings = audit_repository_consistency(project, metadata)
        after_experience.findings.extend(consistency_findings)
        if consistency_findings:
            for finding in consistency_findings:
                after_experience.dimensions["navigation_consistency"] = max(
                    0, after_experience.dimensions["navigation_consistency"] - 3
                )
            after_experience.score = sum(after_experience.dimensions.values())
        result["before_experience"] = before_experience.to_dict()
        result["after_experience"] = after_experience.to_dict()
        result["authorization"] = {
            "apply": bool(args.apply),
            "commit": False,
            "push": False,
            "next_required_user_action": "review candidate and preview before applying" if not args.apply else "review applied README before committing",
        }
        all_findings = list(after.findings) + list(after_experience.findings)
        finding_counts = {
            kind: sum(
                getattr(finding, "remediation", "suggested_fix") == kind
                for finding in all_findings
            )
            for kind in ("safe_fix", "suggested_fix", "needs_input")
        }
        result["interaction"] = {
            "module": "readme-magic",
            "version": __version__,
            "stage": "review" if not args.apply else "apply",
            "status": "awaiting_user_review" if not args.apply else "applied_pending_commit_review",
            "target": workflow_state.target,
            "execution_mode": workflow_state.execution_mode,
            "scores": {
                "overall": after.score,
                "content_evidence": after.score,
                "core_documentation": after.to_dict()["core_score"],
                "showcase_enhancement": after.to_dict()["presentation_score"],
                "reading_experience": after_experience.score,
            },
            "workflow_kind": workflow_kind,
            "baseline_available": has_readme,
            "message": (
                "README.md found; candidate optimization is ready for review."
                if has_readme
                else "README.md not found; a first README candidate is ready for review."
            ),
            "findings": finding_counts,
            "quality_tier": after.to_dict()["tier"],
            "strict_evidence_gate": after.to_dict()["strict_evidence_gate"],
            "candidate": str(destination.resolve()),
            "preview": None,
            "next_actions": ["apply", "revise", "keep_original"] if not args.apply else ["review_application", "commit"],
        }
        result["publish_ready"] = bool(
            after.to_dict()["core_quality_gate"] and after_experience.score >= 80
            and not any(finding.severity == "high" for finding in after.findings + after_experience.findings)
        )
        manifest_path = Path(metadata.path) / "artifacts" / "asset-manifest.json"
        if manifest_path.exists():
            result["asset_manifest"] = json.loads(manifest_path.read_text(encoding="utf-8"))
            native_requests = []
            for asset in result["asset_manifest"].get("assets", []):
                if asset.get("status") == "native_required":
                    native_requests.append({
                        "type": "generate_image",
                        "tool": "image_generation",
                        "asset": asset.get("key"),
                        "prompt": asset.get("prompt", ""),
                        "save_to": str((project / asset.get("filename", "")).resolve()),
                    })
            if native_requests:
                result["interaction"]["visual_actions"] = native_requests
        if not args.no_preview:
            preview_path = Path(args.preview_output).expanduser()
            if not preview_path.is_absolute():
                preview_path = project / preview_path
            if args.apply:
                before_path = project / "README.md.bak"
            else:
                before_path = Path(metadata.readme_path) if metadata.readme_path else project / "README.md"
            before_content = before_path.read_text(encoding="utf-8") if before_path.exists() else ""
            after_content = destination.read_text(encoding="utf-8")
            summary = _preview_summary(
                before_content, after_content, before.score if has_readme else None, after.score,
                before_experience, after_experience, after,
            )
            summary["workflow_kind"] = workflow_kind
            summary["baseline_available"] = has_readme
            summary["publish_ready"] = result["publish_ready"]
            if manifest_path.exists():
                statuses = {}
                for asset in result["asset_manifest"].get("assets", []):
                    status = asset.get("status", "unknown")
                    statuses[status] = statuses.get(status, 0) + 1
                summary["asset_statuses"] = statuses
            preview_path.parent.mkdir(parents=True, exist_ok=True)
            if has_readme:
                preview_html = _preview_html(
                    before_content, before_path.name, after_content, destination.name, summary
                )
            else:
                preview_html = _preview_html(after_content, destination.name, summary=summary)
            preview_path.write_text(preview_html, encoding="utf-8")
            result["preview"] = {"path": str(preview_path.resolve()), "summary": summary}
            result["interaction"]["preview"] = str(preview_path.resolve())
            workflow_state.preview_status = "generated_pending_open"

        preview_review_status = (
            "preview_pending_open"
            if result.get("preview") and not args.apply
            else result["interaction"]["status"]
        )
        result["interaction"]["preview_status"] = (
            "generated_pending_open" if preview_review_status == "preview_pending_open" else workflow_state.preview_status
        )
        if preview_review_status == "preview_pending_open":
            result["interaction"]["status"] = "preview_pending_open"
            result["interaction"]["next_actions"] = ["open_preview"]
            result["interaction"]["host_action"] = {
                "type": "open_file",
                "tool": "mcp__codex_app__open_in_codex",
                "path": result["interaction"]["preview"],
                "then": (
                    "readme-magic preview --project-path <project> "
                    + (f"--input {before_path.name} --compare {destination.name} " if has_readme else f"--input {destination.name} ")
                    + f"--output {Path(result['interaction']['preview']).name} --opened"
                ),
            }

        result["interaction"]["events"] = _interaction_events(
            result["interaction"]["target"],
            result["interaction"]["execution_mode"],
            result["interaction"]["candidate"],
            result["interaction"].get("preview") or "",
            result["interaction"]["next_actions"],
            preview_review_status,
            workflow_kind,
        )
        # Persist the same interaction contract that is returned to the Agent.
        # This makes a run inspectable even when the caller does not request JSON.
        workflow_state.status = result["interaction"]["status"]
        workflow_state.target = result["interaction"]["target"]
        workflow_state.scores = {
            "content_before": before.score,
            "content_after": after.score,
            "core_documentation_before": before.to_dict()["core_score"],
            "core_documentation_after": after.to_dict()["core_score"],
            "showcase_enhancement_before": before.to_dict()["presentation_score"],
            "showcase_enhancement_after": after.to_dict()["presentation_score"],
            "reading_experience_before": before_experience.score,
            "reading_experience_after": after_experience.score,
            "quality_tier": after.to_dict()["tier"],
            "strict_evidence_gate": after.to_dict()["strict_evidence_gate"],
        }
        workflow_state.artifacts["candidate"] = str(destination.resolve())
        if result.get("preview"):
            workflow_state.artifacts["preview"] = result["preview"]["path"]
        workflow_state.findings = [
            {
                "code": finding.code,
                "section": getattr(finding, "section", "content"),
                "severity": finding.severity,
                "remediation": getattr(finding, "remediation", "suggested_fix"),
                "message": finding.message,
            }
            for finding in (after.findings + after_experience.findings)
        ]
        workflow_state.next_actions = result["interaction"]["next_actions"]
        save_state(workflow_state, project)
        interaction_path = project / "artifacts" / "interaction-card.json"
        interaction_path.parent.mkdir(parents=True, exist_ok=True)
        interaction_path.write_text(
            json.dumps(result["interaction"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        result["interaction_card"] = str(interaction_path.resolve())
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Optimized README -> {destination.resolve()}")
            for event in result["interaction"]["events"]:
                marker = "⏸️" if event["status"] in ("awaiting_user_review", "preview_pending_open") else "✓"
                print(f"{marker} ReadmeMagic · {event['stage']}: {event['label']}")
            print(f"ReadmeMagic status: {result['interaction']['status']}")
            print(
                "Workflow: " + (
                    "optimize existing README" if result["workflow_kind"] == "optimize"
                    else "create first README"
                )
            )
            print(f"Execution mode: {workflow_state.execution_mode}")
            print(f"Target: {workflow_state.target}")
            if has_readme:
                print(f"Core Documentation: {before.to_dict()['core_score']}/70 -> {after.to_dict()['core_score']}/70")
                print(f"Showcase Enhancement: {before.to_dict()['presentation_score']}/30 -> {after.to_dict()['presentation_score']}/30")
                print(f"Overall README score: {before.score}/100 -> {after.score}/100")
            else:
                print(f"Core Documentation readiness: {after.to_dict()['core_score']}/70")
                print(f"Showcase Enhancement: {after.to_dict()['presentation_score']}/30")
            print(f"Reading Experience: {before_experience.score}/100 -> {after_experience.score}/100")
            print(f"Publish readiness: {'Ready for review' if result['publish_ready'] else 'Not ready'}")
            if result.get("preview"):
                print(f"Visual review -> {result['preview']['path']}")
            print(f"Interaction card -> {interaction_path.resolve()}")
            if manifest_path.exists():
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                statuses = {}
                for asset in manifest.get("assets", []):
                    statuses[asset.get("status", "unknown")] = statuses.get(asset.get("status", "unknown"), 0) + 1
                print("Visual assets: " + ", ".join(f"{key}={value}" for key, value in sorted(statuses.items())))
            if after.findings:
                print("Remaining presentation/content gaps:")
                for finding in after.findings:
                    print(f"- {finding.message}: {finding.recommendation}")
            if after_experience.findings:
                print("Remaining reading-experience gaps:")
                for finding in after_experience.findings:
                    print(f"- {finding.code} ({finding.section}): {finding.recommendation}")
            if args.apply:
                print("Original backup: README.md.bak")
            else:
                print("Review the candidate, then rerun with --apply to replace README.md.")

    # -- handle generate ------------------------------------------------------
    elif args.command == "generate":
        lang_label = {"en": "English", "zh": "Chinese (中文)", "bilingual": "Bilingual (中英双语)"}[args.lang]
        print(f"✨ Generating README")
        print(f"   Template  : {args.template}")
        print(f"   Language  : {lang_label}")
        print(f"   Project   : {args.project_path}")
        print(f"   Output    : {args.output}")
        if getattr(args, "gen_banner", False):
            print(f"   Banner    : auto-generate (GPT Image)")
        elif getattr(args, "banner", None):
            print(f"   Banner    : {args.banner}")

        content = _generate_readme(args)

        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = Path(args.project_path).expanduser().resolve() / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print(f"✅ README generated → {output_path.resolve()}")

    # ── handle preview ────────────────────────────────────────────────────────
    elif args.command == "preview":
        project_path = Path(args.project_path).expanduser().resolve()
        input_path = Path(args.input)
        if not input_path.is_absolute():
            input_path = project_path / input_path
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = project_path / output_path
        # A missing input is a valid baseline for first-time README creation
        # when the candidate is supplied via --compare.
        if not input_path.exists() and not args.compare:
            print(f"❌ Input file not found: {input_path}", file=sys.stderr)
            sys.exit(1)

        md_content = input_path.read_text(encoding="utf-8") if input_path.exists() else ""
        compare_path = Path(args.compare) if args.compare else None
        if compare_path and not compare_path.is_absolute():
            compare_path = project_path / compare_path
        if compare_path and not compare_path.exists():
            print(f"❌ Comparison file not found: {compare_path}", file=sys.stderr)
            sys.exit(1)
        html = _preview_html(md_content, input_path.name, compare_path.read_text(encoding="utf-8") if compare_path else "", compare_path.name if compare_path else "")
        output_path.write_text(html, encoding="utf-8")
        if args.opened:
            try:
                state_path = mark_preview_opened(project_path)
                print(f"✅ Preview marked opened → {state_path}")
            except (FileNotFoundError, ValueError) as exc:
                print(f"⚠️  Preview was rendered but not marked opened: {exc}", file=sys.stderr)
        print(f"👀 Preview saved → {output_path.resolve()}")
        print(f"   Open in browser: file://{output_path.resolve()}")

    # -- handle image-config -------------------------------------------------
    elif args.command == "image-config":
        project_path = Path(args.project_path).expanduser().resolve()
        config_path = Path(args.file).expanduser() if args.file else project_path / ".readme-magic.json"
        if args.init:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            if config_path.exists():
                parser.error(f"config already exists: {config_path}")
            config_path.write_text(json.dumps({"image_generation": DEFAULT_CONFIG}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if not args.json:
                print(f"Image config initialized → {config_path}")
        config = load_image_config(project_path, config_path=config_path if config_path.exists() else None)
        if args.json or not args.init:
            print(json.dumps(config.to_dict(), ensure_ascii=False, indent=2))

    # ── handle templates ──────────────────────────────────────────────────────
    elif args.command == "templates":
        desc_map = TEMPLATE_DESCRIPTIONS.get(args.lang, TEMPLATE_DESCRIPTIONS["en"])
        lang_label = {"en": "English", "zh": "Chinese", "bilingual": "Bilingual"}[args.lang]
        print(f"📝 Available templates ({lang_label}):\n")
        for name in TEMPLATE_CHOICES:
            desc = desc_map.get(name, "")
            available = []
            for lang in LANG_CHOICES:
                p = _template_path(name, lang)
                if p.exists():
                    available.append(lang)
            avail_str = ", ".join(available) if available else "not yet available"
            print(f"  {name:<14} {desc}")
            print(f"  {'':14} Languages: {avail_str}\n")


if __name__ == "__main__":
    main()
