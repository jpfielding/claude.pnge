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

## Actual Repository Structure (v0.9.0)

The authoritative skill tree lives in [`README.md`](../README.md) — see its
"Project Structure" section for the full directory layout. Plugin currently
ships **76 skills (43 data access, 33 computational)**, **12 agents**, and
**12 commands**.

Top-level layout:

```
claude.pnge/
├── README.md                    # Overview, install, full skill tree
├── LICENSE                      # Apache-2.0
├── .env.example                 # Template for API keys (never commit real keys)
├── .gitignore
│
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest (name: pnge, v0.9.0)
│
├── skills/                      # 76 skills (43 data access + 33 computational)
├── agents/                      # 12 research and engineering agents
├── commands/                    # 12 slash commands
└── docs/
    ├── TOKENS.md                # API key acquisition guide
    ├── DATA_SOURCES.md          # Authoritative data-source reference
    └── PACKAGING.md             # Distribution and packaging guide (this file)
```

For the full per-skill listing, see [`README.md`](../README.md) and
[`docs/DATA_SOURCES.md`](DATA_SOURCES.md).

---

## Distribution Channels

### 1. GitHub Repository (Primary — Team/Academic)

**Audience:** WVU PNGE lab, collaborators, open-source community
**Method:** Public or private GitHub repo

```bash
# Consumer installs to Claude Code (personal)
git clone https://github.com/{user}/pnge-research-skills.git
cp -r pnge-research-skills/skills/* ~/.claude/skills/

# Or project-level (shared via repo)
cd my-research-project
cp -r ../pnge-research-skills/skills/* .claude/skills/
git add .claude/skills/
git commit -m "Add PNGE research data skills"
```

**Pros:** Version controlled, PRs for contributions, issues for bugs,
         CI can run evals on every change, works for Claude Code natively.
**Cons:** Manual install steps; Claude.ai users need to re-upload .skill files.

### 2. `.skill` ZIP Files (Claude.ai Upload)

**Audience:** Claude.ai users (individual)
**Method:** Upload through Settings > Customize > Skills

```bash
# Build all .skill files
make package-all
# => dist/usgs-produced-waters.skill
# => dist/eia-data.skill
# => ...

# Or build one
python -m scripts.package_skill skills/usgs-produced-waters dist/
```

Then upload each `.skill` file in Claude.ai Settings.

**Pros:** Works in Claude.ai web/mobile/desktop, no CLI needed.
**Cons:** Individual per-user; no centralized management on free/Pro plans.

### 3. Claude Code Plugin (Marketplace)

**Audience:** Broader Claude Code user base
**Method:** Bundle skills into a plugin for the marketplace

```
pnge-research-plugin/
├── plugin.json              # Plugin manifest
├── skills/
│   ├── usgs-produced-waters/
│   ├── usgs-minerals/
│   └── ...
└── README.md
```

**Pros:** Discoverable in marketplace, one-command install.
**Cons:** Requires plugin packaging spec compliance; newer ecosystem.

### 4. Claude API Workspace (Programmatic)

**Audience:** Developers building on the Claude API
**Method:** Upload via `/v1/skills` endpoints

```bash
# Upload a skill to your API workspace
curl -X POST https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: multipart/form-data" \
  -F "file=@dist/usgs-produced-waters.skill"
```

**Pros:** Workspace-wide, all members get access.
**Cons:** Requires API access; separate from Claude.ai skills.

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

## Makefile Targets

```makefile
SKILLS_DIR := skills
DIST_DIR := dist
SKILL_CREATOR := /mnt/skills/examples/skill-creator

.PHONY: validate-all package-all test clean

validate-all:
	@for skill in $(SKILLS_DIR)/*/; do \
		echo "Validating $$skill..."; \
		python $(SKILL_CREATOR)/scripts/quick_validate.py $$skill; \
	done

package-all: validate-all
	@mkdir -p $(DIST_DIR)
	@for skill in $(SKILLS_DIR)/*/; do \
		python $(SKILL_CREATOR)/scripts/package_skill.py $$skill $(DIST_DIR); \
	done

test:
	@echo "Running evals..."
	# Integrate with skill-creator eval runner

clean:
	rm -rf $(DIST_DIR)
```

---

## Installing the Plugin

```bash
# Install directly from GitHub into Claude Code
claude plugin install pnge@jpfielding/claude.pnge

# Or clone and point Claude Code at the local directory
git clone https://github.com/jpfielding/claude.pnge.git
claude --plugin-dir ./claude.pnge

# Validate all skill frontmatter
claude plugin validate .
```

## Packaging Individual Skills for Claude.ai

Each skill directory can be zipped into a `.skill` file and uploaded at
Settings > Customize > Skills in Claude.ai:

```bash
# Package one skill
cd claude.pnge
zip -r dist/eia-data.skill skills/eia-data/

# Package all skills
mkdir -p dist
for d in skills/*/; do
  name=$(basename "$d")
  zip -r "dist/${name}.skill" "$d"
done
```

## Adding a New Skill

1. Create `skills/<name>/SKILL.md` with valid YAML frontmatter:
   - `name`: kebab-case, ≤64 chars
   - `description`: ≤1024 chars, no `<` or `>`, include trigger phrases
2. Add reference files under `skills/<name>/references/` for anything
   over ~30 lines of detail (schema docs, Go client examples, API tables)
3. Follow the credential resolution pattern in `docs/TOKENS.md`
4. Run `claude plugin validate .` to check frontmatter
5. Update `README.md` skill count and tables
6. Update `docs/DATA_SOURCES.md` with the new skill entry
