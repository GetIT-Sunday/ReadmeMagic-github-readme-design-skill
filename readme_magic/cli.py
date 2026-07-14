"""ReadmeMagic CLI - One spell, beautiful README"""
import argparse
import os
import sys
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

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


def _generate_readme(args) -> str:
    """Load the selected template and substitute known placeholders."""
    content = _load_template(args.template, args.lang)

    # Determine project name from path
    project_path = Path(args.project_path).resolve()
    project_name = project_path.name if project_path.exists() else args.project_path

    # Basic placeholder substitutions
    substitutions = {
        "{{PROJECT_NAME}}": project_name,
        "{{PRIMARY_COLOR}}": args.primary_color,
        "{{SECONDARY_COLOR}}": args.secondary_color,
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


def main():
    parser = argparse.ArgumentParser(
        prog="readme-magic",
        description="✨ ReadmeMagic - One spell, beautiful README",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
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

    # ── preview ───────────────────────────────────────────────────────────────
    preview = subparsers.add_parser("preview", help="Preview README as HTML")
    preview.add_argument("--input", "-i", default="README.md", help="Input README file (default: README.md)")
    preview.add_argument("--output", "-o", default="preview.html", help="Output HTML file (default: preview.html)")

    # ── templates ─────────────────────────────────────────────────────────────
    tmpl = subparsers.add_parser("templates", help="List available templates")
    tmpl.add_argument("--lang", "-l", default="en", choices=LANG_CHOICES,
                      help="Language for descriptions (default: en)")

    # ── version ───────────────────────────────────────────────────────────────
    parser.add_argument("--version", "-v", action="version", version="ReadmeMagic 1.2.0")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # ── handle generate ───────────────────────────────────────────────────────
    if args.command == "generate":
        lang_label = {"en": "English", "zh": "Chinese (中文)", "bilingual": "Bilingual (中英双语)"}[args.lang]
        print(f"✨ Generating README")
        print(f"   Template  : {args.template}")
        print(f"   Language  : {lang_label}")
        print(f"   Project   : {args.project_path}")
        print(f"   Output    : {args.output}")

        content = _generate_readme(args)

        output_path = Path(args.output)
        output_path.write_text(content, encoding="utf-8")
        print(f"✅ README generated → {output_path.resolve()}")

    # ── handle preview ────────────────────────────────────────────────────────
    elif args.command == "preview":
        input_path = Path(args.input)
        output_path = Path(args.output)
        if not input_path.exists():
            print(f"❌ Input file not found: {input_path}", file=sys.stderr)
            sys.exit(1)

        md_content = input_path.read_text(encoding="utf-8")
        html = (
            "<!DOCTYPE html><html><head>"
            '<meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<style>body{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;}</style>'
            "</head><body><pre style='white-space:pre-wrap'>"
            + md_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            + "</pre></body></html>"
        )
        output_path.write_text(html, encoding="utf-8")
        print(f"👀 Preview saved → {output_path.resolve()}")
        print(f"   Open in browser: file://{output_path.resolve()}")

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
