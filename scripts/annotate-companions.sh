#!/bin/bash
# annotate-companions.sh — append a "## Required Companion Plugins" section
# to each agent markdown that references skills owned by other plugins.
# Idempotent: skips files that already contain the section header.
set -eo pipefail

cd "$(dirname "$0")/.."
OWNERSHIP_SH="$(pwd)/scripts/ownership.sh"

annotated=0
skipped=0

bash "$OWNERSHIP_SH" list_of agent | while IFS=$'\t' read -r name owner; do
  file="plugins/$owner/agents/$name.md"
  [ -f "$file" ] || continue

  if grep -q '^## Required Companion Plugins' "$file"; then
    skipped=$((skipped+1))
    continue
  fi

  # Build the companion set.
  refs=$(grep -oE '\bpnge-[a-z-]+:[a-z0-9][a-z0-9-]*' "$file" 2>/dev/null | sort -u || true)
  companions=$(echo "$refs" | awk -F: '{print $1}' | sort -u | grep -v "^${owner}$" | grep -v '^$' || true)
  [ -n "$companions" ] || { skipped=$((skipped+1)); continue; }

  {
    printf '\n'
    printf '## Required Companion Plugins\n\n'
    printf 'This agent is shipped by `%s`. It references skills in other plugins — install the companions below for full coverage. If a companion is not installed, the agent will still run and will note which pathway is unavailable.\n\n' "$owner"
    printf '| Companion plugin | Skills referenced |\n'
    printf '|---|---|\n'
    for c in $companions; do
      used=$(echo "$refs" | grep "^${c}:" | awk -F: '{print $2}' | paste -sd ',' - | sed 's/,/, /g')
      printf '| `%s` | %s |\n' "$c" "$used"
    done
    printf '\nInstall any missing companion with:\n\n'
    printf '```bash\n'
    for c in $companions; do
      printf 'claude plugin install %s@claude-pnge\n' "$c"
    done
    printf '```\n'
  } >> "$file"

  echo "annotated: $file"
  annotated=$((annotated+1))
done

echo
echo "Done (see above). Run this script again to verify idempotency."
