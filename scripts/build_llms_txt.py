#!/usr/bin/env python3
"""Build a useful compact llms.txt for the docs site.

Great Docs generates llms.txt from the API reference only. For SerpApi Python,
the compact LLM entry point is more useful when it includes the homepage and
getting-started flow before the reference links.
"""

from __future__ import annotations

import posixpath
import re
from pathlib import Path


def find_paths() -> tuple[Path, Path]:
    script_path = Path(__file__).resolve()

    if script_path.parent.name == "scripts" and script_path.parent.parent.name == "great-docs":
        build_dir = script_path.parent.parent
        repo_root = build_dir.parent
    else:
        repo_root = script_path.parent.parent
        build_dir = repo_root / "great-docs"

    return repo_root, build_dir


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        if lines[index].strip() == "---":
            end = index + 1
            while end < len(lines) and lines[end].strip() != "---":
                end += 1
            if end < len(lines):
                index = end + 1
                continue

        output.append(lines[index])
        index += 1

    return "\n".join(output).strip()


def clean_markdown(text: str) -> str:
    text = strip_frontmatter(text)
    text = re.sub(r"<style\b[^>]*>.*?</style>\s*", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(
        r'<div class="docs-home-actions">.*?</div>\s*',
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    text = re.sub(r"^:::\s*\{[^}]+\}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^:::\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def demote_headings(text: str) -> str:
    return re.sub(
        r"^(#{1,5})(\s+)",
        lambda match: f"#{match.group(1)}{match.group(2)}",
        text,
        flags=re.MULTILINE,
    )


def site_url_from_config(config_path: Path) -> str:
    if not config_path.exists():
        return ""

    match = re.search(r"^site_url:\s*(.+?)\s*$", read_text(config_path), flags=re.MULTILINE)
    if not match:
        return ""

    site_url = match.group(1).strip().strip('"').strip("'")
    return site_url if site_url.endswith("/") else f"{site_url}/"


def normalize_links(text: str, *, site_url: str, base_path: str = "") -> str:
    def replace(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        if re.match(r"^(?:[a-z][a-z0-9+.-]*:|#)", target, flags=re.IGNORECASE):
            return f"]({target})"

        path = target[2:] if target.startswith("./") else target
        joined = posixpath.normpath(posixpath.join(base_path, path))
        if joined == ".":
            joined = ""

        joined = re.sub(r"\.q?md($|#)", r".html\1", joined)
        return f"]({site_url}{joined})" if site_url else f"]({joined})"

    return re.sub(r"\]\(([^)]+)\)", replace, text)


def api_reference_from_default(default_llms: str) -> str:
    marker = "### API Reference"
    if marker not in default_llms:
        return ""

    api_reference = default_llms.split(marker, 1)[1].strip()
    api_reference = re.sub(r"^####(\s+)", r"###\1", api_reference, flags=re.MULTILINE)
    return api_reference


def main() -> None:
    repo_root, build_dir = find_paths()
    site_url = site_url_from_config(repo_root / "great-docs.yml")

    index = clean_markdown(read_text(repo_root / "docs" / "index.md"))
    getting_started = clean_markdown(
        read_text(repo_root / "docs" / "user_guide" / "00-getting-started.md")
    )
    getting_started = re.sub(r"^#\s+Getting Started\s*", "", getting_started).strip()

    index = demote_headings(normalize_links(index, site_url=site_url))
    getting_started = demote_headings(
        normalize_links(getting_started, site_url=site_url, base_path="user-guide")
    )

    api_reference = api_reference_from_default(read_text(build_dir / "llms.txt"))

    lines = [
        "# SerpApi Python",
        "",
        "> Official Python client for SerpApi search data in applications, AI workflows, RAG, and data pipelines.",
        "",
        "## Homepage",
        "",
        index,
        "",
        "## Getting Started",
        "",
        getting_started,
        "",
    ]

    if api_reference:
        lines.extend(["## API Reference", "", api_reference, ""])

    if site_url:
        lines.extend(
            [
                "## More LLM Context",
                "",
                f"- [Full LLM documentation]({site_url}llms-full.txt)",
                f"- [Documentation homepage]({site_url}index.html)",
                "",
            ]
        )

    output = "\n".join(lines).strip() + "\n"
    (build_dir / "llms.txt").write_text(output, encoding="utf-8")
    print("Updated llms.txt with homepage and getting-started content")


if __name__ == "__main__":
    main()
