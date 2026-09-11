"""ReadmeMagic CLI - One spell, beautiful README"""
import argparse
import difflib
import html as html_lib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from .analyzer import inspect_project
from .assets import DEFAULT_CONFIG, IMAGE_MODES, load_image_config
from .optimizer import optimize_project
from .quality import analyze_readme

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


def _print_report(report) -> None:
    print(f"README score: {report.score}/{report.max_score}")
    print("Dimensions: " + " | ".join(
        f"{name} {value}" for name, value in report.dimensions.items()
    ))
    if not report.findings:
        print("No quality issues found.")
        return
    for finding in report.findings:
        print(f"- [{finding.severity}] {finding.message}")
        print(f"  {finding.recommendation}")


def _print_inspection(metadata) -> None:
    """Print the evidence inventory used by the README planner."""
    print(f"Project: {metadata.name}")
    print(f"Type: {metadata.project_type} (confidence {metadata.type_confidence:.0%})")
    print(f"Language: {metadata.language}")
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
        "version": f'<img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat-square" alt="Version">',
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
    """Small dependency-free renderer for local README review."""
    output = []
    in_code = False
    code_lines = []
    code_language = ""
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            if in_code:
                code = html_lib.escape("\n".join(code_lines))
                if code_language == "mermaid":
                    output.append('<div class="mermaid">' + code + "</div>")
                else:
                    output.append("<pre><code>" + code + "</code></pre>")
                code_lines = []
                code_language = ""
                in_code = False
            else:
                in_code = True
                code_language = line[3:].strip().lower()
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            continue
        # README files commonly use HTML for centered banners and image grids.
        # Keep presentation HTML visible in the local preview.
        if re.search(r"<\/?(?:img|p|div|table|tr|td|th|thead|tbody|tfoot|a|strong|em|br|details|summary|h[1-6]|ul|ol|li|code|pre|blockquote|sub|sup|span|small)\b", line, re.I):
            output.append(line)
            continue
        if line.startswith("---"):
            output.append("<hr>")
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            output.append(f"<h{level}>{html_lib.escape(heading.group(2))}</h{level}>")
            continue
        image = re.fullmatch(r"!\[([^]]*)\]\(([^)]+)\)", line.strip())
        if image:
            alt, src = image.groups()
            output.append(f'<p><img src="{html_lib.escape(src, quote=True)}" alt="{html_lib.escape(alt, quote=True)}"></p>')
            continue
        if re.match(r"^[-*]\s+", line):
            item = re.sub(r"^[-*]\s+", "", line)
            if not output or not output[-1].startswith("<ul>"):
                output.append("<ul>")
            output.append("<li>" + html_lib.escape(item) + "</li>")
            continue
        text = html_lib.escape(line)
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        output.append("<p>" + text + "</p>")
    if in_code:
        code = html_lib.escape("\n".join(code_lines))
        output.append('<div class="mermaid">' + code + "</div>" if code_language == "mermaid" else "<pre><code>" + code + "</code></pre>")
    if output and output[-1].startswith("<li>"):
        output.append("</ul>")
    return "\n".join(output)


def _heading_titles(markdown: str) -> list:
    # Ignore fenced examples so shell comments are not reported as README sections.
    markdown = re.sub(r"(?ms)^```[^\n]*\n.*?^```\s*$", "", markdown)
    return [
        re.sub(r"[`*_]", "", match.group(2)).strip()
        for match in re.finditer(r"(?m)^(#{1,6})\s+(.+?)\s*$", markdown)
    ]


def _preview_summary(before: str, after: str, before_score=None, after_score=None) -> dict:
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
    }
    if before_score is not None:
        summary["before_score"] = before_score
    if after_score is not None:
        summary["after_score"] = after_score
    return summary


