# Contributing to Veil_lore

All lore lives in `codex/` as a self-validating package: three hand-authored
sources, a deterministic build, and a harness of blocking invariants. Every change
goes through the same loop, and CI enforces it on every pull request.

## Quickstart

```bash
git clone https://github.com/bfunkmcgee/Veil_lore
cd Veil_lore/codex
python3 build.py --no-docx   # regenerate targets (markdown only)
python3 harness.py           # expect: INVARIANTS: PASS / LINT: clean
```

Requirements: Python 3.10+ (standard library only). `pandoc` is required only if
you want local DOCX output (`python3 build.py` without the flag); CI builds DOCX
for you as workflow artifacts.

## What you may edit

**Sources (hand-edited):**
- `codex/Veil_Unified_World_Bible.md` — the world/reference master
- `codex/veil_canon_ledger.json` — structured canon (see the schema notes in `meta.schema_notes`)
- `codex/Veil_Scenes.md` — dramatized scenes

**Generated (never hand-edit; the harness byte-checks them):**
- `codex/README.md`, `codex/Veil_Core_World_Bible.md`, `codex/Veil_Operational_Annexes.md`
- ledger `meta.latest_ruling_sequence` and `meta.engineering_revision` (derived by build.py)

Found a typo in the Core bible or the Annexes? Fix it **in the master**, rebuild,
and commit — the generated files will follow.

`docs/` holds strategy documents outside the build system; edit freely.

## The edit loop

Always run the tools from inside `codex/` (paths are cwd-relative):

```bash
cd codex
# edit source(s)
python3 build.py --no-docx
python3 harness.py           # must print INVARIANTS: PASS
git add -A && git commit     # commit sources + regenerated targets together
```

## Making a canon change (ruling required)

Canon changes are recorded twice, and the harness enforces that the two records
match in order:

1. Append a ruling to `rulings_log` in the ledger — unique `id`, `sequence` =
   previous max + 1, `kind` (one of `canon`, `continuity`, `narrative`,
   `integration`, `build`, `engineering`, `editorial`, `provisional`), `date`,
   and the full `decision` text.
2. Add the matching changelog entry to the master via the helper (entry text must
   start with `**<ID> — `):
   ```bash
   python3 add_ruling.py my_entry.txt
   ```
3. Rebuild, run the harness, commit.

Adding or updating an **entity** in the ledger? Give it a globally unique `id`, use
`ref` for cross-references, and include the mandatory `status` object
(`identity_status`, `narrative_status`, `game_state_status`, `unfiled`).

Open canon questions don't need a ruling — edit the master's
`# CURRENT OPEN CANON QUESTIONS` section.

## Reading a CI failure

The `canon / rebuild + invariants` check runs the same loop you run locally:

- **"Committed files must match a fresh rebuild"** failed → you edited a source
  without rerunning `build.py --no-docx` (or hand-edited a generated file). Rebuild
  and commit the result.
- **"Canon harness"** failed → read the lines starting with `✗`; each names the
  file and the violated invariant (stale build, broken ruling sequence,
  ledger/changelog order divergence, unresolved `ref`, missing status field,
  scene-ID mismatch, ruled-canon regression, …).
- **Tier 2 lint** (`•` lines) never fails the build — but if your change introduces
  a new warning, say why in the PR.

## Pull requests

Use the checklist in the PR template. The short version: sources only, rebuilt,
`INVARIANTS: PASS`, ruling + changelog entry for canon changes, no hand edits to
generated files.
