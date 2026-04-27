# PNGE Research Skills — Packaging & Distribution Guide

## The Native Format: `.skill` Files

A `.skill` file is a ZIP archive containing the skill directory. The skill-creator
includes `scripts/package_skill.py` that validates and packages automatically.

```
usgs-produced-waters.skill  (ZIP)
└── usgs-produced-waters/
    ├── SKILL.md              # Required — frontmatter + instructions
    ├── references/
    │   ├── schema.md
    │   ├── formations.md
    │   └── golang_client.go
    └── scripts/              # Optional — deterministic helpers
        └── download_db.sh
```

Validation rules enforced at packaging time:
- SKILL.md must exist with valid YAML frontmatter
- Required fields: `name` (kebab-case, ≤64 chars), `description` (≤1024 chars)
- Allowed frontmatter keys: name, description, license, allowed-tools, metadata, compatibility
- Excludes: __pycache__, node_modules, *.pyc, .DS_Store, evals/

---

## Actual Repository Structure (v1.0.0 — marketplace)

The authoritative layout and per-plugin skill listing live in
[`README.md`](../README.md) and [`docs/DATA_SOURCES.md`](DATA_SOURCES.md).
The repository is a **Claude Code marketplace** (not a single plugin) shipping
**8 themed plugins** totaling 76 skills / 12 agents / 12 commands.

Top-level layout:

```
claude.pnge/
├── README.md                       # Marketplace overview + install recipes
├── CHANGELOG.md                    # v0.9 → v1.0 breaking change + migration
├── LICENSE                         # Apache-2.0
├── .env.example                    # Template for API keys (never commit real keys)
├── .gitignore
│
├── .claude-plugin/
│   └── marketplace.json            # Marketplace catalog (claude-pnge, v1.0.0)
│
├── plugins/                        # One directory per sub-plugin
│   ├── pnge-core/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/ agents/ commands/
│   ├── pnge-federal-data/
│   ├── pnge-state-regulatory/
│   ├── pnge-economics/
│   ├── pnge-patents/
│   ├── pnge-well-engineering/
│   ├── pnge-geochem-pw/
│   └── pnge-engineering-science/
│
├── scripts/
│   ├── ownership.tsv               # Authoritative skill/agent/command → plugin map
│   ├── ownership.sh                # Read-only helpers over ownership.tsv
│   ├── rewrite-namespaces.sh       # One-shot migration sweep (can be rerun)
│   ├── verify-namespaces.sh        # Positive + negative namespace check
│   ├── annotate-companions.sh      # Append companion-plugin tables to agents
│   └── move-files.sh               # One-shot git mv helper (historical)
│
└── docs/
    ├── TOKENS.md                   # API key acquisition guide (plugin-keyed)
    ├── DATA_SOURCES.md             # Per-skill data-source reference + plugin index
    └── PACKAGING.md                # This file
```

---

## Distribution Channels

### 1. Claude Code Marketplace (Primary)

**Audience:** Claude Code users.
**Method:** `claude plugin marketplace add` + per-plugin `claude plugin install`.

```bash
# Add the marketplace once
claude plugin marketplace add jpfielding/claude.pnge
# or for local development against a checkout:
claude plugin marketplace add ./claude.pnge

# Install only the plugins you need
claude plugin install pnge-core@claude-pnge
claude plugin install pnge-state-regulatory@claude-pnge
# ... etc.
```

Common subset recipes live in [`CHANGELOG.md`](../CHANGELOG.md) and
[`README.md`](../README.md).

**Pros:** Discoverable, per-plugin install, versioned by plugin.
**Cons:** Requires `claude plugin` CLI; not for Claude.ai consumers.

### 2. `.skill` ZIP Files (Claude.ai Upload)

**Audience:** Claude.ai users (individual)
**Method:** Upload through Settings > Customize > Skills

```bash
# Build all .skill files (across all 8 plugins)
mkdir -p dist
for d in plugins/*/skills/*/; do
  name=$(basename "$d")
  ( cd "$(dirname "$d")" && zip -r - "$name" ) > "dist/${name}.skill"
done
```

Then upload each `.skill` file in Claude.ai Settings.

**Pros:** Works in Claude.ai web/mobile/desktop, no CLI needed.
**Cons:** Individual per-user; no centralized management on free/Pro plans.

### 3. Claude API Workspace (Programmatic)

**Audience:** Developers building on the Claude API.
**Method:** Upload individual `.skill` files via `/v1/skills` endpoints.

```bash
# Upload a skill to your API workspace
curl -X POST https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: multipart/form-data" \
  -F "file=@dist/usgs-produced-waters.skill"
```

**Pros:** Workspace-wide, all members get access.
**Cons:** Requires API access; separate from the Claude Code marketplace.

---

## Credential Management (Critical for Distribution)

Skills that require API keys MUST NOT bundle credentials. Follow the EIA pattern:

```
Resolution order (per skill):
  1. ~/.config/{service}/credentials  (file, chmod 600)
  2. Environment variable             (e.g., EIA_API_KEY)
  3. Prompt user with signup URL

Shared template (.env.example):
  EIA_API_KEY=
  NETL_EDX_API_KEY=
  EPA_API_KEY=
  # USGS, BOEM, BSEE, WVGES, FracFocus = no key needed
```

The `shared/credential_resolver.go` and `.sh` files implement this pattern once.
Each skill's SKILL.md references the shared pattern with service-specific details.

---

## Validating the Marketplace

```bash
# Validate every sub-plugin's manifest (no `claude plugin marketplace validate` exists)
for p in plugins/*/; do claude plugin validate "$p" || exit 1; done

# Confirm the namespace sweep is clean (no legacy pnge: refs, every ref on-owner)
bash scripts/verify-namespaces.sh
```

---

## Packaging Individual Skills for Claude.ai

Each skill directory can be zipped into a `.skill` file and uploaded at
Settings > Customize > Skills in Claude.ai:

```bash
# Package one skill
zip -r dist/eia-data.skill -j - plugins/pnge-core/skills/eia-data/ > /dev/null

# Package all skills across the marketplace
mkdir -p dist
for d in plugins/*/skills/*/; do
  name=$(basename "$d")
  parent=$(dirname "$d")
  ( cd "$parent" && zip -r - "$name" ) > "dist/${name}.skill"
done
```

## Adding a New Skill

1. **Choose the owning plugin** (one of the 8). If the new skill doesn't fit any existing plugin's charter, propose a new sub-plugin rather than a junk-drawer add.
2. **Register the ownership first** — add a `skill` row to `scripts/ownership.tsv`, then run `bash scripts/ownership.sh selftest` to verify counts. Skill names must be globally unique across the marketplace (the ownership map and namespace scripts rely on uniqueness).
3. Create `plugins/<owner>/skills/<name>/SKILL.md` with valid YAML frontmatter:
   - `name`: kebab-case, ≤64 chars
   - `description`: ≤1024 chars, no `<` or `>`, include trigger phrases
4. Add reference files under `plugins/<owner>/skills/<name>/references/` for anything over ~30 lines of detail (schema docs, Go client examples, API tables).
5. Follow the credential resolution pattern in `docs/TOKENS.md`.
6. If the skill needs a credential, update the credential map in `docs/TOKENS.md`.
7. Update `docs/DATA_SOURCES.md` (the plugin index + the per-category table).
8. Bump `plugins/<owner>/.claude-plugin/plugin.json` `version` — otherwise installed users won't refresh.
9. If the skill is referenced by cross-plugin agents, rerun `bash scripts/annotate-companions.sh` (idempotent).
10. Validate: `claude plugin validate plugins/<owner>`.
