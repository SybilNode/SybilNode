#!/usr/bin/env python3
import sys
import json
from pathlib import Path

# ============================
#  Custom Language Colors
# ============================
LANGUAGE_COLORS = {
    "Python":     "#3572A5",
    "JavaScript": "#F1E05A",
    "TypeScript": "#2B7489",
    "HTML":       "#E34C26",
    "CSS":        "#563D7C",
    "Rust":       "#DEA584",
    "Go":         "#00ADD8",
    "Shell":      "#89E051",
    "Bash":       "#89E051",
    "TOML":       "#FF6B6B",
    "INI":        "#AAAAAA",
    "JSON":       "#292929",
    "Markdown":   "#083FA1",
}
DEFAULT_COLOR = "#ff4444"


def format_number(num):
    return f"{num:,}"


def load_exclude_languages():
    """Read excluded languages from repos.json so the SVG respects the same
    filter list used during counting."""
    repos_file = Path("repos.json")
    if not repos_file.exists():
        return set()
    with open(repos_file) as f:
        config = json.load(f)
    # Normalise to lowercase for case-insensitive comparison
    return {lang.lower() for lang in config.get("exclude_languages", [])}


def generate_svg(loc_data, exclude_languages=None):
    if exclude_languages is None:
        exclude_languages = set()

    total_code  = int(loc_data.get("Total", {}).get("code",  0))
    total_files = int(loc_data.get("Total", {}).get("files", 0))

    if total_code == 0:
        print("Warning: total code count is 0 — SVG will be empty", file=sys.stderr)

    # Extract, filter, and sort languages
    # FIX: apply exclude_languages from repos.json so filtered langs don't
    # appear in the SVG (previously exclude_languages was defined in repos.json
    # but never read by this script).
    languages = {}
    for lang, stats in loc_data.items():
        if lang == "Total":
            continue
        if lang.lower() in exclude_languages:
            print(f"Debug: excluding '{lang}' per repos.json", file=sys.stderr)
            continue
        if isinstance(stats, dict) and "code" in stats and stats["code"] > 0:
            languages[lang] = stats["code"]

    top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:6]

    if not top_langs:
        print("Error: no language data found after filtering — cannot generate SVG", file=sys.stderr)
        sys.exit(1)

    # Dynamic height based on actual number of language rows
    row_height   = 28
    header_space = 170
    footer_pad   = 30
    height = header_space + len(top_langs) * row_height + footer_pad

    svg = f"""<svg width="800" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="800" height="{height}" fill="#000000" rx="10"/>

  <!-- Total lines -->
  <text x="40" y="55" font-family="monospace" font-size="32" fill="#ffffff">{format_number(total_code)}</text>
  <text x="40" y="78" font-family="monospace" font-size="13" fill="#aaaaaa">LINES OF CODE</text>

  <!-- Total files -->
  <text x="760" y="55" font-family="monospace" font-size="24" fill="#ffffff" text-anchor="end">{format_number(total_files)}</text>
  <text x="760" y="75" font-family="monospace" font-size="12" fill="#aaaaaa" text-anchor="end">FILES</text>

  <!-- Divider -->
  <line x1="30" y1="100" x2="770" y2="100" stroke="#30363d" stroke-width="1"/>

  <!-- Section heading -->
  <text x="40" y="132" font-family="monospace" font-size="15" fill="#ff4444">TOP LANGUAGES</text>
"""

    y         = header_space
    max_width = 450
    max_code  = top_langs[0][1] if top_langs else 1

    for lang, code in top_langs:
        bar_width = max(1, (code / max_code) * max_width)
        bar_color = LANGUAGE_COLORS.get(lang, DEFAULT_COLOR)
        svg += f"""
  <text x="40" y="{y}" font-family="monospace" font-size="13" fill="#ffffff">{lang}</text>
  <rect x="180" y="{y - 13}" width="{max_width}" height="16" fill="#21262d" rx="4"/>
  <rect x="180" y="{y - 13}" width="{bar_width:.1f}" height="16" fill="{bar_color}" rx="4"/>
  <text x="650" y="{y}" font-family="monospace" font-size="12" fill="#cccccc">{format_number(code)}</text>
"""
        y += row_height

    svg += "\n</svg>"
    return svg


def main():
    loc_file = Path("loc-data.json")

    if not loc_file.exists():
        print("Error: loc-data.json not found", file=sys.stderr)
        sys.exit(1)

    if loc_file.stat().st_size == 0:
        print("Error: loc-data.json is empty", file=sys.stderr)
        sys.exit(1)

    with open(loc_file) as f:
        try:
            raw_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: loc-data.json is not valid JSON — {e}", file=sys.stderr)
            sys.exit(1)

    if not isinstance(raw_data, dict) or not raw_data:
        print("Error: loc-data.json has unexpected structure or is empty", file=sys.stderr)
        sys.exit(1)

    print(f"Debug: top-level keys: {list(raw_data.keys())[:10]}", file=sys.stderr)

    # count-loc.sh now always produces flat Tokei output (languages + Total at
    # top level), so we no longer need the multi-repo merge path.
    if "Total" not in raw_data:
        print("Error: 'Total' key missing — loc-data.json may be malformed.", file=sys.stderr)
        sys.exit(1)

    print(f"Debug: total code={raw_data['Total'].get('code', 0)}, "
          f"files={raw_data['Total'].get('files', 0)}", file=sys.stderr)

    # FIX: load exclude list from repos.json and pass it in
    exclude_languages = load_exclude_languages()
    print(f"Debug: excluding languages: {exclude_languages}", file=sys.stderr)

    svg = generate_svg(raw_data, exclude_languages)

    with open("loc-stats.svg", "w") as f:
        f.write(svg)

    print("SVG generated successfully")


if __name__ == "__main__":
    main()