#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


ROOT_README = "README.md"
README_TEMPLATE = "README.md.template"
EXCLUDED_DIRS = {".git", ".github", ".idea", "__pycache__"}
MANUAL_START = "<!-- BEGIN MANUAL NOTES -->"
MANUAL_END = "<!-- END MANUAL NOTES -->"
AUTO_START = "<!-- BEGIN AUTO INDEX -->"
AUTO_END = "<!-- END AUTO INDEX -->"

DATE_RE = re.compile(r"^- Date\s*:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
TAGS_RE = re.compile(r"^- Tags\s*:\s*(.+?)\s*$", re.MULTILINE)
TITLE_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


@dataclass(frozen=True)
class Article:
    path: Path
    relative_path: Path
    title: str
    summary: str
    published_on: date
    tags: tuple[str, ...]
    folder: Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def should_skip_markdown(path: Path, root: Path) -> bool:
    if path.name.lower() == ROOT_README.lower():
        return True
    if path.relative_to(root).parts[0] in EXCLUDED_DIRS:
        return True
    return False


def discover_markdown_files(root: Path) -> list[Path]:
    markdown_files = []
    for path in sorted(root.rglob("*.md")):
        if any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts):
            continue
        if should_skip_markdown(path, root):
            continue
        markdown_files.append(path)
    return markdown_files


def parse_date(raw: str) -> date:
    match = DATE_RE.search(raw)
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d").date()
    return date.today()


def normalize_tag(tag: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._/-]+", "", tag.strip())
    return cleaned.strip("-_/")


def canonicalize_tag(tag: str) -> str:
    if not tag:
        return tag
    if tag.isupper():
        return tag
    if tag.lower() == tag:
        parts = re.split(r"([-_/])", tag)
        return "".join(part.title() if part not in "-_/" else part for part in parts)
    return tag


def parse_tags(raw: str, relative_path: Path) -> tuple[str, ...]:
    match = TAGS_RE.search(raw)
    tags: list[str] = []
    if match:
        raw_tags = match.group(1).replace(",", " ")
        tags.extend(normalize_tag(token[1:]) for token in raw_tags.split() if token.startswith("#"))

    if not tags:
        tags.extend(part for part in relative_path.parent.parts if part != ".")

    deduped: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        tag = canonicalize_tag(tag)
        lowered = tag.lower()
        if tag and lowered not in seen:
            deduped.append(tag)
            seen.add(lowered)
    return tuple(deduped)


def prettify_stem(stem: str) -> str:
    return stem.replace("-", " ").replace("_", " ").strip().title()


def parse_title(raw: str, path: Path) -> str:
    match = TITLE_RE.search(raw)
    if match:
        return match.group(1).strip()
    return prettify_stem(path.stem)


def collect_body_lines(raw: str) -> list[str]:
    lines = raw.splitlines()
    heading_found = False
    in_code_block = False
    body_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not heading_found:
            if TITLE_RE.match(line):
                heading_found = True
            continue
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        body_lines.append(line.rstrip())

    if not heading_found:
        body_lines = lines

    cleaned: list[str] = []
    for line in body_lines:
        stripped = line.strip()
        if not stripped:
            if cleaned:
                break
            continue
        if stripped.startswith("- Date :") or stripped.startswith("- Tags :"):
            continue
        cleaned.append(stripped)
    return cleaned


def summarize(raw: str) -> str:
    body_lines = collect_body_lines(raw)
    if not body_lines:
        return "No summary yet."

    paragraph = " ".join(body_lines)
    paragraph = LINK_RE.sub(r"\1", paragraph)
    paragraph = re.sub(r"`([^`]+)`", r"\1", paragraph)
    paragraph = re.sub(r"\s+", " ", paragraph).strip()

    if len(paragraph) <= 140:
        return paragraph
    return paragraph[:137].rstrip() + "..."


