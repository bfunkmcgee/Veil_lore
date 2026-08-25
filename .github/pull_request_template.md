## Summary

<!-- What changed, in canon terms. Cite ruling IDs if any. -->

## Checklist

- [ ] Edited only authoritative sources (`Veil_Unified_World_Bible.md`, `veil_canon_ledger.json`, `Veil_Scenes.md`) — or this is an explicitly flagged toolchain/infra change
- [ ] Ran `cd codex && python3 build.py --no-docx` and committed the regenerated files with the source edits
- [ ] `python3 harness.py` prints `INVARIANTS: PASS` (paste the last two lines below)
- [ ] Canon change: ledger `rulings_log` entry added (next contiguous `sequence`, correct `kind`) **and** matching changelog entry added via `add_ruling.py`
- [ ] No hand edits to generated files (`codex/README.md`, Core, Annexes) or derived ledger meta
- [ ] New Tier 2 lint warnings: none / justified below

## Harness output

```
<!-- paste the INVARIANTS / LINT lines here -->
```
