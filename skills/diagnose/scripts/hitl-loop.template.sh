#!/usr/bin/env bash
set -euo pipefail

# Human-in-the-loop repro loop for bugs that cannot be driven fully by the agent.
# Copy this file into a scratch/debug location before editing it for a specific bug.

BUG_LABEL="${BUG_LABEL:-describe-the-bug}"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="${OUT_DIR:-.cruise/debug/${BUG_LABEL}-${RUN_ID}}"
mkdir -p "$OUT_DIR"

cat <<PROMPT
[Cruise diagnose HITL loop]

1. Reproduce the bug manually.
2. Paste the exact observation into:
   $OUT_DIR/observation.txt
3. Add any copied logs, screenshots, HAR files, or terminal output under:
   $OUT_DIR/
4. Press Enter here when the artifact is ready.

PROMPT

read -r _

if [ ! -s "$OUT_DIR/observation.txt" ]; then
  echo "Missing $OUT_DIR/observation.txt" >&2
  exit 1
fi

echo "Captured HITL observation:"
sed -n '1,120p' "$OUT_DIR/observation.txt"
echo
echo "Artifacts written under: $OUT_DIR"