def _summary_panel(summary: dict) -> str:
    if not summary:
        return ""
    before_score = summary.get("before_score", "-")
    after_score = summary.get("after_score", "-")
    similarity = "{:.0%}".format(summary.get("similarity", 0))

    def items(values, empty="None"):
        return "".join(f"<li>{html_lib.escape(value)}</li>" for value in values) or f"<li class=\"muted\">{empty}</li>"

    asset_statuses = summary.get("asset_statuses", {})
    asset_text = ", ".join(f"{key}: {value}" for key, value in sorted(asset_statuses.items())) or "Not generated"

    return (
        '<aside class="audit-panel">'
        '<h2>What changed</h2>'
        '<div class="metrics">'
        f'<div><strong>{html_lib.escape(str(before_score))}</strong><span>Original score</span></div>'
        f'<div><strong>{html_lib.escape(str(after_score))}</strong><span>Candidate score</span></div>'
        f'<div><strong>{html_lib.escape(str(summary.get("before_lines", 0)))}</strong><span>Original lines</span></div>'
        f'<div><strong>{html_lib.escape(str(summary.get("after_lines", 0)))}</strong><span>Candidate lines</span></div>'
        f'<div><strong>{similarity}</strong><span>Text similarity</span></div>'
        '</div>'
        '<div class="change-columns">'
        f'<div><h3>Added sections ({len(summary.get("added_sections", []))})</h3><ul>{items(summary.get("added_sections", []))}</ul></div>'
        f'<div><h3>Removed sections ({len(summary.get("removed_sections", []))})</h3><ul>{items(summary.get("removed_sections", []))}</ul></div>'
        f'<div><h3>Preserved sections ({len(summary.get("preserved_sections", []))})</h3><ul>{items(summary.get("preserved_sections", []))}</ul></div>'
        '</div>'
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
        body = (
            '<main class="comparison-wrap">'
            f'{panel}<div class="comparison">'
            f'<section class="github-markdown"><div class="file-label">{html_lib.escape(primary_name)}</div>{primary_html}</section>'
            f'<section class="github-markdown"><div class="file-label candidate-label">{html_lib.escape(comparison_name)}</div>{comparison_html}</section>'
            '</div></main>'
        )
    else:
        body = f'<main class="single-wrap">{panel}<section class="github-markdown"><div class="file-label">{html_lib.escape(primary_name)}</div>{primary_html}</section></main>'
    return """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ReadmeMagic GitHub README preview</title>
<style>
:root{color-scheme:light dark}body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55;margin:0;background:#f6f8fa;color:#24292f}.comparison-wrap,.single-wrap{max-width:1480px;margin:0 auto;padding:24px}.comparison{display:grid;grid-template-columns:1fr 1fr;gap:16px}.github-markdown{background:#fff;border:1px solid #d0d7de;border-radius:6px;padding:32px;min-width:0;box-shadow:0 1px 2px rgba(27,31,36,.04)}.file-label{font:600 13px ui-monospace,SFMono-Regular,monospace;color:#57606a;background:#f6f8fa;border-bottom:1px solid #d0d7de;margin:-32px -32px 24px;padding:10px 14px;border-radius:6px 6px 0 0}.candidate-label{color:#0969da}.github-markdown h1,.github-markdown h2,.github-markdown h3{line-height:1.25;border-bottom:1px solid #d8dee4;padding-bottom:.3em}.github-markdown h1{font-size:2em}.github-markdown h2{font-size:1.5em;margin-top:24px}.github-markdown h3{font-size:1.25em;border-bottom:0}.github-markdown img{max-width:100%;height:auto}.github-markdown pre{overflow:auto;background:#f6f8fa;padding:16px;border-radius:6px}.github-markdown code{font-family:ui-monospace,SFMono-Regular,monospace;background:#afb8c133;padding:.2em .4em;border-radius:6px}.github-markdown pre code{background:transparent;padding:0}.github-markdown table{border-collapse:collapse;width:100%;display:block;overflow:auto}.github-markdown td,.github-markdown th{border:1px solid #d0d7de;padding:6px 13px}.audit-panel{background:#fff;border:1px solid #d0d7de;border-radius:6px;padding:20px;margin-bottom:16px}.audit-panel h2{margin:0 0 14px}.metrics{display:flex;flex-wrap:wrap;gap:10px}.metrics div{min-width:110px;padding:10px 12px;background:#f6f8fa;border-radius:6px}.metrics strong,.metrics span{display:block}.metrics strong{font-size:20px}.metrics span{font-size:12px;color:#57606a}.change-columns{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:18px}.change-columns h3{font-size:13px;margin-bottom:4px}.change-columns ul{margin-top:4px;padding-left:20px}.muted,.audit-note{color:#57606a}.audit-note{font-size:13px;margin:18px 0 0}.single-wrap{max-width:1000px}@media(max-width:900px){.comparison{display:block}.github-markdown+ .github-markdown{margin-top:16px}.change-columns{grid-template-columns:1fr}}@media(prefers-color-scheme:dark){body{background:#0d1117;color:#e6edf3}.github-markdown,.audit-panel{background:#161b22;border-color:#30363d}.file-label,.metrics div{background:#0d1117;border-color:#30363d}.github-markdown pre{background:#0d1117}.github-markdown td,.github-markdown th{border-color:#30363d}.metrics span,.muted,.audit-note{color:#8b949e}}
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
                          help="Candidate path (default: <project>/README.optimized.md)")
    optimize.add_argument("--lang", "-l", default="auto", choices=["auto", "en", "zh"],
                          help="Output language; auto preserves the current README language")
    optimize.add_argument(
        "--apply",
        action="store_true",
        help="Replace README.md after saving README.md.bak (default: candidate only)",
    )
    optimize.add_argument("--image-mode", choices=IMAGE_MODES, default=None,
                          help="Visual asset mode: api, prompt_only, or disabled")
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
    optimize.add_argument("--json", action="store_true", help="Print a machine-readable result")

    # ── preview ───────────────────────────────────────────────────────────────
    preview = subparsers.add_parser("preview", help="Preview README as HTML")
    preview.add_argument("--project-path", "-p", default=".", help="Project path (default: current directory)")
    preview.add_argument("--input", "-i", default="README.md", help="Input README file (default: README.md)")
    preview.add_argument("--output", "-o", default="preview.html", help="Output HTML file (default: preview.html)")
    preview.add_argument("--compare", help="Optional second README to show beside the input")

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
    parser.add_argument("--version", "-v", action="version", version="ReadmeMagic 2.0.0")

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
        if args.json:
            print(json.dumps({"project": metadata.to_dict(), "report": report.to_dict()},
                             ensure_ascii=False, indent=2))
        else:
            print(f"Project: {metadata.name}")
            print(f"Detected: {metadata.language} | template: {metadata.template}")
            _print_report(report)

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
            )
        except ValueError as exc:
            parser.error(str(exc))
        result = {
            "project": metadata.to_dict(),
            "output": str(destination.resolve()),
            "applied": args.apply,
            "before": before.to_dict(),
            "after": after.to_dict(),
        }
        manifest_path = Path(metadata.path) / "artifacts" / "asset-manifest.json"
        if manifest_path.exists():
            result["asset_manifest"] = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not args.no_preview:
            project = Path(metadata.path)
            preview_path = Path(args.preview_output).expanduser()
            if not preview_path.is_absolute():
                preview_path = project / preview_path
            if args.apply:
                before_path = project / "README.md.bak"
            else:
                before_path = Path(metadata.readme_path) if metadata.readme_path else project / "README.md"
            before_content = before_path.read_text(encoding="utf-8") if before_path.exists() else ""
            after_content = destination.read_text(encoding="utf-8")
            summary = _preview_summary(before_content, after_content, before.score, after.score)
            if manifest_path.exists():
                statuses = {}
                for asset in result["asset_manifest"].get("assets", []):
                    status = asset.get("status", "unknown")
                    statuses[status] = statuses.get(status, 0) + 1
                summary["asset_statuses"] = statuses
            preview_path.parent.mkdir(parents=True, exist_ok=True)
            preview_path.write_text(
                _preview_html(before_content, before_path.name, after_content, destination.name, summary),
                encoding="utf-8",
            )
            result["preview"] = {"path": str(preview_path.resolve()), "summary": summary}
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Optimized README -> {destination.resolve()}")
            print(f"Score: {before.score}/100 -> {after.score}/100")
            if result.get("preview"):
                print(f"Visual review -> {result['preview']['path']}")
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
        if not input_path.exists():
            print(f"❌ Input file not found: {input_path}", file=sys.stderr)
            sys.exit(1)

        md_content = input_path.read_text(encoding="utf-8")
        compare_path = Path(args.compare) if args.compare else None
        if compare_path and not compare_path.is_absolute():
            compare_path = project_path / compare_path
        if compare_path and not compare_path.exists():
            print(f"❌ Comparison file not found: {compare_path}", file=sys.stderr)
            sys.exit(1)
        html = _preview_html(md_content, input_path.name, compare_path.read_text(encoding="utf-8") if compare_path else "", compare_path.name if compare_path else "")
        output_path.write_text(html, encoding="utf-8")
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
