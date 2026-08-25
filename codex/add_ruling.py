#!/usr/bin/env python3
"""Append a changelog entry for a ruling, safely.

Three hand-insertions in a row silently landed at character 1 because
`str.find` returned -1 and `t[:j+2]` quietly became `t[:1]`. This helper
asserts the anchor exists, inserts before the open-questions section
(always the changelog tail), and verifies order against the ledger.
"""
from pathlib import Path
import json, re, sys

MASTER = "Veil_Unified_World_Bible.md"
LEDGER = "veil_canon_ledger.json"
OQ = "# CURRENT OPEN CANON QUESTIONS"


def add(entry_text: str) -> None:
    m = Path(MASTER)
    t = m.read_text(encoding="utf-8")
    rid = re.match(r"\*\*([A-Z][A-Za-z0-9.]*\d(?:\.\d)?) — ", entry_text)
    assert rid, "entry must start with **ID — "
    assert f"**{rid.group(1)} — " not in t, f"{rid.group(1)} already in changelog"
    i = t.find(OQ)
    assert i > 0, "open-questions section not found"
    head = t[:i].rstrip().rstrip("-").rstrip()
    t = head + "\n\n" + entry_text.strip() + "\n\n---\n\n" + t[i:]
    m.write_text(t, encoding="utf-8")

    led = [r["id"] for r in json.loads(Path(LEDGER).read_text(encoding="utf-8"))["rulings_log"]]
    mst = re.findall(r"\*\*([A-Z][A-Za-z0-9.]*\d(?:\.\d)?) — ", t.split("# CANON CHANGELOG")[1])
    assert led == mst, f"order broken: ledger tail {led[-3:]} vs master tail {mst[-3:]}"
    assert t.startswith("# The Veil Codex — Unified World Bible"), "H1 damaged"
    print(f"added {rid.group(1)}; changelog order verified ({len(mst)} rulings)")


if __name__ == "__main__":
    add(Path(sys.argv[1]).read_text(encoding="utf-8"))
