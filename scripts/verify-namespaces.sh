#!/bin/bash
# verify-namespaces.sh — two checks:
#   1. No `pnge:<x>` orphans (stale prefix from pre-marketplace era).
#   2. Every known skill/agent reference in plugins/**/ uses its owner's plugin prefix.
# Runs fast. Exits non-zero on any finding.
set -eo pipefail

cd "$(dirname "$0")/.."
OWNERSHIP_SH="$(pwd)/scripts/ownership.sh"

# Scan plugins markdown + golang/python reference files.
mapfile_into() {
  # bash 3.2 has no `mapfile`; accumulate into an array via a file descriptor.
  :
}
FILES=$(find plugins -type f \( -name '*.md' -o -name '*.go' -o -name '*.py' -o -name '*.sh' \))

fail=0

# --- Check 1: no legacy `pnge:` prefix ---
orphans=$({ echo "$FILES" | xargs grep -n 'pnge:[a-z0-9]' 2>/dev/null || true; } | head -30)
if [ -n "$orphans" ]; then
  echo "FAIL: legacy 'pnge:<x>' references remain:"
  echo "$orphans"
  fail=1
else
  echo "OK: no legacy 'pnge:<x>' refs"
fi

# --- Check 2: every skill/agent reference points to the correct owner plugin ---
check_refs() {
  local kind="$1"
  bash "$OWNERSHIP_SH" list_of "$kind" | while IFS=$'\t' read -r name owner; do
    wrong=$({ echo "$FILES" \
      | xargs grep -n -E "\\b[a-z0-9-]+:${name}([^a-z0-9-]|\$)" 2>/dev/null \
      || true; } | grep -vE "\\b${owner}:${name}([^a-z0-9-]|\$)" || true)
    if [ -n "$wrong" ]; then
      echo "FAIL: $kind '$name' referenced with wrong plugin prefix (owner: $owner):"
      echo "$wrong" | head -5
      exit 99
    fi
  done
}

if ! check_refs skill; then fail=1; fi
if ! check_refs agent; then fail=1; fi

exit "$fail"
