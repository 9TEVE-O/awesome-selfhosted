#!/usr/bin/env python3
"""Analyzer for the awesome-selfhosted list.

Parses README.md and reports statistics on the self-hosted software entries,
including counts by category, license, and programming language.

Usage:
    python3 analyzer.py [--file README.md]
"""

import argparse
import re
from collections import Counter


ENTRY_RE = re.compile(r"^- \[.+?\]\(.+?\)")
BACKTICK_RE = re.compile(r"`([^`]+)`")
H2_RE = re.compile(r"^## (.+)$")
H3_RE = re.compile(r"^### (.+)$")


def parse_readme(path: str) -> tuple[list[dict], dict[str, int]]:
    """Parse software entries and per-category counts from a README file."""
    entries = []
    category_counts: dict[str, int] = {}
    current_category = ""
    in_software_section = False

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")

            h2 = H2_RE.match(line)
            if h2:
                title = h2.group(1)
                if title == "Software":
                    in_software_section = True
                elif in_software_section:
                    # Reached the section after Software – stop parsing entries
                    in_software_section = False
                continue

            if not in_software_section:
                continue

            h3 = H3_RE.match(line)
            if h3:
                current_category = h3.group(1)
                category_counts.setdefault(current_category, 0)
                continue

            if not current_category:
                continue

            if ENTRY_RE.match(line):
                fields = BACKTICK_RE.findall(line)
                # Skip warning markers; the last two fields are license & lang
                fields = [f for f in fields if f != "⚠"]
                if len(fields) >= 2:
                    license_field = fields[-2]
                    lang_field = fields[-1]
                    licenses = [lic.strip() for lic in license_field.split("/")]
                    languages = [lang.strip() for lang in lang_field.split("/")]
                    entries.append(
                        {
                            "category": current_category,
                            "licenses": licenses,
                            "languages": languages,
                        }
                    )
                    category_counts[current_category] = (
                        category_counts.get(current_category, 0) + 1
                    )

    return entries, category_counts


def print_top(title: str, counter: Counter, n: int = 10) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    for item, count in counter.most_common(n):
        print(f"  {item:<45} {count:>5}")


def analyze(path: str) -> None:
    entries, category_counts = parse_readme(path)

    license_counter: Counter = Counter()
    lang_counter: Counter = Counter()
    for entry in entries:
        for lic in entry["licenses"]:
            license_counter[lic] += 1
        for lang in entry["languages"]:
            lang_counter[lang] += 1

    total = len(entries)
    print(f"awesome-selfhosted list analyzer")
    print(f"=================================")
    print(f"Source file   : {path}")
    print(f"Total entries : {total}")
    print(f"Categories    : {len(category_counts)}")

    print_top("Top 10 categories by entry count", Counter(category_counts))
    print_top("Top 10 licenses", license_counter)
    print_top("Top 10 languages / platforms", lang_counter)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file",
        default="README.md",
        help="Path to the awesome-selfhosted README (default: README.md)",
    )
    args = parser.parse_args()
    analyze(args.file)


if __name__ == "__main__":
    main()
