"""README reading-experience audit and deterministic presentation fixes."""

from dataclasses import asdict, dataclass, field
import math
import re
from typing import Dict, List, Set, Tuple
from urllib.parse import unquote
from pathlib import Path


BACK_TO_TOP_RE = re.compile(
    r'(?is)\n*<div\s+align=["\']right["\']>\s*<a\s+href=["\']#[^"\']+["\']>'
    r'\s*(?:↑|⬆️?|&uarr;)?\s*(?:back\s+to\s+top|返回顶部|回到顶部)\s*</a>\s*</div>\n*'
)
STAR_PARAGRAPH_RE = re.compile(
    r'(?is)\n*<p\s+[^>]*align=["\']center["\'][^>]*>(?:(?!</p>).)*?'
    r'(?:star-history\.com|api\.star-history\.com|(?:star[-_ ]history)[^"\']*\.(?:png|jpe?g|webp))'
    r'(?:(?!</p>).)*?</p>\n*'
)


@dataclass
class ExperienceFinding:
    code: str
    category: str
    section: str
    severity: str
    message: str
    recommendation: str
    remediation: str
    evidence: Dict[str, object] = field(default_factory=dict)
    auto_fix: bool = False
    scope: str = "section"


@dataclass
class ExperienceReport:
    score: int
    max_score: int
    dimensions: Dict[str, int]
    findings: List[ExperienceFinding]
    passed_checks: List[str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "score": self.score,
            "max_score": self.max_score,
            "dimensions": self.dimensions,
            "findings": [asdict(item) for item in self.findings],
            "passed_checks": self.passed_checks,
            "remediation_counts": {
                kind: sum(item.remediation == kind for item in self.findings)
                for kind in ("safe_fix", "suggested_fix", "needs_input")
            },
        }


def _plain_heading(title: str) -> str:
    title = re.sub(r"<[^>]+>|\[[^]]+\]\([^)]+\)", " ", title)
    title = re.sub(r"[^\w\u4e00-\u9fff -]", " ", title, flags=re.UNICODE)
    return re.sub(r"\s+", " ", title).strip().lower()


def _slug(title: str) -> str:
    title = re.sub(r"<[^>]+>", "", title).strip().lower()
    title = re.sub(r"[^\w\u4e00-\u9fff -]", "", title, flags=re.UNICODE)
    return re.sub(r"[- ]+", "-", title).strip("-")


def _github_slug(title: str) -> str:
    """Approximate GitHub's heading slug while retaining meaningful emoji."""
    title = re.sub(r"<[^>]+>", "", title).strip().lower()
    title = re.sub(r"[^\w\u4e00-\u9fff -]", "", title, flags=re.UNICODE)
    # GitHub drops punctuation/emoji but replaces the following heading space,
    # which commonly produces a leading dash for emoji-prefixed headings.
    return re.sub(r"[- ]+", "-", title)


def _sections(content: str) -> List[Tuple[str, str, int, int]]:
    matches = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", content))
    return [
        (
            match.group(1).strip(),
            content[match.end():(matches[index + 1].start() if index + 1 < len(matches) else len(content))],
            match.start(),
            matches[index + 1].start() if index + 1 < len(matches) else len(content),
        )
        for index, match in enumerate(matches)
    ]


def _star_instances(content: str) -> List[re.Match]:
    return list(STAR_PARAGRAPH_RE.finditer(content))


def _repo_from_star(block: str) -> str:
    match = re.search(r"(?i)api\.star-history\.com/svg\?repos=([^&\"']+)", block)
    if match:
        return unquote(match.group(1)).strip()
    match = re.search(r"(?i)star-history\.com/#([^&\"']+)", block)
    return unquote(match.group(1)).strip() if match else ""