def parse_article(path: Path, root: Path) -> Article:
    raw = read_text(path)
    relative_path = path.relative_to(root)
    return Article(
        path=path,
        relative_path=relative_path,
        title=parse_title(raw, path),
        summary=summarize(raw),
        published_on=parse_date(raw),
        tags=parse_tags(raw, relative_path),
        folder=relative_path.parent,
    )


def scan_articles(root: Path) -> list[Article]:
    articles = [parse_article(path, root) for path in discover_markdown_files(root)]
    articles.sort(key=lambda article: (article.published_on, str(article.relative_path).lower()), reverse=True)
    return articles


def markdown_link(label: str, target: Path) -> str:
    return f"[{label}]({target.as_posix()})"


def format_tags(tags: tuple[str, ...]) -> str:
    if not tags:
        return "-"
    return ", ".join(f"`{tag}`" for tag in tags)


def build_recent_table(articles: list[Article], limit: int = 10) -> str:
    lines = [
        "## Recent Entries",
        "",
        "| Title | Folder | Date | Tags |",
        "| --- | --- | --- | --- |",
    ]
    for article in articles[:limit]:
        folder_label = article.folder.as_posix() if article.folder.as_posix() != "." else "/"
        lines.append(
            "| {title} | {folder} | {published_on} | {tags} |".format(
                title=markdown_link(article.title, article.relative_path),
                folder=folder_label,
                published_on=article.published_on.isoformat(),
                tags=format_tags(article.tags),
            )
        )
    return "\n".join(lines)


def build_folder_section(articles: list[Article]) -> str:
    grouped: dict[Path, list[Article]] = defaultdict(list)
    for article in articles:
        grouped[article.folder].append(article)

    lines = ["## Organized by Folder", ""]
    for folder in sorted(grouped):
        folder_readme = folder / ROOT_README
        lines.append(f"### {markdown_link(folder.as_posix(), folder_readme)}")
        lines.append("")
        lines.append("| Title | Date | Tags | Summary |")
        lines.append("| --- | --- | --- | --- |")
        for article in sorted(grouped[folder], key=lambda item: item.published_on, reverse=True):
            lines.append(
                "| {title} | {published_on} | {tags} | {summary} |".format(
                    title=markdown_link(article.title, article.relative_path),
                    published_on=article.published_on.isoformat(),
                    tags=format_tags(article.tags),
                    summary=article.summary.replace("|", "\\|"),
                )
            )
        lines.append("")
    return "\n".join(lines).rstrip()


def build_tag_section(articles: list[Article]) -> str:
    grouped: dict[str, list[Article]] = defaultdict(list)
    for article in articles:
        for tag in article.tags:
            grouped[tag].append(article)

    lines = ["## Organized by Tag", ""]
    for tag in sorted(grouped, key=str.lower):
        lines.append(f"### `{tag}`")
        lines.append("")
        for article in sorted(grouped[tag], key=lambda item: item.published_on, reverse=True):
            lines.append(
                "- {title} ({folder}, {published_on})".format(
                    title=markdown_link(article.title, article.relative_path),
                    folder=article.folder.as_posix(),
                    published_on=article.published_on.isoformat(),
                )
            )
        lines.append("")
    return "\n".join(lines).rstrip()


def build_overview(articles: list[Article]) -> str:
    folder_count = len({article.folder for article in articles})
    tag_count = len({tag.lower() for article in articles for tag in article.tags})
    lines = [
        "| Summary | Value |",
        "| --- | --- |",
        f"| Last synced | {date.today().isoformat()} |",
        f"| Total entries | {len(articles)} |",
        f"| Folders with entries | {folder_count} |",
        f"| Unique tags | {tag_count} |",
        "",
    ]
    return "\n".join(lines)


def build_root_content(template: str, articles: list[Article]) -> str:
    sections = [
        build_overview(articles),
        build_recent_table(articles),
        "",
        build_folder_section(articles),
        "",
        build_tag_section(articles),
    ]
    return template.replace("{TOC}", "\n".join(sections).rstrip() + "\n")


