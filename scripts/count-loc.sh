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
done

echo "Running Tokei across all cloned repos..."
tokei "$WORKDIR" --output json > loc-data.json

echo "LOC data written to loc-data.json"

echo "--- Summary ---"
jq '{total_code: .Total.code, total_files: .Total.files}' loc-data.json