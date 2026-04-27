# CHANGELOG

All notable changes to the claude-pnge project.

## [1.0.0] — 2026-04-27

**Breaking change.** The monolithic `pnge` plugin is retired. `claude.pnge` is now a **Claude Code marketplace** of 8 themed plugins. Users install only the plugins they need.

### Migration from v0.9.x

If you currently have `pnge@jpfielding/claude.pnge` installed, run this once:

```bash
# 1. Remove the old monolithic plugin
claude plugin uninstall pnge

# 2. Add the new marketplace
claude plugin marketplace add jpfielding/claude.pnge

# 3. Install what you actually need (everything = the 8 lines below)
claude plugin install pnge-core@claude-pnge
claude plugin install pnge-federal-data@claude-pnge
claude plugin install pnge-state-regulatory@claude-pnge
claude plugin install pnge-economics@claude-pnge
claude plugin install pnge-patents@claude-pnge
claude plugin install pnge-well-engineering@claude-pnge
claude plugin install pnge-geochem-pw@claude-pnge
claude plugin install pnge-engineering-science@claude-pnge
```

Common subset recipes:

| Focus | Install |
|---|---|
| Li/Mg prospecting (most common) | `pnge-core`, `pnge-state-regulatory`, `pnge-geochem-pw` |
| Appalachia field engineering | `pnge-core`, `pnge-state-regulatory`, `pnge-well-engineering` |
| ChBE coursework / tutoring | `pnge-engineering-science` (optionally `pnge-geochem-pw`) |
| TEA / LCA + supply-chain | `pnge-core`, `pnge-economics`, `pnge-patents` |
| Regulatory / disposal / seismicity | `pnge-core`, `pnge-state-regulatory`, `pnge-federal-data` |

### Skill invocation syntax changed

Skill references now namespace by plugin:

| Old (v0.9.x) | New (v1.0.0) |
|---|---|
| `pnge:eia-data` | `pnge-core:eia-data` |
| `pnge:tx-rrc` | `pnge-state-regulatory:tx-rrc` |
| `pnge:frac-design` | `pnge-well-engineering:frac-design` |
| `pnge:phreeqc-geochem` | `pnge-geochem-pw:phreeqc-geochem` |
| `pnge:patentsview` | `pnge-patents:patentsview` |
| `pnge:fred-prices` | `pnge-economics:fred-prices` |
| `pnge:wri-aqueduct` | `pnge-federal-data:wri-aqueduct` |
| `pnge:pnge-tutor` (agent) | `pnge-engineering-science:pnge-tutor` |

See `docs/DATA_SOURCES.md` for the full skill → plugin mapping. All 12 slash commands (`/prospect`, `/doctor`, `/regulatory-screen`, etc.) keep their names — only their owning plugin changed.

### Added

- `.claude-plugin/marketplace.json` — marketplace catalog listing 8 plugins.
- `plugins/<name>/.claude-plugin/plugin.json` × 8 — per-plugin manifests with `version: 1.0.0`.
- `scripts/ownership.tsv` + `scripts/ownership.sh` — authoritative skill/agent/command ownership map.
- `scripts/rewrite-namespaces.sh`, `scripts/verify-namespaces.sh`, `scripts/annotate-companions.sh` — migration helpers.
- "Required Companion Plugins" section appended to every cross-cutting agent, listing which sibling plugins it depends on.

### Changed

- `/doctor` redesigned as a static-catalog health check that covers all 76 skills across the 8 plugins. It probes credentials + endpoints; it does **not** try to walk sibling plugin caches (those are isolated by Claude Code). Use the built-in `/plugin` slash command for installed-plugin inventory.

### Structural moves

- `pnge-production` merged into `pnge-well-engineering` — a single workflow plugin instead of a no-agent/no-command orphan.
- `kggs-well-logs`, `macrostrat` → `pnge-well-engineering` (they serve petrophysics/stratigraphy, not literature).
- `patentsview` + `dle-patent-scout` + `/patent-landscape` → `pnge-patents` (standalone patent-landscape plugin).
- `wri-aqueduct` → `pnge-federal-data` (environmental/sustainability input, not economics).
- `ospar-discharges` → `pnge-state-regulatory` (discharge-compliance regulation).

### Removed

- `.claude-plugin/plugin.json` (monolithic manifest).
- Empty root `skills/`, `agents/`, `commands/` directories.

---

## [0.9.0] — 2026-04-21

Adversarial review fixes: 6 new skills, 3 merges, 4 cuts, `/doctor` rewrite.

## [0.8.0] — 2026-04-15

Added 15 skills, 6 agents, 6 commands from adversarial review.

## [0.7.0] — 2026-04-14

66 skills. Updated docs and plugin manifest.

## [0.6.0] — Earlier

Tax-delinquent mineral property skills for WV, PA, OH.

## [0.5.0] — Earlier

Local operations review skills.