def folder_label(folder: Path) -> str:
    return folder.name.replace("-", " ") if folder.name else "Folder"


def collect_relevant_directories(articles: list[Article]) -> list[Path]:
    directories: set[Path] = set()
    for article in articles:
        current = article.folder
        while current != Path("."):
            directories.add(current)
            current = current.parent
    return sorted(directories)


def extract_manual_notes(existing: str | None) -> str:
    if not existing:
        return "_Add folder-specific notes here._"

    start = existing.find(MANUAL_START)
    end = existing.find(MANUAL_END)
    if start == -1 or end == -1 or end < start:
        return "_Add folder-specific notes here._"

    manual = existing[start + len(MANUAL_START):end].strip("\n")
    return manual.strip() or "_Add folder-specific notes here._"


def build_folder_auto_index(folder: Path, articles: list[Article], directories: list[Path]) -> str:
    direct_articles = [article for article in articles if article.folder == folder]
    child_directories = [path for path in directories if path.parent == folder]

    lines = [
        f"## Index",
        "",
        f"- Last synced: `{date.today().isoformat()}`",
        f"- Direct entries: `{len(direct_articles)}`",
        f"- Child folders: `{len(child_directories)}`",
        "",
    ]

    if child_directories:
        lines.append("## Child Folders")
        lines.append("")
        for child in child_directories:
            lines.append(f"- {markdown_link(child.name, Path(child.name) / ROOT_README)}")
        lines.append("")

    if direct_articles:
        lines.append("## Entries")
        lines.append("")
        lines.append("| Title | Date | Tags | Summary |")
        lines.append("| --- | --- | --- | --- |")
        for article in sorted(direct_articles, key=lambda item: item.published_on, reverse=True):
            relative_target = Path(article.relative_path.name)
            lines.append(
                "| {title} | {published_on} | {tags} | {summary} |".format(
                    title=markdown_link(article.title, relative_target),
                    published_on=article.published_on.isoformat(),
                    tags=format_tags(article.tags),
                    summary=article.summary.replace("|", "\\|"),
                )
            )
        lines.append("")
    else:
        lines.append("## Entries")
        lines.append("")
        lines.append("_No markdown entries in this folder yet._")
        lines.append("")

    return "\n".join(lines).rstrip()


def build_folder_readme(folder: Path, manual_notes: str, auto_index: str) -> str:
    title = folder_label(folder)
    return "\n".join(
        [
            f"# {title}",
            "",
            "This README is partly managed by `./til sync`.",
            "Keep your folder notes inside the manual section below.",
            "",
            MANUAL_START,
            manual_notes.rstrip(),
            MANUAL_END,
            "",
            AUTO_START,
            auto_index,
            AUTO_END,
            "",
        ]
    )


def update_folder_readmes(root: Path, articles: list[Article]) -> None:
    directories = collect_relevant_directories(articles)
    for folder in directories:
        readme_path = root / folder / ROOT_README
        existing = read_text(readme_path) if readme_path.exists() else None
        manual_notes = extract_manual_notes(existing)
        auto_index = build_folder_auto_index(folder, articles, directories)
        write_text(readme_path, build_folder_readme(folder, manual_notes, auto_index))


def sync_readmes(root: Path) -> int:
    articles = scan_articles(root)
    template_path = root / README_TEMPLATE
    if not template_path.exists():
        raise FileNotFoundError(f"Missing template: {template_path}")

    template = read_text(template_path)
    write_text(root / ROOT_README, build_root_content(template, articles))
    update_folder_readmes(root, articles)
    return len(articles)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync root and folder README files for TIL entries.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to the current directory.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    article_count = sync_readmes(root)
    print(f"Synced README files for {article_count} entries.")


if __name__ == "__main__":
    main()
