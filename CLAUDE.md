# Veil_lore — guide for Claude sessions

Canon repository for **The Veil** fictional world. The package in `codex/` is a
self-validating canon system with its own build and invariant harness. Your job in
this repo is almost always: edit an authoritative source, rebuild, validate, commit.

## Architecture (rulings EN1/EN2 — a canonical source *set*, deliberately not single-source)

**Authoritative, hand-edited sources — the only files you edit for lore changes:**

| File | Role |
|---|---|
| `codex/Veil_Unified_World_Bible.md` | World/reference master: 11 Books, Appendices, `# CANON CHANGELOG`, `# CURRENT OPEN CANON QUESTIONS` tail |
| `codex/veil_canon_ledger.json` | Structured canon: entities, `rulings_log` (with `sequence` + `kind`), timeline, scenes index, `meta` |
| `codex/Veil_Scenes.md` | Dramatized narrative; scenes carry `<!-- scene-id: ... -->` markers parity-checked against the ledger |

**Generated — NEVER hand-edit** (the harness byte-compares them against a fresh rebuild):
`codex/README.md`, `codex/Veil_Core_World_Bible.md`, `codex/Veil_Operational_Annexes.md`,
and the ledger meta fields `latest_ruling_sequence` / `engineering_revision` (derived by build.py).
DOCX renditions are CI artifacts (see below), never committed.

`docs/` holds strategy documents (SANDLINE roadmap/integration plan for the sister game repo
`github.com/bfunkmcgee/ThinShot`); they are plain documents outside the build system.

## The edit loop

All codex paths are cwd-relative — **always run the tools from `codex/`**.

```bash
cd codex
# edit one or more of the three sources
python3 build.py --no-docx
python3 harness.py          # must print: INVARIANTS: PASS
git add -A && git commit    # sources + regenerated targets together, one commit
```

Requirements: Python 3.10+ (stdlib only). `pandoc` is needed only for DOCX; the
normal loop is `--no-docx`.

## Adding a canon ruling (required for any canon change)

Both halves are required; the harness enforces ordered ledger↔changelog parity and a
contiguous `sequence` 1..N.

1. **Ledger first** — append to `rulings_log` in `codex/veil_canon_ledger.json`:
   unique `id` (thematic prefix + number, e.g. `KC6`, `CV2`),
   `sequence` = previous max + 1,
   `kind` ∈ `canon | continuity | narrative | integration | build | engineering | editorial | provisional`,
   `date` (YYYY-MM-DD), `decision` (full prose), optional `affected_entities` (entity ids).
2. **Changelog second** — write the matching entry to a temp file starting with
   `**<ID> — Title.** body`, then:
   ```bash
   python3 add_ruling.py /path/to/entry.txt
   ```
   It inserts before `# CURRENT OPEN CANON QUESTIONS` and asserts order against the ledger.
3. Rebuild + harness + commit as above (build.py re-derives `latest_ruling_sequence`).

Open canon questions need no ruling: edit the master's `# CURRENT OPEN CANON QUESTIONS` tail.

## Ledger contract (from `meta.schema_notes` — read it before schema work)

- Canon tags: `C` canon · `G` game-state · `D` dossier candidate · `P` proposed ·
  `X` conflict-resolved · `R` ratified · `?` unfiled. The `tag` string field is
  deprecated display text — software reasons from `status.*`.
- Every canonical entity carries a `status` object with **all** of
  `identity_status` (C/D/P/R), `narrative_status` (C/D/P/R),
  `game_state_status` (G or "n/a"), and boolean `unfiled`.
- `id` values are globally unique across the ledger; cross-references use `ref`
  and must resolve to a canonical entity id.
- Canon precedence (pinned by the harness; do not change):
  1 `rulings` (all canon, highest sequence governs) → 2 `scenes` (interior state only) →
  3 `doctrine_and_event_records` (external fact) → 4 `merged_source_prose` (default) →
  5 `R4` (same-generation wording only).
- Revision line lives in the master's `### Second Reconciled Edition …` header
  (currently canon CR3 · build CR2.1 · narrative NF2) and is cross-checked
  against ledger meta.

## Validation semantics

- **Tier 1 invariants are blocking** (harness exit 1): build freshness, README
  byte-parity, ledger schema/id/ref integrity, contiguous ruling sequence,
  ledger↔changelog ordered parity, timeline anchors, scene-ID parity, structural
  text defects, ruled-canon regression guards.
- **Tier 2 lint is advisory** (printed, exit 0) — editorial phrasing watches. New
  warnings should be justified in the PR, not silenced.
- The ruled-canon regression phrases hard-coded in `harness.py` are **intentional
  guards**, not bugs. Never weaken `harness.py`, `build.py`, or `add_ruling.py` to
  get green; toolchain changes are engineering rulings (kind `engineering`/`build`)
  and need the ruling recipe above.

## Repo hygiene

- CI (`.github/workflows/canon-ci.yml`) mirrors the loop: rebuild → committed files
  must byte-match → harness must pass. A red "match a fresh rebuild" check means
  someone forgot to run build.py or hand-edited a generated file.
- The `docx` CI job (manual dispatch or `v*` tags) installs pandoc and uploads all
  DOCX as the `veil-codex-docx` workflow artifact.
- Everything is LF (`.gitattributes` enforces it); the harness is byte-sensitive.
- `codex/` gains no new files — only source edits and build outputs. Repo
  infrastructure lives at the root.
- Two READMEs: root `README.md` is hand-written; `codex/README.md` is **generated**.