def _canonical_star_history(repo: str) -> str:
    return (
        '<p align="center">\n'
        f'  <a href="https://star-history.com/#{repo}&Date">\n'
        f'    <img src="https://api.star-history.com/svg?repos={repo}&type=Date" '
        'alt="Star History Chart" width="600">\n'
        '  </a>\n'
        '</p>'
    )


def analyze_experience(content: str, repo: str = "") -> ExperienceReport:
    """Score reading experience independently from content completeness."""
    maxima = {
        "information_hierarchy": 20,
        "scanability": 20,
        "density_rhythm": 15,
        "repetition_noise": 15,
        "navigation_consistency": 15,
        "visual_evidence_layout": 15,
    }
    dimensions = dict(maxima)
    findings: List[ExperienceFinding] = []
    passed: List[str] = []

    def add(code: str, dimension: str, deduction: int, section: str, severity: str,
            message: str, recommendation: str, remediation: str,
            evidence: Dict[str, object], auto_fix: bool = False, scope: str = "section") -> None:
        dimensions[dimension] = max(0, dimensions[dimension] - deduction)
        findings.append(ExperienceFinding(
            code, "reading_experience", section, severity, message, recommendation,
            remediation, evidence, auto_fix, scope,
        ))

    sections = _sections(content)
    titles: Dict[str, List[str]] = {}
    for title, _, _, _ in sections:
        titles.setdefault(_plain_heading(title), []).append(title)
    duplicates = [values for key, values in titles.items() if key and len(values) > 1]
    if duplicates:
        add("duplicate_sections", "information_hierarchy", 8, "global", "high",
            "The README contains duplicate top-level sections.",
            "Merge duplicate sections and keep one clear destination for each topic.",
            "suggested_fix", {"titles": duplicates}, scope="document_structure")
    else:
        passed.append("unique_sections")

    oversized = []
    total_lines = max(1, len(content.splitlines()))
    for title, body, _, _ in sections:
        lines = len(body.splitlines())
        if lines > 90 or (lines > 60 and lines / total_lines > 0.28):
            oversized.append({"section": title, "lines": lines})
    if oversized:
        add("oversized_section", "scanability", 8, oversized[0]["section"], "medium",
            "A section is long enough to hide the reader's next useful action.",
            "Split reference-heavy material from the quick path or move details to documentation.",
            "suggested_fix", {"sections": oversized, "recommended_max_lines": 90}, scope="section_structure")
    else:
        passed.append("scannable_section_length")

    rule_count = len(re.findall(r"(?m)^\s*---+\s*$", content))
    recommended_rules = max(2, math.ceil(max(1, len(sections)) / 2))
    if rule_count > recommended_rules:
        add("excessive_horizontal_rules", "density_rhythm", 6, "global", "medium",
            "Horizontal rules interrupt the page more often than they clarify groups.",
            "Use spacing and headings for ordinary sections; reserve rules for major transitions.",
            "safe_fix", {"count": rule_count, "recommended_max": recommended_rules}, True, "visual_rhythm")
    else:
        passed.append("balanced_horizontal_rules")

    back_count = len(BACK_TO_TOP_RE.findall(content))
    back_max = 0
    if back_count > back_max:
        add("repeated_back_to_top", "repetition_noise", 8, "global", "medium",
            "Back-to-top controls are repeated too often.",
            "Remove back-to-top controls; GitHub and browsers already provide native page navigation.",
            "safe_fix", {"count": back_count, "recommended_max": back_max}, True, "navigation_only")
    else:
        passed.append("restrained_back_to_top")

    cta_patterns = (
        r"(?i)(?:don't forget to|consider)\s+(?:give|giving)[^\n.]{0,80}(?:⭐|star)",
        r"(?i)if [^\n.]{0,80} saved you time[^\n.]{0,80}(?:⭐|star)",
    )
    cta_count = sum(len(re.findall(pattern, content)) for pattern in cta_patterns)
    if cta_count > 1:
        add("repeated_call_to_action", "repetition_noise", 5, "global", "low",
            "The same starring call to action appears more than once.",
            "Keep one concise call to action near the final community visual.",
            "safe_fix", {"count": cta_count, "recommended_max": 1}, True, "copy_only")
    else:
        passed.append("single_call_to_action")

    anchors = {_slug(title) for title, _, _, _ in sections}
    anchors.update(_github_slug(title) for title, _, _, _ in sections)
    anchors.update(value.lower() for value in re.findall(
        r'(?i)<(?:a\s+name|[a-z][a-z0-9]*\s+id)=["\']([^"\']+)', content
    ))
    links = [unquote(value).lower().replace("\ufe0f", "").strip() for value in re.findall(
        r'(?i)(?:href=["\']#([^"\']+)|\[[^]]+\]\(#([^)]+)\))', content
    ) for value in value if value]
    broken = sorted({link for link in links if link and link not in anchors})
    if broken:
        add("broken_navigation_anchor", "navigation_consistency", 12, "header/navigation", "high",
            "Navigation contains anchors that do not resolve to a README section.",
            "Correct each target or add a stable explicit anchor before its destination heading.",
            "safe_fix", {"anchors": broken}, True, "navigation_only")
    else:
        passed.append("valid_navigation_anchors")

    stars = _star_instances(content)
    star_repos = [_repo_from_star(match.group(0)) for match in stars]
    effective_repo = repo or next((item for item in star_repos if item), "")
    if effective_repo and not stars:
        add("community_star_history", "visual_evidence_layout", 3, "footer/community", "low",
            "The public GitHub project has no Star History closing visual.",
            "Add one dynamic Star History SVG as the final visual module.",
            "safe_fix", {"repo": effective_repo}, True, "footer_only")
    if len(stars) > 1:
        add("duplicate_star_history", "visual_evidence_layout", 5, "footer/community", "medium",
            "Star History appears more than once.", "Keep exactly one chart at the document end.",
            "safe_fix", {"count": len(stars)}, True, "footer_only")
    if stars:
        last = stars[-1]
        trailing = re.sub(r"(?ms)^\s*---+\s*$", "", content[last.end():]).strip()
        if trailing:
            add("misplaced_star_history", "visual_evidence_layout", 5, "footer/community", "medium",
                "Star History is not the final visual module.",
                "Move it after Contributing, License, and optional Acknowledgments.",
                "safe_fix", {"trailing_characters": len(trailing)}, True, "footer_only")
        else:
            passed.append("terminal_star_history")
        static = [match.group(0) for match in stars if "api.star-history.com/svg?repos=" not in match.group(0)]
        if static:
            add("static_star_history_asset", "visual_evidence_layout", 4, "footer/community", "medium",
                "Star History uses a static or noncanonical asset.",
                "Use the dynamic api.star-history.com SVG URL.",
                "safe_fix", {"count": len(static)}, True, "footer_only")
        mismatches = [item for item in star_repos if effective_repo and item and item != effective_repo]
        if mismatches:
            add("star_history_repo_mismatch", "visual_evidence_layout", 8, "footer/community", "high",
                "Star History points to a different repository.",
                "Regenerate both chart and link from the detected owner/repository.",
                "safe_fix", {"expected": effective_repo, "found": mismatches}, True, "footer_only")
    elif not effective_repo:
        passed.append("star_history_not_applicable")

    return ExperienceReport(sum(dimensions.values()), 100, dimensions, findings, passed)


