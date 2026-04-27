#!/bin/bash
# rewrite-namespaces.sh — rewrite `pnge:<skill-or-agent>` refs in plugins/**/*.md
# to `<owner-plugin>:<name>` using scripts/ownership.tsv.
#
# Idempotent: rerunning is a no-op once the sweep has been applied.
# Use BSD sed -i '' for macOS compatibility.
set -eo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
OWNERSHIP_SH="$REPO_ROOT/scripts/ownership.sh"

# ----- Build the replacement table -----
# Emits lines: <old-pattern>\t<new-replacement>
replacements() {
  # Skills: pnge:<skill> → <owner>:<skill>
  bash "$OWNERSHIP_SH" list_of skill | while IFS=$'\t' read -r name owner; do
    printf 'pnge:%s\t%s:%s\n' "$name" "$owner" "$name"
  done
  # Agents: pnge:<agent> → <owner>:<agent>  (rare; some docs reference agents this way)
  bash "$OWNERSHIP_SH" list_of agent | while IFS=$'\t' read -r name owner; do
    printf 'pnge:%s\t%s:%s\n' "$name" "$owner" "$name"
  done
  # Known stale alias: tnav-reservoir-sim was renamed to tnav.
  printf 'pnge:tnav-reservoir-sim\tpnge-geochem-pw:tnav\n'
}

FILES=$(find plugins -type f -name '*.md')

count_refs() {
  # Stable count even when nothing matches. grep returns 1 on no-match; we swallow that.
  { echo "$FILES" | xargs grep -h 'pnge:[a-z0-9]' 2>/dev/null || true; } | wc -l | tr -d ' '
}

count_total_before=$(count_refs)
echo "Before: $count_total_before 'pnge:...' references across $(echo "$FILES" | wc -l | tr -d ' ') markdown files"

# Apply longest-old-pattern first so `pnge:tnav-reservoir-sim` rewrites before `pnge:tnav`.
replacements | awk -F'\t' '{ print length($1)"\t"$0 }' | sort -rn | cut -f2- | while IFS=$'\t' read -r old new; do
  # macOS BSD sed requires `-i ''`; skill names are kebab-case so no regex metachars.
  # No leading word boundary (BSD -E lacks \b). Trailing negative char class ensures
  # `pnge:tnav` doesn't gobble `pnge:tnav-reservoir-sim` — and because we apply
  # longest-old-pattern first, the alias is rewritten before the short form runs.
  echo "$FILES" | xargs sed -i '' -E "s/${old}([^a-z0-9-]|\$)/${new}\\1/g"
done

count_total_after=$(count_refs)
echo "After:  $count_total_after 'pnge:...' references remaining (should be 0)"

if [ "$count_total_after" -ne 0 ]; then
  echo
  echo "Residue:"
  { echo "$FILES" | xargs grep -n 'pnge:[a-z0-9]' 2>/dev/null || true; } | head -30
  exit 1
fi
echo "OK"
