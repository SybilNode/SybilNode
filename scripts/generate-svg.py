#!/usr/bin/env python3
# ⒸAngelaMos | 2025 | CertGames.com
import sys
import json
from pathlib import Path

# ============================
#  Custom Language Colors
# ============================
LANGUAGE_COLORS = {
    "Python": "#3572A5",
    "TOML": "#FF0000",
    "HTML": "#E34C26",
    "INI": "#FFFFFF",
}

DEFAULT_COLOR = "#ff4444"

def format_number(num):
    return f"{num:,}"

def merge_repos(loc_data):
    """
    Tokei multi-repo JSON looks like:
    {
      "Repo1": { "Python": {...}, "Total": {...} },
      "Repo2": { "JavaScript": {...}, "Total": {...} }
    }

    We need to merge all repos into:
    {
      "Total": { "code": X, "files": Y },
      "Python": { "code": A },
      "JavaScript": { "code": B },
      ...
    }
    """

    combined = {"Total": {"code": 0, "files": 0}}
    languages = {}

    for repo_name, repo_data in loc_data.items():
        if not isinstance(repo_data, dict):
            continue

        # Merge totals
        total = repo_data.get("Total", {})
        combined["Total"]["code"] += int(total.get("code", 0))
        combined["Total"]["files"] += int(total.get("files", 0))

        # Merge languages
        for lang, stats in repo_data.items():
            if lang == "Total":
                continue
            if isinstance(stats, dict):
                code = int(stats.get("code", 0))
                if code > 0:
                    languages[lang] = languages.get(lang, 0) + code

    # Add merged languages to combined dict
    for lang, code in languages.items():
        combined[lang] = {"code": code}

    return combined

def generate_svg(loc_data):
    total_code = int(loc_data.get('Total', {}).get('code', 0))
    total_files = int(loc_data.get('Total', {}).get('files', 0))

    # Extract languages
    languages = {
        lang: stats["code"]
        for lang, stats in loc_data.items()
        if lang != "Total" and isinstance(stats, dict) and "code" in stats
    }

    # Sort top languages
    top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:6]

    svg = f"""
<svg width="800" height="320" xmlns="http://www.w3.org/2000/svg">
  <rect width="800" height="320" fill="#000000" rx="10"/>
  <text x="40" y="55" font-family="monospace" font-size="32" fill="#ffffff">{format_number(total_code)}</text>
  <text x="40" y="80" font-family="monospace" font-size="14" fill="#ffffff">LINES OF CODE</text>
  <text x="760" y="55" font-family="monospace" font-size="24" fill="#ffffff" text-anchor="end">{format_number(total_files)}</text>
  <text x="760" y="75" font-family="monospace" font-size="12" fill="#ffffff" text-anchor="end">FILES</text>
  <line x1="30" y1="100" x2="770" y2="100" stroke="#30363d" stroke-width="1"/>
  <text x="40" y="130" font-family="monospace" font-size="16" fill="#ff4444">TOP LANGUAGES</text>
"""

    y = 160
    max_width = 450
    max_code = top_langs[0][1] if top_langs else 1

    for lang, code in top_langs:
        width = (code / max_code) * max_width
        bar_color = LANGUAGE_COLORS.get(lang, DEFAULT_COLOR)

        svg += f"""
  <text x="40" y="{y}" font-family="monospace" font-size="13" fill="#ffffff">{lang}</text>
  <rect x="180" y="{y-12}" width="{max_width}" height="16" fill="#21262d" rx="4"/>
  <rect x="180" y="{y-12}" width="{width}" height="16" fill="{bar_color}" rx="4"/>
  <text x="650" y="{y}" font-family="monospace" font-size="12" fill="#ffffff">{format_number(code)}</text>
"""
        y += 25

    svg += "</svg>"
    return svg

def main():
    loc_file = Path("loc-data.json")
    if not loc_file.exists():
        print("loc-data.json not found", file=sys.stderr)
        sys.exit(1)

    with open(loc_file) as f:
        raw_data = json.load(f)

    # Detect if multi-repo format
    if "Total" not in raw_data:
        merged = merge_repos(raw_data)
    else:
        merged = raw_data

    svg = generate_svg(merged)

    with open("loc-stats.svg", "w") as f:
        f.write(svg)

    print("SVG generated successfully")

if __name__ == "__main__":
    main()
