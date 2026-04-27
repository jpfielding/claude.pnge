#!/bin/bash
# ownership.sh — read-only helpers over scripts/ownership.tsv.
# Works on macOS bash 3.2 (no associative arrays).
#
# Usage:
#   owner_of <kind> <name>            # echo plugin or empty
#   list_of  <kind>                   # echo "<name>\t<plugin>" lines
#   list_plugins                      # echo unique plugin names
#   selftest                          # sanity-check counts
#
# Run directly with no args → selftest.

set -e
OWNERSHIP_TSV="$(cd "$(dirname "$0")" && pwd)/ownership.tsv"

owner_of() {
  local kind="$1" name="$2"
  awk -F'\t' -v k="$kind" -v n="$name" '
    /^#/ || NF<3 { next }
    $1==k && $2==n { print $3; exit }
  ' "$OWNERSHIP_TSV"
}

list_of() {
  local kind="$1"
  awk -F'\t' -v k="$kind" '
    /^#/ || NF<3 { next }
    $1==k { print $2"\t"$3 }
  ' "$OWNERSHIP_TSV"
}

list_plugins() {
  awk -F'\t' '/^#/ || NF<3 {next} {print $3}' "$OWNERSHIP_TSV" | sort -u
}

selftest() {
  local ns na nc
  ns=$(list_of skill   | wc -l | tr -d ' ')
  na=$(list_of agent   | wc -l | tr -d ' ')
  nc=$(list_of command | wc -l | tr -d ' ')
  echo "Plugins: $(list_plugins | wc -l | tr -d ' ')"
  echo "Skills:  $ns"
  echo "Agents:  $na"
  echo "Cmds:    $nc"
  [ "$ns" -eq 76 ] || { echo "FAIL: expected 76 skills"; exit 1; }
  [ "$na" -eq 12 ] || { echo "FAIL: expected 12 agents"; exit 1; }
  [ "$nc" -eq 12 ] || { echo "FAIL: expected 12 commands"; exit 1; }

  local repo_root
  repo_root="$(cd "$(dirname "$0")/.." && pwd)"
  if [ -d "$repo_root/skills" ]; then
    for d in "$repo_root/skills"/*/; do
      [ -d "$d" ] || continue
      n=$(basename "$d")
      [ -n "$(owner_of skill "$n")" ] || echo "WARN: skill '$n' on disk has no owner"
    done
  fi
  if [ -d "$repo_root/agents" ]; then
    for f in "$repo_root/agents"/*.md; do
      [ -f "$f" ] || continue
      n=$(basename "$f" .md)
      [ -n "$(owner_of agent "$n")" ] || echo "WARN: agent '$n' on disk has no owner"
    done
  fi
  if [ -d "$repo_root/commands" ]; then
    for f in "$repo_root/commands"/*.md; do
      [ -f "$f" ] || continue
      n=$(basename "$f" .md)
      [ -n "$(owner_of command "$n")" ] || echo "WARN: command '$n' on disk has no owner"
    done
  fi
  echo "OK"
}

# Dispatch
case "${1:-selftest}" in
  owner_of)      shift; owner_of "$@" ;;
  list_of)       shift; list_of "$@" ;;
  list_plugins)  list_plugins ;;
  selftest|"")   selftest ;;
  *) echo "unknown: $1"; exit 2 ;;
esac
