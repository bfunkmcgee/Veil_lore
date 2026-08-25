#!/usr/bin/env python3
"""Veil Codex build: canonical source set -> generated distribution targets.

ARCHITECTURE (rulings EN1/EN2). There is no single source of truth. There are three
authoritative, hand-edited sources:

    1. Veil_Unified_World_Bible.md  — world / reference source
    2. veil_canon_ledger.json       — structured canon source
    3. Veil_Scenes.md               — dramatized narrative source

and generated distribution targets, produced only by this script:

    Veil_Core_World_Bible.md (+ .docx)
    Veil_Operational_Annexes.md (+ .docx)
    Veil_Scenes.docx

Run build.py after ANY source edit, then harness.py.
Usage:  python3 build.py [--no-docx]
"""
from pathlib import Path
import json, re, subprocess, sys

LEDGER = "veil_canon_ledger.json"
README = "README.md"
MASTER = "Veil_Unified_World_Bible.md"
CORE   = "Veil_Core_World_Bible.md"
ANNEX  = "Veil_Operational_Annexes.md"
SCENES = "Veil_Scenes.md"


def read(p):  return Path(p).read_text(encoding="utf-8")
def write(p, s): Path(p).write_text(s, encoding="utf-8")


def revision(master_text):
    """Single source for the revision string: the master's own header."""
    m = re.search(r"^### Second Reconciled Edition[^\n]*", master_text, re.M)
    assert m, "build: revision header not found in master"
    return m.group(0)


def local_resources(*texts):
    """Local (non-URL) markdown image/link resources referenced by the given texts."""
    found = set()
    for t in texts:
        for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", t):
            r = m.group(1).strip()
            if not r.startswith(("http://", "https://", "#")):
                found.add(r)
    return sorted(found)


def preflight(*texts):
    """Fail the build if any referenced local asset is missing (EN2)."""
    missing = [r for r in local_resources(*texts) if not Path(r).exists()]
    if missing:
        raise FileNotFoundError(f"build: missing local resources {missing} — cannot reproduce artifacts")
    return local_resources(*texts)


def _slice(text, start, end):
    i = text.find(start); j = text.find(end, i)
    assert i >= 0 and j > i, f"build: anchor not found -> {start[:50]!r}"
    return text[i:j]


def build(master_text):
    """Return (core_text, annex_text) derived from master_text."""
    core, blocks = master_text, []

    seg = _slice(core, "## VII.1 Tactical Manual: Vine Squad Small-Unit Tactics [C]", "## VII.4 The Armory")
    blocks.append(("Field Doctrine Manuals (Vine Tactical Manual · Steel Roses Urban Shadows · Bramble Kit VFM-23-8)", seg))
    core = core.replace(seg, "\n**VII.1–VII.3 Field Doctrine Manuals [C]** — *moved to the Operational Annexes volume; "
                             "the Vine manual carries a Raven Doctrine Desk Field Errata (ruling IA1).*\n\n", 1)

    ai = core.find("## VII.4 The Armory"); aj = core.find("# BOOK VIII — THE GAME LAYER", ai)
    armory = core[ai:aj]; new_armory, cats = armory, []
    for m in re.finditer(r"### VII\.4\.\d ([^\n]+)", armory):
        s = armory.find("**Assault rifles", m.end()); e = armory.find("\n---", s)
        e = e if e > 0 else len(armory)
        cat = armory[s:e]
        cats.append(f"### Catalog — {m.group(1)}\n\n{cat.strip()}")
        new_armory = new_armory.replace(cat, "*Full 52-arm catalog — see the Operational Annexes volume.*\n", 1)
    assert len(cats) == 5, f"build: expected 5 catalogs, found {len(cats)}"
    core = core.replace(armory, new_armory, 1)
    blocks.append(("The Armory — Full Weapon Catalogs (260 arms across five houses)", "\n\n---\n\n".join(cats)))

    seg = _slice(core, "## VIII.1 Whispers of the Veil — Campaign Codex [G]", "## VIII.3 SANDLINE — The Kestrel Campaign")
    blocks.append(("Game Documents (Whispers of the Veil Campaign Codex · SANDLINE Design Document)", seg))
    core = core.replace(seg, "\n**VIII.1–VIII.2 Game Documents [G]** — *moved to the Operational Annexes volume.*\n\n", 1)

    core = core.replace("# The Veil Codex — Unified World Bible", "# The Veil Codex — Core World Bible", 1)

    annex = [f"# The Veil Codex — Operational Annexes\n\n{revision(master_text)}\n"]
    for title, seg in blocks:
        annex.append(f"\n---\n\n# ANNEX: {title}\n\n{seg.strip()}\n")
    return core, "\n".join(annex)


