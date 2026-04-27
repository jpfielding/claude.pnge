#!/bin/bash
# move-files.sh — relocate skills/agents/commands into plugins/<theme>/ via git mv.
# Idempotent: skips entries already moved. Must be run from repo root.
set -eo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
OWNERSHIP="$REPO_ROOT/scripts/ownership.sh"

moved=0
skipped=0

move_one() {
  # $1=kind (skill|agent|command), $2=src-path, $3=dest-path
  local kind="$1" src="$2" dest="$3"
  if [ ! -e "$src" ]; then
    if [ -e "$dest" ]; then
      skipped=$((skipped+1))
      return 0
    fi
    echo "FAIL: neither source nor destination exists for $kind: $src → $dest" >&2
    return 1
  fi
  mkdir -p "$(dirname "$dest")"
  git mv "$src" "$dest"
  moved=$((moved+1))
}

# Skills: skills/<name>/  → plugins/<plugin>/skills/<name>/
while IFS=$'\t' read -r name plugin; do
  move_one skill "skills/$name" "plugins/$plugin/skills/$name"
done < <(bash "$OWNERSHIP" list_of skill)

# Agents: agents/<name>.md → plugins/<plugin>/agents/<name>.md
while IFS=$'\t' read -r name plugin; do
  move_one agent "agents/$name.md" "plugins/$plugin/agents/$name.md"
done < <(bash "$OWNERSHIP" list_of agent)

# Commands: commands/<name>.md → plugins/<plugin>/commands/<name>.md
while IFS=$'\t' read -r name plugin; do
  move_one command "commands/$name.md" "plugins/$plugin/commands/$name.md"
done < <(bash "$OWNERSHIP" list_of command)

echo "Moved: $moved"
echo "Already-moved (skipped): $skipped"