def _trim_back_to_top(content: str) -> str:
    """Remove legacy back-to-top controls from optimized candidates."""
    return BACK_TO_TOP_RE.sub("\n", content)


def _reduce_horizontal_rules(content: str) -> str:
    """Keep separators only between major section groups."""
    matches = list(re.finditer(r"(?m)^\s*---+\s*$", content))
    sections = _sections(content)
    maximum = max(2, math.ceil(max(1, len(sections)) / 2))
    if len(matches) <= maximum:
        return content
    kept = set()
    if matches:
        kept.add(matches[0].start())
        kept.add(matches[-1].start())
    remaining = max(0, maximum - len(kept))
    middle = matches[1:-1]
    for index in range(remaining):
        position = round((index + 1) * (len(middle) + 1) / (remaining + 1)) - 1
        if middle:
            kept.add(middle[max(0, min(position, len(middle) - 1))].start())
    return re.sub(
        r"(?m)^\s*---+\s*$",
        lambda match: "---" if match.start() in kept else "",
        content,
    )


def _deduplicate_star_cta(content: str) -> str:
    """Keep the footer CTA and remove earlier requests to star the project."""
    patterns = (
        r"(?i)(?:don't forget to|consider)\s+(?:give|giving)[^\n.]{0,80}(?:⭐|star)[^\n.]*[.!]?",
        r"(?i)if [^\n.]{0,80} saved you time[^\n.]{0,80}(?:⭐|star)[^\n.]*[.!]?",
    )
    occurrences = []
    for pattern in patterns:
        occurrences.extend(re.finditer(pattern, content))
    occurrences.sort(key=lambda match: match.start())
    if len(occurrences) <= 1:
        return content
    for match in sorted(occurrences[:-1], key=lambda item: item.start(), reverse=True):
        content = content[:match.start()] + content[match.end():]
    return content


