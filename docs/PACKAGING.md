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

## Recommended Repository Structure

```
pnge-research-skills/
├── README.md                    # Overview, install instructions, WVU-specific notes
├── LICENSE                      # Apache 2.0 or MIT
├── Makefile                     # package-all, validate-all, test targets
├── .env.example                 # Template for API keys (never commit real keys)
│
├── skills/
│   ├── eia-data/                # Phase 0 — already exists
│   │   ├── SKILL.md
│   │   └── references/
│   ├── usgs-produced-waters/    # Phase 1
│   │   ├── SKILL.md
│   │   └── references/
│   ├── usgs-minerals/           # Phase 1
│   ├── netl-edx/                # Phase 1
│   ├── wvges-wells/             # Phase 2
│   ├── boem-offshore/           # Phase 2
│   ├── fracfocus/               # Phase 2
│   ├── epa-enviro/              # Phase 2
│   ├── usgs-pubs/               # Phase 3
│   ├── doe-osti/                # Phase 3
│   ├── li-mg-prospector/        # Phase 4 (agent)
│   └── pnge-research-assistant/ # Phase 4 (agent)
│
├── dist/                        # Built .skill files (gitignored)
│   ├── eia-data.skill
│   ├── usgs-produced-waters.skill
│   └── ...
│
├── shared/                      # Common code/config shared across skills
│   ├── credential_resolver.go   # Shared credential pattern
│   ├── credential_resolver.sh
│   └── api_patterns.md          # Common REST/JSON patterns
│
├── evals/                       # Test cases for all skills
│   ├── usgs-produced-waters/
│   │   └── evals.json
│   └── ...
│
└── docs/
    ├── SETUP.md                 # First-time setup (keys, accounts)
    ├── CONTRIBUTING.md          # How to add a new skill
    ├── DATA_SOURCES.md          # ← the plan doc we already built
    └── WVU_ACCESS.md            # WVU-specific: library proxy, Enverus, IHS
```

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

## Recommended Approach for This Project

Given the context (WVU undergrad, research lab, Li/Mg focus):

1. **Start with a GitHub repo** — it's the most flexible and version-controlled
2. **Build `.skill` files via Makefile** for easy Claude.ai upload
3. **Use `shared/` for DRY credential management** across all skills
4. **Write a SETUP.md** that walks a new WVU student through:
   - Cloning the repo
   - Getting free API keys (EIA, NETL EDX, EPA)
   - Checking WVU library access (Enverus, IHS, OnePetro)
   - Installing skills to their preferred surface
5. **Consider a Claude Code Plugin** later if the skills prove useful
   beyond your immediate lab group

The key insight: **build each skill as a standalone directory that works
independently**, but package the collection as a cohesive repo with shared
infrastructure. A consumer can grab one skill or the whole set.
