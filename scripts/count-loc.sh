#!/bin/bash
set -e

echo "Reading repos.json..."
REPOS=$(jq -r '.repos[]' repos.json)
EXCLUDE_LANGS=$(jq -r '.exclude_languages // [] | join(",")' repos.json)

WORKDIR="loc-temp"
rm -rf "$WORKDIR"
mkdir "$WORKDIR"

echo "Cloning repositories..."
for REPO in $REPOS; do
    echo "Cloning $REPO..."
    TARGET="$WORKDIR/$(basename $REPO)"
    git clone --depth 1 "https://github.com/$REPO.git" "$TARGET"    
    
echo "Running Tokei across all cloned repos..."
# FIX: run tokei once across the entire workdir so it produces a single flat
# JSON (languages as top-level keys + a "Total" key).  The old approach of
# running tokei per-repo and merging with `jq * ` did a shallow object merge
# that overwrote language counts instead of summing them.
tokei "$WORKDIR" --output json > loc-data.json

echo "LOC data written to loc-data.json"

# Optional: show a quick summary
echo "--- Summary ---"
jq '{total_code: .Total.code, total_files: .Total.files}' loc-data.json