def _split_oversized_usage(content: str) -> str:
    """Promote natural H3 groups in a very long Usage section into H2 sections."""
    sections = _sections(content)
    for title, body, start, end in sections:
        if "usage" not in _plain_heading(title) and "使用" not in _plain_heading(title):
            continue
        if len(body.splitlines()) <= 90:
            continue
        groups = list(re.finditer(r"(?m)^###\s+(.+?)\s*$", body))
        if len(groups) < 2:
            return content
        replacement = content[start:end]
        replacements = []
        for group in groups[1:]:
            heading = group.group(1).strip()
            # Preserve feature-card HTML headings; only Markdown H3 is touched.
            replacements.append((group.start(), group.end(), f"## {heading}"))
        body_start = content[start:end].find(body)
        for group_start, group_end, heading in reversed(replacements):
            absolute_start = body_start + group_start
            absolute_end = body_start + group_end
            replacement = replacement[:absolute_start] + heading + replacement[absolute_end:]
        return content[:start] + replacement + content[end:]
    return content


def _repair_navigation(content: str) -> str:
    """Remove only header navigation links whose destinations do not exist."""
    first_section = re.search(r"(?m)^##\s+", content)
    if not first_section:
        return content
    header = content[:first_section.start()]
    body = content[first_section.start():]
    anchors = {_slug(title) for title, _, _, _ in _sections(content)}
    anchors.update(_github_slug(title) for title, _, _, _ in _sections(content))
    anchors.update(value.lower() for value in re.findall(
        r'(?i)<(?:a\s+name|[a-z][a-z0-9]*\s+id)=["\']([^"\']+)', content
    ))

    def replace(match: re.Match) -> str:
        target = unquote(match.group(1)).lower().replace("\ufe0f", "").strip()
        if target in anchors:
            return match.group(0)
        start, end = match.span()
        prefix = header[max(0, start - 12):start]
        suffix = header[end:end + 12]
        if re.search(r"(?:•|·|\|)\s*$", prefix):
            return "__README_MAGIC_REMOVE_PREVIOUS_SEPARATOR__"
        if re.match(r"\s*(?:•|·|\|)", suffix):
            return ""
        return ""

    header = re.sub(r'<a\s+href=["\']#([^"\']+)["\'][^>]*>.*?</a>', replace, header, flags=re.I | re.S)
    header = re.sub(
        r"(?:•|·|\|)\s*__README_MAGIC_REMOVE_PREVIOUS_SEPARATOR__",
        "",
        header,
    )
    header = re.sub(r"(?m)^\s*(?:•|·|\|)\s*$", "", header)
    return header + body