def docx(md_path):
    out = md_path.replace(".md", ".docx")
    subprocess.run(["pandoc", md_path, "-o", out, "--resource-path=."], check=True)
    return out


def sync_metadata_and_readme(master_text):
    """Derive ledger metadata from rulings_log and generate README (EN2.2).

    latest_ruling_sequence and engineering_revision are DERIVED, never hand-typed,
    because hand-maintained counters drift.
    """
    db = json.loads(Path(LEDGER).read_text(encoding="utf-8"))
    rl = db["rulings_log"]
    max_seq = max(r["sequence"] for r in rl)
    latest_eng = max((r for r in rl if r.get("kind") == "engineering"), key=lambda r: r["sequence"])
    db["meta"]["latest_ruling_sequence"] = max_seq
    db["meta"]["engineering_revision"] = latest_eng["id"]
    Path(LEDGER).write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8")

    Path(README).write_text(render_readme(db), encoding="utf-8")
    print(f"metadata synced: {len(rl)} rulings, latest sequence {max_seq}, engineering {latest_eng['id']}")
    return db


SCOPE_LABEL = {"all": "all canon", "interior_state": "interior state only",
               "external_and_metaphysical_fact": "external fact",
               "default": "default", "same_generation_wording_only": "same-generation wording only"}


def render_readme(db):
    """Single renderer for README — harness compares its output byte-for-byte (EN2.3)."""
    rl = db["rulings_log"]; m = db["meta"]
    max_seq = max(r["sequence"] for r in rl)
    status = (f"**Canon {m['canon_revision']} · build {m['build_revision']} · "
              f"narrative {m['narrative_revision']} · engineering {m['engineering_revision']} · "
              f"{len(rl)} rulings (latest sequence {max_seq})**")
    prec = "\n".join(
        f"{p['rank']}. `{p['source']}` — {SCOPE_LABEL.get(p.get('scope',''), p.get('scope',''))}"
        + (f" ({p['rule']})" if p.get("rule") else "")
        for p in m["canon_precedence"])
    return README_TEMPLATE.format(status=status, precedence=prec)


README_TEMPLATE = """# The Veil Codex — Complete Package
{status}

*This file is GENERATED by build.py from veil_canon_ledger.json — do not hand-edit.*

## Authoritative source files
*Canon content is hand-authored; derived metadata fields are maintained by build.py.*
- `Veil_Unified_World_Bible.md` — world/reference master
- `veil_canon_ledger.json` — structured canon (rulings with sequence + kind, entities, timeline)
- `Veil_Scenes.md` — dramatized narrative (machine-readable scene IDs)

## Assets
- `rodar_sprite.png` — required to reproduce the Core DOCX

## Generated targets (do not edit)
`README.md` · `Veil_Core_World_Bible.md/.docx` · `Veil_Operational_Annexes.md/.docx` · `Veil_Scenes.docx`

## Toolchain
```
python3 build.py            # regenerate all targets (fails on missing assets or DOCX errors)
python3 build.py --no-docx  # markdown only
python3 harness.py          # must print INVARIANTS: PASS
```
Requires `pandoc`.

**Tier 1 invariants (blocking):** build freshness · asset completeness · ledger schema across
all canonical collections · id uniqueness · ref resolution against canonical entity ids ·
derived-metadata currency · contiguous ruling sequence · ordered ruling/changelog parity ·
README parity · timeline anchors · scene ID parity · structural text defects · ruled-canon
regressions.
**Tier 2 lint (advisory):** mechanical publication defects and editorial phrasing watches.

## Canon precedence
*Rendered from `veil_canon_ledger.json` → `meta.canon_precedence`.*

{precedence}
"""


def main(with_docx=True):
    master = read(MASTER)
    sync_metadata_and_readme(master)
    core, annex = build(master)
    write(CORE, core); write(ANNEX, annex)
    print(f"built: core {len(core):,} chars | annex {len(annex):,} chars")
    assets = preflight(master, core, annex, read(SCENES))
    print(f"preflight OK: {len(assets)} local resource(s) present {assets}")
    if with_docx:
        for md in (CORE, ANNEX, SCENES):
            print("  docx:", docx(md))   # exceptions propagate: a failed target fails the build


if __name__ == "__main__":
    main(with_docx="--no-docx" not in sys.argv)
