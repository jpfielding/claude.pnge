#!/bin/bash
# companion-plugins.sh — for each agent and command, compute the set of
# non-owner plugins it references, and emit a single-block suggestion.
# Read-only: does not modify files. Operators paste the output into the
# agent/command body under a "Required companion plugins" heading.
set -eo pipefail

cd "$(dirname "$0")/.."
OWNERSHIP_SH="$(pwd)/scripts/ownership.sh"

process() {
  local kind="$1"   # agent | command
  bash "$OWNERSHIP_SH" list_of "$kind" | while IFS=$'\t' read -r name owner; do
    local subdir
    if [ "$kind" = agent ]; then subdir=agents; else subdir=commands; fi
    local file="plugins/$owner/$subdir/$name.md"
    [ -f "$file" ] || { echo "MISSING: $file" >&2; continue; }

    # Pull every distinct `<plugin>:<id>` reference.
    local refs
    refs=$(grep -oE '\bpnge-[a-z-]+:[a-z0-9][a-z0-9-]*' "$file" 2>/dev/null \
           | sort -u)
    local companions
    companions=$(echo "$refs" | awk -F: '{print $1}' | sort -u | grep -v "^${owner}$" || true)

    if [ -n "$companions" ]; then
      echo "=== $kind: $name (owner: $owner) ==="
      echo "Companion plugins (needed for full behavior):"
      for c in $companions; do
        local used
        used=$(echo "$refs" | grep "^${c}:" | tr '\n' ' ')
        echo "  $c — refs: $used"
      done
      echo
    fi
  done
}

echo "### AGENTS"
process agent
echo "### COMMANDS"
process command