def apply_safe_experience_fixes(content: str, repo: str = "") -> str:
    """Apply only deterministic fixes; leave structural/copy judgments for review."""
    fixed = _split_oversized_usage(_deduplicate_star_cta(_repair_navigation(_trim_back_to_top(content))))
    stars = _star_instances(fixed)
    detected_repo = repo or next((_repo_from_star(match.group(0)) for match in stars if _repo_from_star(match.group(0))), "")
    if detected_repo:
        fixed = STAR_PARAGRAPH_RE.sub("\n", fixed)
        fixed = re.sub(r"(?:\n\s*---+\s*)+$", "", fixed.rstrip())
        fixed = fixed.rstrip() + "\n\n---\n\n" + _canonical_star_history(detected_repo) + "\n"
    fixed = _reduce_horizontal_rules(fixed)
    return re.sub(r"\n{4,}", "\n\n\n", fixed).rstrip() + "\n"


def audit_repository_consistency(project_path: Path, metadata=None) -> List[ExperienceFinding]:
    """Check cross-language README parity and obvious positioning drift signals."""
    findings: List[ExperienceFinding] = []
    project = Path(project_path)
    readme = project / "README.md"
    zh = project / "README_ZH.md"
    if readme.exists() and zh.exists():
        en = readme.read_text(encoding="utf-8", errors="ignore")
        cn = zh.read_text(encoding="utf-8", errors="ignore")
        # Compare visual assets only. A language switch such as
        # ``[中文](README_ZH.md)`` is a navigation link, not an asset.
        def visual_assets(markdown: str) -> Set[str]:
            html_assets = re.findall(r'(?is)<img\b[^>]*\bsrc=["\']([^"\']+)', markdown)
            md_assets = re.findall(r'!\[[^\]]*\]\(([^)\s]+)', markdown)
            return {unquote(item).strip() for item in (*html_assets, *md_assets) if item.strip()}

        en_images = visual_assets(en)
        cn_images = visual_assets(cn)
        if en_images != cn_images:
            findings.append(ExperienceFinding(
                "bilingual_asset_mismatch", "consistency", "README.md ↔ README_ZH.md",
                "medium", "English and Chinese README assets are not synchronized.",
                "Compare headings, image paths, and important links before applying.",
                "suggested_fix", {"english_only": sorted(en_images - cn_images), "chinese_only": sorted(cn_images - en_images)},
                False, "bilingual_sync",
            ))
        en_title = re.search(r"(?m)^#\s+(.+)$", en)
        cn_title = re.search(r"(?m)^#\s+(.+)$", cn)
        if en_title and cn_title and ("readme" in en_title.group(1).lower()) != ("readme" in cn_title.group(1).lower()):
            findings.append(ExperienceFinding(
                "bilingual_positioning_mismatch", "consistency", "README.md ↔ README_ZH.md",
                "medium", "English and Chinese README titles do not describe the same product.",
                "Align the title and primary value proposition in both language files.",
                "suggested_fix", {"english_title": en_title.group(1), "chinese_title": cn_title.group(1)},
                False, "bilingual_sync",
            ))
    if metadata is not None and readme.exists():
        text = readme.read_text(encoding="utf-8", errors="ignore").lower()
        recent_signals = " ".join(metadata.features + metadata.usage_commands).lower()
        if metadata.project_type == "cli" and "cli" not in text and "command" not in text and "命令" not in text:
            findings.append(ExperienceFinding(
                "positioning_drift", "consistency", "hero/first screen", "medium",
                "The README's primary story does not mention the repository's detected CLI workflow.",
                "Reconcile the first-screen promise with the current package entry point and tested usage.",
                "suggested_fix", {"project_type": metadata.project_type, "signals": recent_signals},
                False, "positioning",
            ))
    return findings
